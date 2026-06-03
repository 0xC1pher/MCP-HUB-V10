"""
MCPs Module
Specialized MCP implementations
"""
from .base_mcp import BaseMCP
from .architect_mcp import ArchitectMCP
from .developer_mcp import DeveloperMCP
from .backend_developer_mcp import BackendDeveloperMCP
from .frontend_developer_mcp import FrontendDeveloperMCP
from .tester_mcp import TesterMCP

# VisionSpecialist opcional - funciona sin dependencias pesadas
try:
    from .vision_specialist_mcp_optional import VisionSpecialistMCP
    VISION_AVAILABLE = True
except ImportError:
    # Fallback: clase dummy
    from .base_mcp import BaseMCP as VisionSpecialistMCP
    VISION_AVAILABLE = False

__all__ = [
    'BaseMCP',
    'ArchitectMCP',
    'DeveloperMCP',
    'BackendDeveloperMCP',
    'FrontendDeveloperMCP',
    'TesterMCP',
    'VisionSpecialistMCP'
]
