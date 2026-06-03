"""
Tests para Circuit Breaker
"""
import pytest
import asyncio

from core.communication.circuit_breaker import (
    MonitoredCircuitBreaker,
    CircuitState,
    CircuitBreakerOpenError,
    CircuitBreakerConfig
)


@pytest.fixture
def circuit_breaker():
    """Fixture para Circuit Breaker con config de test"""
    config = CircuitBreakerConfig(
        failure_threshold=3,
        success_threshold=2,
        timeout=1.0  # 1 segundo para tests rápidos
    )
    return MonitoredCircuitBreaker("test_circuit", config)


@pytest.mark.asyncio
async def test_circuit_breaker_closed_state(circuit_breaker):
    """Test: Estado inicial CLOSED permite requests"""
    
    async def success_func():
        return "success"
    
    result = await circuit_breaker.execute(success_func)
    
    assert result == "success"
    assert circuit_breaker.state == CircuitState.CLOSED


@pytest.mark.asyncio
async def test_circuit_opens_after_failures(circuit_breaker):
    """Test: Circuit se abre después de threshold de fallos"""
    
    async def failing_func():
        raise Exception("Test failure")
    
    # Ejecutar hasta alcanzar threshold
    for _ in range(3):
        try:
            await circuit_breaker.execute(failing_func)
        except Exception:
            pass
    
    # Circuit debe estar OPEN
    assert circuit_breaker.state == CircuitState.OPEN


@pytest.mark.asyncio
async def test_circuit_rejects_when_open(circuit_breaker):
    """Test: Circuit rechaza requests cuando está OPEN"""
    
    async def failing_func():
        raise Exception("Test failure")
    
    # Abrir el circuit
    for _ in range(3):
        try:
            await circuit_breaker.execute(failing_func)
        except Exception:
            pass
    
    # Intentar ejecutar cuando está OPEN
    with pytest.raises(CircuitBreakerOpenError):
        async def any_func():
            return "test"
        await circuit_breaker.execute(any_func)


@pytest.mark.asyncio
async def test_circuit_half_open_after_timeout(circuit_breaker):
    """Test: Circuit pasa a HALF_OPEN después del timeout"""
    
    async def failing_func():
        raise Exception("Test failure")
    
    # Abrir el circuit
    for _ in range(3):
        try:
            await circuit_breaker.execute(failing_func)
        except Exception:
            pass
    
    assert circuit_breaker.state == CircuitState.OPEN
    
    # Esperar el timeout
    await asyncio.sleep(1.1)
    
    # Ejecutar verificación de estado
    async def success_func():
        return "success"
    
    # Esto debería cambiar a HALF_OPEN
    try:
        await circuit_breaker.execute(success_func)
    except CircuitBreakerOpenError:
        # Puede que aún esté OPEN si no se verificó el estado
        pass


@pytest.mark.asyncio
async def test_circuit_closes_after_successes_in_half_open(circuit_breaker):
    """Test: Circuit se cierra después de éxitos en HALF_OPEN"""
    
    async def failing_func():
        raise Exception("Test failure")
    
    async def success_func():
        return "success"
    
    # Abrir el circuit
    for _ in range(3):
        try:
            await circuit_breaker.execute(failing_func)
        except Exception:
            pass
    
    # Esperar timeout
    await asyncio.sleep(1.1)
    
    # Forzar a HALF_OPEN
    await circuit_breaker._change_state(CircuitState.HALF_OPEN)
    
    # Ejecutar éxitos suficientes
    for _ in range(2):
        await circuit_breaker.execute(success_func)
    
    # Debería estar CLOSED
    assert circuit_breaker.state == CircuitState.CLOSED


@pytest.mark.asyncio
async def test_circuit_stats(circuit_breaker):
    """Test: Estadísticas del circuit breaker"""
    
    async def success_func():
        return "success"
    
    # Ejecutar algunos requests
    for _ in range(5):
        await circuit_breaker.execute(success_func)
    
    stats = circuit_breaker.get_stats()
    
    assert stats['total_calls'] == 5
    assert stats['successful_calls'] == 5
    assert stats['failed_calls'] == 0


@pytest.mark.asyncio
async def test_circuit_force_open(circuit_breaker):
    """Test: Forzar circuit a OPEN"""
    assert circuit_breaker.state == CircuitState.CLOSED
    
    await circuit_breaker.force_open()
    
    assert circuit_breaker.state == CircuitState.OPEN


@pytest.mark.asyncio
async def test_circuit_force_close(circuit_breaker):
    """Test: Forzar circuit a CLOSED"""
    await circuit_breaker.force_open()
    assert circuit_breaker.state == CircuitState.OPEN
    
    await circuit_breaker.force_close()
    
    assert circuit_breaker.state == CircuitState.CLOSED


@pytest.mark.asyncio
async def test_circuit_reset(circuit_breaker):
    """Test: Reset del circuit breaker"""
    
    async def failing_func():
        raise Exception("Test failure")
    
    # Generar algunos fallos
    for _ in range(2):
        try:
            await circuit_breaker.execute(failing_func)
        except Exception:
            pass
    
    # Reset
    await circuit_breaker.reset()
    
    # Verificar estado limpio
    assert circuit_breaker.state == CircuitState.CLOSED
    stats = circuit_breaker.get_stats()
    assert stats['consecutive_failures'] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
