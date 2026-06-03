"""
Tester MCP Contracts
Contratos de entrada y salida para el MCP Tester
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum


class ValidationSeverity(str, Enum):
    """Severidad de validación"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationIssue(BaseModel):
    """Issue encontrado en validación"""
    severity: ValidationSeverity
    category: str
    message: str
    line_number: Optional[int] = None
    file_path: Optional[str] = None
    suggestion: Optional[str] = None


class TesterInputContract(BaseModel):
    """Contrato de entrada para Tester MCP"""
    
    component_name: str = Field(
        ...,
        description="Nombre del componente a validar"
    )
    
    code_files: List[Dict[str, str]] = Field(
        ...,
        min_length=1,
        description="Archivos de código a validar"
    )
    
    validation_rules: Optional[List[str]] = Field(
        default=None,
        description="Reglas de validación específicas"
    )
    
    run_static_analysis: bool = Field(
        default=True,
        description="Ejecutar análisis estático"
    )
    
    check_security: bool = Field(
        default=True,
        description="Verificar seguridad"
    )
    
    check_performance: bool = Field(
        default=False,
        description="Verificar performance"
    )
    
    existing_tests: Optional[List[str]] = Field(
        default=None,
        description="Tests existentes a ejecutar"
    )
    
    @validator('code_files')
    def validate_code_files_structure(cls, v):
        """Validar estructura de archivos"""
        for code_file in v:
            if 'path' not in code_file or 'content' not in code_file:
                raise ValueError('Cada archivo debe tener "path" y "content"')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "component_name": "User",
                "code_files": [
                    {
                        "path": "models/user.py",
                        "content": "class User: pass"
                    }
                ],
                "validation_rules": ["PEP8", "Django best practices"],
                "run_static_analysis": True,
                "check_security": True
            }
        }


class TesterOutputContract(BaseModel):
    """Contrato de salida para Tester MCP"""
    
    component_name: str = Field(
        ...,
        description="Nombre del componente validado"
    )
    
    validation_passed: bool = Field(
        ...,
        description="Si la validación pasó completamente"
    )
    
    issues: List[ValidationIssue] = Field(
        default_factory=list,
        description="Issues encontrados"
    )
    
    metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Métricas de calidad del código"
    )
    
    security_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Score de seguridad (0-100)"
    )
    
    code_quality_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Score de calidad (0-100)"
    )
    
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recomendaciones de mejora"
    )
    
    blocking_issues: List[ValidationIssue] = Field(
        default_factory=list,
        description="Issues que bloquean la implementación"
    )
    
    @validator('blocking_issues', always=True)
    def extract_blocking_issues(cls, v, values):
        """Extraer issues bloqueantes de la lista de issues"""
        if 'issues' in values:
            blocking = [
                issue for issue in values['issues']
                if issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
            ]
            return blocking
        return v
    
    @validator('validation_passed', always=True)
    def validate_passed_logic(cls, v, values):
        """Validar lógica de passed"""
        if 'blocking_issues' in values and values['blocking_issues']:
            # Si hay issues bloqueantes, no puede pasar
            return False
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "component_name": "User",
                "validation_passed": True,
                "issues": [
                    {
                        "severity": "warning",
                        "category": "style",
                        "message": "Línea muy larga",
                        "line_number": 42,
                        "suggestion": "Dividir en múltiples líneas"
                    }
                ],
                "metrics": {
                    "lines_of_code": 150,
                    "complexity": 5
                },
                "security_score": 95.0,
                "code_quality_score": 88.0,
                "recommendations": ["Agregar docstrings"],
                "blocking_issues": []
            }
        }
