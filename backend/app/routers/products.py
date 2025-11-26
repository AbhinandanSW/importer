from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional
from ..database import get_db
from ..models import Product
from ..schemas import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from ..services.webhook_service import trigger_webhooks
from ..models import EventType
import asyncio

router = APIRouter()


@router.get("", response_model=ProductListResponse)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    sku: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List products with filtering and pagination"""
    query = db.query(Product)
    
    # Apply filters
    if sku:
        query = query.filter(func.lower(Product.sku).contains(sku.lower()))
    if name:
        query = query.filter(func.lower(Product.name).contains(name.lower()))
    if description:
        query = query.filter(func.lower(Product.description).contains(description.lower()))
    if active is not None:
        query = query.filter(Product.active == active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    products = query.order_by(Product.id).offset(offset).limit(page_size).all()
    
    total_pages = (total + page_size - 1) // page_size
    
    return ProductListResponse(
        items=products,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a single product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    # Check for duplicate SKU (case-insensitive)
    existing = db.query(Product).filter(
        func.lower(Product.sku) == product.sku.lower()
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Product with SKU '{product.sku}' already exists"
        )
    
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Trigger webhook asynchronously
    product_data = {
        "id": db_product.id,
        "sku": db_product.sku,
        "name": db_product.name,
        "description": db_product.description,
        "active": db_product.active
    }
    asyncio.create_task(trigger_webhooks(EventType.product_created, product_data))
    
    return db_product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Update a product"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check SKU uniqueness if updating SKU
    if product_update.sku and product_update.sku.lower() != db_product.sku.lower():
        existing = db.query(Product).filter(
            func.lower(Product.sku) == product_update.sku.lower(),
            Product.id != product_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Product with SKU '{product_update.sku}' already exists"
            )
    
    # Update fields
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    
    # Trigger webhook asynchronously
    product_data = {
        "id": db_product.id,
        "sku": db_product.sku,
        "name": db_product.name,
        "description": db_product.description,
        "active": db_product.active
    }
    asyncio.create_task(trigger_webhooks(EventType.product_updated, product_data))
    
    return db_product


@router.delete("/bulk", status_code=204)
def bulk_delete_products(db: Session = Depends(get_db)):
    """Delete all products"""
    db.query(Product).delete()
    db.commit()
    return None


@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Store product data for webhook before deletion
    product_data = {
        "id": db_product.id,
        "sku": db_product.sku,
        "name": db_product.name,
        "description": db_product.description,
        "active": db_product.active
    }
    
    db.delete(db_product)
    db.commit()
    
    # Trigger webhook asynchronously
    asyncio.create_task(trigger_webhooks(EventType.product_deleted, product_data))
    
    return None

