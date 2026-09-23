import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, Server, AlertTriangle, MessageSquare, 
  CheckSquare, FileText, Sliders, LogOut, Shield, ChevronRight
} from 'lucide-react';
import { api } from './api';

import Login from './pages/Login';
import Overview from './pages/Overview';
import Services from './pages/Services';
import ServiceDetails from './pages/ServiceDetails';
import Incidents from './pages/Incidents';
import IncidentDetails from './pages/IncidentDetails';
import AIAssistant from './pages/AIAssistant';
import RemediationApproval from './pages/RemediationApproval';
import AuditLogs from './pages/AuditLogs';
import Settings from './pages/Settings';

export default function App() {
  const [currentUser, setCurrentUser] = useState(api.getCurrentUser());
  const [currentPage, setCurrentPage] = useState('overview');
  const [selectedService, setSelectedService] = useState('payment-service');
  const [selectedIncidentId, setSelectedIncidentId] = useState(null);

  useEffect(() => {
    // If no token exists, set demo admin as default in dev mode
    if (!currentUser) {
      const defaultUser = {
        user_id: 'usr-admin-01',
        email: 'admin@smartops.ai',
        role: 'ADMIN',
        permissions: ['read:all', 'action:all', 'remediation:approve:all']
      };
      setCurrentUser(defaultUser);
    }
  }, []);

  const navigateTo = (page, param = null) => {
    if (page === 'service-details' && param) {
      setSelectedService(param);
    }
    if (page === 'incident-details' && param) {
      setSelectedIncidentId(param);
    }
    setCurrentPage(page);
  };

  const handleLogout = () => {
    api.logout();
    setCurrentUser(null);
  };

  if (!currentUser) {
    return <Login onLoginSuccess={(u) => setCurrentUser(u)} />;
  }

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo-badge">SO</div>
          <div>
            <h2 style={{ fontSize: '1.05rem', fontWeight: 800 }}>SmartOps AI</h2>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Agentic Incident Platform</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <button 
            className={`nav-item ${currentPage === 'overview' ? 'active' : ''}`}
            onClick={() => navigateTo('overview')}
          >
            <LayoutDashboard size={18} /> Overview
          </button>

          <button 
            className={`nav-item ${currentPage === 'services' || currentPage === 'service-details' ? 'active' : ''}`}
            onClick={() => navigateTo('services')}
          >
            <Server size={18} /> Services Fleet
          </button>

          <button 
            className={`nav-item ${currentPage === 'incidents' || currentPage === 'incident-details' ? 'active' : ''}`}
            onClick={() => navigateTo('incidents')}
          >
            <AlertTriangle size={18} /> Incidents
          </button>

          <button 
            className={`nav-item ${currentPage === 'ai-assistant' ? 'active' : ''}`}
            onClick={() => navigateTo('ai-assistant')}
          >
            <MessageSquare size={18} /> AI Assistant (MCP)
          </button>

          <button 
            className={`nav-item ${currentPage === 'remediation-approval' ? 'active' : ''}`}
            onClick={() => navigateTo('remediation-approval')}
          >
            <CheckSquare size={18} /> Approvals Queue
          </button>

          <button 
            className={`nav-item ${currentPage === 'audit-logs' ? 'active' : ''}`}
            onClick={() => navigateTo('audit-logs')}
          >
            <FileText size={18} /> Audit Trail
          </button>

          <button 
            className={`nav-item ${currentPage === 'settings' ? 'active' : ''}`}
            onClick={() => navigateTo('settings')}
          >
            <Sliders size={18} /> Settings
          </button>
        </nav>

        {/* User Badge at Bottom of Sidebar */}
        <div style={{ padding: '16px', borderTop: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, display: 'block' }}>{currentUser.email}</span>
            <span className="badge badge-normal" style={{ fontSize: '0.68rem', padding: '2px 6px' }}>{currentUser.role}</span>
          </div>
          <button onClick={handleLogout} className="btn" style={{ padding: '6px', color: 'var(--text-muted)' }} title="Sign Out">
            <LogOut size={16} />
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        <header className="top-bar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: 'var(--text-dim)' }}>
            <span>SmartOps</span>
            <ChevronRight size={14} />
            <span style={{ color: 'var(--text-main)', textTransform: 'capitalize' }}>{currentPage.replace('-', ' ')}</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span className="badge" style={{ background: 'rgba(6, 182, 212, 0.1)', color: 'var(--accent-cyan)' }}>
              MCP Protocol: FastMCP Active
            </span>
          </div>
        </header>

        <div className="page-wrapper">
          {currentPage === 'overview' && <Overview onNavigate={navigateTo} />}
          {currentPage === 'services' && <Services onNavigate={navigateTo} />}
          {currentPage === 'service-details' && (
            <ServiceDetails serviceName={selectedService} onBack={() => navigateTo('services')} />
          )}
          {currentPage === 'incidents' && <Incidents onNavigate={navigateTo} />}
          {currentPage === 'incident-details' && (
            <IncidentDetails incidentId={selectedIncidentId} onBack={() => navigateTo('incidents')} />
          )}
          {currentPage === 'ai-assistant' && <AIAssistant />}
          {currentPage === 'remediation-approval' && <RemediationApproval onNavigate={navigateTo} />}
          {currentPage === 'audit-logs' && <AuditLogs />}
          {currentPage === 'settings' && <Settings />}
        </div>
      </main>
    </div>
  );
}
