import os
from typing import Dict, Any, List, Optional
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.kubernetes.driver import KubernetesDriver
from backend.app.kubernetes.mock_driver import MockKubernetesDriver

class RealKubernetesDriver(KubernetesDriver):
    def __init__(self):
        try:
            from kubernetes import client, config
            try:
                config.load_incluster_config()
            except Exception:
                config.load_kube_config()
            self.apps_v1 = client.AppsV1Api()
            self.core_v1 = client.CoreV1Api()
            logger.info("Real Kubernetes client initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to connect to real Kubernetes cluster: {e}. Falling back to Mock Driver.")
            raise e

    def scale_deployment(self, name: str, replicas: int, namespace: str = "smartops") -> Dict[str, Any]:
        body = {"spec": {"replicas": replicas}}
        resp = self.apps_v1.patch_namespaced_deployment_scale(name, namespace, body)
        return {
            "status": "SUCCESS",
            "deployment": name,
            "desired_replicas": replicas,
            "ready_replicas": resp.status.replicas,
            "namespace": namespace
        }

    def restart_deployment(self, name: str, namespace: str = "smartops") -> Dict[str, Any]:
        import datetime
        now = datetime.datetime.utcnow().isoformat() + "Z"
        body = {
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "kubectl.kubernetes.io/restartedAt": now
                        }
                    }
                }
            }
        }
        self.apps_v1.patch_namespaced_deployment(name, namespace, body)
        return {"status": "SUCCESS", "deployment": name, "action": "ROLLOUT_RESTART"}

    def restart_pod(self, pod_name: str, namespace: str = "smartops") -> Dict[str, Any]:
        self.core_v1.delete_namespaced_pod(pod_name, namespace)
        return {"status": "SUCCESS", "pod_name": pod_name, "action": "POD_DELETED"}

    def rollback_deployment(self, name: str, namespace: str = "smartops", revision: int = 0) -> Dict[str, Any]:
        # Typically handled by deployment rollback API or annotation patch
        return self.restart_deployment(name, namespace)

    def update_resources(self, name: str, cpu_request: str, memory_request: str, namespace: str = "smartops") -> Dict[str, Any]:
        body = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": name,
                            "resources": {
                                "requests": {"cpu": cpu_request, "memory": memory_request},
                                "limits": {"cpu": cpu_request, "memory": memory_request}
                            }
                        }]
                    }
                }
            }
        }
        self.apps_v1.patch_namespaced_deployment(name, namespace, body)
        return {"status": "SUCCESS", "deployment": name, "resources": {"cpu": cpu_request, "memory": memory_request}}

    def get_deployment_status(self, name: str, namespace: str = "smartops") -> Dict[str, Any]:
        dep = self.apps_v1.read_namespaced_deployment(name, namespace)
        return {
            "name": name,
            "desired_replicas": dep.spec.replicas,
            "ready_replicas": dep.status.ready_replicas or 0,
            "namespace": namespace
        }

    def get_pods(self, service_name: Optional[str] = None, namespace: str = "smartops") -> List[Dict[str, Any]]:
        label_selector = f"app={service_name}" if service_name else None
        pods = self.core_v1.list_namespaced_pod(namespace, label_selector=label_selector)
        return [{
            "pod_name": p.metadata.name,
            "status": p.status.phase,
            "ready": any(c.ready for c in (p.status.container_statuses or [])),
            "restart_count": sum(c.restart_count for c in (p.status.container_statuses or []))
        } for p in pods.items]

def get_kubernetes_driver() -> KubernetesDriver:
    if settings.MOCK_KUBERNETES:
        return MockKubernetesDriver()
    try:
        return RealKubernetesDriver()
    except Exception:
        logger.info("Falling back to MockKubernetesDriver")
        return MockKubernetesDriver()

k8s_driver = get_kubernetes_driver()
