import { useState, useRef } from 'react';
import { uploadAPI } from '../services/api';

function FileUpload({ onUploadComplete }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.type === 'text/csv') {
      setFile(selectedFile);
      setError(null);
      setSuccess(false);
    } else {
      setError('Please select a valid CSV file');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileSelect(droppedFile);
    }
  };

  const handleFileInputChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      handleFileSelect(selectedFile);
    }
  };

  const connectToProgressStream = (jobId) => {
    const progressUrl = uploadAPI.getProgress(jobId);
    const eventSource = new EventSource(progressUrl);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setProgress(data.progress || 0);
        setStatus(data.message || '');

        if (data.status === 'complete') {
          setSuccess(true);
          setUploading(false);
          eventSource.close();
          if (onUploadComplete) {
            onUploadComplete();
          }
        } else if (data.status === 'error') {
          setError(data.message || 'Upload failed');
          setUploading(false);
          eventSource.close();
        }
      } catch (e) {
        // Ignore parse errors
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      eventSource.close();
      // Don't set error here as the upload might still be processing
    };
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(false);
    setProgress(0);
    setStatus('Uploading file...');

    try {
      const response = await uploadAPI.upload(file);
      const { job_id } = response.data;

      setStatus('Processing CSV...');
      connectToProgressStream(job_id);
    } catch (error) {
      setError(error.response?.data?.detail || 'Upload failed. Please try again.');
      setUploading(false);
    }
  };

  const handleRetry = () => {
    setError(null);
    setSuccess(false);
    setProgress(0);
    setStatus('');
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload CSV File</h2>
      <p style={{ marginBottom: '1.5rem', color: '#555' }}>
        Upload a CSV file with up to 500,000 products. Duplicate SKUs will be overwritten.
      </p>

      <div
        className={`upload-area ${isDragging ? 'dragover' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileInputChange}
          disabled={uploading}
        />
        {file ? (
          <div>
            <p style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>Selected file:</p>
            <p style={{ fontWeight: 'bold', color: '#3498db' }}>{file.name}</p>
            <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
        ) : (
          <div>
            <p style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>
              Drag and drop a CSV file here
            </p>
            <p style={{ color: '#666' }}>or click to browse</p>
          </div>
        )}
      </div>

      <button
        className="upload-button"
        onClick={handleUpload}
        disabled={!file || uploading}
      >
        {uploading ? 'Uploading...' : 'Upload CSV'}
      </button>

      {(uploading || progress > 0) && (
        <div className="progress-container">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progress}%` }}
            >
              {progress > 0 && `${Math.round(progress)}%`}
            </div>
          </div>
          {status && <div className="progress-status">{status}</div>}
        </div>
      )}

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
          <button
            className="btn btn-primary"
            onClick={handleRetry}
            style={{ marginTop: '0.5rem', display: 'block' }}
          >
            Retry
          </button>
        </div>
      )}

      {success && (
        <div className="success-message">
          <strong>Success!</strong> File uploaded and processed successfully.
        </div>
      )}
    </div>
  );
}

export default FileUpload;

