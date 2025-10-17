from __future__ import annotations

import json
import hashlib
# import numpy as np  # Removed to fix deployment issues
from pathlib import Path
from typing import List, Dict, Any


DATA_FILE = Path("data/sample_listings.jsonl")
ARTIFACTS_DIR = Path("artifacts")
EMBEDDINGS_FILE = ARTIFACTS_DIR / "embeddings.npy"
METADATA_FILE = ARTIFACTS_DIR / "metadata.jsonl"
MODEL_NAME_FILE = ARTIFACTS_DIR / "model_name.txt"

MODEL_NAME = "mock-embedding-model"


def load_documents(path: Path) -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            docs.append(json.loads(line))
    return docs


def make_text(doc: Dict[str, Any]) -> str:
    parts: List[str] = []
    for key in ["title", "category", "region", "price", "unit", "description", "seller", "tags", "date"]:
        val = doc.get(key)
        if val is None:
            continue
        if isinstance(val, list):
            val = ",".join(map(str, val))
        parts.append(f"{key}:{val}")
    return " \n ".join(parts)


def create_mock_embedding(text: str, dimension: int = 384) -> np.ndarray:
    """Create a mock embedding based on text hash for demonstration"""
    # Use hash of text to create deterministic but varied embeddings
    hash_obj = hashlib.md5(text.encode('utf-8'))
    hash_bytes = hash_obj.digest()
    
    # Convert hash to float array
    embedding = np.zeros(dimension, dtype=np.float32)
    for i in range(min(len(hash_bytes), dimension)):
        embedding[i] = (hash_bytes[i] - 128) / 128.0  # Normalize to [-1, 1]
    
    # Fill remaining dimensions with random values based on hash
    np.random.seed(int.from_bytes(hash_bytes[:4], 'big'))
    if dimension > len(hash_bytes):
        embedding[len(hash_bytes):] = np.random.normal(0, 0.1, dimension - len(hash_bytes))
    
    # Normalize to unit vector
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm
    
    return embedding


def main() -> None:
    assert DATA_FILE.exists(), f"Data file not found: {DATA_FILE}"
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    docs = load_documents(DATA_FILE)
    texts = [make_text(d) for d in docs]

    # Create mock embeddings
    vectors = [create_mock_embedding(text) for text in texts]
    arr = np.asarray(vectors, dtype=np.float32)

    np.save(EMBEDDINGS_FILE, arr)
    with METADATA_FILE.open("w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    with MODEL_NAME_FILE.open("w", encoding="utf-8") as f:
        f.write(MODEL_NAME)

    print(f"Created mock index with {len(docs)} docs, shape={arr.shape}")
    print("Note: This is a mock index for demonstration purposes only.")


if __name__ == "__main__":
    main()




