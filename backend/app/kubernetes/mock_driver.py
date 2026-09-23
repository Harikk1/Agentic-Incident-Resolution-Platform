import time
import copy
from typing import Dict, Any, List, Optional
from backend.app.kubernetes.driver import KubernetesDriver
from backend.app.core.logging import logger

class MockKubernetesDriver(KubernetesDriver):
    def __init__(self):
        self._deployments: Dict[str, Dict[str, Any]] = {
            "user-service": {
                "name": "user-service",
                "namespace": "smartops",
                "desired_replicas": 2,
                "ready_replicas": 2,
                "version": "v1.0.0",
                "revisions": ["v1.0.0"],
                "resources": {"cpu": "250m", "memory": "256Mi"},
                "updated_at": time.time()
            },
            "order-service": {
                "name": "order-service",
                "namespace": "smartops",
                "desired_replicas": 2,
                "ready_replicas": 2,
                "version": "v1.0.0",
                "revisions": ["v1.0.0"],
                "resources": {"cpu": "250m", "memory": "256Mi"},
                "updated_at": time.time()
            },
            "payment-service": {
                "name": "payment-service",
                "namespace": "smartops",
                "desired_replicas": 2,
                "ready_replicas": 2,
                "version": "v1.0.0",
                "revisions": ["v1.0.0"],
                "resources": {"cpu": "500m", "memory": "512Mi"},
                "updated_at": time.time()
            }
        }
        self._pods: Dict[str, List[Dict[str, Any]]] = {}
        self._reseed_pods()

    def _reseed_pods(self):
        for dep_name, dep in self._deployments.items():
            self._pods[dep_name] = []
            for i in range(dep["desired_replicas"]):
                self._pods[dep_name].append({
                    "pod_name": f"{dep_name}-{i+1}",
                    "service": dep_name,
                    "namespace": dep["namespace"],
                    "status": "Running",
                    "ready": True,
                    "restart_count": 0,
                    "cpu_usage": "45m",
                    "memory_usage": "115Mi",
                    "node": "kind-worker"
                })

    def scale_deployment(self, name: str, replicas: int, namespace: str = "smartops") -> Dict[str, Any]:
        dep = self._deployments.get(name)
        if not dep:
            raise ValueError(f"Deployment '{name}' not found in namespace '{namespace}'")

        old_replicas = dep["desired_replicas"]
        dep["desired_replicas"] = replicas
        dep["ready_replicas"] = replicas
        dep["updated_at"] = time.time()
        self._reseed_pods()

        logger.info(f"[MOCK K8S] Scaled deployment {name} from {old_replicas} to {replicas} replicas", extra={"mock": True})
        return {
            "status": "SUCCESS",
            "deployment": name,
            "previous_replicas": old_replicas,
            "desired_replicas": replicas,
            "ready_replicas": replicas,
            "namespace": namespace
        }

    def restart_deployment(self, name: str, namespace: str = "smartops") -> Dict[str, Any]:
        dep = self._deployments.get(name)
        if not dep:
            raise ValueError(f"Deployment '{name}' not found in namespace '{namespace}'")

        dep["updated_at"] = time.time()
        for p in self._pods.get(name, []):
            p["restart_count"] += 1
            p["status"] = "Running"
            p["ready"] = True

        logger.info(f"[MOCK K8S] Performed rollout restart on deployment {name}", extra={"mock": True})
        return {
            "status": "SUCCESS",
            "deployment": name,
            "action": "ROLLOUT_RESTART",
            "ready_replicas": dep["ready_replicas"],
            "namespace": namespace
        }

    def restart_pod(self, pod_name: str, namespace: str = "smartops") -> Dict[str, Any]:
        found = False
        target_service = None
        for svc, pods in self._pods.items():
            for p in pods:
                if p["pod_name"] == pod_name or pod_name in p["pod_name"]:
                    p["restart_count"] += 1
                    p["status"] = "Running"
                    p["ready"] = True
                    found = True
                    target_service = svc
                    break
        if not found:
            # If specified by service prefix or first pod
            for svc, pods in self._pods.items():
                if svc == pod_name and len(pods) > 0:
                    pods[0]["restart_count"] += 1
                    found = True
                    target_service = svc
                    pod_name = pods[0]["pod_name"]
                    break

        logger.info(f"[MOCK K8S] Restarted pod {pod_name}", extra={"mock": True})
        return {
            "status": "SUCCESS",
            "pod_name": pod_name,
            "service": target_service,
            "action": "POD_DELETED_RECREATED",
            "namespace": namespace
        }

    def rollback_deployment(self, name: str, namespace: str = "smartops", revision: int = 0) -> Dict[str, Any]:
        dep = self._deployments.get(name)
        if not dep:
            raise ValueError(f"Deployment '{name}' not found in namespace '{namespace}'")

        previous_version = dep["version"]
        stable_version = "v1.0.0"
        dep["version"] = stable_version
        dep["updated_at"] = time.time()
        self.restart_deployment(name, namespace)

        logger.info(f"[MOCK K8S] Rolled back deployment {name} from {previous_version} to {stable_version}", extra={"mock": True})
        return {
            "status": "SUCCESS",
            "deployment": name,
            "previous_version": previous_version,
            "current_version": stable_version,
            "namespace": namespace
        }

    def update_resources(self, name: str, cpu_request: str, memory_request: str, namespace: str = "smartops") -> Dict[str, Any]:
        dep = self._deployments.get(name)
        if not dep:
            raise ValueError(f"Deployment '{name}' not found in namespace '{namespace}'")

        dep["resources"] = {"cpu": cpu_request, "memory": memory_request}
        dep["updated_at"] = time.time()

        logger.info(f"[MOCK K8S] Patched resources for deployment {name}: cpu={cpu_request}, memory={memory_request}", extra={"mock": True})
        return {
            "status": "SUCCESS",
            "deployment": name,
            "resources": dep["resources"],
            "namespace": namespace
        }

    def get_deployment_status(self, name: str, namespace: str = "smartops") -> Dict[str, Any]:
        dep = self._deployments.get(name)
        if not dep:
            return {"error": f"Deployment {name} not found"}
        return copy.deepcopy(dep)

    def get_pods(self, service_name: Optional[str] = None, namespace: str = "smartops") -> List[Dict[str, Any]]:
        if service_name:
            return copy.deepcopy(self._pods.get(service_name, []))
        all_pods = []
        for pod_list in self._pods.values():
            all_pods.extend(copy.deepcopy(pod_list))
        return all_pods
