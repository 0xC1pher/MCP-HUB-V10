"""
Architect MCP Contracts
Contratos de entrada y salida para el MCP Architect
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum


class Complexity(str, Enum):
    """Niveles de complejidad"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ArchitectInputContract(BaseModel):
    """Contrato de entrada para Architect MCP"""
    
    feature_description: str = Field(
        ...,
        min_length=10,
        description="Descripción detallada de la feature a implementar"
    )
    
    project_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Contexto del proyecto (tecnologías, arquitectura, etc)"
    )
    
    existing_models: Optional[List[str]] = Field(
        default=None,
        description="Modelos existentes en el proyecto"
    )
    
    constraints: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Restricciones técnicas o de negocio"
    )
    
    performance_requirements: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Requerimientos de performance"
    )
    
    @validator('feature_description')
    def validate_description(cls, v):
        """Validar descripción no vacía y con contenido"""
        if len(v.strip()) < 10:
            raise ValueError('feature_description debe tener al menos 10 caracteres')
        if not any(c.isalpha() for c in v):
            raise ValueError('feature_description debe contener texto')
        return v.strip()
    
    @validator('project_context')
    def validate_project_context(cls, v):
        """Validar que el contexto tenga información mínima"""
        if v and 'technology' not in v:
            v['technology'] = 'django'  # Default
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "feature_description": "Crear sistema de autenticación con JWT",
                "project_context": {
                    "technology": "django",
                    "version": "4.2"
                },
                "existing_models": ["User", "Profile"],
                "constraints": {
                    "max_response_time": "200ms",
                    "database": "postgresql"
                }
            }
        }


class ComponentSpec(BaseModel):
    """Especificación de un componente"""
    name: str
    type: str  # 'model', 'view', 'serializer', etc.
    description: str
    dependencies: List[str] = Field(default_factory=list)
    estimated_complexity: Complexity


class ArchitectOutputContract(BaseModel):
    """Contrato de salida para Architect MCP"""
    
    plan_id: str = Field(
        ...,
        description="ID único del plan generado"
    )
    
    components: List[ComponentSpec] = Field(
        ...,
        min_length=1,
        description="Componentes a implementar"
    )
    
    implementation_order: List[str] = Field(
        ...,
        min_length=1,
        description="Orden de implementación de componentes"
    )
    
    dependencies_graph: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Grafo de dependencias entre componentes"
    )
    
    estimated_effort: str = Field(
        ...,
        description="Esfuerzo estimado (ej: '2-3 days')"
    )
    
    risks: List[str] = Field(
        default_factory=list,
        description="Riesgos identificados"
    )
    
    guarantees: List[str] = Field(
        default_factory=list,
        description="Garantías del plan"
    )
    
    limitations: List[str] = Field(
        default_factory=list,
        description="Limitaciones conocidas"
    )
    
    @validator('implementation_order')
    def validate_order_matches_components(cls, v, values):
        """Validar que el orden coincida con los componentes"""
        if 'components' in values:
            component_names = {c.name for c in values['components']}
            order_names = set(v)
            
            if not order_names.issubset(component_names):
                raise ValueError('implementation_order contiene componentes no definidos')
            
            if len(order_names) != len(component_names):
                raise ValueError('implementation_order debe incluir todos los componentes')
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "plan_id": "plan_12345",
                "components": [
                    {
                        "name": "JWTAuthentication",
                        "type": "authentication",
                        "description": "Sistema de autenticación JWT",
                        "dependencies": ["User"],
                        "estimated_complexity": "medium"
                    }
                ],
                "implementation_order": ["JWTAuthentication"],
                "dependencies_graph": {"JWTAuthentication": ["User"]},
                "estimated_effort": "1-2 days",
                "risks": ["Complejidad de seguridad"],
                "guarantees": ["Autenticación stateless"],
                "limitations": ["Requiere configuración adicional"]
            }
        }
