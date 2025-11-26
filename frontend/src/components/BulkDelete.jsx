import { useState } from 'react';
import { productsAPI } from '../services/api';

function BulkDelete({ onDeleteComplete }) {
  const [showConfirm, setShowConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [notification, setNotification] = useState(null);

  const showNotif = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await productsAPI.bulkDelete();
      showNotif('All products deleted successfully');
      setShowConfirm(false);
      if (onDeleteComplete) {
        onDeleteComplete();
      }
    } catch (error) {
      showNotif('Failed to delete products', 'error');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="bulk-delete-container">
      <button
        className="btn btn-danger"
        onClick={() => setShowConfirm(true)}
        disabled={deleting}
      >
        Delete All Products
      </button>

      {showConfirm && (
        <div className="modal-overlay" onClick={() => !deleting && setShowConfirm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Confirm Bulk Delete</h3>
              <button
                className="modal-close"
                onClick={() => setShowConfirm(false)}
                disabled={deleting}
              >
                ×
              </button>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <p style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>
                Are you sure you want to delete ALL products?
              </p>
              <p style={{ color: '#e74c3c', fontWeight: 'bold' }}>
                This action cannot be undone.
              </p>
            </div>

            <div className="form-actions">
              <button
                className="btn"
                onClick={() => setShowConfirm(false)}
                disabled={deleting}
                style={{ backgroundColor: '#95a5a6', color: 'white' }}
              >
                Cancel
              </button>
              <button
                className="btn btn-danger"
                onClick={handleDelete}
                disabled={deleting}
              >
                {deleting ? 'Deleting...' : 'Delete All'}
              </button>
            </div>
          </div>
        </div>
      )}

      {notification && (
        <div className={`notification ${notification.type}`}>
          {notification.message}
        </div>
      )}
    </div>
  );
}

export default BulkDelete;

