import React, { useState } from 'react';
import { ShieldCheck, UserCheck, Key, AlertCircle } from 'lucide-react';
import { api } from '../api';

export default function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('admin@smartops.ai');
  const [password, setPassword] = useState('adminpassword');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const data = await api.login(email, password);
      onLoginSuccess(data);
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const selectQuickRole = (roleEmail, rolePass) => {
    setEmail(roleEmail);
    setPassword(rolePass);
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: '20px' }}>
      <div className="glass-card" style={{ maxWidth: '440px', width: '100%', padding: '36px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '24px' }}>
          <div className="logo-badge" style={{ width: '44px', height: '44px', fontSize: '1.2rem' }}>SO</div>
          <div>
            <h1 style={{ fontSize: '1.4rem', fontWeight: 800 }}>SmartOps AI</h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>MCP-Powered Incident Response Platform</p>
          </div>
        </div>

        {error && (
          <div style={{ padding: '12px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid var(--accent-red)', borderRadius: 'var(--radius-md)', color: 'var(--accent-red)', fontSize: '0.85rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={16} /> {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '6px', fontWeight: 600 }}>EMAIL ADDRESS</label>
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{ width: '100%', padding: '10px 14px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', color: '#fff', fontSize: '0.9rem', outline: 'none' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-dim)', marginBottom: '6px', fontWeight: 600 }}>PASSWORD</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{ width: '100%', padding: '10px 14px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', color: '#fff', fontSize: '0.9rem', outline: 'none' }}
            />
          </div>

          <button type="submit" disabled={loading} className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', marginTop: '8px' }}>
            <ShieldCheck size={18} /> {loading ? 'Signing in...' : 'Sign In to Dashboard'}
          </button>
        </form>

        <div style={{ marginTop: '28px', borderTop: '1px solid var(--border-color)', paddingTop: '20px' }}>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Quick Switch Demo Role:</p>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button type="button" onClick={() => selectQuickRole('admin@smartops.ai', 'adminpassword')} className="btn" style={{ flex: 1, padding: '6px 8px', fontSize: '0.76rem', background: 'rgba(255,255,255,0.04)', color: 'var(--accent-purple)' }}>
              Admin
            </button>
            <button type="button" onClick={() => selectQuickRole('engineer@smartops.ai', 'engineerpassword')} className="btn" style={{ flex: 1, padding: '6px 8px', fontSize: '0.76rem', background: 'rgba(255,255,255,0.04)', color: 'var(--accent-cyan)' }}>
              Engineer
            </button>
            <button type="button" onClick={() => selectQuickRole('viewer@smartops.ai', 'viewerpassword')} className="btn" style={{ flex: 1, padding: '6px 8px', fontSize: '0.76rem', background: 'rgba(255,255,255,0.04)', color: 'var(--accent-green)' }}>
              Viewer
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
