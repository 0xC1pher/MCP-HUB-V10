"""
Contratos Pydantic para FrontendDeveloperMCP
Define los formatos de entrada y salida para el desarrollador frontend
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal


class FrontendDeveloperInputContract(BaseModel):
    """Input para FrontendDeveloperMCP"""
    component_name: str = Field(..., description="Nombre del componente frontend a implementar")
    component_type: Literal["page", "component", "layout", "hook", "utility", "style"] = Field(
        ...,
        description="Tipo de componente frontend"
    )
    requirements: List[str] = Field(..., description="Lista de requerimientos funcionales")
    architecture_context: Optional[Dict] = Field(
        default=None,
        description="Contexto de arquitectura (framework, state management)"
    )
    design_specs: Optional[Dict] = Field(
        default=None,
        description="Especificaciones de diseño (colores, tipografía, spacing)"
    )
    api_endpoints: Optional[List[Dict]] = Field(
        default=None,
        description="Endpoints backend a consumir"
    )
    parent_component: Optional[str] = Field(
        default=None,
        description="Componente padre si es un subcomponente"
    )


class UIComponent(BaseModel):
    """Definición de un componente UI"""
    name: str
    type: Literal["functional", "class", "atomic"]
    props: Dict[str, str] = {}  # prop_name: prop_type
    state: List[str] = []
    events: List[str] = []
    children_components: List[str] = []
    description: str


class StyleDefinition(BaseModel):
    """Definición de estilos"""
    file_path: str
    type: Literal["css", "scss", "styled-components", "tailwind", "css-modules"]
    variables: Dict[str, str] = {}
    classes: List[str] = []


class APIIntegration(BaseModel):
    """Integración con API backend"""
    endpoint: str
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    used_in_component: str
    request_payload: Optional[Dict] = None
    response_handler: str
    error_handler: str


class FrontendCodeFile(BaseModel):
    """Archivo de código frontend generado"""
    path: str
    content: str
    file_type: Literal["component", "page", "style", "hook", "utility", "test", "config"]
    framework: str = "react"


class FrontendDeveloperOutputContract(BaseModel):
    """Output de FrontendDeveloperMCP"""
    implementation_id: str = Field(..., description="ID único de la implementación")
    component_name: str
    code_files: List[FrontendCodeFile] = Field(..., description="Archivos de código generados")
    ui_components: List[UIComponent] = Field(
        default=[],
        description="Componentes UI implementados"
    )
    styles: Optional[List[StyleDefinition]] = Field(
        default=None,
        description="Definiciones de estilos"
    )
    api_integrations: Optional[List[APIIntegration]] = Field(
        default=None,
        description="Integraciones con APIs backend"
    )
    routes: Optional[List[Dict]] = Field(
        default=None,
        description="Rutas añadidas/modificadas"
    )
    state_management: Optional[Dict] = Field(
        default=None,
        description="Estado global/store si aplica"
    )
    dependencies: List[str] = Field(
        default=[],
        description="Dependencias npm/yarn"
    )
    assets_needed: Optional[List[str]] = Field(
        default=None,
        description="Assets necesarios (iconos, imágenes, fuentes)"
    )
    responsive_breakpoints: List[str] = Field(
        default=["mobile", "tablet", "desktop"],
        description="Breakpoints soportados"
    )
    accessibility_notes: str = Field(..., description="Notas sobre accesibilidad (a11y)")
    browser_support: List[str] = Field(
        default=["Chrome", "Firefox", "Safari", "Edge"],
        description="Navegadores soportados"
    )
    testing_notes: str = Field(..., description="Notas sobre testing de componentes")
