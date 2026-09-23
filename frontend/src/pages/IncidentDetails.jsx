import React, { useEffect, useState } from 'react';
import { ArrowLeft, CheckCircle, AlertTriangle, ShieldCheck, Zap, XCircle, Clock, Search, Layers } from 'lucide-react';
import { api } from '../api';

export default function IncidentDetails({ incidentId, onBack }) {
  const [incident, setIncident] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionMsg, setActionMsg] = useState('');

  const load = async () => {
    try {
      const data = await api.getIncident(incidentId);
      setIncident(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, [incidentId]);

  const handleInvestigate = async () => {
    setActionMsg('Investigating telemetry & logs...');
    await api.investigateIncident(incidentId);
    await load();
    setActionMsg('');
  };

  const handleDiagnose = async () => {
    setActionMsg('Evaluating 12 RCA candidates and historical RAG...');
    await api.diagnoseIncident(incidentId);
    await load();
    setActionMsg('');
  };

  const handleApprove = async () => {
    setActionMsg('Executing verified remediation via Kubernetes API...');
    await api.approveIncident(incidentId);
    await load();
    setActionMsg('');
  };

  const handleReject = async () => {
    setActionMsg('Rejecting remediation plan...');
    await api.rejectIncident(incidentId, 'Manual override by operator');
    await load();
    setActionMsg('');
  };

  if (!incident) return <p style={{ padding: '24px' }}>Loading incident details...</p>;

  const rca = incident.rca || {};
  const isResolved = incident.status === 'RESOLVED';
  const isWaitingApproval = incident.status === 'WAITING_APPROVAL' || incident.status === 'REMEDIATION_PROPOSED';

  return (
    <div>
      <button onClick={onBack} className="btn" style={{ background: 'rgba(255,255,255,0.05)', marginBottom: '18px' }}>
        <ArrowLeft size={16} /> Back to Incidents
      </button>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '6px' }}>
            <h1 style={{ fontSize: '1.6rem', fontWeight: 800, fontFamily: 'var(--font-mono)' }}>{incident.incident_id}</h1>
            <span className={`badge ${incident.severity === 'CRITICAL' ? 'badge-critical' : 'badge-high'}`}>{incident.severity}</span>
            <span className="badge" style={{ background: 'rgba(59, 130, 246, 0.15)', color: 'var(--accent-blue)' }}>{incident.status}</span>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>{incident.title} (Service: <b>{incident.service}</b>)</p>
        </div>

        {/* Action Buttons based on State Machine */}
        <div style={{ display: 'flex', gap: '10px' }}>
          {incident.status === 'DETECTED' && (
            <button onClick={handleInvestigate} className="btn btn-primary">
              <Search size={16} /> Investigate Telemetry
            </button>
          )}

          {incident.status === 'INVESTIGATING' && (
            <button onClick={handleDiagnose} className="btn btn-primary">
              <Zap size={16} /> Run RCA Diagnosis
            </button>
          )}

          {isWaitingApproval && (
            <>
              <button onClick={handleApprove} className="btn btn-success">
                <CheckCircle size={16} /> Approve & Execute Remediation
              </button>
              <button onClick={handleReject} className="btn btn-danger">
                <XCircle size={16} /> Reject Plan
              </button>
            </>
          )}
        </div>
      </div>

      {actionMsg && (
        <div style={{ padding: '12px 18px', background: 'rgba(6, 182, 212, 0.15)', border: '1px solid var(--accent-cyan)', borderRadius: 'var(--radius-md)', color: 'var(--accent-cyan)', marginBottom: '20px', fontSize: '0.88rem' }}>
          {actionMsg}
        </div>
      )}

      {/* Grid: Diagnosis & Remediation */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '20px', marginBottom: '24px' }}>
        {/* RCA Box */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Zap size={18} color="var(--accent-cyan)" /> Evidence-Based Root Cause Analysis
          </h2>
          {rca.root_cause ? (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>PROBABLE ROOT CAUSE</span>
                <span style={{ fontSize: '0.82rem', color: 'var(--accent-cyan)', fontWeight: 700 }}>{Math.round((rca.confidence || 0) * 100)}% CONFIDENCE</span>
              </div>
              <p style={{ fontSize: '1.25rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)', marginBottom: '16px' }}>
                {rca.root_cause}
              </p>

              <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)', display: 'block', marginBottom: '8px' }}>EVALUATED EVIDENCE:</span>
              <ul style={{ paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.88rem' }}>
                {(rca.evidence || []).map((ev, idx) => (
                  <li key={idx} style={{ color: 'var(--text-main)' }}>{ev}</li>
                ))}
              </ul>
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Diagnosis pending. Click 'Run RCA Diagnosis' to analyze evidence.</p>
          )}
        </div>

        {/* Proposed Remediation Box */}
        <div className="glass-card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldCheck size={18} color="var(--accent-green)" /> Safe Remediation Plan
          </h2>
          {incident.recommended_action ? (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>RECOMMENDED ACTION</span>
                <span className="badge badge-high">{incident.risk_level || 'MEDIUM'} RISK</span>
              </div>
              <p style={{ fontSize: '1.25rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--accent-green)', marginBottom: '16px' }}>
                {incident.recommended_action}
              </p>

              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: 'var(--radius-md)', fontFamily: 'var(--font-mono)', fontSize: '0.82rem', marginBottom: '16px' }}>
                {JSON.stringify(incident.action_parameters || {}, null, 2)}
              </div>

              {isResolved && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-green)', fontSize: '0.9rem', fontWeight: 600 }}>
                  <CheckCircle size={18} /> Verified & Resolved in Cluster
                </div>
              )}
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No remediation action proposed yet.</p>
          )}
        </div>
      </div>

      {/* State Machine Timeline */}
      <div className="glass-card" style={{ padding: '24px' }}>
        <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Clock size={18} color="var(--accent-purple)" /> Incident State Machine Lifecycle Timeline
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {(incident.timeline || []).map((t, idx) => (
            <div key={idx} style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: 'var(--accent-cyan)', marginTop: '5px', flexShrink: 0 }} />
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '2px' }}>
                  <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>{t.to_state}</span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>Actor: {t.actor}</span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginLeft: 'auto' }}>
                    {new Date(t.timestamp * 1000).toLocaleTimeString()}
                  </span>
                </div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{t.message}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
