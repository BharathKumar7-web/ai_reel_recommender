"""
Unit tests for Content Understanding and Embedding Engine.
"""

import pytest
import numpy as np
from utils.embeddings import EmbeddingEngine
from modules.content_understanding import ContentUnderstanding

def test_embedding_engine_fallback():
    engine = EmbeddingEngine()
    emb = engine.get_embedding("Java developer debugging late at night")
    assert isinstance(emb, np.ndarray)
    assert len(emb) == 384
    norm = np.linalg.norm(emb)
    assert 0.95 <= norm <= 1.05

def test_cosine_similarity():
    engine = EmbeddingEngine()
    v1 = engine.get_embedding("Software engineering system design")
    v2 = engine.get_embedding("Distributed systems architecture")
    v3 = engine.get_embedding("Cosmetics and makeup tutorials")
    
    sim_tech = engine.compute_similarity(v1, v2)
    sim_unrelated = engine.compute_similarity(v1, v3)
    
    assert sim_tech > sim_unrelated

def test_content_understanding_analysis():
    cu = ContentUnderstanding()
    sample_reel = {
        "reel_id": "REEL_TEST",
        "title": "Java Developer Debugging at 2 AM",
        "caption": "NullPointerException strikes again #java #coding",
        "transcript": "Why is user null?",
        "category": "Java",
        "topic": "Java Debugging",
        "quality_score": 0.85
    }
    
    result = cu.analyze_reel(sample_reel)
    assert result["topic"] == "Java Debugging"
    assert result["category"] == "Java"
    assert result["broader_domain"] == "Software Engineering"
    assert "embedding" in result
    assert isinstance(result["embedding"], np.ndarray)
