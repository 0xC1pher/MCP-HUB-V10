"""
MempalaceStorage - Replaces MP4Storage + VectorEngine.

All code chunks are stored as mempalace drawers with semantic search.
No MP4 files, no HNSW index, no sentence-transformers dependency.
"""
import json
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

import structlog

logger = structlog.get_logger()


@dataclass
class VirtualChunk:
    """Represents a code/text chunk stored in mempalace."""
    chunk_id: str
    file_path: str
    start_line: int
    end_line: int
    section: str
    summary: str
    text_hash: str

    def get_text(self) -> str:
        """Read text from source file."""
        try:
            with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            return "".join(lines[self.start_line - 1:self.end_line])
        except (OSError, IndexError):
            return ""

    def to_dict(self) -> Dict:
        return {
            "chunk_id": self.chunk_id, "file_path": self.file_path,
            "start_line": self.start_line, "end_line": self.end_line,
            "section": self.section, "summary": self.summary,
            "text_hash": self.text_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "VirtualChunk":
        return cls(**{k: v for k, v in data.items()
                      if k in cls.__dataclass_fields__})


class MempalaceStorage:
    """Unified storage replacing MP4Storage + VectorEngine.

    Instead of MP4 files and HNSW indexes, this stores everything
    as mempalace drawers with automatic semantic search.
    """

    def __init__(self, wing: str = "hub", **kwargs):
        self.wing = wing
        self.chunks: List[VirtualChunk] = []
        self.metadata: Dict = {
            "version": "10.0.0-mempalace",
            "total_vectors": 0,
            "embedding_model": "mempalace-default",
        }
        self._backend = None

    def _get_backend(self):
        """Lazy-load mempalace backend."""
        if self._backend is None:
            from ..mempalace_backend import MempalaceStorage as MB
            self._backend = MB(self.wing)
        return self._backend

    def create_snapshot(self, chunks: List, vectors_blob: bytes = None,
                        hnsw_blob: bytes = None,
                        metadata: Dict = None) -> str:
        """Store chunks as mempalace drawers (no MP4 file)."""
        from ..mempalace_backend import add_drawer, Room
        count = 0
        for chunk_data in chunks:
            if isinstance(chunk_data, dict):
                content = json.dumps(chunk_data, default=str)
            else:
                content = str(chunk_data)
            try:
                add_drawer(wing=self.wing, room=Room.CODE,
                           content=content, source_file="snapshot")
                count += 1
            except Exception as e:
                logger.warning("Failed to store chunk", error=str(e))
        self.metadata["total_vectors"] = count
        logger.info("Snapshot stored in mempalace", chunks=count)
        return f"mempalace:{count}"

    def load_snapshot(self) -> bool:
        """Load chunks from mempalace (no MP4 to load)."""
        from ..mempalace_backend import list_drawers, Room
        drawers = list_drawers(wing=self.wing, room=Room.CODE, limit=1000)
        self.chunks = []
        for d in drawers:
            try:
                data = json.loads(d.get("content", "{}"))
                self.chunks.append(VirtualChunk.from_dict(data))
            except (json.JSONDecodeError, TypeError):
                continue
        self.metadata["total_vectors"] = len(self.chunks)
        return bool(self.chunks)

    def search_chunks(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search chunks using mempalace semantic search."""
        from ..mempalace_backend import search, Room
        results = search(query=query, wing=self.wing, room=Room.CODE,
                         limit=top_k)
        return [
            {"chunk_id": r.get("id", ""), "score": r.get("score", 0.0),
             "content": r.get("content", "")}
            for r in results
        ]

    def get_stats(self) -> Dict:
        """Get storage statistics."""
        return {
            "backend": "mempalace",
            "wing": self.wing,
            "total_chunks": len(self.chunks),
            "metadata": self.metadata,
        }


class VectorEngine:
    """Lightweight vector engine replacement using mempalace search.

    Provides the same API as the original VectorEngine but delegates
    to mempalace's built-in semantic search.
    """

    def __init__(self, config: Dict = None, **kwargs):
        self.config = config or {}
        self.wing = self.config.get("wing", "hub")
        self._search_cache = {}

    def embed_text(self, text: str):
        """Embedding is handled by mempalace internally."""
        return text  # Pass-through; mempalace handles embeddings

    def embed_query(self, text: str):
        """Alias for embed_text."""
        return self.embed_text(text)

    def embed_batch(self, texts: List[str]):
        """Batch embedding handled by mempalace."""
        return texts

    def search_with_mvr(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search using mempalace semantic search."""
        from ..mempalace_backend import search, Room
        results = search(query=query, wing=self.wing, room=Room.CODE,
                         limit=top_k)
        return [{"chunk_id": r.get("id", ""), "score": r.get("score", 0.0)}
                for r in results]

    def search(self, query: str, top_k: int = 5) -> Tuple[List[str], List[float]]:
        """Search returning chunk_ids and scores."""
        results = self.search_with_mvr(query, top_k)
        ids = [r["chunk_id"] for r in results]
        scores = [r["score"] for r in results]
        return ids, scores

    def create_index(self, num_elements: int) -> None:
        """No-op: mempalace handles indexing."""
        pass

    def add_vectors(self, vectors, chunk_ids) -> None:
        """Store chunks as mempalace drawers instead of vectors."""
        from ..mempalace_backend import add_drawer, Room
        for chunk_id, _ in zip(chunk_ids, vectors):
            add_drawer(wing=self.wing, room=Room.CODE,
                       content=f"chunk:{chunk_id}",
                       source_file="vector_engine")

    def serialize_index(self) -> bytes:
        """No-op: mempalace persists automatically."""
        return b""

    def load_index_from_bytes(self, data: bytes, num_elements: int) -> None:
        """No-op: mempalace loads on demand."""
        pass

    def get_stats(self) -> Dict:
        """Get engine statistics."""
        return {
            "status": "mempalace-backend",
            "num_vectors": 0,
            "dimension": 384,
            "model": "mempalace-default",
            "note": "Embeddings handled by mempalace ChromaDB",
        }
