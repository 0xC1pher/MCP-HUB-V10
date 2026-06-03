"""
Vision Specialist MCP: Especialista en análisis visual multimodal
- Análisis de diagramas para Architect MCP
- Debugging visual para Developer MCP  
- Comparación de screenshots para Tester MCP
- Integración con VisionHub FastVLM-WebGPU
"""
import asyncio
from typing import Dict, Any, List

from mcps.base_mcp import BaseMCP
from core.vision.vision_hub import vision_hub, AnalyzeRequest

class VisionSpecialistMCP(BaseMCP):
    """
    MCP especializado en capacidades visuales
    """
    
    def __init__(self, mcp_id: str, hub):
        super().__init__(mcp_id, hub)
        self.vision_hub = vision_hub
    
    async def _execute_task(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if method == "analyze_image":
            image_b64 = params.get("image_base64")
            prompt = params.get("prompt", "Describe the image in detail.")
            if not image_b64:
                raise ValueError("image_base64 required")
            
            request = AnalyzeRequest(image_base64=image_b64, prompt=prompt)
            response = await self.vision_hub.app.post("/analyze", json=request.dict())
            data = response.json()
            
            # Save to memory for multimodal unificada
            session_id = params.get('session_id', 'default')
            await self.hub.add_turn(
                session_id, 
                "vision_specialist", 
                data["caption"], 
                metadata={
                    'confidence': data["confidence"],
                    'from_cache': data["from_cache"],
                    'fallback_used': data["fallback_used"],
                    'processing_time_ms': data["processing_time_ms"],
                    'prompt': prompt,
                    'image_hash': self.vision_hub.cache.get_key(image_b64, prompt)
                }
            )
            
            return {
                "caption": data["caption"],
                "confidence": data["confidence"],
                "from_cache": data["from_cache"],
                "fallback_used": data["fallback_used"],
                "processing_time_ms": data["processing_time_ms"],
                "memory_saved": True
            }
        
        elif method == "batch_analyze":
            images = params.get("images", [])  # List of {"base64": str, "prompt": str}
            results = []
            for img_data in images:
                result = await self._execute_task("analyze_image", img_data)
                results.append(result)
            return {"batch_results": results}
        
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def get_capabilities(self) -> List[str]:
        return [
            "analyze_image",
            "batch_analyze",
            "compare_screenshots",  # Future
            "diagram_analysis"     # Future
        ]
