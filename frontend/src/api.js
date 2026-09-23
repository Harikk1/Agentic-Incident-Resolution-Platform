const API_BASE = '/api';

function getAuthHeaders() {
  const token = localStorage.getItem('smartops_token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {})
  };
}

export const api = {
  // Auth
  async login(email, password) {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) throw new Error('Invalid credentials');
    const data = await res.json();
    localStorage.setItem('smartops_token', data.access_token);
    localStorage.setItem('smartops_user', JSON.stringify(data));
    return data;
  },

  getCurrentUser() {
    const raw = localStorage.getItem('smartops_user');
    return raw ? JSON.parse(raw) : null;
  },

  logout() {
    localStorage.removeItem('smartops_token');
    localStorage.removeItem('smartops_user');
  },

  // Services
  async getServices() {
    const res = await fetch(`${API_BASE}/services`, { headers: getAuthHeaders() });
    return res.json();
  },

  async getServiceMetrics(service) {
    const res = await fetch(`${API_BASE}/services/${service}/metrics`, { headers: getAuthHeaders() });
    return res.json();
  },

  async getServiceHealth(service) {
    const res = await fetch(`${API_BASE}/services/${service}/health`, { headers: getAuthHeaders() });
    return res.json();
  },

  // Incidents
  async getIncidents(status = null) {
    const url = status ? `${API_BASE}/incidents?status=${status}` : `${API_BASE}/incidents`;
    const res = await fetch(url, { headers: getAuthHeaders() });
    return res.json();
  },

  async getIncident(id) {
    const res = await fetch(`${API_BASE}/incidents/${id}`, { headers: getAuthHeaders() });
    return res.json();
  },

  async investigateIncident(id) {
    const res = await fetch(`${API_BASE}/incidents/${id}/investigate`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    return res.json();
  },

  async diagnoseIncident(id) {
    const res = await fetch(`${API_BASE}/incidents/${id}/diagnose`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    return res.json();
  },

  async approveIncident(id) {
    const res = await fetch(`${API_BASE}/incidents/${id}/approve`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    return res.json();
  },

  async rejectIncident(id, reason = '') {
    const res = await fetch(`${API_BASE}/incidents/${id}/reject?reason=${encodeURIComponent(reason)}`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    return res.json();
  },

  async getIncidentTimeline(id) {
    const res = await fetch(`${API_BASE}/incidents/${id}/timeline`, { headers: getAuthHeaders() });
    return res.json();
  },

  // Chat / Agentic Mode B
  async chatWithAgent(message, sessionId = 'ses-default-01', approved = false, actionOverride = null) {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        message,
        session_id: sessionId,
        approved,
        action_override: actionOverride
      })
    });
    return res.json();
  },

  // Audit Logs
  async getAuditLogs(limit = 50) {
    const res = await fetch(`${API_BASE}/audit?limit=${limit}`, { headers: getAuthHeaders() });
    return res.json();
  }
};
