from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..database import get_db, SessionLocal
from ..schemas import UploadResponse, ProgressResponse
from ..services.csv_processor import process_csv_file, get_progress, create_job_id
import asyncio
import json

router = APIRouter()


def process_csv_in_thread(content: bytes, job_id: str):
    """Process CSV in a separate thread with its own database session"""
    db = SessionLocal()
    try:
        process_csv_file(content, db, job_id)
    finally:
        db.close()


@router.post("", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    # Read file content
    content = await file.read()
    
    # Create job ID
    job_id = create_job_id()
    
    # Process file in background thread
    try:
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        loop.run_in_executor(
            None,
            process_csv_in_thread,
            content,
            job_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    
    return UploadResponse(job_id=job_id, message="File upload started")


@router.get("/progress/{job_id}")
async def get_upload_progress(job_id: str):
    """SSE endpoint for upload progress"""
    
    async def event_generator():
        while True:
            progress_data = get_progress(job_id)
            
            if not progress_data:
                yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
                break
            
            response = ProgressResponse(
                job_id=job_id,
                status=progress_data["status"],
                progress=progress_data["progress"],
                message=progress_data["message"],
                total_records=progress_data.get("total_records"),
                processed_records=progress_data.get("processed_records")
            )
            
            yield f"data: {json.dumps(response.dict())}\n\n"
            
            # Stop if complete or error
            if progress_data["status"] in ["complete", "error"]:
                break
            
            await asyncio.sleep(0.5)  # Update every 500ms
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

