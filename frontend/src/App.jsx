import React, { useState, useEffect } from 'react';

const API_URL = import.meta.env.VITE_API_URL || '/api';

// ── Icons ──────────────────────────────────────────────────
const Building2 = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/>
    <path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/>
    <path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/>
    <path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/>
  </svg>
);
const CheckCircle = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>
  </svg>
);
const XCircle = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>
  </svg>
);
const Plus = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M5 12h14"/><path d="M12 5v14"/>
  </svg>
);
const Pencil = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/>
  </svg>
);
const Trash2 = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/>
    <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
  </svg>
);
const Mail = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
  </svg>
);
const Clock = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
  </svg>
);
const Users = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
    <circle cx="9" cy="7" r="4"/>
    <path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
  </svg>
);
const FileText = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
    <polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/>
    <line x1="16" x2="8" y1="17" y2="17"/><line x1="10" x2="8" y1="9" y2="9"/>
  </svg>
);
const RefreshCw = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
    <path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
    <path d="M8 16H3v5"/>
  </svg>
);
const AlertCircle = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/>
    <line x1="12" x2="12.01" y1="16" y2="16"/>
  </svg>
);

// ── Helpers ────────────────────────────────────────────────
// Backend sends naive UTC timestamps (no timezone suffix) — append "Z" so the
// browser parses them as UTC instead of local time.
const parseUTC = (d) => new Date(/[Z+-]\d{2}:?\d{2}$|Z$/.test(d) ? d : `${d}Z`);
const fmt = (d) => {
  if (!d) return 'Never';
  return parseUTC(d).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
};
const fmtShort = (d) => {
  if (!d) return '--';
  return parseUTC(d).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
};
const daysSince = (d) => {
  if (!d) return null;
  return Math.floor((Date.now() - parseUTC(d)) / 86400000);
};

const OUTREACH_STATUS_META = {
  data_received: { label: 'Replied - No Addresses', color: '#fbbf24', bg: 'rgba(250,204,21,0.15)', border: 'rgba(250,204,21,0.3)' },
  pending: { label: 'Pending', color: '#fbbf24', bg: 'rgba(250,204,21,0.15)', border: 'rgba(250,204,21,0.3)' },
  fee_required: { label: 'Fee Required', color: '#fbbf24', bg: 'rgba(250,204,21,0.15)', border: 'rgba(250,204,21,0.3)' },
  refused: { label: 'Refused', color: '#fc8181', bg: 'rgba(245,101,101,0.15)', border: 'rgba(245,101,101,0.3)' },
  redirected: { label: 'Redirected', color: '#fc8c4a', bg: 'rgba(252,140,74,0.15)', border: 'rgba(252,140,74,0.3)' },
  wrong_county: { label: 'Wrong County', color: '#fc8c4a', bg: 'rgba(252,140,74,0.15)', border: 'rgba(252,140,74,0.3)' },
  bounced: { label: 'Bounced', color: '#fc8181', bg: 'rgba(245,101,101,0.15)', border: 'rgba(245,101,101,0.3)' },
  no_reply: { label: 'No Reply Yet', color: '#a1a1aa', bg: 'rgba(255,255,255,0.06)', border: 'rgba(255,255,255,0.12)' },
};
const outreachMeta = (s) => OUTREACH_STATUS_META[s] || OUTREACH_STATUS_META.no_reply;

const OutreachBadge = ({ status, notes }) => {
  const m = outreachMeta(status);
  return (
    <span
      title={notes || ''}
      style={{
        display: 'inline-flex', alignItems: 'center', padding: '5px 12px',
        borderRadius: '20px', fontSize: '12px', fontWeight: 600,
        color: m.color, background: m.bg, border: `1px solid ${m.border}`,
        cursor: notes ? 'help' : 'default',
      }}
    >
      {m.label}
    </span>
  );
};

// ── App ────────────────────────────────────────────────────
export default function App() {
  const [tab, setTab] = useState('counties');
  const [counties, setCounties] = useState([]);
  const [emailLogs, setEmailLogs] = useState([]);
  const [receivedFiles, setReceivedFiles] = useState([]);
  const [receivedEmails, setReceivedEmails] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [logsLoading, setLogsLoading] = useState(false);
  const [receivedLoading, setReceivedLoading] = useState(false);
  const [polling, setPolling] = useState(false);
  const [emailSending, setEmailSending] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingCounty, setEditingCounty] = useState(null);
  const [logFilter, setLogFilter] = useState('all');
  const [showFollowUps, setShowFollowUps] = useState(false);
  const [formData, setFormData] = useState({
    county_name: '', state: '', phone: '', email: '',
    contact_person: '', status: 'active', notes: ''
  });

  useEffect(() => { loadCounties(); loadStats(); }, []);
  useEffect(() => { if (tab === 'logs') loadEmailLogs(); }, [tab]);
  useEffect(() => { if (tab === 'received') loadReceivedData(); }, [tab]);

  const loadCounties = async () => {
    try {
      const r = await fetch(`${API_URL}/counties`);
      setCounties(await r.json());
    } catch (e) { console.error(e); } finally { setLoading(false); }
  };
  const loadStats = async () => {
    try {
      const r = await fetch(`${API_URL}/stats`);
      setStats(await r.json());
    } catch (e) { console.error(e); }
  };
  const loadEmailLogs = async () => {
    setLogsLoading(true);
    try {
      const r = await fetch(`${API_URL}/email-logs`);
      setEmailLogs(await r.json());
    } catch (e) { console.error(e); } finally { setLogsLoading(false); }
  };

  const loadReceivedData = async () => {
    setReceivedLoading(true);
    try {
      const [files, emails] = await Promise.all([
        fetch(`${API_URL}/received-files`).then(r => r.json()),
        fetch(`${API_URL}/received-emails`).then(r => r.json()),
      ]);
      setReceivedFiles(files);
      setReceivedEmails(emails);
    } catch (e) { console.error(e); } finally { setReceivedLoading(false); }
  };

  const handlePollInbox = async () => {
    setPolling(true);
    try {
      await fetch(`${API_URL}/poll-inbox`, { method: 'POST' });
      setTimeout(() => { loadReceivedData(); loadStats(); }, 5000);
      alert('Inbox check started! Results will appear in a few seconds.');
    } catch (e) { alert('Error: ' + e.message); }
    finally { setPolling(false); }
  };

  const openAddModal = () => {
    setEditingCounty(null);
    setFormData({ county_name: '', state: '', phone: '', email: '', contact_person: '', status: 'active', notes: '' });
    setModalOpen(true);
  };
  const openEditModal = async (id) => {
    try {
      const r = await fetch(`${API_URL}/counties/${id}`);
      const c = await r.json();
      setEditingCounty(c);
      setFormData({ county_name: c.county_name, state: c.state, phone: c.phone || '', email: c.email || '', contact_person: c.contact_person || '', status: c.status, notes: c.notes || '' });
      setModalOpen(true);
    } catch (e) { console.error(e); }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const url = editingCounty ? `${API_URL}/counties/${editingCounty.id}` : `${API_URL}/counties`;
      const r = await fetch(url, { method: editingCounty ? 'PUT' : 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formData) });
      if (r.ok) { setModalOpen(false); loadCounties(); loadStats(); }
      else { const err = await r.json(); alert('Error: ' + (err.detail || 'Failed to save')); }
    } catch (e) { alert('Error saving county: ' + e.message); }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete "${name}"?`)) return;
    try {
      const r = await fetch(`${API_URL}/counties/${id}`, { method: 'DELETE' });
      if (r.ok) { loadCounties(); loadStats(); }
    } catch (e) { alert('Error deleting county'); }
  };

  const handleSendEmails = async () => {
    if (!window.confirm('Send Lis Pendens request emails to all active counties now?')) return;
    setEmailSending(true);
    try {
      const r = await fetch(`${API_URL}/send-emails`, { method: 'POST' });
      const d = await r.json();
      if (r.ok) {
        alert(`Email sending started!\n\n${d.recipients} counties will receive emails.\nCheck the Email Logs tab for results.`);
        loadCounties(); loadStats();
      } else alert('Error: ' + (d.detail || 'Unknown error'));
    } catch (e) { alert('Error: ' + e.message); }
    finally { setEmailSending(false); }
  };

  // ── Derived ──
  const noReplyCounties = counties.filter(c => {
    if (c.status !== 'active' || !c.last_request_sent) return false;
    return daysSince(c.last_request_sent) >= 7;
  });
  const filteredLogs = logFilter === 'all' ? emailLogs : emailLogs.filter(l => l.status === logFilter);
  const sentCount = emailLogs.filter(l => l.status === 'sent').length;
  const failedCount = emailLogs.filter(l => l.status === 'failed').length;
  const outreachCounts = counties.reduce((acc, c) => {
    const key = c.outreach_status || 'no_reply';
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
  const dataReceivedCount = outreachCounts.data_received || 0;
  const bouncedCount = outreachCounts.bounced || 0;

  return (
    <div className="container">
      {/* Header */}
      <div className="header">
        <div>
          <h1>County Pre-Foreclosure System</h1>
          <p>Automated Lis Pendens data collection across judicial foreclosure states</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ color: '#68d391', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px' }}>
            <CheckCircle /> System Online
          </div>
          <button className="btn btn-success" onClick={handleSendEmails} disabled={emailSending}>
            <Mail /> {emailSending ? 'Sending...' : 'Send Emails Now'}
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-row"><h3>Total Counties</h3><Building2 /></div>
          <div className="number">{stats?.total_counties || 0}</div>
          <div className="subtitle">across all states</div>
        </div>
        <div className="stat-card">
          <div className="stat-row"><h3>Replied, No Addresses</h3><Users /></div>
          <div className="number" style={{ color: dataReceivedCount > 0 ? '#fbbf24' : '#a1a1aa' }}>{dataReceivedCount}</div>
          <div className="subtitle">of {counties.length} counties - no usable data yet</div>
        </div>
        <div className="stat-card">
          <div className="stat-row"><h3>Emails Sent</h3><Mail /></div>
          <div className="number" style={{ color: '#667eea' }}>{stats?.emails_sent || 0}</div>
          <div className="subtitle">total requests sent</div>
        </div>
        <div className="stat-card">
          <div className="stat-row"><h3>Next Auto-Send</h3><Clock /></div>
          <div className="number" style={{ fontSize: '18px' }}>{stats ? fmtShort(stats.next_email_schedule) : '--'}</div>
          <div className="subtitle">Mon & Thu at 9 AM</div>
        </div>
      </div>

      {/* Outreach Breakdown */}
      {counties.length > 0 && (
        <div className="main-content" style={{ marginBottom: '20px', padding: '20px 30px' }}>
          <div style={{ fontSize: '13px', color: '#a1a1aa', marginBottom: '14px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '1px' }}>
            Outreach Breakdown ({counties.length} counties contacted)
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {Object.entries(OUTREACH_STATUS_META).map(([key, meta]) => {
              const count = outreachCounts[key] || 0;
              if (count === 0) return null;
              return (
                <div
                  key={key}
                  style={{
                    display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 14px',
                    borderRadius: '10px', background: meta.bg, border: `1px solid ${meta.border}`,
                  }}
                >
                  <strong style={{ color: meta.color, fontSize: '16px' }}>{count}</strong>
                  <span style={{ fontSize: '13px', color: '#e4e4e7' }}>{meta.label}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Follow-up Alert */}
      {noReplyCounties.length > 0 && (
        <div className="alert-banner">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', width: '100%' }}>
            <AlertCircle />
            <span style={{ flex: 1 }}>
              <strong>{noReplyCounties.length} counties</strong> haven't replied in 7+ days — consider following up.
            </span>
            <button
              className="btn btn-secondary btn-small"
              style={{ flexShrink: 0 }}
              onClick={() => setShowFollowUps(v => !v)}
            >
              {showFollowUps ? 'Hide list' : 'View list'}
            </button>
          </div>
          {showFollowUps && (
            <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid rgba(252,140,74,0.2)', fontSize: '13px', lineHeight: 1.8 }}>
              {noReplyCounties.map(c => `${c.county_name}, ${c.state}`).join(' · ')}
            </div>
          )}
        </div>
      )}

      {/* Tabs */}
      <div className="tabs">
        <button className={`tab ${tab === 'counties' ? 'tab-active' : ''}`} onClick={() => setTab('counties')}>
          <Building2 /> Counties ({counties.length})
        </button>
        <button className={`tab ${tab === 'logs' ? 'tab-active' : ''}`} onClick={() => setTab('logs')}>
          <Mail /> Email Logs
        </button>
        <button className={`tab ${tab === 'received' ? 'tab-active' : ''}`} onClick={() => setTab('received')}>
          <FileText /> Received Data
        </button>
      </div>

      {/* ── Tab: Counties ── */}
      {tab === 'counties' && (
        <div className="main-content">
          <div className="section-header">
            <h2>County List</h2>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button className="btn btn-secondary btn-small" onClick={() => { loadCounties(); loadStats(); }}>
                <RefreshCw /> Refresh
              </button>
              <button className="btn" onClick={openAddModal}><Plus /> Add County</button>
            </div>
          </div>
          <div className="table-container">
            {loading ? (
              <div className="loading"><div className="spinner"></div><p>Loading...</p></div>
            ) : counties.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state-icon">📭</div>
                <h3>No counties added yet</h3>
                <p>Click "Add County" to get started</p>
              </div>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>County</th>
                    <th>State</th>
                    <th>Email</th>
                    <th>Outreach Status</th>
                    <th>Last Emailed</th>
                    <th>Days Since</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {counties.map((c, i) => {
                    const days = daysSince(c.last_request_sent);
                    const isStale = days !== null && days >= 30;
                    return (
                      <tr key={c.id} className={i % 2 === 1 ? 'row-alt' : ''}>
                        <td><strong>{c.county_name}</strong></td>
                        <td><span className="state-badge">{c.state}</span></td>
                        <td style={{ fontSize: '12px', color: '#a1a1aa' }}>{c.email || '-'}</td>
                        <td>
                          <OutreachBadge status={c.outreach_status} notes={c.status_notes} />
                        </td>
                        <td style={{ fontSize: '13px' }}>{fmt(c.last_request_sent)}</td>
                        <td>
                          {days !== null ? (
                            <span style={{ color: isStale ? '#fc8c4a' : '#a1a1aa', fontWeight: 500, fontSize: '13px' }}>
                              {days}d ago
                            </span>
                          ) : <span style={{ color: '#a1a1aa', fontSize: '13px' }}>-</span>}
                        </td>
                        <td>
                          <div className="actions">
                            <button className="btn btn-success btn-small" onClick={() => openEditModal(c.id)}><Pencil /> Edit</button>
                            <button className="btn btn-danger btn-small" onClick={() => handleDelete(c.id, c.county_name)}><Trash2 /> Delete</button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}

      {/* ── Tab: Email Logs ── */}
      {tab === 'logs' && (
        <div className="main-content">
          <div className="section-header">
            <h2>Email Logs</h2>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <div className="log-summary">
                <span style={{ color: '#68d391' }}>✓ {sentCount} sent</span>
                <span style={{ color: '#fc8181' }}>✗ {failedCount} failed</span>
              </div>
              <select className="filter-select" value={logFilter} onChange={e => setLogFilter(e.target.value)}>
                <option value="all">All</option>
                <option value="sent">Sent</option>
                <option value="failed">Failed</option>
              </select>
              <button className="btn btn-secondary btn-small" onClick={loadEmailLogs}><RefreshCw /> Refresh</button>
            </div>
          </div>
          {logsLoading ? (
            <div className="loading"><div className="spinner"></div><p>Loading logs...</p></div>
          ) : filteredLogs.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📬</div>
              <h3>No email logs yet</h3>
              <p>Logs appear here after emails are sent</p>
            </div>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Recipient</th>
                    <th>Subject</th>
                    <th>Status</th>
                    <th>Sent At</th>
                    <th>Error</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredLogs.map(l => (
                    <tr key={l.id}>
                      <td style={{ fontSize: '13px' }}>{l.recipient}</td>
                      <td style={{ fontSize: '12px', color: '#a1a1aa', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{l.subject}</td>
                      <td>
                        <span className={`badge ${l.status === 'sent' ? 'badge-active' : l.status === 'failed' ? 'badge-inactive' : 'badge-pending'}`}>
                          {l.status === 'sent' ? <CheckCircle /> : l.status === 'failed' ? <XCircle /> : <Clock />}
                          {l.status}
                        </span>
                      </td>
                      <td style={{ fontSize: '13px' }}>{fmt(l.sent_at)}</td>
                      <td style={{ fontSize: '12px', color: '#fc8181' }}>{l.error_message || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ── Tab: Received Data ── */}
      {tab === 'received' && (
        <div className="main-content">
          <div className="section-header">
            <h2>Received Data</h2>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button className="btn btn-secondary btn-small" onClick={loadReceivedData}><RefreshCw /> Refresh</button>
              <button className="btn btn-success" onClick={handlePollInbox} disabled={polling}>
                <Mail /> {polling ? 'Checking...' : 'Check Inbox Now'}
              </button>
            </div>
          </div>

          {receivedLoading ? (
            <div className="loading"><div className="spinner"></div><p>Loading...</p></div>
          ) : (
            <>
              {/* Summary cards */}
              <div className="received-summary">
                <div className="received-summary-card">
                  <div style={{ fontSize: '28px', fontWeight: 700, color: '#667eea' }}>{receivedFiles.length}</div>
                  <div style={{ fontSize: '12px', color: '#a1a1aa', marginTop: '4px' }}>Files Received</div>
                </div>
                <div className="received-summary-card">
                  <div style={{ fontSize: '28px', fontWeight: 700, color: '#68d391' }}>
                    {receivedFiles.reduce((s, f) => s + (f.addresses_extracted || 0), 0)}
                  </div>
                  <div style={{ fontSize: '12px', color: '#a1a1aa', marginTop: '4px' }}>Addresses Extracted</div>
                </div>
                <div className="received-summary-card">
                  <div style={{ fontSize: '28px', fontWeight: 700, color: '#fbbf24' }}>{receivedEmails.length}</div>
                  <div style={{ fontSize: '12px', color: '#a1a1aa', marginTop: '4px' }}>Reply Emails Logged</div>
                </div>
                <div className="received-summary-card">
                  <div style={{ fontSize: '13px', fontWeight: 600, color: '#a1a1aa' }}>Auto-checks every</div>
                  <div style={{ fontSize: '22px', fontWeight: 700, color: '#667eea' }}>15 min</div>
                </div>
              </div>

              {/* Files table */}
              {receivedFiles.length > 0 ? (
                <>
                  <h3 style={{ margin: '24px 0 14px', fontSize: '15px', color: '#a1a1aa' }}>Received Files</h3>
                  <div className="table-container">
                    <table>
                      <thead>
                        <tr>
                          <th>County</th>
                          <th>State</th>
                          <th>Filename</th>
                          <th>Type</th>
                          <th>Size</th>
                          <th>Addresses Extracted</th>
                          <th>Status</th>
                          <th>Received At</th>
                        </tr>
                      </thead>
                      <tbody>
                        {receivedFiles.map(f => (
                          <tr key={f.id}>
                            <td><strong>{f.county_name}</strong></td>
                            <td><span className="state-badge">{f.state}</span></td>
                            <td style={{ fontSize: '13px' }}>{f.filename}</td>
                            <td><span className="state-badge">{f.file_type?.toUpperCase()}</span></td>
                            <td style={{ fontSize: '13px' }}>{f.file_size_kb || 0} KB</td>
                            <td style={{ fontWeight: 700, color: '#68d391' }}>{f.addresses_extracted || 0}</td>
                            <td>
                              <span className={`badge ${f.processing_status === 'processed' ? 'badge-active' : f.processing_status === 'empty' ? 'badge-inactive' : 'badge-pending'}`}>
                                {f.processing_status === 'processed' ? <CheckCircle /> : f.processing_status === 'empty' ? <XCircle /> : <Clock />}
                                {f.processing_status}
                              </span>
                            </td>
                            <td style={{ fontSize: '13px' }}>{fmt(f.received_at)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              ) : (
                <div className="empty-state" style={{ paddingTop: '40px' }}>
                  <div className="empty-state-icon">📥</div>
                  <h3>No files received yet</h3>
                  <p>When counties reply with CSV/Excel attachments,<br />they'll be automatically parsed and shown here.</p>
                  <div style={{ marginTop: '30px' }}>
                    <p style={{ fontSize: '13px', color: '#a1a1aa', marginBottom: '12px' }}>Counties awaiting reply:</p>
                    <div className="received-status-grid">
                      {counties.filter(c => c.status === 'active' && c.last_request_sent).map(c => {
                        const days = daysSince(c.last_request_sent);
                        return (
                          <div key={c.id} className="received-county-card">
                            <div style={{ fontWeight: 600, fontSize: '14px' }}>{c.county_name}, {c.state}</div>
                            <div style={{ fontSize: '12px', color: '#a1a1aa', marginTop: '4px' }}>Emailed {days}d ago</div>
                            <div style={{ marginTop: '8px' }}>
                              <span className="badge badge-pending"><Clock /> Awaiting reply</span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* Modal */}
      {modalOpen && (
        <div className="modal-overlay" onClick={() => setModalOpen(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingCounty ? 'Edit County' : 'Add New County'}</h2>
              <button className="modal-close" onClick={() => setModalOpen(false)}>&times;</button>
            </div>
            <div className="modal-body">
              <form onSubmit={handleSubmit}>
                <div className="form-grid">
                  <div className="form-group">
                    <label>County Name *</label>
                    <input type="text" value={formData.county_name} onChange={e => setFormData({ ...formData, county_name: e.target.value })} placeholder="e.g., Miami-Dade" required />
                  </div>
                  <div className="form-group">
                    <label>State *</label>
                    <input type="text" value={formData.state} onChange={e => setFormData({ ...formData, state: e.target.value })} placeholder="e.g., FL" required />
                  </div>
                  <div className="form-group">
                    <label>Clerk Email</label>
                    <input type="email" value={formData.email} onChange={e => setFormData({ ...formData, email: e.target.value })} placeholder="clerk@county.gov" />
                  </div>
                  <div className="form-group">
                    <label>Phone</label>
                    <input type="tel" value={formData.phone} onChange={e => setFormData({ ...formData, phone: e.target.value })} placeholder="(555) 123-4567" />
                  </div>
                  <div className="form-group">
                    <label>Contact Person</label>
                    <input type="text" value={formData.contact_person} onChange={e => setFormData({ ...formData, contact_person: e.target.value })} placeholder="John Doe" />
                  </div>
                  <div className="form-group">
                    <label>Status</label>
                    <select value={formData.status} onChange={e => setFormData({ ...formData, status: e.target.value })}>
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  </div>
                  <div className="form-group full-width">
                    <label>Notes</label>
                    <textarea value={formData.notes} onChange={e => setFormData({ ...formData, notes: e.target.value })} placeholder="Additional info..." />
                  </div>
                </div>
                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setModalOpen(false)}>Cancel</button>
                  <button type="submit" className="btn">{editingCounty ? 'Update County' : 'Add County'}</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
