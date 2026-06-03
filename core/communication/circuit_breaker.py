"""
Circuit Breaker Pattern
Protección contra fallos en cascada con estados monitoreados
"""
import asyncio
import time
from typing import Callable, Any, Optional, Dict
from enum import Enum
from dataclasses import dataclass
import structlog

logger = structlog.get_logger()


class CircuitState(Enum):
    """Estados del circuit breaker"""
    CLOSED = "closed"      # Normal, requests pasan
    OPEN = "open"          # Cortado, requests fallan inmediatamente
    HALF_OPEN = "half_open"  # Testing, solo algunos requests pasan


@dataclass
class CircuitBreakerConfig:
    """Configuración del circuit breaker"""
    failure_threshold: int = 5  # Fallos antes de abrir
    success_threshold: int = 2  # Éxitos en half-open para cerrar
    timeout: float = 60.0  # Segundos en estado OPEN antes de HALF_OPEN
    window_size: int = 100  # Tamaño de ventana para estadísticas


class CircuitBreakerOpenError(Exception):
    """Error cuando el circuit breaker está abierto"""
    pass


class MonitoredCircuitBreaker:
    """
    Circuit Breaker con monitoring y alerting.
    Protege servicios de fallos en cascada.
    """
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        on_state_change: Optional[Callable[[CircuitState, CircuitState], None]] = None
    ):
        """
        Inicializar Circuit Breaker
        
        Args:
            name: Nombre del circuit breaker
            config: Configuración (usa defaults si None)
            on_state_change: Callback para cambios de estado
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._on_state_change = on_state_change
        self.logger = logger.bind(component='circuit_breaker', name=name)
        
        # Contadores
        self._failure_count = 0
        self._success_count = 0
        self._consecutive_failures = 0
        self._consecutive_successes = 0
        
        # Timestamps
        self._last_failure_time: Optional[float] = None
        self._state_changed_at = time.time()
        
        # Estadísticas
        self._stats = {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'rejected_calls': 0,
            'state_changes': 0
        }
        
        self._lock = asyncio.Lock()
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Ejecutar función protegida por circuit breaker
        
        Args:
            func: Función a ejecutar (puede ser sync o async)
            *args, **kwargs: Argumentos para la función
            
        Returns:
            Resultado de la función
            
        Raises:
            CircuitBreakerOpenError: Si el circuit está abierto
        """
        # Verificar estado con lock
        async with self._lock:
            self._stats['total_calls'] += 1
            
            # Verificar estado
            await self._check_state_unlocked()
            
            if self._state == CircuitState.OPEN:
                self._stats['rejected_calls'] += 1
                self.logger.warning(
                    "Request rechazado - Circuit OPEN",
                    failure_count=self._failure_count,
                    time_since_open=(time.time() - self._state_changed_at)
                )
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.name}' está OPEN"
                )
        
        # Ejecutar función FUERA del lock para evitar deadlock
        try:
            # Verificar si es async
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Success - actualizar estado con lock
            await self._on_success()
            return result
            
        except Exception as e:
            # Failure - actualizar estado con lock
            await self._on_failure()
            raise e
    
    async def _check_state(self):
        """Verificar y actualizar estado según condiciones (con lock)"""
        async with self._lock:
            await self._check_state_unlocked()
    
    async def _check_state_unlocked(self):
        """Verificar y actualizar estado según condiciones (sin lock - llamar dentro de lock)"""
        now = time.time()
        
        if self._state == CircuitState.OPEN:
            # Verificar si es tiempo de intentar recuperación
            time_open = now - self._state_changed_at
            if time_open >= self.config.timeout:
                await self._change_state_unlocked(CircuitState.HALF_OPEN)
                self.logger.info(
                    "Intentando recuperación",
                    time_open=time_open
                )
    
    async def _on_success(self):
        """Manejar ejecución exitosa"""
        async with self._lock:
            self._success_count += 1
            self._consecutive_successes += 1
            self._consecutive_failures = 0
            self._stats['successful_calls'] += 1
            
            self.logger.debug(
                "Ejecución exitosa",
                consecutive_successes=self._consecutive_successes,
                state=self._state.value
            )
            
            # Si estamos en HALF_OPEN, verificar si podemos cerrar
            if self._state == CircuitState.HALF_OPEN:
                if self._consecutive_successes >= self.config.success_threshold:
                    await self._change_state_unlocked(CircuitState.CLOSED)
                    self.logger.info(
                        "Circuit recuperado",
                        consecutive_successes=self._consecutive_successes
                    )
    
    async def _on_failure(self):
        """Manejar fallo en ejecución"""
        async with self._lock:
            self._failure_count += 1
            self._consecutive_failures += 1
            self._consecutive_successes = 0
            self._last_failure_time = time.time()
            self._stats['failed_calls'] += 1
            
            self.logger.warning(
                "Ejecución fallida",
                consecutive_failures=self._consecutive_failures,
                state=self._state.value
            )
            
            # Si llegamos al threshold, abrir circuit
            if self._consecutive_failures >= self.config.failure_threshold:
                if self._state != CircuitState.OPEN:
                    await self._change_state_unlocked(CircuitState.OPEN)
                    self.logger.error(
                        "Circuit ABIERTO por exceso de fallos",
                        consecutive_failures=self._consecutive_failures
                    )
            
            # Si estamos en HALF_OPEN y falla, volver a OPEN
            elif self._state == CircuitState.HALF_OPEN:
                await self._change_state_unlocked(CircuitState.OPEN)
                self.logger.warning("Recuperación fallida, volviendo a OPEN")
    
    async def _change_state(self, new_state: CircuitState):
        """
        Cambiar estado del circuit breaker (con lock)
        
        Args:
            new_state: Nuevo estado
        """
        async with self._lock:
            await self._change_state_unlocked(new_state)
    
    async def _change_state_unlocked(self, new_state: CircuitState):
        """
        Cambiar estado del circuit breaker (sin lock - llamar dentro de lock)
        
        Args:
            new_state: Nuevo estado
        """
        if new_state == self._state:
            return
        
        old_state = self._state
        self._state = new_state
        self._state_changed_at = time.time()
        self._stats['state_changes'] += 1
        
        # Reset counters según el nuevo estado
        if new_state == CircuitState.CLOSED:
            self._consecutive_failures = 0
            self._consecutive_successes = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._consecutive_successes = 0
        
        self.logger.warning(
            "Circuit breaker cambió de estado",
            old_state=old_state.value,
            new_state=new_state.value,
            state_changes=self._stats['state_changes']
        )
        
        # Callback
        if self._on_state_change:
            try:
                self._on_state_change(old_state, new_state)
            except Exception as e:
                self.logger.error(
                    "Error en callback de cambio de estado",
                    error=str(e)
                )
    
    @property
    def state(self) -> CircuitState:
        """Estado actual del circuit breaker"""
        return self._state
    
    @property
    def is_open(self) -> bool:
        """Verificar si el circuit está abierto"""
        return self._state == CircuitState.OPEN
    
    @property
    def is_closed(self) -> bool:
        """Verificar si el circuit está cerrado"""
        return self._state == CircuitState.CLOSED
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del circuit breaker"""
        total = self._stats['total_calls']
        success_rate = (self._stats['successful_calls'] / total * 100) if total > 0 else 0
        rejection_rate = (self._stats['rejected_calls'] / total * 100) if total > 0 else 0
        
        return {
            **self._stats,
            'state': self._state.value,
            'consecutive_failures': self._consecutive_failures,
            'consecutive_successes': self._consecutive_successes,
            'success_rate': f"{success_rate:.2f}%",
            'rejection_rate': f"{rejection_rate:.2f}%",
            'time_in_current_state': time.time() - self._state_changed_at,
            'last_failure_time': self._last_failure_time
        }
    
    async def reset(self):
        """Resetear circuit breaker al estado inicial"""
        async with self._lock:
            old_state = self._state
            self._state = CircuitState.CLOSED
            self._failure_count = 0
            self._success_count = 0
            self._consecutive_failures = 0
            self._consecutive_successes = 0
            self._last_failure_time = None
            self._state_changed_at = time.time()
            
            self.logger.info(
                "Circuit breaker reseteado",
                old_state=old_state.value
            )
    
    async def force_open(self):
        """Forzar circuit a estado OPEN (para mantenimiento)"""
        async with self._lock:
            await self._change_state_unlocked(CircuitState.OPEN)
            self.logger.warning("Circuit breaker forzado a OPEN")
    
    async def force_close(self):
        """Forzar circuit a estado CLOSED (para recuperación manual)"""
        async with self._lock:
            await self._change_state_unlocked(CircuitState.CLOSED)
            self._consecutive_failures = 0
            self.logger.warning("Circuit breaker forzado a CLOSED")
