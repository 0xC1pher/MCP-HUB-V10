"""
VectorEngine - Redirected to mempalace backend.
No more sentence-transformers or hnswlib.
"""
from .mempalace_storage import VectorEngine

__all__ = ['VectorEngine']
