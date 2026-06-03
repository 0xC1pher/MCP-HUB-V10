"""
Memory Engine con Consistencia
Gestiona la memoria del sistema con resolución de conflictos y versionado
"""
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import structlog
import time

from .event_store import PersistentEventStore, Event

logger = structlog.get_logger()


@dataclass
class MemoryWrite:
    """Representa una escritura en memoria"""
    project_id: str
    mcp_source: str
    data: Dict[str, Any]
    timestamp: float
    version: int


class ConflictResolutionStrategy:
    """Estrategias de resolución de conflictos"""
    
    @staticmethod
    def last_write_wins(writes: List[MemoryWrite]) -> MemoryWrite:
        """Last-Write-Wins: El último timestamp gana"""
        return max(writes, key=lambda w: w.timestamp)
    
    @staticmethod
    def highest_version_wins(writes: List[MemoryWrite]) -> MemoryWrite:
        """Highest-Version-Wins: La versión más alta gana"""
        return max(writes, key=lambda w: w.version)
    
    @staticmethod
    def merge_writes(writes: List[MemoryWrite]) -> Dict[str, Any]:
        """Merge: Combinar todas las escrituras"""
        merged = {}
        for write in sorted(writes, key=lambda w: w.timestamp):
            merged.update(write.data)
        return merged


class ConsistentMemoryEngine:
    """
    Motor de memoria con consistencia eventual y resolución de conflictos.
    Gestiona el estado del sistema a través de event sourcing.
    """
    
    def __init__(
        self,
        event_store: PersistentEventStore,
        conflict_strategy: str = 'last_write_wins'
    ):
        """
        Inicializar Memory Engine
        
        Args:
            event_store: Event store para persistencia
            conflict_strategy: Estrategia de resolución de conflictos
                             ('last_write_wins', 'highest_version_wins', 'merge')
        """
        self.event_store = event_store
        self.conflict_strategy = conflict_strategy
        self.logger = logger.bind(component='memory_engine')
        
        # Cache en memoria para acceso rápido
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_lock = asyncio.Lock()
        
        # Tracking de escrituras pendientes
        self._pending_writes: Dict[str, List[MemoryWrite]] = {}
        self._write_lock = asyncio.Lock()
    
    async def write_memory(
        self,
        project_id: str,
        mcp_source: str,
        event_type: str,
        data: Dict[str, Any],
        expected_version: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Escribir en memoria con detección de conflictos
        
        Args:
            project_id: ID del proyecto
            mcp_source: Origen del evento
            event_type: Tipo de evento
            data: Datos a escribir
            expected_version: Versión esperada (para optimistic locking)
            
        Returns:
            Dict con status y versión resultante
        """
        async with self._write_lock:
            current_version = await self.event_store.get_latest_version(project_id)
            
            # Detectar conflicto
            if expected_version is not None and current_version != expected_version:
                self.logger.warning(
                    "Conflicto de versión detectado",
                    project_id=project_id,
                    expected=expected_version,
                    current=current_version
                )
                
                # Registrar escritura pendiente para resolución
                write = MemoryWrite(
                    project_id=project_id,
                    mcp_source=mcp_source,
                    data=data,
                    timestamp=time.time(),
                    version=current_version + 1
                )
                
                if project_id not in self._pending_writes:
                    self._pending_writes[project_id] = []
                self._pending_writes[project_id].append(write)
                
                # Resolver conflicto
                resolved_data = await self._resolve_conflict(project_id)
                data = resolved_data
            
            # Escribir evento
            event = await self.event_store.append_event(
                project_id=project_id,
                mcp_source=mcp_source,
                event_type=event_type,
                data=data
            )
            
            # Actualizar cache
            await self._update_cache(project_id, event)
            
            # Limpiar escrituras pendientes
            if project_id in self._pending_writes:
                del self._pending_writes[project_id]
            
            self.logger.info(
                "Escritura en memoria completada",
                project_id=project_id,
                version=event.version,
                event_type=event_type
            )
            
            return {
                'status': 'success',
                'version': event.version,
                'event_id': event.id,
                'conflict_resolved': expected_version is not None and current_version != expected_version
            }
    
    async def read_memory(
        self,
        project_id: str,
        version: Optional[int] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Leer estado de memoria de un proyecto
        
        Args:
            project_id: ID del proyecto
            version: Versión específica a leer (None = última)
            use_cache: Usar cache si está disponible
            
        Returns:
            Estado del proyecto
        """
        # Intentar desde cache
        if use_cache and version is None:
            async with self._cache_lock:
                if project_id in self._cache:
                    self.logger.debug("Cache hit", project_id=project_id)
                    return self._cache[project_id]
        
        # Leer desde event store
        state = await self.event_store.get_project_state(project_id, version)
        
        # Actualizar cache
        if version is None:
            async with self._cache_lock:
                self._cache[project_id] = state
        
        self.logger.debug(
            "Memoria leída",
            project_id=project_id,
            version=state.get('version'),
            from_cache=False
        )
        
        return state
    
    async def _has_conflicting_writes(self, project_id: str) -> bool:
        """Verificar si hay escrituras conflictivas pendientes"""
        return project_id in self._pending_writes and len(self._pending_writes[project_id]) > 1
    
    async def _resolve_conflict(self, project_id: str) -> Dict[str, Any]:
        """
        Resolver conflictos de escritura según la estrategia configurada
        
        Args:
            project_id: ID del proyecto con conflicto
            
        Returns:
            Datos resueltos
        """
        if project_id not in self._pending_writes or not self._pending_writes[project_id]:
            return {}
        
        writes = self._pending_writes[project_id]
        
        self.logger.info(
            "Resolviendo conflicto",
            project_id=project_id,
            num_writes=len(writes),
            strategy=self.conflict_strategy
        )
        
        if self.conflict_strategy == 'last_write_wins':
            winner = ConflictResolutionStrategy.last_write_wins(writes)
            resolved_data = winner.data
        elif self.conflict_strategy == 'highest_version_wins':
            winner = ConflictResolutionStrategy.highest_version_wins(writes)
            resolved_data = winner.data
        elif self.conflict_strategy == 'merge':
            resolved_data = ConflictResolutionStrategy.merge_writes(writes)
        else:
            # Fallback a last-write-wins
            winner = ConflictResolutionStrategy.last_write_wins(writes)
            resolved_data = winner.data
        
        self.logger.info(
            "Conflicto resuelto",
            project_id=project_id,
            strategy=self.conflict_strategy
        )
        
        return resolved_data
    
    async def _update_cache(self, project_id: str, event: Event):
        """Actualizar cache con nuevo evento"""
        async with self._cache_lock:
            if project_id not in self._cache:
                # Inicializar cache desde event store
                self._cache[project_id] = await self.event_store.get_project_state(project_id)
            else:
                # Actualizar cache incremental
                cache = self._cache[project_id]
                cache['version'] = event.version
                cache['last_updated'] = event.timestamp
                cache['events_count'] = cache.get('events_count', 0) + 1
                
                # Aplicar cambios según tipo de evento
                if event.event_type == 'plan_created':
                    cache['data']['plan'] = event.data
                elif event.event_type == 'code_generated':
                    if 'code_files' not in cache['data']:
                        cache['data']['code_files'] = []
                    cache['data']['code_files'].append(event.data)
                elif event.event_type == 'test_passed':
                    cache['data']['test_results'] = event.data
    
    async def invalidate_cache(self, project_id: Optional[str] = None):
        """
        Invalidar cache
        
        Args:
            project_id: Proyecto específico (None = todos)
        """
        async with self._cache_lock:
            if project_id:
                if project_id in self._cache:
                    del self._cache[project_id]
                    self.logger.debug("Cache invalidado", project_id=project_id)
            else:
                self._cache.clear()
                self.logger.info("Cache completo invalidado")
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del motor de memoria"""
        async with self._cache_lock:
            cache_size = len(self._cache)
        
        async with self._write_lock:
            pending_writes = sum(len(writes) for writes in self._pending_writes.values())
        
        total_events = await self.event_store.count_events()
        
        return {
            'cache_size': cache_size,
            'pending_writes': pending_writes,
            'total_events': total_events,
            'conflict_strategy': self.conflict_strategy
        }
