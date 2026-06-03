"""
Base MCP Class
Abstract base class for all Specialized MCPs
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import structlog
from datetime import datetime

from core.communication.protocol import MCPCommunicationProtocol, MCPRequest, MCPResponse
from core.memory.session_manager import SessionManager
from mcp_hub_v6 import MCPHubV6

logger = structlog.get_logger()


class BaseMCP(ABC):
    """
    Abstract Base Class for Specialized MCPs
    
    Responsibilities:
    - Handle communication protocol
    - Manage local state/memory
    - Execute specialized tasks
    - Report status and metrics
    """
    
    def __init__(
        self, 
        mcp_id: str, 
        hub: MCPHubV6,
        protocol: Optional[MCPCommunicationProtocol] = None
    ):
        self.mcp_id = mcp_id
        self.hub = hub
        self.protocol = protocol or MCPCommunicationProtocol()
        self.status = "initialized"
        self.started_at = datetime.now().isoformat()
        
        logger.info("mcp_initialized", mcp_id=mcp_id)
    
    async def start(self):
        """Start the MCP service"""
        self.status = "running"
        logger.info("mcp_started", mcp_id=self.mcp_id)
        # Here we would register with the Orchestrator/Hub
    
    async def stop(self):
        """Stop the MCP service"""
        self.status = "stopped"
        logger.info("mcp_stopped", mcp_id=self.mcp_id)
    
    async def process_request(self, request: MCPRequest) -> MCPResponse:
        """
        Process an incoming request
        Wrapper around _execute_task to handle protocol details
        """
        try:
            logger.info("processing_request", mcp_id=self.mcp_id, request_id=request.request_id)
            
            # Validate capability
            if request.method not in self.get_capabilities():
                return MCPResponse(
                    request_id=request.request_id,
                    status="error",
                    error=f"Method {request.method} not supported by {self.mcp_id}"
                )
            
            # Execute task
            result = await self._execute_task(request.method, request.params)
            
            return MCPResponse(
                request_id=request.request_id,
                status="success",
                data=result
            )
            
        except Exception as e:
            logger.error("request_failed", mcp_id=self.mcp_id, error=str(e))
            return MCPResponse(
                request_id=request.request_id,
                status="error",
                error=str(e)
            )
    
    @abstractmethod
    async def _execute_task(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the specific task logic
        Must be implemented by subclasses
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of supported methods"""
        pass
    
    async def _get_context(self, query: str, session_id: Optional[str] = None, top_k: int = 5) -> Dict[str, Any]:
        """Helper to get context from Hub"""
        return await self.hub.get_context(query, session_id, top_k)
    
    async def _save_memory(self, session_id: str, key: str, value: Any):
        """Helper to save to session memory"""
        await self.hub.add_turn(
            session_id, 
            f"store_memory:{key}", 
            str(value),
            metadata={'type': 'internal_memory', 'key': key}
        )

