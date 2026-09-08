"""Memory service for Hermes Agent.

Provides persistent long-term memory storage using Supabase with pgvector support.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from supabase import Client
from supabase.exceptions import APIError

from .client import get_supabase_client

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for managing long-term memory in Hermes Agent."""

    # Valid memory types
    MEMORY_TYPES = [
        "fact",
        "preference",
        "project",
        "relationship",
        "habit",
        "instruction",
        "experience",
    ]

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.client: Client = get_supabase_client()
        self.table = self.client.table("memories")

    def save_memory(
        self,
        memory_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.85,
        user_id: Optional[str] = None,
    ) -> str:
        """Save a memory to the database.

        Args:
            memory_type: Type of memory (fact, preference, project, etc.)
            content: Memory content
            metadata: Additional metadata
            importance: Memory importance score (0.0-1.0)
            user_id: User ID (defaults to constructor value)

        Returns:
            Memory ID
        """
        if memory_type not in self.MEMORY_TYPES:
            raise ValueError(
                f"Invalid memory type: {memory_type}. "
                f"Valid types: {self.MEMORY_TYPES}"
            )

        user_id = user_id or self.user_id
        metadata = metadata or {}

        data = {
            "user_id": user_id,
            "memory_type": memory_type,
            "content": content,
            "metadata": metadata,
            "importance": importance,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        try:
            response = self.table.insert(data).execute()
            if response.error:
                logger.error(f"Failed to save memory: {response.error}")
                raise response.error

            memory_id = response.data["id"]
            logger.info(f"Saved memory {memory_id} (type: {memory_type})")
            return memory_id
        except APIError as e:
            logger.error(f"APIError saving memory: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving memory: {e}")
            raise

    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a memory by ID."""
        try:
            response = self.table.select("*").eq("id", memory_id).execute()
            if response.error:
                logger.error(f"Failed to get memory {memory_id}: {response.error}")
                return None
            return response.data[0] if response.data else None
        except APIError as e:
            logger.error(f"APIError getting memory {memory_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting memory {memory_id}: {e}")
            return None

    def search_memories(
        self,
        query_embedding: List[float],
        threshold: float = 0.7,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search for semantically similar memories using vector similarity.

        Args:
            query_embedding: Embedding vector to search for
            threshold: Similarity threshold (0.0-1.0)
            limit: Maximum number of results to return

        Returns:
            List of memory records sorted by similarity
        """
        # ponyail: vector search placeholder - actual implementation needs pgvector RPC call
        # Real implementation would use:
        # response = self.client.rpc("match_memories", {
        #     "query_embedding": query_embedding,
        #     "match_threshold": threshold,
        #     "match_count": limit,
        # }).execute()
        logger.warning("Vector search not yet implemented - needs pgvector RPC")
        return []

    def list_memories(
        self,
        memory_type: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List memories with optional filtering."""
        query = self.table.select("*")

        if user_id:
            query = query.eq("user_id", user_id)
        elif hasattr(self, "user_id"):
            query = query.eq("user_id", self.user_id)

        if memory_type:
            query = query.eq("memory_type", memory_type)

        query = query.order("created_at", desc=True).limit(limit)

        try:
            response = query.execute()
            if response.error:
                logger.error(f"Failed to list memories: {response.error}")
                return []
            return response.data
        except APIError as e:
            logger.error(f"APIError listing memories: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing memories: {e}")
            return []

    def update_memory(
        self, memory_id: str, content: str, importance: Optional[float] = None
    ) -> bool:
        """Update an existing memory."""
        data = {
            "content": content,
            "updated_at": datetime.utcnow().isoformat(),
        }
        if importance is not None:
            data["importance"] = importance

        try:
            response = self.table.update(data).eq("id", memory_id).execute()
            if response.error:
                logger.error(f"Failed to update memory: {response.error}")
                return False
            logger.info(f"Updated memory {memory_id}")
            return True
        except APIError as e:
            logger.error(f"APIError updating memory {memory_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating memory {memory_id}: {e}")
            return False

    def forget_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        try:
            response = self.table.delete().eq("id", memory_id).execute()
            if response.error:
                logger.error(f"Failed to delete memory: {response.error}")
                return False
            logger.info(f"Deleted memory {memory_id}")
            return True
        except APIError as e:
            logger.error(f"APIError deleting memory {memory_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting memory {memory_id}: {e}")
            return False