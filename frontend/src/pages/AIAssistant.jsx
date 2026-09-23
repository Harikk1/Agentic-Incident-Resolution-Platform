import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, CheckCircle, XCircle, ShieldAlert, Sparkles, Terminal, ArrowRight } from 'lucide-react';
import { api } from '../api';

export default function AIAssistant() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `👋 **Welcome to SmartOps AI Agent.** I am connected to your microservices environment through **Model Context Protocol (MCP)**.
      
Ask me to investigate performance issues, analyze anomalies, perform root-cause analysis (RCA), or fix incidents in Kubernetes with safe, verified remediations.`,
      tool_traces: []
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (textToSend, approved = false, actionOverride = null) => {
    const text = textToSend || input;
    if (!text.trim() && !approved) return;

    if (!approved) {
      setMessages(prev => [...prev, { role: 'user', content: text, tool_traces: [] }]);
      setInput('');
    }
    setLoading(true);

    try {
      const data = await api.chatWithAgent(
        text || 'Approved remediation execution',
        'ses-demo-01',
        approved,
        actionOverride
      );

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
          tool_traces: data.tool_traces || [],
          approval_card: data.approval_card,
          verification_result: data.verification_result
        }
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `⚠️ Error communicating with agent: ${err.message}`,
          tool_traces: []
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveAction = (card) => {
    handleSend(`Approved action: ${card.recommended_action}`, true, card.recommended_action);
  };

  const handleRejectAction = () => {
    setMessages(prev => [
      ...prev,
      { role: 'user', content: 'Remediation rejected. Retain current state.' },
      { role: 'assistant', content: 'Understood. Remediation cancelled. Escalating to manual SRE review.', tool_traces: [] }
    ]);
  };

  return (
    <div className="chat-container">
      <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Sparkles size={22} color="var(--accent-cyan)" /> SmartOps AI Assistant (Mode B: Agentic MCP)
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>Autonomous multi-step investigation, MCP tool calling, RCA & verified Kubernetes remediations</p>
        </div>
      </div>

      {/* Quick Prompts Bar */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '14px', flexWrap: 'wrap' }}>
        {[
          'Payment service is slow. Find the cause and fix it.',
          'Payment started failing after the latest deployment.',
          'Check whether Payment has a memory leak.',
          'Inspect all services and detect anomalies.'
        ].map((prompt, i) => (
          <button
            key={i}
            onClick={() => handleSend(prompt)}
            className="btn"
            style={{ fontSize: '0.78rem', padding: '6px 12px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-color)', color: 'var(--text-muted)' }}
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Messages Scroll Area */}
      <div className="glass-card" style={{ flex: 1, padding: '20px', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <div className="chat-messages">
          {messages.map((msg, i) => (
            <div key={i} className={`chat-bubble ${msg.role === 'user' ? 'chat-user' : 'chat-assistant'}`}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', opacity: 0.85, fontSize: '0.8rem', fontWeight: 600 }}>
                {msg.role === 'user' ? <User size={14} /> : <Bot size={14} color="var(--accent-cyan)" />}
                {msg.role === 'user' ? 'You' : 'SmartOps Agent'}
              </div>

              {/* Tool Execution Traces */}
              {msg.tool_traces && msg.tool_traces.length > 0 && (
                <div style={{ marginBottom: '12px', padding: '10px 12px', background: 'rgba(0,0,0,0.25)', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Terminal size={12} color="var(--accent-purple)" /> MCP Tool Traces ({msg.tool_traces.length} operations):
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap' }}>
                    {msg.tool_traces.map((t, idx) => (
                      <span key={idx} className="trace-pill">
                        ✓ {t.tool_name}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Message Content */}
              <div style={{ whiteSpace: 'pre-wrap', fontSize: '0.92rem' }}>
                {msg.content}
              </div>

              {/* Inline Approval Card */}
              {msg.approval_card && msg.approval_card.approval_status === 'PENDING' && (
                <div style={{ marginTop: '16px', padding: '16px', background: 'rgba(6, 182, 212, 0.08)', border: '1px solid rgba(6, 182, 212, 0.3)', borderRadius: 'var(--radius-md)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontWeight: 700, color: 'var(--accent-cyan)', fontSize: '0.9rem' }}>Human Approval Required</span>
                    <span className="badge badge-high">{msg.approval_card.risk_level} Risk</span>
                  </div>
                  <p style={{ fontSize: '0.85rem', marginBottom: '12px', color: 'var(--text-main)' }}>
                    Execute proposed action: <b>`{msg.approval_card.recommended_action}`</b> on <b>{msg.approval_card.service}</b>?
                  </p>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button onClick={() => handleApproveAction(msg.approval_card)} className="btn btn-success" style={{ padding: '6px 14px', fontSize: '0.82rem' }}>
                      <CheckCircle size={14} /> Approve & Execute in K8s
                    </button>
                    <button onClick={handleRejectAction} className="btn btn-danger" style={{ padding: '6px 14px', fontSize: '0.82rem' }}>
                      <XCircle size={14} /> Reject
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="chat-bubble chat-assistant" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Bot size={16} color="var(--accent-cyan)" />
              <span style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>Investigating telemetry via MCP tools...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div style={{ marginTop: '16px', display: 'flex', gap: '10px', borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}>
          <input
            type="text"
            placeholder="Ask SmartOps Agent (e.g. 'Payment service is slow. Find the cause and fix it.')..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            disabled={loading}
            style={{ flex: 1, padding: '12px 18px', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', color: '#fff', fontSize: '0.92rem', outline: 'none' }}
          />
          <button onClick={() => handleSend()} disabled={loading || !input.trim()} className="btn btn-primary" style={{ padding: '0 20px' }}>
            <Send size={16} /> Send
          </button>
        </div>
      </div>
    </div>
  );
}
