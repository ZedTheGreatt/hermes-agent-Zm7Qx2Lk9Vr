"""Embeddings service for Hermes Agent.

Provides vector embedding storage and semantic search using Supabase pgvector.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from supabase import Client
from supabase.exceptions import APIError

from .client import get_supabase_client

logger = logging.getLogger(__name__)


class VectorService:
    """Service for managing vector embeddings and semantic search."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.client: Client = get_supabase_client()
        self.table = self.client.table("embeddings")

    def store_embedding(
        self,
        content_id: str,
        content_type: str,
        embedding: List[float],
        content_text: str,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """Store a vector embedding.

        Args:
            content_id: ID of the associated content (memory_id, task_id, etc.)
            content_type: Type of content (memory, task, preference, etc.)
            embedding: Vector embedding (list of floats)
            content_text: Original text content
            metadata: Additional metadata (optional)
            user_id: User ID (defaults to constructor value)

        Returns:
            Embedding ID
        """
        user_id = user_id or self.user_id
        now = datetime.utcnow().isoformat()

        data = {
            "user_id": user_id,
            "content_id": content_id,
            "content_type": content_type,
            "embedding": embedding,
            "content_text": content_text,
            "metadata": metadata or {},
            "created_at": now,
        }

        try:
            response = self.table.insert(data).execute()
            if response.error:
                logger.error(f"Failed to store embedding: {response.error}")
                raise response.error

            embedding_id = response.data["id"]
            logger.debug(f"Stored embedding {embedding_id} for {content_type}:{content_id}")
            return embedding_id
        except APIError as e:
            logger.error(f"APIError storing embedding: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error storing embedding: {e}")
            raise

    def search_similar(
        self,
        query_embedding: List[float],
        threshold: float = 0.7,
        limit: int = 10,
        content_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar embeddings using pgvector.

        Args:
            query_embedding: Query vector
            threshold: Similarity threshold (0.0-1.0)
            limit: Maximum number of results
            content_type: Filter by content type (optional)

        Returns:
            List of similar embeddings with similarity scores
        """
        # ponyail: vector search placeholder - actual implementation needs pgvector RPC
        # Real implementation would call Supabase RPC:
        # response = self.client.rpc("match_embeddings", {
        #     "query_embedding": query_embedding,
        #     "match_threshold": threshold,
        #     "match_count": limit,
        #     "p_user_id": self.user_id,
        #     "p_content_type": content_type,
        # }).execute()
        logger.warning("Vector similarity search not yet implemented - needs pgvector RPC")
        return []

    def delete_embedding(self, content_id: str, content_type: str) -> bool:
        """Delete embeddings associated with content."""
        try:
            response = (
                self.table.delete()
                .eq("user_id", self.user_id)
                .eq("content_id", content_id)
                .eq("content_type", content_type)
                .execute()
            )
            if response.error:
                logger.error(f"Failed to delete embedding: {response.error}")
                return False
            logger.debug(f"Deleted embeddings for {content_type}:{content_id}")
            return True
        except APIError as e:
            logger.error(f"APIError deleting embedding: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting embedding: {e}")
            return False

    def get_embeddings(self, content_id: str, content_type: str) -> List[Dict[str, Any]]:
        """Get embeddings for specific content."""
        try:
            response = (
                self.table.select("*")
                .eq("user_id", self.user_id)
                .eq("content_id", content_id)
                .eq("content_type", content_type)
                .execute()
            )
            if response.error:
                logger.error(f"Failed to get embeddings: {response.error}")
                return []
            return response.data
        except APIError as e:
            logger.error(f"APIError getting embeddings: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting embeddings: {e}")
            return []