"""
Storage Module - Mempalace-backed storage layer.
No more MP4 files, no more JSONL, no more scattered JSON.
"""
from .mempalace_storage import MempalaceStorage, VirtualChunk, VectorEngine

__all__ = ['MempalaceStorage', 'VirtualChunk', 'VectorEngine']
