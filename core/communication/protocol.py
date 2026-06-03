"""
Protocolo de Comunicación MCP
Maneja comunicación entre MCPs con retry, backoff y timeouts
"""
import asyncio
import random
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

logger = structlog.get_logger()


@dataclass
class MCPRequest:
    """Request a un MCP"""
    mcp_id: str
    method: str
    params: Dict[str, Any]
    request_id: Optional[str] = None
    timeout: float = 30.0
    retry_count: int = 3


@dataclass
class MCPResponse:
    """Respuesta de un MCP"""
    status: str  # 'success', 'error', 'timeout'
    request_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    retries: int = 0


class MCPCommunicationError(Exception):
    """Error de comunicación con MCP"""
    pass


class MCPTimeoutError(MCPCommunicationError):
    """Timeout en comunicación con MCP"""
    pass


class MCPCommunicationProtocol:
    """
    Protocolo de comunicación robusto para MCPs.
    Incluye retry automático, backoff exponencial con jitter y manejo de timeouts.
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        timeout: float = 30.0
    ):
        """
        Inicializar protocolo
        
        Args:
            max_retries: Número máximo de reintentos
            base_delay: Delay base para backoff (segundos)
            max_delay: Delay máximo entre reintentos (segundos)
            timeout: Timeout por defecto para requests (segundos)
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.default_timeout = timeout
        self.logger = logger.bind(component='mcp_protocol')
        
        # Estadísticas
        self.stats = {
            'requests_sent': 0,
            'requests_succeeded': 0,
            'requests_failed': 0,
            'requests_timeout': 0,
            'total_retries': 0
        }
    
    async def send_to_mcp(
        self,
        mcp_handler: Callable,
        request: MCPRequest
    ) -> MCPResponse:
        """
        Enviar request a un MCP con retry automático
        
        Args:
            mcp_handler: Función async del MCP a llamar
            request: Request para enviar
            
        Returns:
            MCPResponse con resultado o error
        """
        self.stats['requests_sent'] += 1
        start_time = asyncio.get_event_loop().time()
        retries = 0
        
        self.logger.info(
            "Enviando request a MCP",
            mcp_id=request.mcp_id,
            method=request.method,
            timeout=request.timeout
        )
        
        for attempt in range(request.retry_count + 1):
            try:
                # Ejecutar con timeout
                result = await asyncio.wait_for(
                    mcp_handler(request.params),
                    timeout=request.timeout
                )
                
                # Success
                execution_time = asyncio.get_event_loop().time() - start_time
                self.stats['requests_succeeded'] += 1
                self.stats['total_retries'] += retries
                
                self.logger.info(
                    "Request exitoso",
                    mcp_id=request.mcp_id,
                    method=request.method,
                    execution_time=execution_time,
                    retries=retries
                )
                
                return MCPResponse(
                    status='success',
                    request_id=request.request_id,
                    data=result,
                    execution_time=execution_time,
                    retries=retries
                )
                
            except asyncio.TimeoutError:
                retries += 1
                self.logger.warning(
                    "Timeout en request",
                    mcp_id=request.mcp_id,
                    method=request.method,
                    attempt=attempt + 1,
                    max_attempts=request.retry_count + 1
                )
                
                if attempt < request.retry_count:
                    # Backoff exponencial con jitter
                    delay = await self._calculate_backoff(attempt)
                    self.logger.debug(f"Reintentando en {delay:.2f}s", delay=delay)
                    await asyncio.sleep(delay)
                else:
                    # No más reintentos
                    self.stats['requests_timeout'] += 1
                    execution_time = asyncio.get_event_loop().time() - start_time
                    
                    return MCPResponse(
                        status='timeout',
                        request_id=request.request_id,
                        error=f"Timeout después de {retries} reintentos",
                        execution_time=execution_time,
                        retries=retries
                    )
                    
            except Exception as e:
                retries += 1
                self.logger.error(
                    "Error en request",
                    mcp_id=request.mcp_id,
                    method=request.method,
                    error=str(e),
                    attempt=attempt + 1
                )
                
                if attempt < request.retry_count:
                    # Retry en caso de error
                    delay = await self._calculate_backoff(attempt)
                    await asyncio.sleep(delay)
                else:
                    # No más reintentos
                    self.stats['requests_failed'] += 1
                    execution_time = asyncio.get_event_loop().time() - start_time
                    
                    return MCPResponse(
                        status='error',
                        request_id=request.request_id,
                        error=str(e),
                        execution_time=execution_time,
                        retries=retries
                    )
        
        # Fallback (no debería llegar aquí)
        execution_time = asyncio.get_event_loop().time() - start_time
        return MCPResponse(
            status='error',
            request_id=request.request_id,
            error="Error desconocido",
            execution_time=execution_time,
            retries=retries
        )
    
    async def _calculate_backoff(self, attempt: int) -> float:
        """
        Calcular delay para backoff exponencial con jitter
        
        Args:
            attempt: Número de intento (0-indexed)
            
        Returns:
            Delay en segundos
        """
        # Backoff exponencial: base_delay * 2^attempt
        exponential_delay = self.base_delay * (2 ** attempt)
        
        # Limitar al máximo
        delay = min(exponential_delay, self.max_delay)
        
        # Agregar jitter (±25%)
        jitter = delay * 0.25 * (2 * random.random() - 1)
        final_delay = delay + jitter
        
        return max(0.1, final_delay)  # Mínimo 100ms
    
    async def broadcast_to_mcps(
        self,
        mcp_handlers: Dict[str, Callable],
        method: str,
        params: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> Dict[str, MCPResponse]:
        """
        Enviar request a múltiples MCPs en paralelo
        
        Args:
            mcp_handlers: Dict de {mcp_id: handler_function}
            method: Método a llamar
            params: Parámetros para el método
            timeout: Timeout opcional
            
        Returns:
            Dict de {mcp_id: MCPResponse}
        """
        timeout = timeout or self.default_timeout
        
        tasks = []
        mcp_ids = []
        
        for mcp_id, handler in mcp_handlers.items():
            request = MCPRequest(
                mcp_id=mcp_id,
                method=method,
                params=params,
                timeout=timeout
            )
            tasks.append(self.send_to_mcp(handler, request))
            mcp_ids.append(mcp_id)
        
        self.logger.info(
            "Broadcasting a MCPs",
            num_mcps=len(mcp_ids),
            method=method
        )
        
        # Ejecutar en paralelo
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Construir respuestas
        responses = {}
        for mcp_id, result in zip(mcp_ids, results):
            if isinstance(result, Exception):
                responses[mcp_id] = MCPResponse(
                    status='error',
                    error=str(result)
                )
            else:
                responses[mcp_id] = result
        
        return responses
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del protocolo"""
        total = self.stats['requests_sent']
        success_rate = (self.stats['requests_succeeded'] / total * 100) if total > 0 else 0
        
        return {
            **self.stats,
            'success_rate': f"{success_rate:.2f}%",
            'average_retries': (self.stats['total_retries'] / total) if total > 0 else 0
        }
    
    def reset_stats(self):
        """Resetear estadísticas"""
        self.stats = {
            'requests_sent': 0,
            'requests_succeeded': 0,
            'requests_failed': 0,
            'requests_timeout': 0,
            'total_retries': 0
        }
        self.logger.info("Estadísticas reseteadas")
