"""
Embedding Engine with SentenceTransformers and deterministic TF-IDF / Subword Fallback.
Guarantees 100% offline functionality and graceful degradation.
"""

import numpy as np
import re
from typing import List, Union

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Domain semantic anchors to ensure rich representations in fallback mode
DOMAIN_KEYWORDS = {
    "Software Engineering": ["developer", "software", "engineer", "code", "architecture", "microservices", "testing", "refactoring", "workflow", "production", "debugging"],
    "Java": ["java", "jvm", "spring", "nullpointerexception", "bytecode", "garbage collection", "jdk", "gradle"],
    "DSA": ["dsa", "algorithms", "data structures", "leetcode", "binary search", "graph", "tree", "dijkstra", "dynamic programming", "time complexity", "o(1)", "o(n)"],
    "AI": ["ai", "machine learning", "llm", "neural", "openai", "agentic", "transformer", "prompts", "inference", "gpt", "model"],
    "Cloud": ["cloud", "devops", "kubernetes", "docker", "aws", "infrastructure", "outage", "bgp", "networking", "distributed"],
    "Cybersecurity": ["security", "cybersecurity", "vulnerability", "auth", "encryption", "mtls", "zero trust", "iam", "exploit"],
    "Hardware": ["hardware", "macbook", "thinkpad", "cpu", "cache", "benchmarks", "ram", "apple silicon", "workstation"],
    "Career": ["career", "faang", "interview", "salary", "promotion", "staff engineer", "standup", "pull request", "resume"],
    "Gaming": ["gaming", "fps", "oled", "desk setup", "rgb", "pc setup", "battlestation"]
}

class EmbeddingEngine:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EmbeddingEngine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if getattr(self, "_initialized", False):
            return
        self.model_name = model_name
        self.model = None
        self.mode = "fallback"
        self.vector_dim = 384

        if HAS_SENTENCE_TRANSFORMERS:
            try:
                self.model = SentenceTransformer(model_name)
                self.mode = "sentence_transformers"
            except Exception:
                self.model = None
                self.mode = "fallback"

        # Initialize TF-IDF Fallback Corpus
        corpus = []
        for domain, words in DOMAIN_KEYWORDS.items():
            corpus.append(f"{domain} " + " ".join(words))
        self.tfidf = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        self.tfidf.fit(corpus)
        self._initialized = True

    def get_embedding(self, text: Union[str, List[str]]) -> np.ndarray:
        """Returns normalized float32 vector embedding for text or list of texts."""
        if not text:
            return np.zeros(self.vector_dim, dtype=np.float32)

        if self.mode == "sentence_transformers" and self.model is not None:
            try:
                emb = self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
                return emb.astype(np.float32)
            except Exception:
                pass  # Fall back on error

        # Deterministic Fallback Mode
        is_single = isinstance(text, str)
        texts = [text] if is_single else text
        results = []

        for t in texts:
            clean = re.sub(r"[^a-zA-Z0-9\s]", " ", str(t).lower())
            # 1. Base TF-IDF features
            tfidf_vec = self.tfidf.transform([clean]).toarray()[0]
            
            # 2. Dense semantic anchor expansion
            anchor_scores = []
            for domain, words in DOMAIN_KEYWORDS.items():
                match_count = sum(1 for w in words if w in clean)
                anchor_scores.append(match_count * 2.0 if domain.lower() in clean else match_count * 1.0)
            
            combined = np.concatenate([tfidf_vec, np.array(anchor_scores, dtype=np.float32)])
            
            # Pad or truncate to fixed vector_dim
            if len(combined) < self.vector_dim:
                pad = np.zeros(self.vector_dim - len(combined), dtype=np.float32)
                # Seed pseudo-random hash features from words for diversity
                hash_val = sum(ord(c) for c in clean) % 100 / 1000.0
                pad.fill(hash_val)
                vec = np.concatenate([combined, pad])
            else:
                vec = combined[:self.vector_dim]

            # L2 Normalization
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            results.append(vec.astype(np.float32))

        return results[0] if is_single else np.array(results, dtype=np.float32)

    def compute_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculates cosine similarity between two vectors bounded in [0.0, 1.0]."""
        v1 = np.asarray(vec1, dtype=np.float32)
        v2 = np.asarray(vec2, dtype=np.float32)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        sim = float(np.dot(v1, v2) / (norm1 * norm2))
        return float(np.clip(sim, 0.0, 1.0))
