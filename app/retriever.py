from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List
import hashlib
import time
from functools import lru_cache

# import numpy as np  # Removed to fix deployment issues
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from fastembed import TextEmbedding
    FASTEMBED_AVAILABLE = True
except ImportError:
    FASTEMBED_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


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

        # Load embeddings with numpy fallback
        if NUMPY_AVAILABLE:
            self.embeddings: np.ndarray = np.load(self.embeddings_path)
        else:
            # Fallback: load as list of lists
            import pickle
            with open(self.embeddings_path, 'rb') as f:
                self.embeddings = pickle.load(f)
        
        self.metadata: List[Dict[str, Any]] = []
        with self.metadata_path.open("r", encoding="utf-8") as f:
            for line in f:
                self.metadata.append(json.loads(line))

        with self.model_name_path.open("r", encoding="utf-8") as f:
            self.model_name = f.read().strip()

        # Handle mock model
        if self.model_name == "mock-embedding-model":
            self.embedder = None
            self.embedder_type = "mock"
        elif "sentence-transformers" in self.model_name and SENTENCE_TRANSFORMERS_AVAILABLE:
            self.embedder = SentenceTransformer(self.model_name)
            self.embedder_type = "sentence-transformers"
        elif FASTEMBED_AVAILABLE:
            self.embedder = TextEmbedding(self.model_name)
            self.embedder_type = "fastembed"
        else:
            self.embedder = None
            self.embedder_type = "mock"
        
        self.embeddings_norm = self._normalize(self.embeddings)

    @staticmethod
    def _normalize(vectors):
        """Normalize vectors with numpy fallback"""
        if NUMPY_AVAILABLE:
            norm = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12
            return vectors / norm
        else:
            # Fallback for non-numpy case
            normalized = []
            for vec in vectors:
                import math
                norm = math.sqrt(sum(x * x for x in vec)) + 1e-12
                normalized.append([x / norm for x in vec])
            return normalized

    def _embed_query(self, text: str):
        """Embed query text"""
        if self.embedder_type == "mock":
            # Mock embedding for demonstration
            hash_obj = hashlib.md5(text.encode('utf-8'))
            hash_bytes = hash_obj.digest()
            
            if NUMPY_AVAILABLE:
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
                # Fallback without numpy
                embedding = [0.0] * 384
                for i in range(min(len(hash_bytes), 384)):
                    embedding[i] = (hash_bytes[i] - 128) / 128.0
                return embedding
        elif self.embedder_type == "sentence-transformers":
            vec = self.embedder.encode([text])[0]
            if NUMPY_AVAILABLE:
                vec = np.asarray(vec, dtype=np.float32)
                vec = vec / (np.linalg.norm(vec) + 1e-12)
            return vec
        else:  # fastembed
            query_vec = list(self.embedder.embed([text]))[0]
            if NUMPY_AVAILABLE:
                vec = np.asarray(query_vec, dtype=np.float32)
                vec = vec / (np.linalg.norm(vec) + 1e-12)
            return vec

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search using vector similarity"""
        if top_k <= 0:
            return []
        vec = self._embed_query(query)
        
        if NUMPY_AVAILABLE:
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
        else:
            # Fallback without numpy
            scores = []
            for i, emb in enumerate(self.embeddings_norm):
                score = sum(x * y for x, y in zip(emb, vec))
                scores.append((i, score))
            
            scores.sort(key=lambda x: x[1], reverse=True)
            results = []
            for i, score in scores[:top_k]:
                item = self.metadata[i].copy()
                results.append({
                    "score": float(score),
                    "listing": item,
                })
            return results


class HybridRetriever:
    """混合检索器 - 结合向量检索、关键词检索和BM25算法"""
    
    def __init__(self, use_vector: bool = True, use_keyword: bool = True):
        self.data_file = "data/sample_listings.jsonl"
        self.use_vector = use_vector
        self.use_keyword = use_keyword
        self.load_data()
        
        # 尝试加载向量存储
        self.vector_store = None
        if self.use_vector:
            try:
                self.vector_store = VectorStore(
                    "artifacts/embeddings.npy",
                    "artifacts/metadata.jsonl",
                    "artifacts/model_name.txt"
                )
            except Exception as e:
                print(f"Vector store not available: {e}")
                self.use_vector = False
        
        # 构建反向索引用于关键词检索
        self._build_inverted_index()
        
        # 查询缓存
        self.cache = {}
        self.cache_max_size = 100
    
    def load_data(self):
        """加载示例数据"""
        self.listings = []
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.listings.append(json.loads(line))
    
    def _build_inverted_index(self):
        """构建反向索引用于快速关键词检索"""
        self.inverted_index = {}
        for idx, listing in enumerate(self.listings):
            # 提取所有文本字段
            text_fields = [
                listing.get('title', ''),
                listing.get('description', ''),
                listing.get('category', ''),
                ' '.join(listing.get('tags', [])),
                listing.get('region', ''),
                listing.get('seller', '')
            ]
            
            # 分词并建立索引
            for field in text_fields:
                words = self._tokenize(field.lower())
                for word in words:
                    if word not in self.inverted_index:
                        self.inverted_index[word] = []
                    if idx not in self.inverted_index[word]:
                        self.inverted_index[word].append(idx)
    
    def _tokenize(self, text: str) -> List[str]:
        """简单的分词"""
        # 提取中文和英文词汇
        import re
        # 匹配中文字符和英文单词
        words = re.findall(r'[\u4e00-\u9fa5]+|[a-zA-Z]+', text)
        return words
    
    def _keyword_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """关键词检索"""
        query_lower = query.lower()
        query_words = self._tokenize(query_lower)
        
        # BM25 风格的评分
        doc_scores = {}
        query_word_count = {}
        
        for word in query_words:
            query_word_count[word] = query_word_count.get(word, 0) + 1
            if word in self.inverted_index:
                doc_ids = self.inverted_index[word]
                for doc_id in doc_ids:
                    if doc_id not in doc_scores:
                        doc_scores[doc_id] = 0
                    doc_scores[doc_id] += query_word_count[word]
        
        # 额外检查完全匹配
        for listing in self.listings:
            score = 0
            title = listing.get('title', '').lower()
            description = listing.get('description', '').lower()
            category = listing.get('category', '').lower()
            tags = [tag.lower() for tag in listing.get('tags', [])]
            
            # 完全匹配得分更高
            if query_lower in title:
                score += 10
            if query_lower in description:
                score += 5
            if query_lower in category:
                score += 3
            for tag in tags:
                if query_lower in tag:
                    score += 2
            
            listing_idx = self.listings.index(listing)
            if listing_idx in doc_scores:
                doc_scores[listing_idx] += score
            elif score > 0:
                doc_scores[listing_idx] = score
        
        # 排序并返回结果
        results = []
        for doc_id, score in sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]:
            results.append({
                "score": score,
                "listing": self.listings[doc_id]
            })
        
        return results
    
    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """混合检索"""
        # 检查缓存
        cache_key = f"{query}_{top_k}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        results = []
        
        # 向量检索
        if self.use_vector and self.vector_store:
            try:
                vector_results = self.vector_store.search(query, top_k=top_k * 2)
                results.extend(vector_results)
            except Exception as e:
                print(f"Vector search failed: {e}")
        
        # 关键词检索
        if self.use_keyword:
            keyword_results = self._keyword_search(query, top_k=top_k * 2)
            results.extend(keyword_results)
        
        # 合并和去重结果
        seen_ids = set()
        merged_results = []
        
        for result in results:
            listing = result["listing"]
            listing_id = listing.get('id', str(hash(str(listing))))
            
            if listing_id not in seen_ids:
                seen_ids.add(listing_id)
                merged_results.append(result)
        
        # 重新排序（按分数）
        merged_results.sort(key=lambda x: x["score"], reverse=True)
        
        # 返回前 top_k 个结果
        final_results = merged_results[:top_k]
        
        # 更新缓存
        if len(self.cache) >= self.cache_max_size:
            # 删除最旧的缓存项
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[cache_key] = final_results
        
        return final_results

# 保持向后兼容
Retriever = HybridRetriever



