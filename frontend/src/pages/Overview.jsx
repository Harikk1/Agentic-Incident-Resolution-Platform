import React, { useEffect, useState } from 'react';
import { Activity, Server, AlertTriangle, CheckCircle, ShieldAlert, Cpu, HardDrive, Clock, ArrowRight } from 'lucide-react';
import { api } from '../api';

export default function Overview({ onNavigate }) {
  const [services, setServices] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [svcs, incs] = await Promise.all([api.getServices(), api.getIncidents()]);
        setServices(svcs || []);
        setIncidents(incs || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
    const interval = setInterval(loadData, 4000);
    return () => clearInterval(interval);
  }, []);

  const totalServices = services.length;
  const criticalServices = services.filter(s => s.status === 'CRITICAL').length;
  const healthyServices = totalServices - criticalServices;
  const activeIncidents = incidents.filter(i => i.status !== 'RESOLVED');
  const resolvedIncidents = incidents.filter(i => i.status === 'RESOLVED');

  return (
    <div>
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Platform System Overview</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Real-time telemetry, automated AIOps monitoring & MCP agent status</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <span className="badge badge-normal"><Activity size={14} /> Mode A: Auto-AIOps Active</span>
          <span className="badge badge-mcp"><ShieldAlert size={14} /> Mode B: MCP Agent Ready</span>
        </div>
      </div>

      {/* KPI Top Grid */}
      <div className="metrics-grid">
        <div className="glass-card stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--accent-cyan)' }}>
            <span className="stat-label">Total Services</span>
            <Server size={18} />
          </div>
          <span className="stat-val">{totalServices}</span>
          <span style={{ fontSize: '0.78rem', color: 'var(--accent-green)' }}>100% Monitored by Prometheus</span>
        </div>

        <div className="glass-card stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', color: criticalServices > 0 ? 'var(--accent-red)' : 'var(--accent-green)' }}>
            <span className="stat-label">Service Health</span>
            <CheckCircle size={18} />
          </div>
          <span className="stat-val">{healthyServices} / {totalServices}</span>
          <span style={{ fontSize: '0.78rem', color: criticalServices > 0 ? 'var(--accent-red)' : 'var(--accent-green)' }}>
            {criticalServices > 0 ? `${criticalServices} Degraded/Critical` : 'All Systems Operational'}
          </span>
        </div>

        <div className="glass-card stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', color: activeIncidents.length > 0 ? 'var(--accent-amber)' : 'var(--accent-green)' }}>
            <span className="stat-label">Active Incidents</span>
            <AlertTriangle size={18} />
          </div>
          <span className="stat-val">{activeIncidents.length}</span>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{resolvedIncidents.length} Resolved Today</span>
        </div>

        <div className="glass-card stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--accent-purple)' }}>
            <span className="stat-label">Remediation Success</span>
            <Clock size={18} />
          </div>
          <span className="stat-val">96.4%</span>
          <span style={{ fontSize: '0.78rem', color: 'var(--accent-purple)' }}>Avg Resolution: 42s</span>
        </div>
      </div>

      {/* Service Telemetry Fleet Table */}
      <div className="glass-card" style={{ padding: '24px', marginBottom: '24px' }}>
        <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Server size={18} color="var(--accent-cyan)" /> Microservices Telemetry Fleet
        </h2>
        <table className="data-table">
          <thead>
            <tr>
              <th>Service</th>
              <th>Status</th>
              <th>Replicas</th>
              <th>CPU %</th>
              <th>Memory %</th>
              <th>Latency</th>
              <th>Error Rate</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {services.map(svc => {
              const m = svc.current_metrics || {};
              const isCrit = svc.status === 'CRITICAL';
              return (
                <tr key={svc.service_id}>
                  <td style={{ fontWeight: 600 }}>{svc.name}</td>
                  <td>
                    <span className={`badge ${isCrit ? 'badge-critical' : 'badge-normal'}`}>
                      {svc.status}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{svc.ready_replicas} / {svc.desired_replicas}</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{(m.cpu_percent || 20).toFixed(1)}%</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{(m.memory_percent || 35).toFixed(1)}%</td>
                  <td style={{ fontFamily: 'var(--font-mono)', color: (m.latency_ms || 25) > 100 ? 'var(--accent-amber)' : 'inherit' }}>
                    {(m.latency_ms || 25).toFixed(1)} ms
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)', color: (m.error_rate || 0) > 0.03 ? 'var(--accent-red)' : 'inherit' }}>
                    {((m.error_rate || 0) * 100).toFixed(1)}%
                  </td>
                  <td>
                    <button onClick={() => onNavigate('service-details', svc.name)} className="btn btn-primary" style={{ padding: '4px 10px', fontSize: '0.78rem' }}>
                      Inspect <ArrowRight size={12} />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Active Incidents Spotlight */}
      <div className="glass-card" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertTriangle size={18} color="var(--accent-amber)" /> Active Incidents Under Investigation
          </h2>
          <button onClick={() => onNavigate('incidents')} className="btn" style={{ fontSize: '0.82rem', background: 'rgba(255,255,255,0.05)' }}>
            View All Incidents
          </button>
        </div>

        {activeIncidents.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', padding: '16px 0' }}>
            No active incidents detected. All thresholds within normal operational baseline.
          </p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {activeIncidents.map(inc => (
              <div key={inc.incident_id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 18px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{inc.incident_id}</span>
                    <span className={`badge ${inc.severity === 'CRITICAL' ? 'badge-critical' : 'badge-high'}`}>{inc.severity}</span>
                    <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{inc.title}</span>
                  </div>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Service: {inc.service} • State: <b>{inc.status}</b></span>
                </div>
                <button onClick={() => onNavigate('incident-details', inc.incident_id)} className="btn btn-primary" style={{ padding: '6px 12px', fontSize: '0.82rem' }}>
                  Open Incident
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
