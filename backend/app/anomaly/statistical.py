import numpy as np
from typing import Dict, Any, List, Optional
from backend.app.core.config import settings
from backend.app.models.metric import TelemetrySnapshot

class StatisticalAnomaly:
    def __init__(self, metric: str, current_value: float, mean: float, std: float, z_score: float, is_anomaly: bool, method: str):
        self.metric = metric
        self.current_value = current_value
        self.mean = mean
        self.std = std
        self.z_score = z_score
        self.is_anomaly = is_anomaly
        self.method = method

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric": self.metric,
            "current_value": round(self.current_value, 2),
            "mean": round(self.mean, 2),
            "std": round(self.std, 2),
            "z_score": round(self.z_score, 2),
            "is_anomaly": self.is_anomaly,
            "method": self.method
        }

class StatisticalDetector:
    def __init__(self, z_threshold: Optional[float] = None, iqr_multiplier: Optional[float] = None):
        self.z_threshold = z_threshold or settings.Z_SCORE_THRESHOLD
        self.iqr_multiplier = iqr_multiplier or settings.IQR_MULTIPLIER

    def detect_zscore(self, current_value: float, history: List[float], metric_name: str) -> StatisticalAnomaly:
        if len(history) < 5:
            return StatisticalAnomaly(metric_name, current_value, current_value, 0.0, 0.0, False, "z_score")

        arr = np.array(history)
        mean = float(np.mean(arr))
        std = float(np.std(arr))

        if std < 1e-4:
            # Low variance: only anomalous if significantly different from mean
            z = 0.0
            is_anomaly = abs(current_value - mean) > 10.0
        else:
            z = (current_value - mean) / std
            is_anomaly = abs(z) >= self.z_threshold

        return StatisticalAnomaly(metric_name, current_value, mean, std, z, is_anomaly, "z_score")

    def detect_iqr(self, current_value: float, history: List[float], metric_name: str) -> Dict[str, Any]:
        if len(history) < 8:
            return {"metric": metric_name, "is_anomaly": False, "method": "iqr"}

        arr = np.array(history)
        q25, q75 = np.percentile(arr, 25), np.percentile(arr, 75)
        iqr = q75 - q25
        lower_bound = q25 - (self.iqr_multiplier * iqr)
        upper_bound = q75 + (self.iqr_multiplier * iqr)
        is_anomaly = current_value < lower_bound or current_value > upper_bound

        return {
            "metric": metric_name,
            "current_value": round(current_value, 2),
            "q25": round(float(q25), 2),
            "q75": round(float(q75), 2),
            "iqr": round(float(iqr), 2),
            "lower_bound": round(float(lower_bound), 2),
            "upper_bound": round(float(upper_bound), 2),
            "is_anomaly": is_anomaly,
            "method": "iqr"
        }

    def analyze_snapshot(self, current: TelemetrySnapshot, history: List[TelemetrySnapshot]) -> List[Dict[str, Any]]:
        anomalies = []
        metrics_to_check = [
            ("latency_ms", current.latency_ms, [h.latency_ms for h in history]),
            ("request_rate", current.request_rate, [h.request_rate for h in history]),
            ("cpu_percent", current.cpu_percent, [h.cpu_percent for h in history]),
            ("memory_percent", current.memory_percent, [h.memory_percent for h in history]),
            ("error_rate", current.error_rate, [h.error_rate for h in history]),
        ]

        for name, curr_val, hist_vals in metrics_to_check:
            z_res = self.detect_zscore(curr_val, hist_vals, name)
            if z_res.is_anomaly:
                anomalies.append(z_res.to_dict())
            else:
                iqr_res = self.detect_iqr(curr_val, hist_vals, name)
                if iqr_res.get("is_anomaly"):
                    anomalies.append(iqr_res)

        return anomalies

statistical_detector = StatisticalDetector()
