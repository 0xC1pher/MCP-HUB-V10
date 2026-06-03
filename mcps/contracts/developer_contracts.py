"""
Developer MCP Contracts
Contratos de entrada y salida para el MCP Developer
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import ast


class DeveloperInputContract(BaseModel):
    """Contrato de entrada para Developer MCP"""
    
    component_name: str = Field(
        ...,
        min_length=1,
        description="Nombre del componente a implementar"
    )
    
    component_type: str = Field(
        ...,
        description="Tipo de componente (model, view, serializer, etc)"
    )
    
    specification: Dict[str, Any] = Field(
        ...,
        description="Especificación detallada del componente"
    )
    
    existing_code_context: Optional[Dict[str, str]] = Field(
        default=None,
        description="Código existente relacionado"
    )
    
    design_references: Optional[List[str]] = Field(
        default=None,
        description="Referencias de diseño del Architect"
    )
    
    performance_requirements: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Requerimientos de performance"
    )
    
    coding_standards: Optional[Dict[str, str]] = Field(
        default=None,
        description="Estándares de código a seguir"
    )
    
    @validator('component_name')
    def validate_component_name(cls, v):
        """Validar nombre de componente"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('component_name debe ser alfanumérico')
        return v
    
    @validator('component_type')
    def validate_component_type(cls, v):
        """Validar tipo de componente"""
        valid_types = ['model', 'view', 'serializer', 'service', 'utility', 'test', 'other']
        if v.lower() not in valid_types:
            raise ValueError(f'component_type debe ser uno de: {valid_types}')
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "component_name": "User",
                "component_type": "model",
                "specification": {
                    "fields": ["email", "password", "name"],
                    "methods": ["authenticate"]
                },
                "existing_code_context": {
                    "models.py": "# Código existente"
                },
                "coding_standards": {
                    "style": "PEP8",
                    "max_line_length": "120"
                }
            }
        }


class CodeFile(BaseModel):
    """Archivo de código generado"""
    file_path: str
    content: str
    language: str = "python"


class DeveloperOutputContract(BaseModel):
    """Contrato de salida para Developer MCP"""
    
    component_name: str = Field(
        ...,
        description="Nombre del componente implementado"
    )
    
    code_files: List[CodeFile] = Field(
        ...,
        min_length=1,
        description="Archivos de código generados"
    )
    
    imports_required: List[str] = Field(
        default_factory=list,
        description="Imports necesarios"
    )
    
    dependencies: List[str] = Field(
        default_factory=list,
        description="Dependencias externas requeridas"
    )
    
    guarantees: List[str] = Field(
        default_factory=list,
        description="Garantías del código generado"
    )
    
    limitations: List[str] = Field(
        default_factory=list,
        description="Limitaciones conocidas"
    )
    
    test_suggestions: Optional[List[str]] = Field(
        default=None,
        description="Sugerencias de testing"
    )
    
    @validator('code_files')
    def validate_code_syntax(cls, v):
        """Validar sintaxis del código Python"""
        for code_file in v:
            if code_file.language == 'python':
                try:
                    ast.parse(code_file.content)
                except SyntaxError as e:
                    raise ValueError(f'Sintaxis inválida en {code_file.file_path}: {e}')
        return v
    
    @validator('code_files')
    def validate_file_paths(cls, v):
        """Validar rutas de archivos"""
        seen_paths = set()
        for code_file in v:
            if code_file.file_path in seen_paths:
                raise ValueError(f'Ruta duplicada: {code_file.file_path}')
            seen_paths.add(code_file.file_path)
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "component_name": "User",
                "code_files": [
                    {
                        "file_path": "models/user.py",
                        "content": "class User:\n    pass",
                        "language": "python"
                    }
                ],
                "imports_required": ["from django.db import models"],
                "dependencies": [],
                "guarantees": ["Código válido sintácticamente"],
                "limitations": ["Requiere migración"],
                "test_suggestions": ["Agregar tests unitarios"]
            }
        }
