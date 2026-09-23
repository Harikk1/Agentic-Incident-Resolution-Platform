import React, { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle, Search, ArrowRight, Filter } from 'lucide-react';
import { api } from '../api';

export default function Incidents({ onNavigate }) {
  const [incidents, setIncidents] = useState([]);
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.getIncidents(statusFilter === 'ALL' ? null : statusFilter);
        setIncidents(data || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
    const interval = setInterval(load, 4000);
    return () => clearInterval(interval);
  }, [statusFilter]);

  return (
    <div>
      <div style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Incidents Management</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Automated detection, investigation lifecycle & verified remediations</p>
        </div>

        {/* Filter buttons */}
        <div style={{ display: 'flex', gap: '8px', background: 'rgba(255,255,255,0.03)', padding: '4px', borderRadius: 'var(--radius-md)' }}>
          {['ALL', 'DETECTED', 'INVESTIGATING', 'DIAGNOSED', 'WAITING_APPROVAL', 'RESOLVED'].map(st => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className="btn"
              style={{
                padding: '6px 12px',
                fontSize: '0.78rem',
                background: statusFilter === st ? 'rgba(6, 182, 212, 0.2)' : 'transparent',
                color: statusFilter === st ? 'var(--accent-cyan)' : 'var(--text-muted)',
                borderColor: statusFilter === st ? 'rgba(6, 182, 212, 0.3)' : 'transparent'
              }}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      <div className="glass-card" style={{ padding: '24px' }}>
        {incidents.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', padding: '24px 0', textAlign: 'center' }}>No incidents matching current filter.</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Incident ID</th>
                <th>Service</th>
                <th>Severity</th>
                <th>State Machine Status</th>
                <th>Title / Symptoms</th>
                <th>Root Cause</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {incidents.map(inc => {
                const rca = inc.rca || {};
                return (
                  <tr key={inc.incident_id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 700 }}>{inc.incident_id}</td>
                    <td style={{ fontWeight: 600 }}>{inc.service}</td>
                    <td>
                      <span className={`badge ${inc.severity === 'CRITICAL' ? 'badge-critical' : 'badge-high'}`}>
                        {inc.severity}
                      </span>
                    </td>
                    <td>
                      <span className="badge" style={{ background: 'rgba(59, 130, 246, 0.15)', color: 'var(--accent-blue)', borderColor: 'rgba(59, 130, 246, 0.3)' }}>
                        {inc.status}
                      </span>
                    </td>
                    <td style={{ maxWidth: '280px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {inc.title}
                    </td>
                    <td>
                      {rca.root_cause ? (
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--accent-cyan)' }}>
                          {rca.root_cause} ({Math.round((rca.confidence || 0) * 100)}%)
                        </span>
                      ) : (
                        <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>Pending RCA</span>
                      )}
                    </td>
                    <td>
                      <button onClick={() => onNavigate('incident-details', inc.incident_id)} className="btn btn-primary" style={{ padding: '5px 12px', fontSize: '0.78rem' }}>
                        View Details <ArrowRight size={12} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
