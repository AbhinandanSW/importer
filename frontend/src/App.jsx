import { useState } from 'react';
import FileUpload from './components/FileUpload';
import ProductList from './components/ProductList';
import BulkDelete from './components/BulkDelete';
import WebhookManager from './components/WebhookManager';
import './styles/App.css';

function App() {
  const [activeTab, setActiveTab] = useState('upload');
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>CSV Product Importer</h1>
        <nav className="tabs">
          <button
            className={activeTab === 'upload' ? 'active' : ''}
            onClick={() => setActiveTab('upload')}
          >
            Upload CSV
          </button>
          <button
            className={activeTab === 'products' ? 'active' : ''}
            onClick={() => setActiveTab('products')}
          >
            Products
          </button>
          <button
            className={activeTab === 'webhooks' ? 'active' : ''}
            onClick={() => setActiveTab('webhooks')}
          >
            Webhooks
          </button>
        </nav>
      </header>

      <main className="app-main">
        {activeTab === 'upload' && (
          <div className="tab-content">
            <FileUpload onUploadComplete={handleRefresh} />
          </div>
        )}
        {activeTab === 'products' && (
          <div className="tab-content">
            <div className="products-header">
              <h2>Product Management</h2>
              <BulkDelete onDeleteComplete={handleRefresh} />
            </div>
            <ProductList key={refreshKey} />
          </div>
        )}
        {activeTab === 'webhooks' && (
          <div className="tab-content">
            <WebhookManager />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;

