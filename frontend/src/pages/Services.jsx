import React, { useEffect, useState } from 'react';
import { Server, ArrowRight, Activity, ShieldCheck, Database, Layers } from 'lucide-react';
import { api } from '../api';

export default function Services({ onNavigate }) {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.getServices();
        setServices(data || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
    const interval = setInterval(load, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Microservices Fleet</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Architecture dependencies, deployment replicas & real-time telemetry</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
        {services.map(svc => {
          const m = svc.current_metrics || {};
          const isCrit = svc.status === 'CRITICAL';
          return (
            <div key={svc.service_id} className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>{svc.name}</h3>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>{svc.namespace} • {svc.version}</span>
                </div>
                <span className={`badge ${isCrit ? 'badge-critical' : 'badge-normal'}`}>{svc.status}</span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', background: 'rgba(255,255,255,0.02)', padding: '14px', borderRadius: 'var(--radius-md)' }}>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block' }}>REPLICAS</span>
                  <span style={{ fontSize: '1.1rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{svc.ready_replicas} / {svc.desired_replicas}</span>
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block' }}>LATENCY</span>
                  <span style={{ fontSize: '1.1rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: (m.latency_ms || 25) > 100 ? 'var(--accent-amber)' : 'inherit' }}>
                    {(m.latency_ms || 25).toFixed(0)} ms
                  </span>
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block' }}>CPU UTILIZATION</span>
                  <span style={{ fontSize: '1.1rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{(m.cpu_percent || 20).toFixed(1)}%</span>
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block' }}>ERROR RATE</span>
                  <span style={{ fontSize: '1.1rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: (m.error_rate || 0) > 0.03 ? 'var(--accent-red)' : 'inherit' }}>
                    {((m.error_rate || 0) * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', display: 'block', marginBottom: '6px' }}>UPSTREAM DEPENDENCIES</span>
                {svc.dependencies && svc.dependencies.length > 0 ? (
                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                    {svc.dependencies.map((d, idx) => (
                      <span key={idx} style={{ fontSize: '0.76rem', padding: '3px 8px', background: 'rgba(255,255,255,0.04)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Layers size={10} color="var(--accent-cyan)" /> {d.target_service}
                      </span>
                    ))}
                  </div>
                ) : (
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>No upstream dependencies</span>
                )}
              </div>

              <button onClick={() => onNavigate('service-details', svc.name)} className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: 'auto' }}>
                Inspect Service Telemetry <ArrowRight size={14} />
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
