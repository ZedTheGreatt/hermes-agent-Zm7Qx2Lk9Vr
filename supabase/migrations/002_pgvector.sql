"""Supabase migration 002: Enable pgvector extension.

This migration enables the pgvector extension for vector similarity search.
"""

MIGRATION_SQL = """
-- Enable pgvector extension for embeddings similarity search
CREATE EXTENSION IF NOT EXISTS vector;
"""