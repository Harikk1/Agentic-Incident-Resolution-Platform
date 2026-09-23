import React, { useEffect, useState } from 'react';
import { ShieldCheck, Terminal, Filter, CheckCircle, XCircle } from 'lucide-react';
import { api } from '../api';

export default function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.getAuditLogs(60);
        setLogs(data || []);
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
        <h1 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Immutable Audit Trail</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Comprehensive compliance record of all AI Agent and Human MCP tool executions</p>
      </div>

      <div className="glass-card" style={{ padding: '24px' }}>
        {logs.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '24px 0' }}>No audit records found.</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Action ID</th>
                <th>Timestamp</th>
                <th>Actor</th>
                <th>MCP Tool</th>
                <th>Risk</th>
                <th>Approval</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log, i) => (
                <tr key={i}>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 700 }}>{log.action_id}</td>
                  <td style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                    {log.iso_timestamp || new Date(log.timestamp * 1000).toLocaleString()}
                  </td>
                  <td style={{ fontWeight: 600 }}>{log.actor}</td>
                  <td>
                    <span className="trace-pill" style={{ color: '#fff', background: 'rgba(255,255,255,0.06)' }}>
                      {log.tool}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${log.risk === 'HIGH' ? 'badge-critical' : log.risk === 'MEDIUM' ? 'badge-high' : 'badge-normal'}`}>
                      {log.risk}
                    </span>
                  </td>
                  <td>
                    {log.approved ? (
                      <span style={{ color: 'var(--accent-green)', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem' }}>
                        <CheckCircle size={14} /> Approved ({log.approved_by || 'auto'})
                      </span>
                    ) : (
                      <span style={{ color: 'var(--accent-amber)', fontSize: '0.85rem' }}>Not Approved</span>
                    )}
                  </td>
                  <td>
                    <span style={{ fontWeight: 700, color: log.result === 'SUCCESS' ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                      {log.result}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
