"""Supabase client module for Hermes Agent.

Provides a singleton client wrapper around supabase-py with proper
error handling and connection management.
"""

import os
import logging
from typing import Optional
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Global client instance
_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create Supabase client instance.

    Returns:
        Client: Configured Supabase client

    Raises:
        RuntimeError: If Supabase credentials are not configured
    """
    global _supabase_client

    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        if not url or not key:
            raise RuntimeError(
                "Supabase credentials not configured. "
                "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables required."
            )

        try:
            _supabase_client = create_client(url, key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise

    return _supabase_client


class SupabaseClient:
    """Wrapper class for Supabase client with additional utility methods."""

    def __init__(self):
        self._client = get_supabase_client()

    @property
    def client(self) -> Client:
        """Access the underlying Supabase client."""
        return self._client

    def health_check(self) -> bool:
        """Check if Supabase connection is healthy.

        Returns:
            bool: True if connection is healthy, False otherwise
        """
        try:
            # Simple query to test connection
            self._client.table("users").select("count", count="exact").limit(1).execute()
            return True
        except Exception as e:
            logger.warning(f"Supabase health check failed: {e}")
            return False

    def close(self):
        """Close the Supabase connection (if applicable)."""
        # Supabase client doesn't require explicit closing in most cases
        # but we provide the method for consistency
        pass