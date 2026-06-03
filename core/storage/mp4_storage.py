"""
MP4Storage - Redirected to MempalaceStorage.
No more MP4 files.
"""
from .mempalace_storage import MempalaceStorage as MP4Storage, VirtualChunk

__all__ = ['MP4Storage', 'VirtualChunk']
