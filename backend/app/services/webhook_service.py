import aiohttp
import asyncio
from datetime import datetime
from ..models import Webhook, EventType
from ..database import SessionLocal


async def trigger_webhooks(
    event_type: EventType,
    product_data: dict,
    timeout: int = 5
) -> None:
    """
    Trigger all enabled webhooks for a given event type.
    Runs asynchronously without blocking.
    Creates its own database session.
    """
    # Create a new session for async operation
    db = SessionLocal()
    try:
        webhooks = db.query(Webhook).filter(
            Webhook.event_type == event_type,
            Webhook.enabled == True
        ).all()
    finally:
        db.close()
    
    if not webhooks:
        return
    
    async def send_webhook(webhook: Webhook):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook.url,
                    json={
                        "event_type": event_type.value,
                        "product": product_data,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    # Webhook sent (we don't wait for response in production)
                    pass
        except Exception:
            # Silently fail for background webhooks
            pass
    
    # Trigger all webhooks concurrently
    tasks = [send_webhook(webhook) for webhook in webhooks]
    # Create background task - fire and forget
    asyncio.create_task(asyncio.gather(*tasks, return_exceptions=True))


async def test_webhook(webhook: Webhook, timeout: int = 10) -> dict:
    """
    Test a webhook and return response details.
    Used for the test endpoint.
    """
    start_time = datetime.utcnow()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                webhook.url,
                json={
                    "event_type": webhook.event_type.value,
                    "test": True,
                    "timestamp": datetime.utcnow().isoformat()
                },
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                end_time = datetime.utcnow()
                response_time = (end_time - start_time).total_seconds() * 1000
                
                return {
                    "success": True,
                    "status_code": response.status,
                    "response_time_ms": round(response_time, 2)
                }
    except asyncio.TimeoutError:
        return {
            "success": False,
            "error": "Request timeout"
        }
    except Exception as e:
        end_time = datetime.utcnow()
        response_time = (end_time - start_time).total_seconds() * 1000
        
        return {
            "success": False,
            "error": str(e),
            "response_time_ms": round(response_time, 2) if 'response_time' in locals() else None
        }

