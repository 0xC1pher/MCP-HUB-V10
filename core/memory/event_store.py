"""
Event Store Persistente con SQLite
Almacena todos los eventos del sistema con versionado y recuperabilidad
"""
import aiosqlite
import json
import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import structlog

logger = structlog.get_logger()


@dataclass
class Event:
    """Evento del sistema"""
    id: Optional[int]
    timestamp: float
    project_id: str
    mcp_source: str
    event_type: str
    data: Dict[str, Any]
    version: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'project_id': self.project_id,
            'mcp_source': self.mcp_source,
            'event_type': self.event_type,
            'data': self.data,
            'version': self.version
        }


class PersistentEventStore:
    """
    Event Store persistente con SQLite para event sourcing.
    Proporciona almacenamiento durable de eventos con consulta eficiente.
    """
    
    def __init__(self, db_path: str = './data/events.db'):
        """
        Inicializar Event Store
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self.logger = logger.bind(component='event_store')
        
    async def initialize(self):
        """Crear tablas e índices necesarios"""
        self.logger.info("Inicializando Event Store", db_path=self.db_path)
        
        async with aiosqlite.connect(self.db_path) as db:
            # Tabla principal de eventos
            await db.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    project_id TEXT NOT NULL,
                    mcp_source TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    created_at REAL DEFAULT (julianday('now'))
                )
            ''')
            
            # Índices para optimización
            await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_project_version 
                ON events(project_id, version)
            ''')
            
            await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_project_timestamp 
                ON events(project_id, timestamp)
            ''')
            
            await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_mcp_source 
                ON events(mcp_source, timestamp)
            ''')
            
            await db.execute('''
                CREATE INDEX IF NOT EXISTS idx_event_type 
                ON events(event_type)
            ''')
            
            await db.commit()
            self.logger.info("Event Store inicializado correctamente")
    
    async def append_event(
        self,
        project_id: str,
        mcp_source: str,
        event_type: str,
        data: Dict[str, Any],
        version: Optional[int] = None
    ) -> Event:
        """
        Agregar un nuevo evento al store
        
        Args:
            project_id: ID del proyecto
            mcp_source: Origen del evento (ej: 'architect', 'developer')
            event_type: Tipo de evento (ej: 'plan_created', 'code_generated')
            data: Datos del evento
            version: Versión del evento (auto-incrementa si no se provee)
            
        Returns:
            Event: Evento creado con ID asignado
        """
        timestamp = time.time()
        
        # Si no se provee versión, obtener la siguiente
        if version is None:
            version = await self._get_next_version(project_id)
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT INTO events (timestamp, project_id, mcp_source, event_type, data, version)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (timestamp, project_id, mcp_source, event_type, json.dumps(data), version))
            
            await db.commit()
            event_id = cursor.lastrowid
        
        event = Event(
            id=event_id,
            timestamp=timestamp,
            project_id=project_id,
            mcp_source=mcp_source,
            event_type=event_type,
            data=data,
            version=version
        )
        
        self.logger.info(
            "Evento agregado",
            event_id=event_id,
            project_id=project_id,
            event_type=event_type,
            version=version
        )
        
        return event
    
    async def get_events(
        self,
        project_id: Optional[str] = None,
        mcp_source: Optional[str] = None,
        event_type: Optional[str] = None,
        from_version: Optional[int] = None,
        to_version: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[Event]:
        """
        Obtener eventos con filtros opcionales
        
        Args:
            project_id: Filtrar por proyecto
            mcp_source: Filtrar por origen MCP
            event_type: Filtrar por tipo de evento
            from_version: Versión mínima (inclusiva)
            to_version: Versión máxima (inclusiva)
            limit: Número máximo de eventos a retornar
            
        Returns:
            Lista de eventos que cumplen los filtros
        """
        query = 'SELECT id, timestamp, project_id, mcp_source, event_type, data, version FROM events WHERE 1=1'
        params = []
        
        if project_id:
            query += ' AND project_id = ?'
            params.append(project_id)
        
        if mcp_source:
            query += ' AND mcp_source = ?'
            params.append(mcp_source)
        
        if event_type:
            query += ' AND event_type = ?'
            params.append(event_type)
        
        if from_version is not None:
            query += ' AND version >= ?'
            params.append(from_version)
        
        if to_version is not None:
            query += ' AND version <= ?'
            params.append(to_version)
        
        query += ' ORDER BY version ASC, timestamp ASC'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
        
        events = []
        for row in rows:
            events.append(Event(
                id=row[0],
                timestamp=row[1],
                project_id=row[2],
                mcp_source=row[3],
                event_type=row[4],
                data=json.loads(row[5]),
                version=row[6]
            ))
        
        self.logger.debug(
            "Eventos obtenidos",
            count=len(events),
            project_id=project_id,
            event_type=event_type
        )
        
        return events
    
    async def get_latest_version(self, project_id: str) -> int:
        """
        Obtener la última versión de eventos para un proyecto
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Última versión (0 si no hay eventos)
        """
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                'SELECT MAX(version) FROM events WHERE project_id = ?',
                (project_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row[0] is not None else 0
    
    async def _get_next_version(self, project_id: str) -> int:
        """Obtener la siguiente versión para un proyecto"""
        current = await self.get_latest_version(project_id)
        return current + 1
    
    async def get_project_state(self, project_id: str, version: Optional[int] = None) -> Dict[str, Any]:
        """
        Reconstruir el estado de un proyecto desde eventos
        
        Args:
            project_id: ID del proyecto
            version: Versión hasta la cual reconstruir (None = última versión)
            
        Returns:
            Estado reconstruido del proyecto
        """
        if version is None:
            version = await self.get_latest_version(project_id)
        
        events = await self.get_events(project_id=project_id, to_version=version)
        
        # Reconstruir estado desde eventos
        state = {
            'project_id': project_id,
            'version': version,
            'events_count': len(events),
            'last_updated': events[-1].timestamp if events else None,
            'data': {}
        }
        
        # Aplicar eventos en orden
        for event in events:
            if event.event_type == 'plan_created':
                state['data']['plan'] = event.data
            elif event.event_type == 'code_generated':
                if 'code_files' not in state['data']:
                    state['data']['code_files'] = []
                state['data']['code_files'].append(event.data)
            elif event.event_type == 'test_passed':
                state['data']['test_results'] = event.data
            # Más tipos de eventos según necesidad
        
        return state
    
    async def count_events(self, project_id: Optional[str] = None) -> int:
        """
        Contar eventos en el store
        
        Args:
            project_id: Filtrar por proyecto (opcional)
            
        Returns:
            Número de eventos
        """
        query = 'SELECT COUNT(*) FROM events'
        params = []
        
        if project_id:
            query += ' WHERE project_id = ?'
            params.append(project_id)
        
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(query, params) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0
    
    async def delete_project_events(self, project_id: str):
        """
        Eliminar todos los eventos de un proyecto
        USAR CON PRECAUCIÓN - Operación destructiva
        
        Args:
            project_id: ID del proyecto a eliminar
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('DELETE FROM events WHERE project_id = ?', (project_id,))
            await db.commit()
        
        self.logger.warning("Eventos de proyecto eliminados", project_id=project_id)
