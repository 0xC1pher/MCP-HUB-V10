"""
Rollback Manager Persistente
Gestiona checkpoints y rollback del sistema con persistencia en disco
"""
import asyncio
import json
import time
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
import structlog

logger = structlog.get_logger()


@dataclass
class Checkpoint:
    """Representa un checkpoint del sistema"""
    id: str
    project_id: str
    timestamp: float
    version: int
    state: Dict[str, Any]
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'timestamp': self.timestamp,
            'version': self.version,
            'state': self.state,
            'description': self.description
        }


class PersistentRollbackManager:
    """
    Gestor de rollback con persistencia en disco.
    Permite crear checkpoints y restaurar el sistema a estados anteriores.
    """
    
    def __init__(
        self,
        checkpoints_dir: str = './data/checkpoints',
        max_checkpoints: int = 10
    ):
        """
        Inicializar Rollback Manager
        
        Args:
            checkpoints_dir: Directorio para almacenar checkpoints
            max_checkpoints: Número máximo de checkpoints a mantener por proyecto
        """
        self.checkpoints_dir = Path(checkpoints_dir)
        self.max_checkpoints = max_checkpoints
        self.logger = logger.bind(component='rollback_manager')
        
        # Cache de checkpoints en memoria
        self._checkpoints_cache: Dict[str, List[Checkpoint]] = {}
        self._lock = asyncio.Lock()
        
        # Crear directorio si no existe
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(
            "Rollback Manager inicializado",
            checkpoints_dir=str(self.checkpoints_dir),
            max_checkpoints=max_checkpoints
        )
    
    async def checkpoint(
        self,
        project_id: str,
        state: Dict[str, Any],
        version: int,
        description: Optional[str] = None
    ) -> Checkpoint:
        """
        Crear un checkpoint del estado actual
        
        Args:
            project_id: ID del proyecto
            state: Estado a guardar
            version: Versión del estado
            description: Descripción opcional del checkpoint
            
        Returns:
            Checkpoint creado
        """
        async with self._lock:
            # Generar ID único para checkpoint
            checkpoint_id = f"{project_id}_{version}_{int(time.time() * 1000)}"
            
            checkpoint = Checkpoint(
                id=checkpoint_id,
                project_id=project_id,
                timestamp=time.time(),
                version=version,
                state=state,
                description=description
            )
            
            # Guardar a disco
            await self._save_checkpoint(checkpoint)
            
            # Actualizar cache
            if project_id not in self._checkpoints_cache:
                self._checkpoints_cache[project_id] = []
            
            self._checkpoints_cache[project_id].append(checkpoint)
            
            # Limitar número de checkpoints
            await self._cleanup_old_checkpoints(project_id)
            
            self.logger.info(
                "Checkpoint creado",
                checkpoint_id=checkpoint_id,
                project_id=project_id,
                version=version,
                description=description
            )
            
            return checkpoint
    
    async def rollback(
        self,
        project_id: str,
        checkpoint_id: Optional[str] = None,
        version: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Restaurar estado desde un checkpoint
        
        Args:
            project_id: ID del proyecto
            checkpoint_id: ID del checkpoint específico (opcional)
            version: Versión a la que rollback (opcional)
            
        Returns:
            Estado restaurado o None si no se encuentra
            
        Note:
            Si no se provee checkpoint_id ni version, se usa el checkpoint más reciente
        """
        async with self._lock:
            # Cargar checkpoints si no están en cache
            if project_id not in self._checkpoints_cache:
                await self._load_checkpoints(project_id)
            
            checkpoints = self._checkpoints_cache.get(project_id, [])
            
            if not checkpoints:
                self.logger.warning(
                    "No hay checkpoints disponibles",
                    project_id=project_id
                )
                return None
            
            # Seleccionar checkpoint
            target_checkpoint = None
            
            if checkpoint_id:
                # Buscar por ID
                target_checkpoint = next(
                    (cp for cp in checkpoints if cp.id == checkpoint_id),
                    None
                )
            elif version is not None:
                # Buscar checkpoint más cercano a la versión
                eligible = [cp for cp in checkpoints if cp.version <= version]
                if eligible:
                    target_checkpoint = max(eligible, key=lambda cp: cp.version)
            else:
                # Usar el más reciente
                target_checkpoint = max(checkpoints, key=lambda cp: cp.timestamp)
            
            if not target_checkpoint:
                self.logger.warning(
                    "Checkpoint no encontrado",
                    project_id=project_id,
                    checkpoint_id=checkpoint_id,
                    version=version
                )
                return None
            
            self.logger.info(
                "Rollback ejecutado",
                project_id=project_id,
                checkpoint_id=target_checkpoint.id,
                version=target_checkpoint.version,
                description=target_checkpoint.description
            )
            
            return target_checkpoint.state
    
    async def list_checkpoints(self, project_id: str) -> List[Checkpoint]:
        """
        Listar checkpoints de un proyecto
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Lista de checkpoints ordenados por timestamp (más reciente primero)
        """
        async with self._lock:
            if project_id not in self._checkpoints_cache:
                await self._load_checkpoints(project_id)
            
            checkpoints = self._checkpoints_cache.get(project_id, [])
            return sorted(checkpoints, key=lambda cp: cp.timestamp, reverse=True)
    
    async def delete_checkpoint(self, checkpoint_id: str, project_id: str):
        """
        Eliminar un checkpoint específico
        
        Args:
            checkpoint_id: ID del checkpoint a eliminar
            project_id: ID del proyecto
        """
        async with self._lock:
            # Eliminar de cache
            if project_id in self._checkpoints_cache:
                self._checkpoints_cache[project_id] = [
                    cp for cp in self._checkpoints_cache[project_id]
                    if cp.id != checkpoint_id
                ]
            
            # Eliminar archivo
            checkpoint_file = self._get_checkpoint_path(checkpoint_id)
            if checkpoint_file.exists():
                checkpoint_file.unlink()
                self.logger.info(
                    "Checkpoint eliminado",
                    checkpoint_id=checkpoint_id,
                    project_id=project_id
                )
    
    async def _save_checkpoint(self, checkpoint: Checkpoint):
        """Guardar checkpoint a disco"""
        checkpoint_file = self._get_checkpoint_path(checkpoint.id)
        
        try:
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint.to_dict(), f, indent=2)
            
            self.logger.debug(
                "Checkpoint guardado a disco",
                checkpoint_id=checkpoint.id,
                file=str(checkpoint_file)
            )
        except Exception as e:
            self.logger.error(
                "Error guardando checkpoint",
                checkpoint_id=checkpoint.id,
                error=str(e)
            )
            raise
    
    async def _load_checkpoints(self, project_id: str):
        """Cargar checkpoints de un proyecto desde disco"""
        checkpoints = []
        
        # Buscar archivos que coincidan con el project_id
        for checkpoint_file in self.checkpoints_dir.glob(f"{project_id}_*.json"):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                checkpoint = Checkpoint(
                    id=data['id'],
                    project_id=data['project_id'],
                    timestamp=data['timestamp'],
                    version=data['version'],
                    state=data['state'],
                    description=data.get('description')
                )
                checkpoints.append(checkpoint)
                
            except Exception as e:
                self.logger.error(
                    "Error cargando checkpoint",
                    file=str(checkpoint_file),
                    error=str(e)
                )
        
        self._checkpoints_cache[project_id] = checkpoints
        
        self.logger.debug(
            "Checkpoints cargados",
            project_id=project_id,
            count=len(checkpoints)
        )
    
    async def _cleanup_old_checkpoints(self, project_id: str):
        """Limpiar checkpoints antiguos manteniendo solo los últimos N"""
        checkpoints = self._checkpoints_cache.get(project_id, [])
        
        if len(checkpoints) <= self.max_checkpoints:
            return
        
        # Ordenar por timestamp (más reciente primero)
        sorted_checkpoints = sorted(
            checkpoints,
            key=lambda cp: cp.timestamp,
            reverse=True
        )
        
        # Mantener solo los max_checkpoints más recientes
        to_keep = sorted_checkpoints[:self.max_checkpoints]
        to_delete = sorted_checkpoints[self.max_checkpoints:]
        
        # Eliminar checkpoints antiguos
        for checkpoint in to_delete:
            checkpoint_file = self._get_checkpoint_path(checkpoint.id)
            if checkpoint_file.exists():
                checkpoint_file.unlink()
        
        self._checkpoints_cache[project_id] = to_keep
        
        self.logger.info(
            "Checkpoints antiguos limpiados",
            project_id=project_id,
            deleted=len(to_delete),
            remaining=len(to_keep)
        )
    
    def _get_checkpoint_path(self, checkpoint_id: str) -> Path:
        """Obtener ruta del archivo de checkpoint"""
        return self.checkpoints_dir / f"{checkpoint_id}.json"
    
    async def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del rollback manager"""
        total_checkpoints = 0
        projects_with_checkpoints = len(self._checkpoints_cache)
        
        for checkpoints in self._checkpoints_cache.values():
            total_checkpoints += len(checkpoints)
        
        # Calcular tamaño en disco
        disk_size = 0
        for checkpoint_file in self.checkpoints_dir.glob("*.json"):
            disk_size += checkpoint_file.stat().st_size
        
        return {
            'total_checkpoints': total_checkpoints,
            'projects_with_checkpoints': projects_with_checkpoints,
            'max_checkpoints_per_project': self.max_checkpoints,
            'disk_size_bytes': disk_size,
            'disk_size_mb': f"{disk_size / 1024 / 1024:.2f} MB",
            'checkpoints_dir': str(self.checkpoints_dir)
        }


# Alias para compatibilidad
RollbackManager = PersistentRollbackManager
