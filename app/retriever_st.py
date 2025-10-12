from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from sentence_transformers import SentenceTransformer


class VectorStore:
    def __init__(
        self,
        embeddings_file: str,
        metadata_file: str,
        model_name_file: str,
    ) -> None:
        self.embeddings_path = Path(embeddings_file)
        self.metadata_path = Path(metadata_file)
        self.model_name_path = Path(model_name_file)

        if not (self.embeddings_path.exists() and self.metadata_path.exists() and self.model_name_path.exists()):
            raise FileNotFoundError("Index artifacts not found. Please run: python scripts/build_index_st.py")

        self.embeddings: np.ndarray = np.load(self.embeddings_path)
        self.metadata: List[Dict[str, Any]] = []
        with self.metadata_path.open("r", encoding="utf-8") as f:
            for line in f:
                self.metadata.append(json.loads(line))

        with self.model_name_path.open("r", encoding="utf-8") as f:
            self.model_name = f.read().strip()

        self.model = SentenceTransformer(self.model_name)
        self.embeddings_norm = self._normalize(self.embeddings)

    @staticmethod
    def _normalize(vectors: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12
        return vectors / norm

    def _embed_query(self, text: str) -> np.ndarray:
        vec = self.model.encode([text])[0]
        vec = np.asarray(vec, dtype=np.float32)
        vec = vec / (np.linalg.norm(vec) + 1e-12)
        return vec

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        if top_k <= 0:
            return []
        vec = self._embed_query(query)
        scores = self.embeddings_norm @ vec
        top_k = min(top_k, len(scores))
        indices = np.argpartition(scores, -top_k)[-top_k:]
        indices = indices[np.argsort(scores[indices])[::-1]]

        results: List[Dict[str, Any]] = []
        for i in indices:
            item = self.metadata[int(i)].copy()
            results.append({
                "score": float(scores[int(i)]),
                "listing": item,
            })
        return results


