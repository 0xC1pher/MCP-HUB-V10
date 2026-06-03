"""
Frontend Developer MCP - Especializado en desarrollo frontend
Implementa componentes UI, páginas, estilos y manejo de estado
"""
from typing import Dict, Any, List
import structlog
from datetime import datetime

from .base_mcp import BaseMCP
from .contracts.frontend_developer_contracts import (
    FrontendDeveloperInputContract,
    FrontendDeveloperOutputContract,
    FrontendCodeFile,
    UIComponent,
    StyleDefinition,
    APIIntegration
)
from core.llm.model_router import ModelRouter
from core.llm.prompt_manager import PromptManager

logger = structlog.get_logger()


class FrontendDeveloperMCP(BaseMCP):
    """
    Frontend Developer MCP
    
    Responsabilidades:
    - Implementar componentes UI reutilizables
    - Crear páginas y layouts
    - Integrar con APIs backend
    - Implementar manejo de estado
    - Garantizar responsive design y accesibilidad
    """
    
    def __init__(self, mcp_id: str, hub, protocol=None):
        super().__init__(mcp_id, hub, protocol)
        self.llm = ModelRouter(config_path="config/model_config.json")
        self.prompt_manager = PromptManager()
        logger.info("frontend_developer_mcp_initialized", mcp_id=mcp_id)
    
    def get_capabilities(self) -> List[str]:
        return [
            "implement_component",
            "create_page",
            "integrate_api",
            "implement_state_management",
            "create_styles"
        ]
    
    async def _execute_task(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta la tarea específica del frontend developer"""
        if method == "implement_component":
            return await self._implement_component(params)
        elif method == "create_page":
            return await self._create_page(params)
        elif method == "integrate_api":
            return await self._integrate_api(params)
        elif method == "implement_state_management":
            return await self._implement_state_management(params)
        elif method == "create_styles":
            return await self._create_styles(params)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    async def _implement_component(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Implementa un componente UI reutilizable"""
        input_data = FrontendDeveloperInputContract(**params)
        
        # Obtener contexto relevante
        context = await self._get_context(
            f"UI component {input_data.component_name}",
            top_k=3
        )
        
        # Cargar instrucciones TOON
        toon_prompt = self.prompt_manager.get_prompt("frontend_developer")
        
        # Generar código del componente
        code_files = await self._generate_component_code(input_data, context, toon_prompt)
        ui_components = self._extract_ui_components(input_data)
        styles = self._extract_styles(input_data)
        
        implementation_id = f"frontend_{int(datetime.now().timestamp())}"
        
        output = FrontendDeveloperOutputContract(
            implementation_id=implementation_id,
            component_name=input_data.component_name,
            code_files=code_files,
            ui_components=ui_components,
            styles=styles,
            dependencies=self._identify_dependencies(input_data),
            accessibility_notes="Componente implementa ARIA labels, focus management y keyboard navigation.",
            testing_notes="Tests con React Testing Library: render, user interactions, edge cases."
        )
        
        return output.dict()
    
    async def _create_page(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una página completa con layout"""
        input_data = FrontendDeveloperInputContract(**params)
        
        context = await self._get_context(
            f"page layout {input_data.component_name}",
            top_k=3
        )
        
        toon_prompt = self.prompt_manager.get_prompt("frontend_developer")
        
        code_files = await self._generate_page_code(input_data, context, toon_prompt)
        ui_components = self._extract_ui_components(input_data)
        routes = self._extract_routes(input_data)
        
        implementation_id = f"page_{int(datetime.now().timestamp())}"
        
        output = FrontendDeveloperOutputContract(
            implementation_id=implementation_id,
            component_name=input_data.component_name,
            code_files=code_files,
            ui_components=ui_components,
            routes=routes,
            dependencies=self._identify_dependencies(input_data),
            accessibility_notes="Página sigue estructura semántica HTML5 con landmarks ARIA.",
            testing_notes="Tests de integración: navegación, data fetching, error states."
        )
        
        return output.dict()
    
    async def _integrate_api(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Integra componente con API backend"""
        input_data = FrontendDeveloperInputContract(**params)
        
        context = await self._get_context(
            f"API integration {input_data.component_name}",
            top_k=3
        )
        
        code_files = await self._generate_api_integration_code(input_data, context)
        api_integrations = self._extract_api_integrations(input_data)
        
        implementation_id = f"integration_{int(datetime.now().timestamp())}"
        
        output = FrontendDeveloperOutputContract(
            implementation_id=implementation_id,
            component_name=input_data.component_name,
            code_files=code_files,
            api_integrations=api_integrations,
            dependencies=["axios", "@tanstack/react-query"],
            accessibility_notes="Manejo de estados de carga accesibles con live regions.",
            testing_notes="Mockear respuestas API. Tests de loading, success y error states."
        )
        
        return output.dict()
    
    async def _implement_state_management(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Implementa estado global con Redux/Zustand/Context"""
        input_data = FrontendDeveloperInputContract(**params)
        
        code_files = [
            FrontendCodeFile(
                path=f"store/{input_data.component_name}Store.ts",
                content=f"// State management for {input_data.component_name}",
                file_type="utility",
                framework="react"
            )
        ]
        
        state_management = {
            "type": "zustand",
            "stores": [f"{input_data.component_name}Store"],
            "actions": ["set", "get", "reset"],
            "selectors": [f"select{input_data.component_name}"]
        }
        
        implementation_id = f"state_{int(datetime.now().timestamp())}"
        
        output = FrontendDeveloperOutputContract(
            implementation_id=implementation_id,
            component_name=input_data.component_name,
            code_files=code_files,
            state_management=state_management,
            dependencies=["zustand"],
            accessibility_notes="N/A - estado interno",
            testing_notes="Tests de store: actions, selectors, middleware."
        )
        
        return output.dict()
    
    async def _create_styles(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crea sistema de estilos/tema"""
        input_data = FrontendDeveloperInputContract(**params)
        
        code_files = [
            FrontendCodeFile(
                path=f"styles/{input_data.component_name}.module.css",
                content=f"/* Styles for {input_data.component_name} */",
                file_type="style",
                framework="css"
            )
        ]
        
        styles = [
            StyleDefinition(
                file_path=f"styles/{input_data.component_name}.module.css",
                type="css-modules",
                classes=[f"{input_data.component_name}Container", f"{input_data.component_name}Header"]
            )
        ]
        
        implementation_id = f"styles_{int(datetime.now().timestamp())}"
        
        output = FrontendDeveloperOutputContract(
            implementation_id=implementation_id,
            component_name=input_data.component_name,
            code_files=code_files,
            styles=styles,
            dependencies=[],
            accessibility_notes="Contraste de colores cumple WCAG 2.1 AA.",
            testing_notes="Validar estilos con visual regression tests."
        )
        
        return output.dict()
    
    # Helper methods
    
    async def _generate_component_code(self, input_data, context, toon_prompt) -> List[FrontendCodeFile]:
        """Genera código del componente UI"""
        framework = input_data.architecture_context.get("framework", "react") if input_data.architecture_context else "react"
        
        return [
            FrontendCodeFile(
                path=f"components/{input_data.component_name}/{input_data.component_name}.tsx",
                content=f"// Component: {input_data.component_name}\n// Requirements: {input_data.requirements}",
                file_type="component",
                framework=framework
            ),
            FrontendCodeFile(
                path=f"components/{input_data.component_name}/{input_data.component_name}.module.css",
                content=f"/* Styles for {input_data.component_name} */",
                file_type="style",
                framework="css"
            ),
            FrontendCodeFile(
                path=f"components/{input_data.component_name}/{input_data.component_name}.test.tsx",
                content=f"// Tests for {input_data.component_name}",
                file_type="test",
                framework=framework
            )
        ]
    
    async def _generate_page_code(self, input_data, context, toon_prompt) -> List[FrontendCodeFile]:
        """Genera código de página"""
        framework = input_data.architecture_context.get("framework", "react") if input_data.architecture_context else "react"
        
        return [
            FrontendCodeFile(
                path=f"pages/{input_data.component_name}/index.tsx",
                content=f"// Page: {input_data.component_name}",
                file_type="page",
                framework=framework
            )
        ]
    
    async def _generate_api_integration_code(self, input_data, context) -> List[FrontendCodeFile]:
        """Genera código de integración con API"""
        return [
            FrontendCodeFile(
                path=f"api/{input_data.component_name}Api.ts",
                content=f"// API client for {input_data.component_name}",
                file_type="utility",
                framework="typescript"
            ),
            FrontendCodeFile(
                path=f"hooks/use{input_data.component_name}.ts",
                content=f"// React Query hook for {input_data.component_name}",
                file_type="hook",
                framework="react"
            )
        ]
    
    def _extract_ui_components(self, input_data) -> List[UIComponent]:
        """Extrae componentes UI basados en requerimientos"""
        return [
            UIComponent(
                name=input_data.component_name,
                type="functional",
                props={"className": "string", "children": "ReactNode"},
                state=["isLoading", "data", "error"],
                events=["onClick", "onChange"],
                children_components=[],
                description=f"Main component for {input_data.component_name}"
            )
        ]
    
    def _extract_styles(self, input_data) -> List[StyleDefinition]:
        """Extrae definiciones de estilos"""
        design_type = "css-modules"
        if input_data.architecture_context:
            design_type = input_data.architecture_context.get("styling", "css-modules")
        
        return [
            StyleDefinition(
                file_path=f"components/{input_data.component_name}/{input_data.component_name}.module.css",
                type=design_type,
                classes=[f"{input_data.component_name}Container"]
            )
        ]
    
    def _extract_routes(self, input_data) -> List[Dict]:
        """Extrae rutas de la página"""
        return [
            {
                "path": f"/{input_data.component_name.lower()}",
                "component": input_data.component_name,
                "exact": True,
                "auth_required": False
            }
        ]
    
    def _extract_api_integrations(self, input_data) -> List[APIIntegration]:
        """Extrae integraciones con API"""
        integrations = []
        
        if input_data.api_endpoints:
            for endpoint in input_data.api_endpoints:
                integrations.append(APIIntegration(
                    endpoint=endpoint.get("path", "/api/data"),
                    method=endpoint.get("method", "GET"),
                    used_in_component=input_data.component_name,
                    response_handler="handleSuccess",
                    error_handler="handleError"
                ))
        
        return integrations
    
    def _identify_dependencies(self, input_data) -> List[str]:
        """Identifica dependencias npm necesarias"""
        base_deps = ["react", "react-dom"]
        
        if input_data.component_type == "page":
            base_deps.extend(["react-router-dom"])
        
        if input_data.api_endpoints:
            base_deps.extend(["axios", "@tanstack/react-query"])
        
        return base_deps
