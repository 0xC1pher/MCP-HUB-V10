"""
Backend Developer MCP - Especializado en desarrollo backend
Implementa APIs, servicios, modelos de datos y lógica de negocio
"""
from typing import Dict, Any, List
import structlog
from datetime import datetime

from .base_mcp import BaseMCP
from .contracts.backend_developer_contracts import (
    BackendDeveloperInputContract,
    BackendDeveloperOutputContract,
    BackendCodeFile,
    APIEndpoint,
    DatabaseModel,
    ServiceDefinition
)
from core.llm.model_router import ModelRouter
from core.llm.prompt_manager import PromptManager

logger = structlog.get_logger()


class BackendDeveloperMCP(BaseMCP):
    """
    Backend Developer MCP
    
    Responsabilidades:
    - Implementar endpoints API REST/GraphQL
    - Crear modelos de datos y migraciones
    - Desarrollar servicios y lógica de negocio
    - Integrar con bases de datos y servicios externos
    - Implementar autenticación y autorización
    """
    
    def __init__(self, mcp_id: str, hub, protocol=None):
        super().__init__(mcp_id, hub, protocol)
        self.llm = ModelRouter(config_path="config/model_config.json")
        self.prompt_manager = PromptManager()
        logger.info("backend_developer_mcp_initialized", mcp_id=mcp_id)
    
    def get_capabilities(self) -> List[str]:
        return [
            "implement_api",
            "create_service",
            "design_database_model",
            "implement_middleware",
            "integrate_external_api"
        ]
    
    async def _execute_task(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta la tarea específica del backend developer"""
        if method == "implement_api":
            return await self._implement_api(params)
        elif method == "create_service":
            return await self._create_service(params)
        elif method == "design_database_model":
            return await self._design_database_model(params)
        elif method == "implement_middleware":
            return await self._implement_middleware(params)
        elif method == "integrate_external_api":
            return await self._integrate_external_api(params)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    async def _implement_api(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Implementa endpoints API basados en requerimientos"""
        input_data = BackendDeveloperInputContract(**params)
        
        # Obtener contexto relevante
        context = await self._get_context(
            f"API implementation for {input_data.component_name}",
            top_k=3
        )
        
        # Cargar instrucciones TOON
        toon_prompt = self.prompt_manager.get_prompt("backend_developer")
        
        # Analizar requerimientos y generar código
        code_files = await self._generate_api_code(input_data, context, toon_prompt)
        endpoints = self._extract_endpoints(input_data)
        
        implementation_id = f"backend_{int(datetime.now().timestamp())}"
        
        output = BackendDeveloperOutputContract(
            implementation_id=implementation_id,
            component_name=input_data.component_name,
            code_files=code_files,
            api_endpoints=endpoints,
            dependencies=self._identify_dependencies(input_data),
            testing_notes="Implementar tests unitarios para cada endpoint. Usar pytest y mocking.",
            deployment_notes="Configurar variables de entorno. Aplicar migraciones antes de deployment."
        )
        
        return output.dict()
    
    async def _create_service(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un servicio backend con lógica de negocio"""
        input_data = BackendDeveloperInputContract(**params)
        
        context = await self._get_context(
            f"service implementation {input_data.component_name}",
            top_k=3
        )
        
        toon_prompt = self.prompt_manager.get_prompt("backend_developer")
        
        code_files = await self._generate_service_code(input_data, context, toon_prompt)
        services = self._extract_services(input_data)
        
        implementation_id = f"service_{int(datetime.now().timestamp())}"
        
        output = BackendDeveloperOutputContract(
            implementation_id=implementation_id,
            component_name=input_data.component_name,
            code_files=code_files,
            services=services,
            dependencies=self._identify_dependencies(input_data),
            testing_notes="Tests unitarios con mocking de dependencias externas.",
            deployment_notes="Verificar configuración de servicios externos."
        )
        
        return output.dict()
    
    async def _design_database_model(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Diseña modelos de base de datos"""
        input_data = BackendDeveloperInputContract(**params)
        
        context = await self._get_context(
            f"database model {input_data.component_name}",
            top_k=3
        )
        
        toon_prompt = self.prompt_manager.get_prompt("backend_developer")
        
        code_files = await self._generate_model_code(input_data, context, toon_prompt)
        models = self._extract_database_models(input_data)
        
        implementation_id = f"model_{int(datetime.now().timestamp())}"
        
        output = BackendDeveloperOutputContract(
            implementation_id=implementation_id,
            component_name=input_data.component_name,
            code_files=code_files,
            database_models=models,
            migration_scripts=[f"migrations/create_{input_data.component_name}.py"],
            dependencies=["sqlalchemy", "alembic"],
            testing_notes="Tests de modelos: validaciones, relaciones, constraints.",
            deployment_notes="Ejecutar migraciones: alembic upgrade head"
        )
        
        return output.dict()
    
    async def _implement_middleware(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Implementa middleware (auth, logging, etc)"""
        input_data = BackendDeveloperInputContract(**params)
        
        code_files = [
            BackendCodeFile(
                path=f"middleware/{input_data.component_name}.py",
                content=self._generate_middleware_code(input_data),
                file_type="service",
                language="python"
            )
        ]
        
        implementation_id = f"middleware_{int(datetime.now().timestamp())}"
        
        output = BackendDeveloperOutputContract(
            implementation_id=implementation_id,
            component_name=input_data.component_name,
            code_files=code_files,
            dependencies=["starlette", "fastapi"],
            testing_notes="Tests de middleware: verificar que intercepta requests correctamente.",
            deployment_notes="Registrar middleware en app principal."
        )
        
        return output.dict()
    
    async def _integrate_external_api(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Integra con APIs externas"""
        input_data = BackendDeveloperInputContract(**params)
        
        code_files = [
            BackendCodeFile(
                path=f"integrations/{input_data.component_name}_client.py",
                content=self._generate_integration_code(input_data),
                file_type="service",
                language="python"
            )
        ]
        
        implementation_id = f"integration_{int(datetime.now().timestamp())}"
        
        output = BackendDeveloperOutputContract(
            implementation_id=implementation_id,
            component_name=input_data.component_name,
            code_files=code_files,
            environment_vars=[f"{input_data.component_name.upper()}_API_KEY", f"{input_data.component_name.upper()}_URL"],
            dependencies=["httpx", "tenacity"],
            testing_notes="Mockear respuestas externas. Tests de retry y error handling.",
            deployment_notes="Configurar API keys y URLs en variables de entorno."
        )
        
        return output.dict()
    
    # Helper methods
    
    async def _generate_api_code(self, input_data, context, toon_prompt) -> List[BackendCodeFile]:
        """Genera código de endpoints API"""
        # Lógica determinística basada en requerimientos
        return [
            BackendCodeFile(
                path=f"api/routes/{input_data.component_name}.py",
                content=f"# API routes for {input_data.component_name}\n# Generated based on: {input_data.requirements}",
                file_type="controller",
                language="python"
            ),
            BackendCodeFile(
                path=f"api/schemas/{input_data.component_name}.py",
                content=f"# Pydantic schemas for {input_data.component_name}",
                file_type="model",
                language="python"
            )
        ]
    
    async def _generate_service_code(self, input_data, context, toon_prompt) -> List[BackendCodeFile]:
        """Genera código de servicio"""
        return [
            BackendCodeFile(
                path=f"services/{input_data.component_name}_service.py",
                content=f"# Service: {input_data.component_name}\n# Business logic implementation",
                file_type="service",
                language="python"
            )
        ]
    
    async def _generate_model_code(self, input_data, context, toon_prompt) -> List[BackendCodeFile]:
        """Genera código de modelos de BD"""
        return [
            BackendCodeFile(
                path=f"models/{input_data.component_name}.py",
                content=f"# Database model: {input_data.component_name}",
                file_type="model",
                language="python"
            )
        ]
    
    def _generate_middleware_code(self, input_data) -> str:
        """Genera código de middleware"""
        return f"# Middleware: {input_data.component_name}\n# Request/Response interceptor"
    
    def _generate_integration_code(self, input_data) -> str:
        """Genera código de integración con API externa"""
        return f"# External API Client: {input_data.component_name}\n# HTTP client with retry logic"
    
    def _extract_endpoints(self, input_data) -> List[APIEndpoint]:
        """Extrae endpoints basados en requerimientos"""
        # Análisis simple de keywords
        endpoints = []
        for req in input_data.requirements:
            req_lower = req.lower()
            if 'create' in req_lower or 'post' in req_lower:
                endpoints.append(APIEndpoint(
                    method="POST",
                    path=f"/api/{input_data.component_name}",
                    description=req,
                    response_schema={"id": "string", "status": "string"}
                ))
            elif 'get' in req_lower or 'list' in req_lower or 'retrieve' in req_lower:
                endpoints.append(APIEndpoint(
                    method="GET",
                    path=f"/api/{input_data.component_name}",
                    description=req,
                    response_schema={"data": "array"}
                ))
        
        return endpoints if endpoints else [
            APIEndpoint(
                method="GET",
                path=f"/api/{input_data.component_name}",
                description="Default endpoint",
                response_schema={"status": "ok"}
            )
        ]
    
    def _extract_services(self, input_data) -> List[ServiceDefinition]:
        """Extrae servicios basados en componente"""
        return [
            ServiceDefinition(
                name=f"{input_data.component_name}Service",
                methods=["process", "validate", "transform"],
                dependencies=["database", "cache"],
                description=f"Business logic for {input_data.component_name}"
            )
        ]
    
    def _extract_database_models(self, input_data) -> List[DatabaseModel]:
        """Extrae modelos de BD basados en esquema"""
        if input_data.database_schema:
            return [
                DatabaseModel(
                    name=input_data.component_name,
                    fields=input_data.database_schema.get("fields", {}),
                    indexes=input_data.database_schema.get("indexes", []),
                    relationships=input_data.database_schema.get("relationships", [])
                )
            ]
        return []
    
    def _identify_dependencies(self, input_data) -> List[str]:
        """Identifica dependencias necesarias"""
        base_deps = ["pydantic", "structlog"]
        
        if input_data.component_type == "api":
            base_deps.extend(["fastapi", "uvicorn"])
        elif input_data.component_type == "service":
            base_deps.extend(["asyncio"])
        elif input_data.component_type == "model":
            base_deps.extend(["sqlalchemy", "alembic"])
        
        return base_deps
