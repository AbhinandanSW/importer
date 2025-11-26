from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .models import EventType


class ProductBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class WebhookBase(BaseModel):
    url: str
    event_type: EventType
    enabled: bool = True


class WebhookCreate(WebhookBase):
    pass


class WebhookUpdate(BaseModel):
    url: Optional[str] = None
    event_type: Optional[EventType] = None
    enabled: Optional[bool] = None


class WebhookResponse(WebhookBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UploadResponse(BaseModel):
    job_id: str
    message: str


class ProgressResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    message: str
    total_records: Optional[int] = None
    processed_records: Optional[int] = None


class WebhookTestResponse(BaseModel):
    success: bool
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    error: Optional[str] = None

