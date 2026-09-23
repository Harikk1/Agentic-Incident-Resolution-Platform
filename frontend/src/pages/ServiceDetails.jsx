import React, { useEffect, useState } from 'react';
import { ArrowLeft, Server, Activity, Cpu, HardDrive, ShieldCheck, RefreshCw, Zap } from 'lucide-react';
import { api } from '../api';

export default function ServiceDetails({ serviceName, onBack }) {
  const [metricsData, setMetricsData] = useState(null);
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [m, h] = await Promise.all([
          api.getServiceMetrics(serviceName),
          api.getServiceHealth(serviceName)
        ]);
        setMetricsData(m);
        setHealthData(h);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, [serviceName]);

  const curr = metricsData?.current || {};
  const history = metricsData?.history || [];

  return (
    <div>
      <button onClick={onBack} className="btn" style={{ background: 'rgba(255,255,255,0.05)', marginBottom: '18px' }}>
        <ArrowLeft size={16} /> Back to Fleet
      </button>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 800 }}>{serviceName}</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Real-time telemetry, pod lifecycle and health verification</p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <span className={`badge ${healthData?.healthy ? 'badge-normal' : 'badge-critical'}`}>
            {healthData?.healthy ? 'Health Probe: PASS' : 'Health Probe: FAIL'}
          </span>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="metrics-grid">
        <div className="glass-card stat-card">
          <span className="stat-label">Response Latency</span>
          <span className="stat-val" style={{ color: (curr.latency_ms || 25) > 100 ? 'var(--accent-amber)' : 'inherit' }}>
            {(curr.latency_ms || 25).toFixed(1)} ms
          </span>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Baseline: 25.0 ms</span>
        </div>

        <div className="glass-card stat-card">
          <span className="stat-label">Request Rate</span>
          <span className="stat-val">{(curr.request_rate || 50).toFixed(1)} /s</span>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Active Connections: {curr.active_requests || 5}</span>
        </div>

        <div className="glass-card stat-card">
          <span className="stat-label">CPU Utilization</span>
          <span className="stat-val">{(curr.cpu_percent || 20).toFixed(1)}%</span>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Threshold Ceiling: 70.0%</span>
        </div>

        <div className="glass-card stat-card">
          <span className="stat-label">Error Rate</span>
          <span className="stat-val" style={{ color: (curr.error_rate || 0) > 0.03 ? 'var(--accent-red)' : 'inherit' }}>
            {((curr.error_rate || 0) * 100).toFixed(1)}%
          </span>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>5xx Errors: {curr.http_5xx_count || 0}</span>
        </div>
      </div>

      {/* Deployment & Health Verification Card */}
      <div className="glass-card" style={{ padding: '24px', marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ShieldCheck size={18} color="var(--accent-green)" /> Kubernetes Deployment State & Health Probes
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <div>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>DESIRED REPLICAS</span>
            <p style={{ fontSize: '1.2rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{healthData?.deployment?.desired_replicas || 2}</p>
          </div>
          <div>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>READY REPLICAS</span>
            <p style={{ fontSize: '1.2rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{healthData?.deployment?.ready_replicas || 2}</p>
          </div>
          <div>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>HTTP PROBE STATUS</span>
            <p style={{ fontSize: '1.2rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>HTTP {healthData?.http_status || 200}</p>
          </div>
          <div>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>DATABASE QUERY LATENCY</span>
            <p style={{ fontSize: '1.2rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{(curr.database_latency_ms || 10).toFixed(1)} ms</p>
          </div>
        </div>
      </div>

      {/* Time Series History */}
      <div className="glass-card" style={{ padding: '24px' }}>
        <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Activity size={18} color="var(--accent-cyan)" /> Telemetry Samples Buffer (Last {history.length} Polling Cycles)
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '300px', overflowY: 'auto' }}>
          {history.slice(-15).reverse().map((h, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 14px', background: 'rgba(255,255,255,0.02)', borderRadius: 'var(--radius-sm)', fontSize: '0.85rem', fontFamily: 'var(--font-mono)' }}>
              <span>Cycle #{history.length - i}</span>
              <span>CPU: {h.cpu_percent.toFixed(1)}%</span>
              <span>Memory: {h.memory_percent.toFixed(1)}%</span>
              <span>Latency: {h.latency_ms.toFixed(1)}ms</span>
              <span>Req: {h.request_rate.toFixed(1)}/s</span>
              <span style={{ color: h.error_rate > 0.03 ? 'var(--accent-red)' : 'var(--accent-green)' }}>
                Err: {(h.error_rate * 100).toFixed(1)}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
