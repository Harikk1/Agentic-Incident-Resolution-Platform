import numpy as np
from typing import List, Dict, Any, Optional
from backend.app.database.repositories import kb_repo

class IncidentRAG:
    """Historical Incident Knowledge Base with Vector Similarity Search"""

    @staticmethod
    def _compute_simple_embedding(text: str) -> np.ndarray:
        """Deterministic keyword-frequency semantic vector for local zero-dependency vector search"""
        keywords = [
            "traffic", "spike", "cpu", "memory", "leak", "database", "bottleneck",
            "timeout", "latency", "error", "deployment", "bad", "nullpointer",
            "restart", "scale", "rollback", "oom", "connection", "pool"
        ]
        text_lower = text.lower()
        vec = [text_lower.count(k) for k in keywords]
        norm = np.linalg.norm(vec)
        if norm > 0:
            return np.array(vec) / norm
        return np.zeros(len(keywords))

    @staticmethod
    def find_similar(service: str, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        all_docs = kb_repo.list_all()
        if not all_docs:
            return []

        query_vec = IncidentRAG._compute_simple_embedding(f"{service} {query}")
        results = []

        for doc in all_docs:
            doc_text = f"{doc.get('service', '')} {doc.get('title', '')} {' '.join(doc.get('symptoms', []))}"
            doc_vec = IncidentRAG._compute_simple_embedding(doc_text)
            similarity = float(np.dot(query_vec, doc_vec))
            
            # Boost if service matches
            if doc.get("service") == service:
                similarity += 0.25

            results.append({
                "doc_id": doc.get("doc_id"),
                "title": doc.get("title"),
                "service": doc.get("service"),
                "root_cause": doc.get("root_cause"),
                "resolution": doc.get("resolution"),
                "result": doc.get("result"),
                "similarity": round(min(similarity, 0.99), 2)
            })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

rag_engine = IncidentRAG()
