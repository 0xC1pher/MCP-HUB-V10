"""
LLM Provider Interface
Manejo real de interacciones con Modelos de Lenguaje
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import structlog
import os
import json

logger = structlog.get_logger()

class LLMProvider(ABC):
    """Interfaz abstracta para proveedores de LLM"""
    
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        """Generar texto plano"""
        pass
    
    @abstractmethod
    async def generate_json(self, prompt: str, schema: Dict[str, Any], system_prompt: str = "") -> Dict[str, Any]:
        """Generar JSON estructurado validado contra esquema"""
        pass

class MockLLMProvider(LLMProvider):
    """
    Proveedor temporal para desarrollo local sin API Key.
    NOTA: En producción, esto se reemplaza por OpenAI/Anthropic Provider.
    """
    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        logger.warning("using_mock_llm_generation", prompt_preview=prompt[:50])
        return f"# Generated code based on: {prompt[:30]}..."

    async def generate_json(self, prompt: str, schema: Dict[str, Any], system_prompt: str = "") -> Dict[str, Any]:
        logger.warning("using_mock_llm_json", schema_keys=list(schema.keys()))
        return {}

class ProductionLLMFactory:
    """
    Factory para obtener el proveedor configurado.
    
    Nota: Esta clase está marcada como obsoleta. Se recomienda usar ModelRouter directamente.
    """
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ProductionLLMFactory, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            from .model_router import ModelRouter
            import os
            
            # Ruta al archivo de configuración de modelos
            config_path = os.environ.get(
                'MODEL_CONFIG_PATH',
                os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'model_config.json')
            )
            
            # Inicializar el ModelRouter con la configuración
            self._model_router = ModelRouter(config_path=config_path)
            self._initialized = True
    
    @classmethod
    def get_provider(cls, config: Optional[Dict[str, Any]] = None) -> LLMProvider:
        """
        Obtiene una instancia del proveedor configurado.
        
        Args:
            config: Configuración opcional para el proveedor (obsoleto, se usa la configuración del archivo)
            
        Returns:
            LLMProvider: Instancia del proveedor configurado
            
        Note:
            Este método está marcado como obsoleto. Se recomienda usar ModelRouter directamente.
        """
        import warnings
        warnings.warn(
            "ProductionLLMFactory está obsoleto. Usa ModelRouter directamente.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Si se proporciona configuración, crear una nueva instancia de ModelRouter
        if config:
            from .model_router import ModelRouter
            return ModelRouter()
            
        # De lo contrario, usar la instancia singleton
        if not cls._instance:
            cls._instance = ProductionLLMFactory()
            
        return cls._instance._model_router
