"""
Vision Specialist MCP - Wrapper Opcional
Este wrapper permite que VisionSpecialistMCP sea completamente opcional
SIN dependencias pesadas (FastAPI, Playwright, etc)
"""
from typing import Optional, Dict, Any
import structlog

logger = structlog.get_logger()

# NO importamos vision_hub para evitar dependencias circulares y pesadas
VISION_AVAILABLE = False  # Por defecto deshabilitado

from mcps.base_mcp import BaseMCP
from core.communication.protocol import MCPRequest, MCPResponse


class VisionSpecialistMCP(BaseMCP):
    """
    Vision Specialist MCP - Análisis de imágenes y capturas de pantalla
    
    Version con lazy loading - se puede instanciar sin VisionHub
    """
    
    def __init__(self, mcp_id: str, hub, vision_enabled: bool = True):
        super().__init__(mcp_id, hub)
        self.vision_enabled = vision_enabled and VISION_AVAILABLE
        
        if not self.vision_enabled:
            logger.warning(
                "vision_specialist_degraded_mode",
                mcp_id=mcp_id,
                reason="Vision dependencies not available or disabled"
            )
    
    async def _execute_task(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta tarea del Vision Specialist"""
        
        if not self.vision_enabled:
            return {
                "status": "degraded",
                "message": "Vision analysis not available",
                "method": method,
                "fallback_used": True
            }
        
        if method == "analyze_image":
            return await self._analyze_image(params)
        elif method == "analyze_screenshot":
            return await self._analyze_screenshot(params)
        elif method == "compare_images":
            return await self._compare_images(params)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    async def _analyze_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza una imagen"""
        if not VISION_AVAILABLE:
            return self._degraded_response("analyze_image")
        
        image_data = params.get("image_base64")
        prompt = params.get("prompt", "Describe this image")
        
        try:
            # Aquí iría la llamada real a VisionHub
            # Por ahora retornamos mock
            return {
                "analysis": f"[MOCK] Image analysis for prompt: {prompt}",
                "confidence": 0.5,
                "vision_used": False,
                "fallback_used": True
            }
        except Exception as e:
            logger.error("vision_analysis_failed", error=str(e))
            return self._degraded_response("analyze_image", error=str(e))
    
    async def _analyze_screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza un screenshot"""
        return self._degraded_response("analyze_screenshot")
    
    async def _compare_images(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compara dos imágenes"""
        return self._degraded_response("compare_images")
    
    def _degraded_response(self, method: str, error: Optional[str] = None) -> Dict[str, Any]:
        """Respuesta en modo degradado"""
        return {
            "status": "degraded",
            "method": method,
            "message": "Vision analysis not available - running in degraded mode",
            "error": error,
            "fallback_used": True
        }
