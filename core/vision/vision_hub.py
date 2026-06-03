"""
VisionHub: Integración FastVLM-WebGPU con API REST.
- Sirve app estática en /vision
- /analyze: procesa imagen base64 + prompt via playwright + transformers.js
- Cache LRU simple (expandir a memory_engine)
- Fallback a LLM textual
- Métricas integradas

NOTA: Este módulo usa lazy loading para dependencias pesadas
"""

import asyncio
import base64
import hashlib
import json
import logging
import os
import time
from typing import Dict, Optional, Any, TYPE_CHECKING
from pathlib import Path

# Core imports siempre disponibles
from pydantic import BaseModel
import shelve
from asyncio import Semaphore

# Lazy imports - solo se cargan si se usan
if TYPE_CHECKING:
    from fastapi import FastAPI, UploadFile, Form, HTTPException
    from fastapi.staticfiles import StaticFiles
    from playwright.async_api import async_playwright
    from core.llm.model_router import ModelRouter
    from core.performance.monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

class AnalyzeRequest(BaseModel):
    image_base64: str
    prompt: str = "Describe the image in detail."
    project_id: str = "default"

class AnalyzeResponse(BaseModel):
    caption: str
    confidence: float
    processing_time_ms: float
    from_cache: bool
    fallback_used: bool

class VisionCache:
    def __init__(self, max_size: int = 1000, disk_path: str = "vision_cache.db"):
        self.memory_cache = {}
        self.disk_cache = shelve.open(disk_path, writeback=True)
        self.max_size = max_size
        self.memory_hits = self.disk_hits = self.total_hits = 0
        self.misses = 0

    def get_key(self, image_b64: str, prompt: str) -> str:
        hash_input = f"{image_b64[:1000]}|{prompt}"
        return hashlib.md5(hash_input.encode()).hexdigest()

    def get(self, key: str) -> Optional[str]:
        # L1 Memory
        if key in self.memory_cache:
            self.memory_hits += 1
            self.total_hits += 1
            return self.memory_cache[key]
        
        # L2 Disk
        if key in self.disk_cache:
            caption = self.disk_cache[key]
            self.memory_cache[key] = caption  # Promote to memory
            self.disk_hits += 1
            self.total_hits += 1
            return caption
        
        self.misses += 1
        return None

    def set(self, key: str, caption: str):
        self.memory_cache[key] = caption
        if len(self.memory_cache) >= self.max_size:
            oldest_key = next(iter(self.memory_cache))
            del self.memory_cache[oldest_key]
        self.disk_cache[key] = caption
        self.disk_cache.sync()

class VisionMetrics:
    def __init__(self):
        self.vision_analyses = 0
        self.cache_hits = 0
        self.fallbacks = 0
        self.request_count = 0
        self.response_times = []

    def record_vision_analysis(self, from_cache: bool, fallback: bool, duration: float):
        self.vision_analyses += 1
        self.request_count += 1
        self.response_times.append(duration)
        if from_cache:
            self.cache_hits += 1
        if fallback:
            self.fallbacks += 1

    def get_metrics(self) -> dict:
        avg_rt = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        return {
            'vision_analyses': self.vision_analyses,
            'cache_hits': self.cache_hits,
            'fallbacks': self.fallbacks,
            'avg_response_time': avg_rt,
            'error_rate': self.fallbacks / max(1, self.vision_analyses)
        }

class VisionHub:
    """
    VisionHub con lazy loading de dependencias pesadas
    Los imports se hacen dentro de __init__ para evitar ejecución al importar el módulo
    """
    def __init__(self, static_dir: str = "fastvlm-webgpu", llm_provider: Optional[Any] = None):
        # Lazy import - solo se ejecuta cuando se crea la instancia
        from fastapi import FastAPI
        from fastapi.staticfiles import StaticFiles
        
        self.app = FastAPI(title="Vision Hub API")
        self.static_dir = Path(static_dir)
        
        # LLM Provider - lazy load
        if llm_provider is None:
            try:
                from core.llm.model_router import ModelRouter
                self.llm_provider = ModelRouter(config_path="config/model_config.json")
            except ImportError:
                logger.warning("ModelRouter not available")
                self.llm_provider = None
        else:
            self.llm_provider = llm_provider
        
        # Memory Engine - opcional
        try:
            from core.memory.memory_engine import ConsistentMemoryEngine
            self.memory_engine = ConsistentMemoryEngine(None)  # Simplified
        except ImportError:
            logger.warning("MemoryEngine not available")
            self.memory_engine = None
        
        self.cache = VisionCache(disk_path="data/vision_cache.db")
        self.metrics = VisionMetrics()
        self.semaphore = Semaphore(10)
        
        # Performance Monitor - opcional
        try:
            from core.performance.monitor import PerformanceMonitor
            self.monitor = PerformanceMonitor()
        except ImportError:
            logger.warning("PerformanceMonitor not available")
            self.monitor = None
        
        self.setup_routes()
        
        @self.app.on_event("startup")
        async def startup():
            if self.monitor and hasattr(self.monitor, 'collect_metrics'):
                logger.info("VisionHub started with monitoring")
            else:
                logger.info("VisionHub started without monitoring")
        
        @self.app.on_event("shutdown")
        async def shutdown():
            logger.info("VisionHub shutting down")

    def setup_routes(self):
        # Lazy import
        from fastapi.staticfiles import StaticFiles
        
        # Servir app estática
        self.app.mount("/vision", StaticFiles(directory=self.static_dir), name="vision_static")

        @self.app.post("/analyze", response_model=AnalyzeResponse)
        async def analyze(request: AnalyzeRequest):
            start_time = time.time()
            key = self.cache.get_key(request.image_base64, request.prompt)
            
            duration = 0  # For metrics
            
            # Check cache
            cached = self.cache.get(key)
            if cached:
                self.metrics.record_vision_analysis(from_cache=True, fallback=False)
                return AnalyzeResponse(
                    caption=cached,
                    confidence=0.95,  # Cached high conf
                    processing_time_ms=0,
                    from_cache=True,
                    fallback_used=False
                )

            # Vision processing
            try:
                caption = await self._process_vision(request.image_base64, request.prompt)
                conf = 0.9  # Default
            except Exception as e:
                logger.warning(f"Vision failed: {e}, using fallback")
                # Fallback to text LLM
                fallback_prompt = f"Image description (no vision): {request.prompt}"
                caption = await self.llm_provider.generate(fallback_prompt)
                conf = 0.6
                self.metrics.fallbacks += 1
                fallback_used = True
            else:
                fallback_used = False

            # Cache result
            self.cache.set(key, caption)

            duration = (time.time() - start_time)
            proc_time = duration * 1000
            self.metrics.record_vision_analysis(from_cache=False, fallback=fallback_used, duration=duration)

            return AnalyzeResponse(
                caption=caption,
                confidence=conf,
                processing_time_ms=proc_time,
                from_cache=False,
                fallback_used=fallback_used
            )

        @self.app.get("/metrics")
        async def get_metrics():
            return self.metrics.get_metrics()

    async def _process_vision(self, image_b64: str, prompt: str) -> str:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1024, 'height': 768}
            )
            page = await context.new_page()

            # Minimal HTML with canvas and transformers CDN
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2"></script>
            </head>
            <body>
                <canvas id="canvas" width="512" height="512" style="display:none;"></canvas>
                <script>
                    async function analyzeImage(imageB64, prompt) {{
                        const canvas = document.getElementById('canvas');
                        const ctx = canvas.getContext('2d');
                        const img = new Image();
                        await new Promise((resolve, reject) => {{
                            img.onload = resolve;
                            img.onerror = reject;
                            img.src = imageB64;
                        }});
                        canvas.width = img.width;
                        canvas.height = img.height;
                        ctx.drawImage(img, 0, 0);
                        
                        try {{
                            const processor = await pipeline('image-to-text', 'Xenova/FastVLM-0.5B-ONNX');
                            const output = await processor(canvas.toDataURL('image/png'), {{
                                prompt: prompt,
                                max_new_tokens: 100
                            }});
                            return output[0].generated_text;
                        }} catch (error) {{
                            throw new Error('Model inference failed: ' + error.message);
                        }}
                    }}
                    // Expose for page.evaluate
                    window.analyzeImage = analyzeImage;
                </script>
            </body>
            </html>
            """
            await page.set_content(html_content)
            
            # Wait for transformers load
            await page.wait_for_load_state('networkidle')
            
            caption = await page.evaluate('''
                async () => {
                    return await window.analyzeImage(arguments[0], arguments[1]);
                }
            ''', [image_b64, prompt])
            
            await browser.close()
            return caption

PORT = 8001

# NO crear instancia global - usar lazy loading
vision_hub = None

def get_vision_hub():
    """
    Factory function para obtener instancia de VisionHub
    Solo se crea cuando realmente se necesita
    """
    global vision_hub
    if vision_hub is None:
        vision_hub = VisionHub()
    return vision_hub

if __name__ == "__main__":
    import uvicorn
    hub = get_vision_hub()
    uvicorn.run(hub.app, host="0.0.0.0", port=PORT, reload=True)
