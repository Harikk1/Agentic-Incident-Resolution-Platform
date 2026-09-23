import time
import abc
from typing import Dict, Any, List, Optional
from backend.app.database.connection import get_mongo_db, is_mongo_available
from backend.app.core.logging import logger

class BaseRepository(abc.ABC):
    @abc.abstractmethod
    def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abc.abstractmethod
    def list_all(self, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        pass

    @abc.abstractmethod
    def save(self, item: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def update(self, item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass

class InMemoryRepository(BaseRepository):
    def __init__(self, key_field: str = "id"):
        self.key_field = key_field
        self._items: Dict[str, Dict[str, Any]] = {}

    def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        return self._items.get(item_id)

    def list_all(self, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not filter_dict:
            return list(self._items.values())
        results = []
        for item in self._items.values():
            match = True
            for k, v in filter_dict.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                results.append(item)
        return results

    def save(self, item: Dict[str, Any]) -> Dict[str, Any]:
        item_id = item.get(self.key_field)
        if not item_id:
            raise ValueError(f"Item must contain key field '{self.key_field}'")
        self._items[item_id] = item
        return item

    def update(self, item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        item = self._items.get(item_id)
        if not item:
            return None
        item.update(updates)
        item["updated_at"] = time.time()
        self._items[item_id] = item
        return item

class MongoRepository(BaseRepository):
    def __init__(self, collection_name: str, key_field: str = "id"):
        self.collection_name = collection_name
        self.key_field = key_field

    @property
    def collection(self):
        db = get_mongo_db()
        if db is None:
            raise RuntimeError("MongoDB is not available")
        return db[self.collection_name]

    def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        doc = self.collection.find_one({self.key_field: item_id}, {"_id": 0})
        return doc

    def list_all(self, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query = filter_dict or {}
        cursor = self.collection.find(query, {"_id": 0})
        return list(cursor)

    def save(self, item: Dict[str, Any]) -> Dict[str, Any]:
        item_id = item.get(self.key_field)
        self.collection.replace_one({self.key_field: item_id}, item, upsert=True)
        return item

    def update(self, item_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updates["updated_at"] = time.time()
        self.collection.update_one({self.key_field: item_id}, {"$set": updates})
        return self.get_by_id(item_id)

class RepositoryFactory:
    """Provides repository instances with automatic MongoDB detection or in-memory fallback"""
    def __init__(self):
        self._in_memory_stores: Dict[str, InMemoryRepository] = {}

    def get_repository(self, collection_name: str, key_field: str = "id") -> BaseRepository:
        if is_mongo_available():
            try:
                return MongoRepository(collection_name, key_field)
            except Exception:
                pass
        
        # Fallback to in-memory store
        if collection_name not in self._in_memory_stores:
            self._in_memory_stores[collection_name] = InMemoryRepository(key_field)
        return self._in_memory_stores[collection_name]

repo_factory = RepositoryFactory()

# Pre-seed initial services and historical incidents
services_repo = repo_factory.get_repository("services", key_field="name")
incidents_repo = repo_factory.get_repository("incidents", key_field="incident_id")
remediation_repo = repo_factory.get_repository("remediation_actions", key_field="action_id")
audit_repo = repo_factory.get_repository("audit_logs", key_field="action_id")
kb_repo = repo_factory.get_repository("knowledge_base", key_field="doc_id")
session_repo = repo_factory.get_repository("agent_sessions", key_field="session_id")

# Seed initial services
services_repo.save({
    "service_id": "svc-user-01",
    "name": "user-service",
    "namespace": "smartops",
    "status": "HEALTHY",
    "version": "v1.0.0",
    "url": "http://127.0.0.1:8001",
    "desired_replicas": 2,
    "ready_replicas": 2,
    "available_replicas": 2,
    "dependencies": [],
    "metadata": {"tier": "backend", "criticality": "HIGH"}
})

services_repo.save({
    "service_id": "svc-order-01",
    "name": "order-service",
    "namespace": "smartops",
    "status": "HEALTHY",
    "version": "v1.0.0",
    "url": "http://127.0.0.1:8002",
    "desired_replicas": 2,
    "ready_replicas": 2,
    "available_replicas": 2,
    "dependencies": [
        {"target_service": "user-service", "dependency_type": "HTTP", "healthy": True, "latency_ms": 12.0}
    ],
    "metadata": {"tier": "backend", "criticality": "HIGH"}
})

services_repo.save({
    "service_id": "svc-payment-01",
    "name": "payment-service",
    "namespace": "smartops",
    "status": "HEALTHY",
    "version": "v1.0.0",
    "url": "http://127.0.0.1:8003",
    "desired_replicas": 2,
    "ready_replicas": 2,
    "available_replicas": 2,
    "dependencies": [
        {"target_service": "order-service", "dependency_type": "HTTP", "healthy": True, "latency_ms": 15.0},
        {"target_service": "mongodb", "dependency_type": "DATABASE", "healthy": True, "latency_ms": 8.0}
    ],
    "metadata": {"tier": "backend", "criticality": "CRITICAL"}
})

# Seed Historical Incidents for RAG Knowledge Base
kb_repo.save({
    "doc_id": "KB-101",
    "title": "Payment Gateway Traffic Spike",
    "service": "payment-service",
    "symptoms": ["Request rate surge above 800 req/s", "CPU reached 92%", "Latency reached 185ms"],
    "root_cause": "TRAFFIC_SPIKE",
    "resolution": "Scaled payment-service deployment from 2 to 5 replicas.",
    "result": "Latency recovered to 45ms and CPU dropped to 48%.",
    "embedding": [0.85, 0.92, 0.31, 0.12, 0.77],
    "created_at": time.time() - 86400 * 7
})

kb_repo.save({
    "doc_id": "KB-102",
    "title": "Database Connection Pool Exhaustion",
    "service": "payment-service",
    "symptoms": ["DB latency exceeded 350ms", "DB timeout errors in logs", "API latency 240ms with normal CPU"],
    "root_cause": "DATABASE_BOTTLENECK",
    "resolution": "Scaled connection pool size and cleared long-running locks.",
    "result": "DB latency returned to 12ms.",
    "embedding": [0.15, 0.45, 0.88, 0.91, 0.23],
    "created_at": time.time() - 86400 * 5
})

kb_repo.save({
    "doc_id": "KB-103",
    "title": "Payment Service Memory Leak Post-Release",
    "service": "payment-service",
    "symptoms": ["Continuous memory growth to 94%", "Container restarts increasing", "OOMKilled events"],
    "root_cause": "MEMORY_LEAK",
    "resolution": "Restarted affected unhealthy pods and patched unclosed buffer leaks.",
    "result": "Memory stabilized at 38%.",
    "embedding": [0.35, 0.89, 0.22, 0.44, 0.81],
    "created_at": time.time() - 86400 * 3
})

kb_repo.save({
    "doc_id": "KB-104",
    "title": "Regression Errors Following Bad Deployment",
    "service": "payment-service",
    "symptoms": ["Error rate jumped to 8.5% immediately after release", "NullPointerExceptions in logs", "Version v2.1.0-bad"],
    "root_cause": "BAD_DEPLOYMENT",
    "resolution": "Rolled back deployment to previous stable revision v1.0.0.",
    "result": "Error rate dropped to 0.1%.",
    "embedding": [0.12, 0.25, 0.95, 0.84, 0.65],
    "created_at": time.time() - 86400 * 1
})
