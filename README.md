# CSV Product Importer Application

A full-stack web application for importing and managing products from CSV files. Built with FastAPI (Python 3.13) and React.

## Features

- **CSV Upload**: Upload CSV files with up to 500,000 products
- **Real-time Progress**: Track upload progress with Server-Sent Events (SSE)
- **Product Management**: View, create, update, and delete products
- **Filtering & Pagination**: Filter products by SKU, name, description, and active status
- **Bulk Operations**: Delete all products with confirmation
- **Webhook Configuration**: Configure webhooks for product events (create, update, delete)
- **Case-insensitive SKU**: Automatic duplicate detection and overwrite based on SKU

## Project Structure

```
importer/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routers/
│   │   └── services/
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── styles/
│   └── package.json
└── README.md
```

## Prerequisites

- Python 3.13
- Node.js 18+ and npm

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment (optional but recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the backend server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

### CSV Format

The CSV file should have the following columns:
- `sku` (required): Product SKU (case-insensitive, must be unique)
- `name` (required): Product name
- `description` (optional): Product description

Example CSV:
```csv
sku,name,description
ABC123,Product 1,Description 1
XYZ789,Product 2,Description 2
```

### Uploading CSV Files

1. Navigate to the "Upload CSV" tab
2. Drag and drop a CSV file or click to browse
3. Click "Upload CSV"
4. Monitor progress in real-time

### Managing Products

1. Navigate to the "Products" tab
2. Use filters to search for products
3. Click "Add Product" to create a new product
4. Click "Edit" to modify a product
5. Click "Delete" to remove a product
6. Use "Delete All Products" to bulk delete (with confirmation)

### Configuring Webhooks

1. Navigate to the "Webhooks" tab
2. Click "Add Webhook"
3. Enter the webhook URL and select event type
4. Enable/disable webhooks using the toggle
5. Test webhooks using the "Test" button

## API Endpoints

### Products
- `GET /api/products` - List products (with filtering and pagination)
- `GET /api/products/{id}` - Get product by ID
- `POST /api/products` - Create product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product
- `DELETE /api/products/bulk` - Delete all products

### Upload
- `POST /api/upload` - Upload CSV file
- `GET /api/upload/progress/{job_id}` - Get upload progress (SSE)

### Webhooks
- `GET /api/webhooks` - List webhooks
- `POST /api/webhooks` - Create webhook
- `PUT /api/webhooks/{id}` - Update webhook
- `DELETE /api/webhooks/{id}` - Delete webhook
- `POST /api/webhooks/{id}/test` - Test webhook

## Database

The application uses SQLite database stored in `products.db` file in the backend directory. The database is automatically created on first run.

## Performance

- CSV processing uses streaming parser to handle large files efficiently
- Batch inserts (1000 records per batch) for optimal performance
- Progress tracking updates every 500ms
- Webhooks are triggered asynchronously without blocking

## Deployment on Render

### Backend Deployment

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure the service:
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.13

4. Add environment variable (optional):
   - `RENDER_SERVICE_URL`: Your Render service URL (for keep-alive)
   - `SERVER_URL`: Alternative to RENDER_SERVICE_URL

### Preventing Server Spin-Down

Render's free tier spins down inactive servers after 15 minutes. To prevent this:

**Option 1: Use the built-in keep-alive (recommended)**
- The app includes a background task that pings `/health` every 10 minutes
- Set the `RENDER_SERVICE_URL` environment variable to your service URL
- Example: `RENDER_SERVICE_URL=https://your-app.onrender.com`

**Option 2: Use external monitoring service**
- Use a free service like [UptimeRobot](https://uptimerobot.com/) or [cron-job.org](https://cron-job.org/)
- Set up a monitor to ping `https://your-app.onrender.com/health` every 10-14 minutes
- This keeps your server active without using server resources

**Option 3: Configure Render Health Check**
- In Render dashboard, go to your service settings
- Set Health Check Path to `/health`
- Render will ping this endpoint periodically

### Frontend Deployment

1. Create a new Static Site on Render
2. Connect your GitHub repository
3. Configure:
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
4. Update API URL in `frontend/src/services/api.js` to point to your backend URL

## Notes

- SKU matching is case-insensitive
- Duplicate SKUs in CSV will overwrite existing products
- Webhooks are triggered for product create, update, and delete events
- The application does not require authentication (as per requirements)
- Health check endpoint available at `/health` for monitoring

