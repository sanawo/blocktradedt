from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from fastembed import TextEmbedding


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
            raise FileNotFoundError("Index artifacts not found. Please run: python scripts/build_index.py")

        self.embeddings: np.ndarray = np.load(self.embeddings_path)
        self.metadata: List[Dict[str, Any]] = []
        with self.metadata_path.open("r", encoding="utf-8") as f:
            for line in f:
                self.metadata.append(json.loads(line))

        with self.model_name_path.open("r", encoding="utf-8") as f:
            self.model_name = f.read().strip()

        # Handle mock model
        if self.model_name == "mock-embedding-model":
            self.embedder = None
        else:
            self.embedder = TextEmbedding(self.model_name)
        self.embeddings_norm = self._normalize(self.embeddings)

    @staticmethod
    def _normalize(vectors: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12
        return vectors / norm

    def _embed_query(self, text: str) -> np.ndarray:
        if self.embedder is None:
            # Mock embedding for demonstration
            import hashlib
            hash_obj = hashlib.md5(text.encode('utf-8'))
            hash_bytes = hash_obj.digest()
            
            embedding = np.zeros(384, dtype=np.float32)
            for i in range(min(len(hash_bytes), 384)):
                embedding[i] = (hash_bytes[i] - 128) / 128.0
            
            np.random.seed(int.from_bytes(hash_bytes[:4], 'big'))
            if 384 > len(hash_bytes):
                embedding[len(hash_bytes):] = np.random.normal(0, 0.1, 384 - len(hash_bytes))
            
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            return embedding
        else:
            query_vec = list(self.embedder.embed([text]))[0]
            vec = np.asarray(query_vec, dtype=np.float32)
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


class Retriever:
    def __init__(self):
        self.data_file = "data/sample_listings.jsonl"
        self.load_data()
    
    def load_data(self):
        """加载示例数据"""
        self.listings = []
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.listings.append(json.loads(line))
    
    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """简单的关键词搜索"""
        results = []
        query_lower = query.lower()
        
        for listing in self.listings:
            score = 0
            title = listing.get('title', '').lower()
            description = listing.get('description', '').lower()
            category = listing.get('category', '').lower()
            tags = [tag.lower() for tag in listing.get('tags', [])]
            
            # 计算相关性分数
            if query_lower in title:
                score += 10
            if query_lower in description:
                score += 5
            if query_lower in category:
                score += 3
            for tag in tags:
                if query_lower in tag:
                    score += 2
            
            if score > 0:
                results.append({
                    "score": score,
                    "listing": listing
                })
        
        # 按分数排序并返回前top_k个结果
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

class LLM:
    def __init__(self):
        pass
    
    def generate_summary(self, query: str, results: List[Dict[str, Any]]) -> str:
        """生成搜索结果摘要"""
        if not results:
            return "未找到相关结果。"
        
        # 简单的摘要生成
        total_results = len(results)
        categories = {}
        regions = {}
        
        for result in results:
            listing = result["listing"]
            category = listing.get('category', '未知')
            region = listing.get('region', '未知')
            
            categories[category] = categories.get(category, 0) + 1
            regions[region] = regions.get(region, 0) + 1
        
        # 生成摘要
        summary_parts = [f"找到 {total_results} 条相关结果。"]
        
        if categories:
            top_category = max(categories.items(), key=lambda x: x[1])
            summary_parts.append(f"主要类别：{top_category[0]} ({top_category[1]}条)")
        
        if regions:
            top_region = max(regions.items(), key=lambda x: x[1])
            summary_parts.append(f"主要地区：{top_region[0]} ({top_region[1]}条)")
        
        return " ".join(summary_parts)



