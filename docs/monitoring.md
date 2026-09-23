# Monitoring & Observability Architecture

SmartOps provides continuous telemetry collection and multi-tier anomaly detection.

## Monitored Metrics
- CPU utilization percent
- Memory utilization percent
- Disk space percent
- Request count & rate (req/s)
- Latency (ms) & request duration
- Error counts & 5xx error rate
- Active concurrent connections
- Pod availability & readiness
- Pod restart cycles & OOMKilled events
- Database query latency & timeouts
- Upstream dependency latency & failures

## Three Detection Layers
1. **Layer 1: Deterministic Threshold Rules**: Configurable bounds returning `NORMAL`, `HIGH`, `CRITICAL`.
2. **Layer 2: Statistical Anomaly Detection**: Rolling window mean, standard deviation, Z-score ($z > 2.5$), and Interquartile Range (IQR).
3. **Layer 3: Machine Learning Outlier Detection**: scikit-learn `IsolationForest` fitted on multivariate telemetry vectors (`cpu`, `memory`, `disk`, `request_rate`, `latency`, `error_rate`).
