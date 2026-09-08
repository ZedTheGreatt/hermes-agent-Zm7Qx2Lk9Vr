"""Events service for Hermes Agent.

Provides event logging and audit trail functionality.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from supabase import Client
from supabase.exceptions import APIError

from .client import get_supabase_client

logger = logging.getLogger(__name__)


class EventService:
    """Service for logging agent events and user interactions."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.client: Client = get_supabase_client()
        self.table = self.client.table("events")

    def log_event(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """Log an event.

        Args:
            event_type: Type of event (agent_started, telegram_message, etc.)
            payload: Event payload data (optional)
            metadata: Additional metadata (optional)
            user_id: User ID (defaults to constructor value)

        Returns:
            Event ID
        """
        user_id = user_id or self.user_id
        now = datetime.utcnow().isoformat()

        data = {
            "user_id": user_id,
            "event_type": event_type,
            "payload": payload or {},
            "metadata": metadata or {},
            "created_at": now,
        }

        try:
            response = self.table.insert(data).execute()
            if response.error:
                logger.error(f"Failed to log event '{event_type}': {response.error}")
                raise response.error

            event_id = response.data["id"]
            logger.debug(f"Logged event {event_id}: '{event_type}'")
            return event_id
        except APIError as e:
            logger.error(f"APIError logging event '{event_type}': {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error logging event '{event_type}': {e}")
            raise

    def list_events(
        self,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List events with optional filtering."""
        query = self.table.select("*").eq("user_id", self.user_id)

        if event_type:
            query = query.eq("event_type", event_type)

        query = query.order("created_at", desc=True).limit(limit)

        try:
            response = query.execute()
            if response.error:
                logger.error(f"Failed to list events: {response.error}")
                return []
            return response.data
        except APIError as e:
            logger.error(f"APIError listing events: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing events: {e}")
            return []

    def get_recent_events(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get events from the last N hours."""
        from datetime import timedelta

        cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()

        try:
            response = (
                self.table.select("*")
                .eq("user_id", self.user_id)
                .gte("created_at", cutoff)
                .order("created_at", desc=True)
                .execute()
            )
            if response.error:
                logger.error(f"Failed to get recent events: {response.error}")
                return []
            return response.data
        except APIError as e:
            logger.error(f"APIError getting recent events: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting recent events: {e}")
            return []