"""
Checkpoint Handler - Manejo de puntos de validación del stakeholder
Permite pausar el flujo, solicitar aprobación y hacer rollback
"""
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import structlog
from pydantic import BaseModel

from core.memory.rollback_manager import RollbackManager

logger = structlog.get_logger()


class CheckpointDecision(str, Enum):
    """Decisiones posibles en un checkpoint"""
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"
    SKIP = "skip"
    ROLLBACK = "rollback"


class Checkpoint(BaseModel):
    """Modelo de un checkpoint de validación"""
    id: str
    task_id: str
    task_title: str
    created_at: datetime
    agent_role: str  # Rol del MCP que generó el resultado
    result_summary: Dict[str, Any]
    
    # Estado del checkpoint
    decision: Optional[CheckpointDecision] = None
    stakeholder_feedback: Optional[str] = None
    decided_at: Optional[datetime] = None
    
    # Para rollback
    snapshot_id: Optional[str] = None


class CheckpointHandler:
    """
    Gestiona checkpoints de validación con stakeholder
    
    Funcionalidades:
    - Crear checkpoints después de cada tarea
    - Pausar flujo para aprobación
    - Capturar feedback del stakeholder
    - Gestionar rollback a checkpoints anteriores
    - Historial de decisiones
    """
    
    def __init__(self, rollback_manager: RollbackManager):
        self.rollback_manager = rollback_manager
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.checkpoint_order: List[str] = []
        self.current_checkpoint_id: Optional[str] = None
        
        # Callbacks para interacción con usuario
        self.on_checkpoint_created: Optional[Callable] = None
        self.on_decision_made: Optional[Callable] = None
        
        logger.info("checkpoint_handler_initialized")
    
    async def create_checkpoint(
        self,
        task_id: str,
        task_title: str,
        agent_role: str,
        result: Dict[str, Any]
    ) -> str:
        """
        Crea un checkpoint de validación
        
        Args:
            task_id: ID de la tarea completada
            task_title: Título de la tarea
            agent_role: Rol del agente (architect, backend_developer, etc)
            result: Resultado generado por el agente
            
        Returns:
            checkpoint_id
        """
        checkpoint_id = f"checkpoint_{len(self.checkpoints) + 1}_{int(datetime.now().timestamp())}"
        
        # Crear snapshot para posible rollback
        snapshot_id = await self.rollback_manager.create_checkpoint(
            checkpoint_name=checkpoint_id,
            metadata={
                "task_id": task_id,
                "agent_role": agent_role,
                "checkpoint_type": "task_completion"
            }
        )
        
        # Extraer resumen del resultado
        result_summary = self._extract_result_summary(result, agent_role)
        
        checkpoint = Checkpoint(
            id=checkpoint_id,
            task_id=task_id,
            task_title=task_title,
            created_at=datetime.now(),
            agent_role=agent_role,
            result_summary=result_summary,
            snapshot_id=snapshot_id
        )
        
        self.checkpoints[checkpoint_id] = checkpoint
        self.checkpoint_order.append(checkpoint_id)
        self.current_checkpoint_id = checkpoint_id
        
        logger.info(
            "checkpoint_created",
            checkpoint_id=checkpoint_id,
            task_title=task_title,
            agent_role=agent_role
        )
        
        # Notificar callback si existe
        if self.on_checkpoint_created:
            await self.on_checkpoint_created(checkpoint)
        
        return checkpoint_id
    
    async def wait_for_decision(self, checkpoint_id: str) -> CheckpointDecision:
        """
        Pausa el flujo esperando decisión del stakeholder
        
        En implementación real, esto esperaría input del usuario
        Por ahora retorna aprobación automática
        """
        if checkpoint_id not in self.checkpoints:
            logger.error("checkpoint_not_found", checkpoint_id=checkpoint_id)
            raise ValueError(f"Checkpoint {checkpoint_id} not found")
        
        checkpoint = self.checkpoints[checkpoint_id]
        
        logger.info(
            "waiting_for_decision",
            checkpoint_id=checkpoint_id,
            task_title=checkpoint.task_title
        )
        
        # TODO: Implementar espera real de input del usuario
        # Por ahora retornamos aprobación automática para tests
        return CheckpointDecision.APPROVE
    
    async def make_decision(
        self,
        checkpoint_id: str,
        decision: CheckpointDecision,
        feedback: Optional[str] = None
    ) -> bool:
        """
        Registra la decisión del stakeholder en un checkpoint
        
        Args:
            checkpoint_id: ID del checkpoint
            decision: Decisión tomada
            feedback: Comentarios del stakeholder
            
        Returns:
            True si la decisión fue registrada exitosamente
        """
        if checkpoint_id not in self.checkpoints:
            logger.error("checkpoint_not_found", checkpoint_id=checkpoint_id)
            return False
        
        checkpoint = self.checkpoints[checkpoint_id]
        checkpoint.decision = decision
        checkpoint.stakeholder_feedback = feedback
        checkpoint.decided_at = datetime.now()
        
        logger.info(
            "decision_made",
            checkpoint_id=checkpoint_id,
            decision=decision.value,
            has_feedback=bool(feedback)
        )
        
        # Ejecutar rollback si fue solicitado
        if decision == CheckpointDecision.ROLLBACK and checkpoint.snapshot_id:
            await self._perform_rollback(checkpoint.snapshot_id)
        
        # Notificar callback si existe
        if self.on_decision_made:
            await self.on_decision_made(checkpoint, decision)
        
        return True
    
    async def rollback_to_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Hace rollback a un checkpoint específico
        
        Args:
            checkpoint_id: ID del checkpoint al que volver
            
        Returns:
            True si el rollback fue exitoso
        """
        if checkpoint_id not in self.checkpoints:
            logger.error("checkpoint_not_found", checkpoint_id=checkpoint_id)
            return False
        
        checkpoint = self.checkpoints[checkpoint_id]
        
        if not checkpoint.snapshot_id:
            logger.error("no_snapshot_available", checkpoint_id=checkpoint_id)
            return False
        
        success = await self._perform_rollback(checkpoint.snapshot_id)
        
        if success:
            logger.info("rollback_successful", checkpoint_id=checkpoint_id)
            # Invalidar checkpoints posteriores
            self._invalidate_subsequent_checkpoints(checkpoint_id)
        
        return success
    
    async def _perform_rollback(self, snapshot_id: str) -> bool:
        """Ejecuta el rollback usando RollbackManager"""
        try:
            await self.rollback_manager.rollback_to_checkpoint(snapshot_id)
            logger.info("rollback_executed", snapshot_id=snapshot_id)
            return True
        except Exception as e:
            logger.error("rollback_failed", snapshot_id=snapshot_id, error=str(e))
            return False
    
    def _invalidate_subsequent_checkpoints(self, checkpoint_id: str):
        """Invalida checkpoints posteriores al rollback"""
        found = False
        for cp_id in self.checkpoint_order:
            if found:
                # Marcar como invalidado
                self.checkpoints[cp_id].decision = None
                self.checkpoints[cp_id].stakeholder_feedback = "Invalidated by rollback"
                logger.debug("checkpoint_invalidated", checkpoint_id=cp_id)
            elif cp_id == checkpoint_id:
                found = True
    
    def _extract_result_summary(self, result: Dict[str, Any], agent_role: str) -> Dict[str, Any]:
        """Extrae resumen legible del resultado para mostrar al stakeholder"""
        summary = {
            "agent_role": agent_role,
            "timestamp": datetime.now().isoformat()
        }
        
        # Extraer información clave según el rol
        if agent_role == "architect":
            summary.update({
                "plan_id": result.get("plan_id"),
                "components_count": len(result.get("components", [])),
                "components": [c.get("name") for c in result.get("components", [])],
                "risks": result.get("risks", []),
                "estimated_effort": result.get("estimated_effort")
            })
        
        elif agent_role in ["backend_developer", "frontend_developer"]:
            summary.update({
                "implementation_id": result.get("implementation_id"),
                "component_name": result.get("component_name"),
                "files_generated": len(result.get("code_files", [])),
                "file_paths": [f.get("path") for f in result.get("code_files", [])],
                "dependencies": result.get("dependencies", [])
            })
        
        elif agent_role == "tester":
            summary.update({
                "validation_passed": result.get("validation_passed"),
                "issues_count": len(result.get("issues", [])),
                "test_coverage": result.get("test_coverage"),
                "critical_issues": [
                    i for i in result.get("issues", [])
                    if i.get("severity") == "critical"
                ]
            })
        
        return summary
    
    def get_checkpoint_history(self) -> List[Dict[str, Any]]:
        """Retorna historial de checkpoints con decisiones"""
        history = []
        
        for cp_id in self.checkpoint_order:
            cp = self.checkpoints[cp_id]
            history.append({
                "id": cp.id,
                "task_title": cp.task_title,
                "agent_role": cp.agent_role,
                "created_at": cp.created_at.isoformat(),
                "decision": cp.decision.value if cp.decision else "pending",
                "feedback": cp.stakeholder_feedback,
                "decided_at": cp.decided_at.isoformat() if cp.decided_at else None
            })
        
        return history
    
    def get_pending_checkpoints(self) -> List[Checkpoint]:
        """Retorna checkpoints pendientes de decisión"""
        return [
            cp for cp in self.checkpoints.values()
            if cp.decision is None
        ]
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Obtiene un checkpoint específico"""
        return self.checkpoints.get(checkpoint_id)
