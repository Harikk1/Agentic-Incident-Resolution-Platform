import abc
from typing import Dict, Any, List, Optional

class KubernetesDriver(abc.ABC):
    @abc.abstractmethod
    def scale_deployment(self, name: str, replicas: int, namespace: str = "smartops") -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def restart_deployment(self, name: str, namespace: str = "smartops") -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def restart_pod(self, pod_name: str, namespace: str = "smartops") -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def rollback_deployment(self, name: str, namespace: str = "smartops", revision: int = 0) -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def update_resources(self, name: str, cpu_request: str, memory_request: str, namespace: str = "smartops") -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def get_deployment_status(self, name: str, namespace: str = "smartops") -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def get_pods(self, service_name: Optional[str] = None, namespace: str = "smartops") -> List[Dict[str, Any]]:
        pass
