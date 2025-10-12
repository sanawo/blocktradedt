from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
from sentence_transformers import SentenceTransformer


DATA_FILE = Path("data/sample_listings.jsonl")
ARTIFACTS_DIR = Path("artifacts")
EMBEDDINGS_FILE = ARTIFACTS_DIR / "embeddings.npy"
METADATA_FILE = ARTIFACTS_DIR / "metadata.jsonl"
MODEL_NAME_FILE = ARTIFACTS_DIR / "model_name.txt"

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


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


def main() -> None:
    assert DATA_FILE.exists(), f"Data file not found: {DATA_FILE}"
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    docs = load_documents(DATA_FILE)
    texts = [make_text(d) for d in docs]

    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    
    print(f"Encoding {len(texts)} documents...")
    vectors = model.encode(texts, show_progress_bar=True)
    arr = np.asarray(vectors, dtype=np.float32)

    np.save(EMBEDDINGS_FILE, arr)
    with METADATA_FILE.open("w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    with MODEL_NAME_FILE.open("w", encoding="utf-8") as f:
        f.write(MODEL_NAME)

    print(f"Wrote {len(docs)} docs, shape={arr.shape}")
    print(f"Index saved to {ARTIFACTS_DIR}")


if __name__ == "__main__":
    main()


