"""
Checklist Manager - Gestión de tareas y estados del proyecto
Coordina el flujo de trabajo con aprobaciones y rollback
"""
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from enum import Enum
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger()


class TaskStatus(str, Enum):
    """Estados posibles de una tarea"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_APPROVAL = "waiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class TaskPriority(str, Enum):
    """Prioridades de tareas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(BaseModel):
    """Modelo de una tarea en el checklist"""
    id: str
    title: str
    description: str
    assigned_to: str  # MCP role: architect, backend_developer, frontend_developer, tester
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    
    # Resultados
    result: Optional[Dict[str, Any]] = None
    output_files: List[str] = []
    
    # Aprobación
    requires_approval: bool = True
    stakeholder_comments: List[Dict[str, str]] = []
    approval_status: Optional[Literal["approved", "rejected", "changes_requested"]] = None
    
    # Dependencias
    depends_on: List[str] = []  # IDs de tareas que deben completarse primero
    blocks: List[str] = []  # IDs de tareas que esta bloquea
    
    # Metadata
    tags: List[str] = []
    estimated_effort: Optional[str] = None
    actual_effort: Optional[float] = None  # En horas


class ChecklistManager:
    """
    Gestiona el checklist de tareas del proyecto
    
    Funcionalidades:
    - Crear y organizar tareas
    - Gestionar estados y transiciones
    - Validar dependencias
    - Manejar aprobaciones de stakeholder
    - Generar reportes de progreso
    """
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.tasks: Dict[str, Task] = {}
        self.task_order: List[str] = []
        self.created_at = datetime.now()
        logger.info("checklist_manager_initialized", project_id=project_id)
    
    def create_task(
        self,
        title: str,
        description: str,
        assigned_to: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        depends_on: List[str] = None,
        requires_approval: bool = True
    ) -> Task:
        """Crea una nueva tarea en el checklist"""
        task_id = f"task_{len(self.tasks) + 1}_{int(datetime.now().timestamp())}"
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            assigned_to=assigned_to,
            priority=priority,
            depends_on=depends_on or [],
            requires_approval=requires_approval
        )
        
        self.tasks[task_id] = task
        self.task_order.append(task_id)
        
        # Actualizar bloqueos en tareas dependientes
        if depends_on:
            for dep_id in depends_on:
                if dep_id in self.tasks:
                    self.tasks[dep_id].blocks.append(task_id)
        
        logger.info("task_created", task_id=task_id, title=title, assigned_to=assigned_to)
        return task
    
    def start_task(self, task_id: str) -> bool:
        """Inicia una tarea si sus dependencias están completas"""
        if task_id not in self.tasks:
            logger.error("task_not_found", task_id=task_id)
            return False
        
        task = self.tasks[task_id]
        
        # Validar dependencias
        if not self._are_dependencies_met(task_id):
            logger.warning("dependencies_not_met", task_id=task_id, depends_on=task.depends_on)
            task.status = TaskStatus.BLOCKED
            return False
        
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        
        logger.info("task_started", task_id=task_id, title=task.title)
        return True
    
    def complete_task(self, task_id: str, result: Dict[str, Any]) -> bool:
        """Completa una tarea y la marca para aprobación si es necesario"""
        if task_id not in self.tasks:
            logger.error("task_not_found", task_id=task_id)
            return False
        
        task = self.tasks[task_id]
        
        if task.status != TaskStatus.IN_PROGRESS:
            logger.error("task_not_in_progress", task_id=task_id, status=task.status)
            return False
        
        task.result = result
        task.completed_at = datetime.now()
        
        if task.requires_approval:
            task.status = TaskStatus.WAITING_APPROVAL
            logger.info("task_awaiting_approval", task_id=task_id, title=task.title)
        else:
            task.status = TaskStatus.COMPLETED
            logger.info("task_completed", task_id=task_id, title=task.title)
        
        return True
    
    def approve_task(self, task_id: str, comment: str = "", approved: bool = True) -> bool:
        """Aprueba o rechaza una tarea por parte del stakeholder"""
        if task_id not in self.tasks:
            logger.error("task_not_found", task_id=task_id)
            return False
        
        task = self.tasks[task_id]
        
        if task.status != TaskStatus.WAITING_APPROVAL:
            logger.error("task_not_waiting_approval", task_id=task_id, status=task.status)
            return False
        
        # Agregar comentario del stakeholder
        task.stakeholder_comments.append({
            "timestamp": datetime.now().isoformat(),
            "comment": comment,
            "action": "approved" if approved else "rejected"
        })
        
        if approved:
            task.status = TaskStatus.APPROVED
            task.approval_status = "approved"
            task.approved_at = datetime.now()
            logger.info("task_approved", task_id=task_id, title=task.title)
        else:
            task.status = TaskStatus.REJECTED
            task.approval_status = "rejected"
            logger.warning("task_rejected", task_id=task_id, title=task.title, reason=comment)
        
        return True
    
    def request_changes(self, task_id: str, changes: str) -> bool:
        """Stakeholder solicita cambios en una tarea"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.stakeholder_comments.append({
            "timestamp": datetime.now().isoformat(),
            "comment": changes,
            "action": "changes_requested"
        })
        task.approval_status = "changes_requested"
        task.status = TaskStatus.PENDING  # Volver a pending para re-trabajo
        
        logger.info("changes_requested", task_id=task_id, changes=changes)
        return True
    
    def get_next_task(self) -> Optional[Task]:
        """Obtiene la siguiente tarea pendiente sin dependencias bloqueadas"""
        for task_id in self.task_order:
            task = self.tasks[task_id]
            if task.status == TaskStatus.PENDING and self._are_dependencies_met(task_id):
                return task
        return None
    
    def get_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """Obtiene todas las tareas con un estado específico"""
        return [task for task in self.tasks.values() if task.status == status]
    
    def get_tasks_by_role(self, role: str) -> List[Task]:
        """Obtiene tareas asignadas a un rol específico"""
        return [task for task in self.tasks.values() if task.assigned_to == role]
    
    def get_progress_report(self) -> Dict[str, Any]:
        """Genera reporte de progreso del checklist"""
        total_tasks = len(self.tasks)
        if total_tasks == 0:
            return {"error": "No tasks in checklist"}
        
        status_counts = {}
        for status in TaskStatus:
            status_counts[status.value] = len(self.get_tasks_by_status(status))
        
        completed = status_counts.get(TaskStatus.APPROVED.value, 0)
        progress_percentage = (completed / total_tasks) * 100
        
        return {
            "project_id": self.project_id,
            "total_tasks": total_tasks,
            "status_breakdown": status_counts,
            "progress_percentage": round(progress_percentage, 2),
            "tasks_pending_approval": status_counts.get(TaskStatus.WAITING_APPROVAL.value, 0),
            "tasks_blocked": status_counts.get(TaskStatus.BLOCKED.value, 0),
            "created_at": self.created_at.isoformat(),
            "estimated_completion": self._estimate_completion()
        }
    
    def _are_dependencies_met(self, task_id: str) -> bool:
        """Verifica si todas las dependencias de una tarea están aprobadas"""
        task = self.tasks[task_id]
        
        for dep_id in task.depends_on:
            if dep_id not in self.tasks:
                logger.warning("dependency_not_found", task_id=task_id, dep_id=dep_id)
                return False
            
            dep_task = self.tasks[dep_id]
            if dep_task.status not in [TaskStatus.APPROVED, TaskStatus.COMPLETED]:
                return False
        
        return True
    
    def _estimate_completion(self) -> Optional[str]:
        """Estima tiempo de completación (placeholder)"""
        # TODO: Implementar estimación basada en effort y velocidad
        return None
    
    def get_checklist_summary(self) -> List[Dict[str, Any]]:
        """Retorna resumen visual del checklist"""
        summary = []
        
        for task_id in self.task_order:
            task = self.tasks[task_id]
            summary.append({
                "id": task.id,
                "title": task.title,
                "assigned_to": task.assigned_to,
                "status": task.status.value,
                "priority": task.priority.value,
                "requires_approval": task.requires_approval,
                "blocked": task.status == TaskStatus.BLOCKED
            })
        
        return summary
