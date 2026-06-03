"""
Contracts Package
Contratos de entrada/salida para MCPs con validación Pydantic
"""

# Architect contracts
from .architect_contracts import (
    ArchitectInputContract,
    ArchitectOutputContract,
    ComponentSpec
)

# Developer contracts
from .developer_contracts import (
    DeveloperInputContract,
    DeveloperOutputContract
)

# Backend Developer contracts
from .backend_developer_contracts import (
    BackendDeveloperInputContract,
    BackendDeveloperOutputContract,
    BackendCodeFile,
    APIEndpoint,
    DatabaseModel,
    ServiceDefinition
)

# Frontend Developer contracts
from .frontend_developer_contracts import (
    FrontendDeveloperInputContract,
    FrontendDeveloperOutputContract,
    FrontendCodeFile,
    UIComponent,
    StyleDefinition,
    APIIntegration
)

# Tester contracts
from .tester_contracts import (
    TesterInputContract,
    TesterOutputContract
)

__all__ = [
    # Architect
    "ArchitectInputContract",
    "ArchitectOutputContract",
    "ComponentSpec",
    # Developer
    "DeveloperInputContract",
    "DeveloperOutputContract",
    # Backend Developer
    "BackendDeveloperInputContract",
    "BackendDeveloperOutputContract",
    "BackendCodeFile",
    "APIEndpoint",
    "DatabaseModel",
    "ServiceDefinition",
    # Frontend Developer
    "FrontendDeveloperInputContract",
    "FrontendDeveloperOutputContract",
    "FrontendCodeFile",
    "UIComponent",
    "StyleDefinition",
    "APIIntegration",
    # Tester
    "TesterInputContract",
    "TesterOutputContract",
]
