"""
Content Understanding Module: Analyzes Reels for Topic, Context, Intent, Broader Domain, and Vector Embeddings.
"""

from typing import Dict, Any, Optional
import numpy as np
from utils.embeddings import EmbeddingEngine
from utils.helpers import sanitize_text_input

# Rule-based contextual knowledge graph for robust zero-dependency offline inference
DOMAIN_TAXONOMY = {
    "Java": {
        "broader_domain": "Software Engineering",
        "default_intent": "Entertainment / Educational",
        "context_clues": ["debugging", "nullpointerexception", "jvm", "backend", "code"]
    },
    "Career": {
        "broader_domain": "Software Engineering",
        "default_intent": "Lifestyle / Career Guidance",
        "context_clues": ["standup", "faang", "lifestyle", "pull request", "salary", "interview"]
    },
    "DSA": {
        "broader_domain": "Computer Science & Engineering",
        "default_intent": "Technical Skill / Interview Prep",
        "context_clues": ["leetcode", "binary search", "algorithms", "graph", "interviewer"]
    },
    "Hardware": {
        "broader_domain": "Developer Tooling & Infrastructure",
        "default_intent": "Productivity / Hardware Review",
        "context_clues": ["macbook", "thinkpad", "docker", "compilation", "benchmark", "workstation"]
    },
    "AI": {
        "broader_domain": "Artificial Intelligence & Tooling",
        "default_intent": "Technology News / Innovation",
        "context_clues": ["llm", "apis", "openai", "agentic", "models", "gpt"]
    },
    "Cloud": {
        "broader_domain": "Systems & Reliability Engineering",
        "default_intent": "System Design / Educational",
        "context_clues": ["outage", "distributed", "kubernetes", "bgp", "microservices"]
    },
    "Gaming": {
        "broader_domain": "Entertainment & Aesthetics",
        "default_intent": "Entertainment / Lifestyle",
        "context_clues": ["setup", "oled", "fps", "gaming", "desk"]
    },
    "Cybersecurity": {
        "broader_domain": "Systems Security",
        "default_intent": "Security / Best Practices",
        "context_clues": ["zero trust", "vulnerability", "auth", "encryption", "iam"]
    },
    "HLD": {
        "broader_domain": "Software Architecture",
        "default_intent": "Architecture / System Design",
        "context_clues": ["microservices", "kafka", "scalability", "load balancer", "high level design"]
    }
}

class ContentUnderstanding:
    def __init__(self, embedding_engine: Optional[EmbeddingEngine] = None):
        self.embedder = embedding_engine or EmbeddingEngine()

    def analyze_reel(self, reel: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts semantic meaning, topic, context, intent, broader domain, and embedding from a Reel.
        """
        title = sanitize_text_input(reel.get("title", ""))
        caption = sanitize_text_input(reel.get("caption", ""))
        transcript = sanitize_text_input(reel.get("transcript", ""))
        category = reel.get("category", "Other")

        full_text = f"{title}. {caption}. {transcript}".strip()

        # Generate semantic vector embedding
        embedding = self.embedder.get_embedding(full_text)

        # Context & Intent Extraction
        taxonomy = DOMAIN_TAXONOMY.get(category, {
            "broader_domain": category if category != "Other" else "General Technology",
            "default_intent": "Informational",
            "context_clues": []
        })

        broader_domain = taxonomy["broader_domain"]
        intent = reel.get("content_type", taxonomy["default_intent"])
        
        # Context extraction from description and clues
        topic = reel.get("topic", category)
        context = reel.get("description", f"Content focusing on {topic} within {broader_domain}.")

        return {
            "reel_id": reel.get("reel_id", ""),
            "topic": topic,
            "category": category,
            "context": context,
            "intent": intent,
            "broader_domain": broader_domain,
            "quality_score": float(reel.get("quality_score", 0.8)),
            "difficulty": reel.get("difficulty", "Intermediate"),
            "embedding": embedding,
            "full_text": full_text
        }
