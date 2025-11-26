import { useState, useEffect } from 'react';
import { webhooksAPI } from '../services/api';

function WebhookManager() {
  const [webhooks, setWebhooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingWebhook, setEditingWebhook] = useState(null);
  const [testingWebhook, setTestingWebhook] = useState(null);
  const [notification, setNotification] = useState(null);

  const showNotif = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  const fetchWebhooks = async () => {
    setLoading(true);
    try {
      const response = await webhooksAPI.list();
      setWebhooks(response.data);
    } catch (error) {
      showNotif('Failed to load webhooks', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWebhooks();
  }, []);

  const handleEdit = (webhook) => {
    setEditingWebhook(webhook);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this webhook?')) {
      return;
    }

    try {
      await webhooksAPI.delete(id);
      showNotif('Webhook deleted successfully');
      fetchWebhooks();
    } catch (error) {
      showNotif('Failed to delete webhook', 'error');
    }
  };

  const handleToggle = async (webhook) => {
    try {
      await webhooksAPI.update(webhook.id, { enabled: !webhook.enabled });
      showNotif('Webhook updated successfully');
      fetchWebhooks();
    } catch (error) {
      showNotif('Failed to update webhook', 'error');
    }
  };

  const handleTest = async (webhook) => {
    setTestingWebhook(webhook.id);
    try {
      const response = await webhooksAPI.test(webhook.id);
      const result = response.data;
      
      if (result.success) {
        showNotif(
          `Test successful! Status: ${result.status_code}, Time: ${result.response_time_ms}ms`,
          'success'
        );
      } else {
        showNotif(`Test failed: ${result.error}`, 'error');
      }
    } catch (error) {
      showNotif('Failed to test webhook', 'error');
    } finally {
      setTestingWebhook(null);
    }
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingWebhook(null);
  };

  const handleFormSuccess = () => {
    handleFormClose();
    showNotif(
      editingWebhook ? 'Webhook updated successfully' : 'Webhook created successfully'
    );
    fetchWebhooks();
  };

  return (
    <div>
      <div className="webhooks-header">
        <h2>Webhook Configuration</h2>
        <button className="btn btn-success" onClick={() => setShowForm(true)}>
          + Add Webhook
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>Loading...</div>
      ) : webhooks.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
          No webhooks configured. Click "Add Webhook" to create one.
        </div>
      ) : (
        <table className="webhooks-table">
          <thead>
            <tr>
              <th>URL</th>
              <th>Event Type</th>
              <th>Enabled</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {webhooks.map((webhook) => (
              <tr key={webhook.id}>
                <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {webhook.url}
                </td>
                <td>{webhook.event_type}</td>
                <td>
                  <div className="enabled-toggle">
                    <label className="toggle-switch">
                      <input
                        type="checkbox"
                        checked={webhook.enabled}
                        onChange={() => handleToggle(webhook)}
                      />
                      <span className="toggle-slider"></span>
                    </label>
                    <span>{webhook.enabled ? 'Enabled' : 'Disabled'}</span>
                  </div>
                </td>
                <td>{new Date(webhook.created_at).toLocaleDateString()}</td>
                <td>
                  <div className="action-buttons">
                    <button
                      className="btn btn-primary"
                      onClick={() => handleTest(webhook)}
                      disabled={testingWebhook === webhook.id}
                    >
                      {testingWebhook === webhook.id ? 'Testing...' : 'Test'}
                    </button>
                    <button
                      className="btn btn-primary"
                      onClick={() => handleEdit(webhook)}
                    >
                      Edit
                    </button>
                    <button
                      className="btn btn-danger"
                      onClick={() => handleDelete(webhook.id)}
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {showForm && (
        <WebhookForm
          webhook={editingWebhook}
          onClose={handleFormClose}
          onSuccess={handleFormSuccess}
        />
      )}

      {notification && (
        <div className={`notification ${notification.type}`}>
          {notification.message}
        </div>
      )}
    </div>
  );
}

function WebhookForm({ webhook, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    url: '',
    event_type: 'product_created',
    enabled: true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (webhook) {
      setFormData({
        url: webhook.url,
        event_type: webhook.event_type,
        enabled: webhook.enabled,
      });
    }
  }, [webhook]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (webhook) {
        await webhooksAPI.update(webhook.id, formData);
      } else {
        await webhooksAPI.create(formData);
      }
      onSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save webhook');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{webhook ? 'Edit Webhook' : 'Create Webhook'}</h3>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>URL *</label>
            <input
              type="url"
              name="url"
              value={formData.url}
              onChange={handleChange}
              required
              placeholder="https://example.com/webhook"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>Event Type *</label>
            <select
              name="event_type"
              value={formData.event_type}
              onChange={handleChange}
              required
              disabled={loading}
            >
              <option value="product_created">Product Created</option>
              <option value="product_updated">Product Updated</option>
              <option value="product_deleted">Product Deleted</option>
            </select>
          </div>

          <div className="form-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                name="enabled"
                checked={formData.enabled}
                onChange={handleChange}
                disabled={loading}
              />
              Enabled
            </label>
          </div>

          {error && (
            <div className="error-message" style={{ marginBottom: '1rem' }}>
              {error}
            </div>
          )}

          <div className="form-actions">
            <button
              type="button"
              className="btn"
              onClick={onClose}
              disabled={loading}
              style={{ backgroundColor: '#95a5a6', color: 'white' }}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? 'Saving...' : webhook ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default WebhookManager;

