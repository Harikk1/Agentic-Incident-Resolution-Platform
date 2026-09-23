import React from 'react';
import { Sliders, ShieldCheck, Database, Server, CheckCircle2 } from 'lucide-react';

export default function Settings() {
  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Platform Settings & Configuration</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Threshold sensitivity, local simulation modes & provider connections</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px' }}>
        {/* Layer 1 Detection Thresholds */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sliders size={18} color="var(--accent-cyan)" /> Detection Thresholds (Layer 1)
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)', display: 'block' }}>CPU UTILIZATION</span>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.95rem' }}>HIGH: <b>70%</b> • CRITICAL: <b>90%</b></p>
            </div>
            <div>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)', display: 'block' }}>MEMORY CEILING</span>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.95rem' }}>HIGH: <b>75%</b> • CRITICAL: <b>90%</b></p>
            </div>
            <div>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)', display: 'block' }}>LATENCY THRESHOLD</span>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.95rem' }}>HIGH: <b>100 ms</b> • CRITICAL: <b>150 ms</b></p>
            </div>
            <div>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)', display: 'block' }}>ERROR RATE THRESHOLD</span>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.95rem' }}>HIGH: <b>3.0%</b> • CRITICAL: <b>5.0%</b></p>
            </div>
          </div>
        </div>

        {/* Local Simulation & Mock Modes */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Server size={18} color="var(--accent-purple)" /> Active Runtime Environment Modes
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', background: 'rgba(255,255,255,0.02)', borderRadius: 'var(--radius-sm)' }}>
              <span>Mock Kubernetes Driver</span>
              <span className="badge badge-normal"><CheckCircle2 size={12} /> ENABLED</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', background: 'rgba(255,255,255,0.02)', borderRadius: 'var(--radius-sm)' }}>
              <span>Deterministic Mock LLM Mode</span>
              <span className="badge badge-normal"><CheckCircle2 size={12} /> ENABLED</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', background: 'rgba(255,255,255,0.02)', borderRadius: 'var(--radius-sm)' }}>
              <span>In-Memory Log Store</span>
              <span className="badge badge-normal"><CheckCircle2 size={12} /> ENABLED</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', background: 'rgba(255,255,255,0.02)', borderRadius: 'var(--radius-sm)' }}>
              <span>In-Memory MongoDB Repository</span>
              <span className="badge badge-normal"><CheckCircle2 size={12} /> ENABLED</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
