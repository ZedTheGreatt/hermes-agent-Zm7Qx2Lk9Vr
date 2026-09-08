"""Supabase integration for Hermes Agent.

Provides persistent long-term memory, preferences, tasks, events,
and vector embeddings alongside Hermes's native SQLite state.

Architecture:
    Hermes Agent
    ├── SQLite (state.db) — native sessions, messages, tool calls, FTS5
    └── Supabase (PostgreSQL + pgvector) — durable application data

Design principle: Do not replace Hermes SQLite with Supabase.
SQLite handles Hermes's internal state. Supabase handles your agent's
durable external data: long-term memory, user profile, preferences,
tasks, events, and semantic search embeddings.
"""

from .client import get_supabase_client, SupabaseClient
from .memory import MemoryService
from .preferences import PreferenceService
from .tasks import TaskService
from .events import EventService
from .embeddings import VectorService

__all__ = [
    "get_supabase_client",
    "SupabaseClient",
    "MemoryService",
    "PreferenceService",
    "TaskService",
    "EventService",
    "VectorService",
]
