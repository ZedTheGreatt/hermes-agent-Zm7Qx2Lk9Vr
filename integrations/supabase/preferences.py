"""Preferences service for Hermes Agent.

Manages user preferences as key-value pairs in Supabase.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from supabase import Client
from supabase.exceptions import APIError

from .client import get_supabase_client

logger = logging.getLogger(__name__)


class PreferenceService:
    """Service for managing user preferences."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.client: Client = get_supabase_client()
        self.table = self.client.table("preferences")

    def set_preference(self, key: str, value: Any, user_id: Optional[str] = None) -> str:
        """Set a preference value. Creates or updates the preference.

        Args:
            key: Preference key
            value: Preference value
            user_id: User ID (defaults to constructor value)

        Returns:
            Preference ID
        """
        user_id = user_id or self.user_id
        now = datetime.utcnow().isoformat()

        data = {
            "user_id": user_id,
            "key": key,
            "value": value,
            "updated_at": now,
        }

        try:
            # Upsert: update if exists, insert if new
            response = self.table.upsert(data, on_conflict="user_id,key").execute()
            if response.error:
                logger.error(f"Failed to set preference '{key}': {response.error}")
                raise response.error

            logger.info(f"Set preference '{key}' for user {user_id}")
            return response.data[0]["id"]
        except APIError as e:
            logger.error(f"APIError setting preference '{key}': {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error setting preference '{key}': {e}")
            raise

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a preference value."""
        try:
            response = (
                self.table.select("value")
                .eq("user_id", self.user_id)
                .eq("key", key)
                .execute()
            )
            if response.error:
                logger.error(f"Failed to get preference '{key}': {response.error}")
                return default
            if response.data:
                return response.data[0]["value"]
            return default
        except APIError as e:
            logger.error(f"APIError getting preference '{key}': {e}")
            return default
        except Exception as e:
            logger.error(f"Unexpected error getting preference '{key}': {e}")
            return default

    def list_preferences(self, prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all preferences for the user."""
        query = self.table.select("*").eq("user_id", self.user_id)
        if prefix:
            query = query.like("key", f"{prefix}%")
        query = query.order("key")

        try:
            response = query.execute()
            if response.error:
                logger.error(f"Failed to list preferences: {response.error}")
                return []
            return response.data
        except APIError as e:
            logger.error(f"APIError listing preferences: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing preferences: {e}")
            return []

    def delete_preference(self, key: str) -> bool:
        """Delete a preference by key."""
        try:
            response = (
                self.table.delete()
                .eq("user_id", self.user_id)
                .eq("key", key)
                .execute()
            )
            if response.error:
                logger.error(f"Failed to delete preference '{key}': {response.error}")
                return False
            logger.info(f"Deleted preference '{key}' for user {self.user_id}")
            return True
        except APIError as e:
            logger.error(f"APIError deleting preference '{key}': {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting preference '{key}': {e}")
            return False