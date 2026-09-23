import numpy as np
from typing import Dict, Any, List, Optional
from sklearn.ensemble import IsolationForest
from backend.app.core.config import settings
from backend.app.models.metric import TelemetrySnapshot

class MLAnomalyResult:
    def __init__(self, is_anomaly: bool, anomaly_score: float, affected_features: List[str], feature_values: Dict[str, float]):
        self.is_anomaly = is_anomaly
        self.anomaly_score = anomaly_score
        self.affected_features = affected_features
        self.feature_values = feature_values

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_anomaly": self.is_anomaly,
            "anomaly_score": round(self.anomaly_score, 4),
            "affected_features": self.affected_features,
            "feature_values": self.feature_values
        }

class MLAnomalyDetector:
    def __init__(self, contamination: Optional[float] = None):
        self.contamination = contamination or settings.ISOLATION_FOREST_CONTAMINATION
        self.feature_names = ["cpu_percent", "memory_percent", "disk_percent", "request_rate", "latency_ms", "error_rate"]

    def _extract_features(self, snapshot: TelemetrySnapshot) -> List[float]:
        return [
            float(snapshot.cpu_percent),
            float(snapshot.memory_percent),
            float(snapshot.disk_percent),
            float(snapshot.request_rate),
            float(snapshot.latency_ms),
            float(snapshot.error_rate)
        ]

    def _generate_synthetic_baseline(self, n_samples: int = 50) -> np.ndarray:
        """Generates realistic normal operating cluster when historical points are still few"""
        np.random.seed(42)
        cpu = np.random.normal(20.0, 5.0, n_samples)
        mem = np.random.normal(35.0, 6.0, n_samples)
        disk = np.random.normal(40.0, 2.0, n_samples)
        req_rate = np.random.normal(50.0, 10.0, n_samples)
        latency = np.random.normal(25.0, 8.0, n_samples)
        error_rate = np.random.exponential(0.005, n_samples)
        return np.column_stack([cpu, mem, disk, req_rate, latency, error_rate])

    def detect(self, current: TelemetrySnapshot, history: Optional[List[TelemetrySnapshot]] = None) -> MLAnomalyResult:
        current_vec = self._extract_features(current)
        
        # Build training set from history or synthetic baseline
        if history and len(history) >= 15:
            train_data = np.array([self._extract_features(h) for h in history])
        else:
            train_data = self._generate_synthetic_baseline(60)

        # Fit Isolation Forest
        model = IsolationForest(
            contamination=self.contamination,
            random_state=42,
            n_estimators=100
        )
        model.fit(train_data)

        # Predict current point: -1 for outlier, 1 for inlier
        pred = model.predict([current_vec])[0]
        # decision_function: lower means more abnormal
        score = float(model.decision_function([current_vec])[0])
        is_anomaly = bool(pred == -1)

        # Identify which features drove the anomaly
        affected_features = []
        feature_dict = dict(zip(self.feature_names, current_vec))
        means = np.mean(train_data, axis=0)
        stds = np.std(train_data, axis=0) + 1e-4

        for i, feat_name in enumerate(self.feature_names):
            z_score = abs(current_vec[i] - means[i]) / stds[i]
            if z_score > 2.0:
                affected_features.append(feat_name)

        return MLAnomalyResult(
            is_anomaly=is_anomaly,
            anomaly_score=score,
            affected_features=affected_features,
            feature_values=feature_dict
        )

ml_anomaly_detector = MLAnomalyDetector()
