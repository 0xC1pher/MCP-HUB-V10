"""
Model Router para el sistema MCP.

Este módulo proporciona funcionalidad para enrutar solicitudes a los modelos
de lenguaje apropiados según el rol del MCP.
"""

from typing import Dict, Optional, Any, Union
import logging
from pathlib import Path
import json
import aiohttp
import asyncio
from typing import List

from .provider import LLMProvider

logger = logging.getLogger(__name__)

class ModelRouter(LLMProvider):
    """
    Enruta las solicitudes a los modelos de lenguaje apropiados según el rol.
    
    Atributos:
        _model_mapping (Dict[str, str]): Mapeo de roles a nombres de modelos
        _model_params (Dict[str, Dict[str, Any]]): Parámetros específicos por modelo
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa el ModelRouter con la configuración proporcionada.
        
        Args:
            config_path: Ruta al archivo de configuración de modelos. Si no se proporciona,
                       se usan valores por defecto.
        """
        super().__init__()
        
        # Configuración por defecto
        self._model_mapping: Dict[str, str] = {
            "arquitecto": "gemma3:270m",
            "desarrollador": "gemma3:270m",
            "tester": "gemma3:270m",
            "orchestrator": "gemma3:270m",
            "default": "gemma3:270m",
            "json_generator": "gemma3:270m"
        }
        
        self._model_params: Dict[str, Dict[str, Any]] = {
            "gemma3:270m": {
                "temperature": 0.7,
                "max_tokens": 4000,
                "top_p": 0.9,
                "top_k": 40,
                "repeat_penalty": 1.1
            },
            "embeddinggemma:latest": {
                "temperature": 0.2,
                "max_tokens": 2000
            }
        }
        
        # Configuración de Ollama
        self._ollama_config = {
            "base_url": "http://localhost:11434",
            "timeout": 120,
            "max_retries": 3
        }
        
        # Cargar configuración personalizada si se proporciona
        if config_path:
            self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> None:
        """
        Carga la configuración de modelos desde un archivo JSON.
        
        Args:
            config_path: Ruta al archivo de configuración.
            
        Raises:
            FileNotFoundError: Si el archivo de configuración no existe.
            json.JSONDecodeError: Si el archivo no es un JSON válido.
        """
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                logger.warning(f"Archivo de configuración no encontrado: {config_path}")
                return
                
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Actualizar mapeo de modelos si está presente
            if "model_mapping" in config:
                self._model_mapping.update(config["model_mapping"])
                logger.info(f"Actualizado mapeo de modelos: {self._model_mapping}")
                
            # Actualizar parámetros de modelos si están presentes
            if "model_params" in config:
                for model, params in config["model_params"].items():
                    if model in self._model_params:
                        self._model_params[model].update(params)
                    else:
                        self._model_params[model] = params
                logger.info("Actualizados parámetros de modelos")
                
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar el archivo de configuración: {e}")
            raise
        except Exception as e:
            logger.error(f"Error al cargar la configuración: {e}")
            raise
    
    def get_model_for_role(self, role: str) -> str:
        """
        Obtiene el nombre del modelo para un rol específico.
        
        Args:
            role: Nombre del rol (ej: 'arquitecto', 'desarrollador')
            
        Returns:
            str: Nombre del modelo configurado para el rol
            
        Raises:
            ValueError: Si el rol no está configurado
        """
        role_lower = role.lower()
        if role_lower not in self._model_mapping:
            raise ValueError(f"Rol no configurado: {role}")
        return self._model_mapping[role_lower]
    
    def get_model_params(self, model_name: str) -> Dict[str, Any]:
        """
        Obtiene los parámetros para un modelo específico.
        
        Args:
            model_name: Nombre del modelo
            
        Returns:
            Dict[str, Any]: Parámetros del modelo o un diccionario vacío si no hay configuración
        """
        return self._model_params.get(model_name, {})
    
    def get_embedding_model(self) -> str:
        """
        Obtiene el nombre del modelo de embeddings.
        
        Returns:
            str: Nombre del modelo de embeddings
        """
        return "embeddinggemma:latest"
    
    def get_embedding_params(self) -> Dict[str, Any]:
        """
        Obtiene los parámetros para el modelo de embeddings.
        
        Returns:
            Dict[str, Any]: Parámetros del modelo de embeddings
        """
        return self._model_params.get("embeddinggemma:latest", {})
    
    def update_model_mapping(self, role: str, model_name: str) -> None:
        """
        Actualiza el mapeo de un rol a un modelo.
        
        Args:
            role: Nombre del rol a actualizar
            model_name: Nombre del modelo a asignar
        """
        self._model_mapping[role.lower()] = model_name
        logger.info(f"Actualizado mapeo: {role} -> {model_name}")
    
    def list_available_models(self) -> Dict[str, Any]:
        """
        Devuelve información sobre los modelos disponibles.
        
        Returns:
            Dict[str, Any]: Diccionario con la configuración de modelos
        """
        return {
            "model_mapping": self._model_mapping,
            "model_params": self._model_params
        }
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: str = "",
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Genera texto utilizando el modelo especificado.
        
        Args:
            prompt: El prompt para la generación
            system_prompt: Instrucciones del sistema (opcional)
            model: Nombre del modelo a usar (opcional, usa el modelo por defecto si no se especifica)
            **kwargs: Parámetros adicionales para la generación
            
        Returns:
            str: Texto generado por el modelo
            
        Raises:
            ValueError: Si el modelo no está configurado o hay un error en la generación
        """
        model_name = model or self._model_mapping.get("default", "gemma3:270m")
        params = self._model_params.get(model_name, {}).copy()
        params.update(kwargs)
        
        try:
            # Implementación básica usando requests síncrono para compatibilidad
            # En producción, debería usarse un cliente asíncrono
            import requests
            
            url = f"{self._ollama_config['base_url']}/api/generate"
            payload = {
                "model": model_name,
                "prompt": f"{system_prompt}\n\n{prompt}" if system_prompt else prompt,
                **params
            }
            
            response = requests.post(
                url,
                json=payload,
                timeout=self._ollama_config.get("timeout", 120)
            )
            response.raise_for_status()
            
            # Procesar la respuesta (formato de la API de Ollama)
            result = ""
            for line in response.text.splitlines():
                if line.strip():
                    chunk = json.loads(line)
                    if "response" in chunk:
                        result += chunk["response"]
                    
            return result
            
        except Exception as e:
            logger.error(f"Error en la generación con {model_name}: {str(e)}")
            raise ValueError(f"Error al generar texto: {str(e)}")
    
    async def generate_json(
        self, 
        prompt: str, 
        schema: Dict[str, Any],
        system_prompt: str = ""
    ) -> Dict[str, Any]:
        """
        Genera una respuesta JSON validada contra un esquema.
        
        Args:
            prompt: El prompt para la generación
            schema: Esquema JSON para validar la salida
            system_prompt: Instrucciones del sistema (opcional)
            
        Returns:
            Dict[str, Any]: Diccionario con la respuesta validada
            
        Raises:
            ValueError: Si la generación falla o la respuesta no cumple con el esquema
        """
        # Construir el prompt para generación de JSON
        json_prompt = (
            f"{system_prompt}\n\n"
            f"Por favor, genera una respuesta en formato JSON que cumpla con el siguiente esquema:\n"
            f"{json.dumps(schema, indent=2)}\n\n"
            f"Prompt: {prompt}\n"
            "Respuesta (solo el JSON, sin comentarios ni texto adicional):"
        )
        
        try:
            # Obtener la respuesta del modelo
            response = await self.generate(
                prompt=json_prompt,
                system_prompt="",  # Ya incluido en el prompt
                model=self._model_mapping.get("json_generator", "gemma3:270m")
            )
            
            # Limpiar la respuesta (eliminar markdown si es necesario)
            if response.strip().startswith('```json'):
                response = response.split('```json')[1].split('```')[0].strip()
            elif response.strip().startswith('```'):
                response = response.split('```')[1].split('```')[0].strip()
                
            # Parsear y validar el JSON
            result = json.loads(response)
            
            # Validación básica del esquema
            # Nota: Para una validación más robusta, considera usar jsonschema
            for key, value_type in schema.get("properties", {}).items():
                if key not in result and "default" not in value_type:
                    raise ValueError(f"Falta el campo requerido: {key}")
                    
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Error al decodificar la respuesta JSON: {e}")
            raise ValueError(f"La respuesta generada no es un JSON válido: {response}")
        except Exception as e:
            logger.error(f"Error en generate_json: {str(e)}")
            raise ValueError(f"Error al generar JSON: {str(e)}")
    
    def _get_ollama_client(self) -> "OllamaClient":
        """
        Crea y devuelve un cliente de Ollama configurado.
        
        Returns:
            OllamaClient: Cliente de Ollama configurado
        """
        # Implementación básica - en una implementación real, esto usaría un cliente HTTP asíncrono
        class OllamaClient:
            def __init__(self, config):
                self.config = config
                self.session = None
                
            async def __aenter__(self):
                self.session = aiohttp.ClientSession(
                    base_url=self.config["base_url"],
                    timeout=aiohttp.ClientTimeout(total=self.config.get("timeout", 120))
                )
                return self
                
            async def __aexit__(self, exc_type, exc_val, exc_tb):
                if self.session:
                    await self.session.close()
                    
            async def generate(self, model: str, prompt: str, **params):
                """Método de ejemplo para generación asíncrona"""
                async with self.session.post(
                    "/api/generate",
                    json={"model": model, "prompt": prompt, **params}
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        
        return OllamaClient(self._ollama_config)
