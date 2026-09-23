import React, { useEffect, useState } from 'react';
import { ShieldAlert, CheckCircle, XCircle, Clock, Zap } from 'lucide-react';
import { api } from '../api';

export default function RemediationApproval({ onNavigate }) {
  const [pendingIncidents, setPendingIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusMessage, setStatusMessage] = useState(null);

  const loadPending = async () => {
    try {
      const [waiting, proposed] = await Promise.all([
        api.getIncidents('WAITING_APPROVAL'),
        api.getIncidents('REMEDIATION_PROPOSED')
      ]);
      const combined = [...(waiting || []), ...(proposed || [])];
      const unique = Array.from(new Map(combined.map(i => [i.incident_id, i])).values());
      setPendingIncidents(unique);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPending();
    const interval = setInterval(loadPending, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleApprove = async (id) => {
    try {
      setStatusMessage({ type: 'info', text: `Executing verified remediation for ${id}...` });
      const res = await api.approveIncident(id);
      if (res && res.detail) {
        setStatusMessage({ type: 'error', text: `Approval failed: ${res.detail}` });
      } else {
        setStatusMessage({ type: 'success', text: `Remediation for ${id} approved & deployed! Verified in Kubernetes.` });
        setTimeout(() => setStatusMessage(null), 4000);
      }
      await loadPending();
    } catch (e) {
      setStatusMessage({ type: 'error', text: `Error approving: ${e.message}` });
    }
  };

  const handleReject = async (id) => {
    try {
      setStatusMessage({ type: 'info', text: `Rejecting plan for ${id}...` });
      await api.rejectIncident(id, 'Rejected in approval queue');
      setStatusMessage({ type: 'warning', text: `Plan for ${id} rejected. Retained safe current state.` });
      setTimeout(() => setStatusMessage(null), 4000);
      await loadPending();
    } catch (e) {
      setStatusMessage({ type: 'error', text: `Error rejecting: ${e.message}` });
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Remediation Approval Queue</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Human-in-the-loop governance for medium and high-risk Kubernetes operations</p>
      </div>

      {statusMessage && (
        <div style={{
          padding: '12px 18px',
          borderRadius: 'var(--radius-md)',
          marginBottom: '20px',
          fontSize: '0.9rem',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          background: statusMessage.type === 'success' ? 'rgba(34, 197, 94, 0.15)' : statusMessage.type === 'error' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(6, 182, 212, 0.15)',
          border: `1px solid ${statusMessage.type === 'success' ? 'var(--accent-green)' : statusMessage.type === 'error' ? 'var(--accent-red)' : 'var(--accent-cyan)'}`,
          color: statusMessage.type === 'success' ? 'var(--accent-green)' : statusMessage.type === 'error' ? 'var(--accent-red)' : 'var(--accent-cyan)'
        }}>
          <Zap size={16} />
          {statusMessage.text}
        </div>
      )}

      {pendingIncidents.length === 0 ? (
        <div className="glass-card" style={{ padding: '36px', textAlign: 'center' }}>
          <CheckCircle size={36} color="var(--accent-green)" style={{ margin: '0 auto 12px' }} />
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '6px' }}>Approval Queue is Clean</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No pending remediation actions requiring human authorization.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {pendingIncidents.map(inc => (
            <div key={inc.incident_id} className="glass-card" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 700, fontFamily: 'var(--font-mono)', fontSize: '1.1rem' }}>{inc.incident_id}</span>
                    <span className="badge badge-high">{inc.risk_level || 'MEDIUM'} RISK</span>
                    <span style={{ fontWeight: 600 }}>{inc.title}</span>
                  </div>
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Target Service: <b>{inc.service}</b></span>
                </div>

                <div style={{ display: 'flex', gap: '10px' }}>
                  <button onClick={() => handleApprove(inc.incident_id)} className="btn btn-success">
                    <CheckCircle size={16} /> Approve & Deploy
                  </button>
                  <button onClick={() => handleReject(inc.incident_id)} className="btn btn-danger">
                    <XCircle size={16} /> Reject
                  </button>
                </div>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '16px', borderRadius: 'var(--radius-md)', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)', display: 'block', marginBottom: '4px' }}>DIAGNOSED ROOT CAUSE</span>
                  <p style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>{inc.rca?.root_cause || 'UNKNOWN'} ({Math.round((inc.rca?.confidence || 0) * 100)}% Confidence)</p>
                </div>
                <div>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)', display: 'block', marginBottom: '4px' }}>PROPOSED ACTION</span>
                  <p style={{ fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--accent-green)' }}>{inc.recommended_action} {JSON.stringify(inc.action_parameters || {})}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
