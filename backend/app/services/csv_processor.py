import csv
import io
import uuid
from typing import Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Product

# In-memory progress tracking
progress_tracker: Dict[str, Dict] = {}


def process_csv_file(file_content: bytes, db: Session, job_id: str) -> None:
    """
    Process CSV file and import products into database.
    Uses streaming parser and batch inserts for performance.
    """
    try:
        # Initialize progress
        progress_tracker[job_id] = {
            "status": "parsing",
            "progress": 0.0,
            "message": "Parsing CSV...",
            "total_records": 0,
            "processed_records": 0
        }

        # Decode file content
        file_text = file_content.decode('utf-8')
        file_io = io.StringIO(file_text)
        
        # Use csv.DictReader for streaming
        reader = csv.DictReader(file_io)
        
        # Validate required columns
        required_columns = {'sku', 'name'}
        if not required_columns.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"CSV must contain columns: {', '.join(required_columns)}")
        
        # Count total records first (for progress calculation)
        file_io.seek(0)
        reader = csv.DictReader(file_io)
        total_records = sum(1 for _ in reader)
        
        progress_tracker[job_id]["total_records"] = total_records
        progress_tracker[job_id]["status"] = "importing"
        progress_tracker[job_id]["message"] = f"Importing {total_records} records..."
        
        # Reset file pointer and process
        file_io.seek(0)
        reader = csv.DictReader(file_io)
        
        batch = []
        batch_size = 1000
        processed = 0
        update_count = 0
        
        for row in reader:
            sku = row.get('sku', '').strip()
            name = row.get('name', '').strip()
            description = row.get('description', '').strip() if row.get('description') else None
            
            if not sku or not name:
                continue  # Skip invalid rows
            
            # Case-insensitive SKU lookup
            existing_product = db.query(Product).filter(
                func.lower(Product.sku) == sku.lower()
            ).first()
            
            if existing_product:
                # Update existing product
                existing_product.name = name
                existing_product.description = description
                existing_product.active = True  # Reactivate if inactive
                update_count += 1
            else:
                # Create new product
                product = Product(
                    sku=sku,
                    name=name,
                    description=description,
                    active=True
                )
                batch.append(product)
            
            processed += 1
            
            # Batch insert and commit periodically
            if len(batch) >= batch_size:
                db.bulk_save_objects(batch)
                db.commit()
                batch = []
                
                # Update progress
                progress = (processed / total_records) * 100
                progress_tracker[job_id]["progress"] = progress
                progress_tracker[job_id]["processed_records"] = processed
                progress_tracker[job_id]["message"] = f"Processed {processed}/{total_records} records..."
            
            # Commit updates periodically
            if update_count > 0 and update_count % batch_size == 0:
                db.commit()
        
        # Insert remaining batch
        if batch:
            db.bulk_save_objects(batch)
            db.commit()
        
        # Final commit for any remaining updates
        db.commit()
        
        # Mark as complete
        progress_tracker[job_id]["status"] = "complete"
        progress_tracker[job_id]["progress"] = 100.0
        progress_tracker[job_id]["processed_records"] = processed
        progress_tracker[job_id]["message"] = f"Import complete! Processed {processed} records."
        
    except Exception as e:
        progress_tracker[job_id]["status"] = "error"
        progress_tracker[job_id]["message"] = f"Error: {str(e)}"
        raise


def get_progress(job_id: str) -> Optional[Dict]:
    """Get progress for a job"""
    return progress_tracker.get(job_id)


def create_job_id() -> str:
    """Create a unique job ID"""
    return str(uuid.uuid4())

