"""Tasks service for Hermes Agent.

Provides task management capabilities for the agent's task system.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from supabase import Client
from supabase.exceptions import APIError

from .client import get_supabase_client

logger = logging.getLogger(__name__)


class TaskStatus:
    """Task status constants."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"


class TaskService:
    """Service for managing user tasks."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.client: Client = get_supabase_client()
        self.table = self.client.table("tasks")

    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: int = 5,
        due_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """Create a new task.

        Args:
            title: Task title
            description: Task description (optional)
            priority: Priority level (1-10, 10 highest)
            due_at: Due date (optional)
            metadata: Additional metadata (optional)
            user_id: User ID (defaults to constructor value)

        Returns:
            Task ID
        """
        user_id = user_id or self.user_id
        now = datetime.utcnow().isoformat()

        data = {
            "user_id": user_id,
            "title": title,
            "description": description,
            "status": TaskStatus.PENDING,
            "priority": priority,
            "due_at": due_at.isoformat() if due_at else None,
            "metadata": metadata or {},
            "created_at": now,
            "updated_at": now,
        }

        try:
            response = self.table.insert(data).execute()
            if response.error:
                logger.error(f"Failed to create task '{title}': {response.error}")
                raise response.error

            task_id = response.data["id"]
            logger.info(f"Created task {task_id}: '{title}'")
            return task_id
        except APIError as e:
            logger.error(f"APIError creating task '{title}': {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error creating task '{title}': {e}")
            raise

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a task by ID."""
        try:
            response = self.table.select("*").eq("id", task_id).execute()
            if response.error:
                logger.error(f"Failed to get task {task_id}: {response.error}")
                return None
            return response.data[0] if response.data else None
        except APIError as e:
            logger.error(f"APIError getting task {task_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting task {task_id}: {e}")
            return None

    def update_task(
        self,
        task_id: str,
        status: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[int] = None,
        due_at: Optional[datetime] = None,
    ) -> bool:
        """Update a task."""
        data = {"updated_at": datetime.utcnow().isoformat()}

        if status is not None:
            data["status"] = status
        if title is not None:
            data["title"] = title
        if description is not None:
            data["description"] = description
        if priority is not None:
            data["priority"] = priority
        if due_at is not None:
            data["due_at"] = due_at.isoformat()

        try:
            response = self.table.update(data).eq("id", task_id).execute()
            if response.error:
                logger.error(f"Failed to update task {task_id}: {response.error}")
                return False
            logger.info(f"Updated task {task_id}")
            return True
        except APIError as e:
            logger.error(f"APIError updating task {task_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating task {task_id}: {e}")
            return False

    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        try:
            response = self.table.delete().eq("id", task_id).execute()
            if response.error:
                logger.error(f"Failed to delete task {task_id}: {response.error}")
                return False
            logger.info(f"Deleted task {task_id}")
            return True
        except APIError as e:
            logger.error(f"APIError deleting task {task_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting task {task_id}: {e}")
            return False

    def list_tasks(
        self,
        status: Optional[str] = None,
        priority_min: Optional[int] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """List tasks with optional filtering."""
        query = self.table.select("*").eq("user_id", self.user_id)

        if status:
            query = query.eq("status", status)
        if priority_min is not None:
            query = query.gte("priority", priority_min)

        query = query.order("priority", desc=True).order("due_at").limit(limit)

        try:
            response = query.execute()
            if response.error:
                logger.error(f"Failed to list tasks: {response.error}")
                return []
            return response.data
        except APIError as e:
            logger.error(f"APIError listing tasks: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing tasks: {e}")
            return []

    def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed."""
        return self.update_task(task_id, status=TaskStatus.COMPLETED)