import React, { useState, useEffect } from 'react';

// Use environment variable for API URL (works in both dev and production)
const API_URL = import.meta.env.VITE_API_URL || '/api';

// Icons as simple SVG components
const Building2 = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/>
    <path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/>
    <path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/>
    <path d="M10 6h4"/>
    <path d="M10 10h4"/>
    <path d="M10 14h4"/>
    <path d="M10 18h4"/>
  </svg>
);

const CheckCircle = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <path d="m9 12 2 2 4-4"/>
  </svg>
);

const XCircle = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <path d="m15 9-6 6"/>
    <path d="m9 9 6 6"/>
  </svg>
);

const Plus = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M5 12h14"/>
    <path d="M12 5v14"/>
  </svg>
);

const Pencil = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/>
    <path d="m15 5 4 4"/>
  </svg>
);

const Trash2 = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 6h18"/>
    <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/>
    <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
  </svg>
);

const Calendar = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="18" height="18" x="3" y="4" rx="2" ry="2"/>
    <line x1="16" x2="16" y1="2" y2="6"/>
    <line x1="8" x2="8" y1="2" y2="6"/>
    <line x1="3" x2="21" y1="10" y2="10"/>
  </svg>
);

const Mail = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="20" height="16" x="2" y="4" rx="2"/>
    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
  </svg>
);

const Users = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
    <circle cx="9" cy="7" r="4"/>
    <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
  </svg>
);

const Clock = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <polyline points="12 6 12 12 16 14"/>
  </svg>
);

function App() {
  const [counties, setCounties] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingCounty, setEditingCounty] = useState(null);
  const [formData, setFormData] = useState({
    county_name: '',
    state: '',
    phone: '',
    email: '',
    contact_person: '',
    status: 'active',
    notes: ''
  });

  useEffect(() => {
    loadCounties();
    loadStats();
  }, []);

  const loadCounties = async () => {
    try {
      const response = await fetch(`${API_URL}/counties`);
      const data = await response.json();
      setCounties(data);
    } catch (error) {
      console.error('Error loading counties:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch(`${API_URL}/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const openAddModal = () => {
    setEditingCounty(null);
    setFormData({
      county_name: '',
      state: '',
      phone: '',
      email: '',
      contact_person: '',
      status: 'active',
      notes: ''
    });
    setModalOpen(true);
  };

  const openEditModal = async (id) => {
    try {
      const response = await fetch(`${API_URL}/counties/${id}`);
      const county = await response.json();
      setEditingCounty(county);
      setFormData({
        county_name: county.county_name,
        state: county.state,
        phone: county.phone || '',
        email: county.email || '',
        contact_person: county.contact_person || '',
        status: county.status,
        notes: county.notes || ''
      });
      setModalOpen(true);
    } catch (error) {
      console.error('Error loading county:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log('🚀 Form submitted!', formData);

    try {
      const url = editingCounty
        ? `${API_URL}/counties/${editingCounty.id}`
        : `${API_URL}/counties`;
      const method = editingCounty ? 'PUT' : 'POST';

      console.log(`📡 Sending ${method} request to:`, url);
      console.log('📦 Request body:', formData);

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      console.log('📨 Response status:', response.status, response.statusText);

      if (response.ok) {
        console.log('✅ County saved successfully!');
        setModalOpen(false);
        loadCounties();
        loadStats();
      } else {
        const error = await response.json();
        console.error('❌ Server error:', error);
        alert('Error: ' + (error.detail || 'Failed to save'));
      }
    } catch (error) {
      console.error('❌ Request failed:', error);
      alert('Error saving county: ' + error.message);
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete "${name}"?`)) return;

    try {
      const response = await fetch(`${API_URL}/counties/${id}`, { method: 'DELETE' });
      if (response.ok) {
        loadCounties();
        loadStats();
      }
    } catch (error) {
      alert('Error deleting county');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatNextSchedule = (dateString) => {
    if (!dateString) return '--';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="container">
      {/* Header */}
      <div className="header">
        <div>
          <h1>County Pre-Foreclosure System</h1>
          <p>Manage county contacts and automate pre-foreclosure data collection</p>
        </div>
        <div style={{ color: '#68d391', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle />
          <span style={{ fontSize: '14px' }}>System Online</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Total Counties</h3>
            <Building2 />
          </div>
          <div className="number">{stats?.total_counties || 0}</div>
        </div>

        <div className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Active Counties</h3>
            <Users />
          </div>
          <div className="number" style={{ color: '#68d391' }}>{stats?.active_counties || 0}</div>
        </div>

        <div className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Inactive Counties</h3>
            <Users />
          </div>
          <div className="number" style={{ color: '#fc8181' }}>{stats?.inactive_counties || 0}</div>
        </div>

        <div className="stat-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>Next Email Schedule</h3>
            <Clock />
          </div>
          <div className="number" style={{ fontSize: '18px' }}>
            {stats ? formatNextSchedule(stats.next_email_schedule) : '--'}
          </div>
          <div className="subtitle">Monday & Thursday at 9 AM</div>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="section-header">
          <h2>County List</h2>
          <button className="btn" onClick={openAddModal}>
            <Plus /> Add New County
          </button>
        </div>

        <div className="table-container">
          {loading ? (
            <div className="loading">
              <div className="spinner"></div>
              <p>Loading counties...</p>
            </div>
          ) : counties.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📭</div>
              <h3>No counties added yet</h3>
              <p>Click "Add New County" to get started</p>
            </div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>County Name</th>
                  <th>State</th>
                  <th>Contact</th>
                  <th>Email</th>
                  <th>Status</th>
                  <th>Last Request Sent</th>
                  <th>Next Schedule</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {counties.map((county) => (
                  <tr key={county.id}>
                    <td><strong>{county.county_name}</strong></td>
                    <td>{county.state}</td>
                    <td>
                      {county.contact_person || '-'}
                      <br />
                      <small style={{ color: '#a1a1aa' }}>{county.phone || ''}</small>
                    </td>
                    <td>{county.email || '-'}</td>
                    <td>
                      <span className={`badge ${county.status === 'active' ? 'badge-active' : 'badge-inactive'}`}>
                        {county.status === 'active' ? <CheckCircle /> : <XCircle />}
                        {county.status}
                      </span>
                    </td>
                    <td>{formatDate(county.last_request_sent)}</td>
                    <td>{formatDate(county.next_scheduled_email)}</td>
                    <td>
                      <div className="actions">
                        <button className="btn btn-success btn-small" onClick={() => openEditModal(county.id)}>
                          <Pencil /> Edit
                        </button>
                        <button className="btn btn-danger btn-small" onClick={() => handleDelete(county.id, county.county_name)}>
                          <Trash2 /> Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Modal */}
      {modalOpen && (
        <div className="modal-overlay" onClick={() => setModalOpen(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingCounty ? 'Edit County' : 'Add New County'}</h2>
              <button className="modal-close" onClick={() => setModalOpen(false)}>&times;</button>
            </div>
            <div className="modal-body">
              <form onSubmit={handleSubmit}>
                <div className="form-grid">
                  <div className="form-group">
                    <label>County Name *</label>
                    <input
                      type="text"
                      value={formData.county_name}
                      onChange={(e) => setFormData({ ...formData, county_name: e.target.value })}
                      placeholder="e.g., Los Angeles County"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label>State *</label>
                    <input
                      type="text"
                      value={formData.state}
                      onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                      placeholder="e.g., California"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label>Phone</label>
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      placeholder="(555) 123-4567"
                    />
                  </div>

                  <div className="form-group">
                    <label>Email</label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      placeholder="clerk@county.gov"
                    />
                  </div>

                  <div className="form-group">
                    <label>Contact Person</label>
                    <input
                      type="text"
                      value={formData.contact_person}
                      onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })}
                      placeholder="John Doe"
                    />
                  </div>

                  <div className="form-group">
                    <label>Status *</label>
                    <select
                      value={formData.status}
                      onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    >
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  </div>

                  <div className="form-group full-width">
                    <label>Notes</label>
                    <textarea
                      value={formData.notes}
                      onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                      placeholder="Additional information..."
                    />
                  </div>
                </div>

                <div className="modal-footer">
                  <button type="button" className="btn btn-secondary" onClick={() => setModalOpen(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn">
                    {editingCounty ? 'Update County' : 'Add County'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;