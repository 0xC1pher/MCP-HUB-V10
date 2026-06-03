"""
Contratos Pydantic para BackendDeveloperMCP
Define los formatos de entrada y salida para el desarrollador backend
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal


class BackendDeveloperInputContract(BaseModel):
    """Input para BackendDeveloperMCP"""
    component_name: str = Field(..., description="Nombre del componente backend a implementar")
    component_type: Literal["api", "service", "model", "middleware", "integration"] = Field(
        ..., 
        description="Tipo de componente backend"
    )
    requirements: List[str] = Field(..., description="Lista de requerimientos funcionales")
    architecture_context: Optional[Dict] = Field(
        default=None,
        description="Contexto de arquitectura del Architect (patrones, tecnologías)"
    )
    database_schema: Optional[Dict] = Field(
        default=None,
        description="Esquema de base de datos si aplica"
    )
    api_contracts: Optional[List[Dict]] = Field(
        default=None,
        description="Contratos de API (endpoints, request/response schemas)"
    )


class APIEndpoint(BaseModel):
    """Definición de un endpoint API"""
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
    path: str
    description: str
    request_schema: Optional[Dict] = None
    response_schema: Dict
    auth_required: bool = True
    rate_limit: Optional[str] = None


class DatabaseModel(BaseModel):
    """Definición de modelo de base de datos"""
    name: str
    fields: Dict[str, str]  # field_name: field_type
    indexes: List[str] = []
    relationships: List[str] = []


class ServiceDefinition(BaseModel):
    """Definición de un servicio backend"""
    name: str
    methods: List[str]
    dependencies: List[str]
    description: str


class BackendCodeFile(BaseModel):
    """Archivo de código backend generado"""
    path: str
    content: str
    file_type: Literal["controller", "service", "model", "migration", "test", "config"]
    language: str = "python"


class BackendDeveloperOutputContract(BaseModel):
    """Output de BackendDeveloperMCP"""
    implementation_id: str = Field(..., description="ID único de la implementación")
    component_name: str
    code_files: List[BackendCodeFile] = Field(..., description="Archivos de código generados")
    api_endpoints: Optional[List[APIEndpoint]] = Field(
        default=None,
        description="Endpoints API implementados"
    )
    database_models: Optional[List[DatabaseModel]] = Field(
        default=None,
        description="Modelos de datos creados/modificados"
    )
    services: Optional[List[ServiceDefinition]] = Field(
        default=None,
        description="Servicios implementados"
    )
    environment_vars: Optional[List[str]] = Field(
        default=None,
        description="Variables de entorno necesarias"
    )
    dependencies: List[str] = Field(
        default=[],
        description="Dependencias externas (paquetes, librerías)"
    )
    migration_scripts: Optional[List[str]] = Field(
        default=None,
        description="Scripts de migración de BD si aplica"
    )
    api_documentation: Optional[str] = Field(
        default=None,
        description="Documentación OpenAPI/Swagger generada"
    )
    testing_notes: str = Field(..., description="Notas sobre testing y validación")
    deployment_notes: str = Field(..., description="Notas sobre deployment y configuración")
