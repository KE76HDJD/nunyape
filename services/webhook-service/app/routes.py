from fastapi import APIRouter, HTTPException, Request, Header, BackgroundTasks
from typing import Optional, Dict, Any
import logging
from .models import (
    WebhookEvent, 
    WebhookResponse, 
    WebhookProvider,
    WebhookStats,
    WebhookFilter
)
from .handlers.stripe_handler import StripeHandler
from .handlers.paypal_handler import PayPalHandler
from .handlers.min_handler import MinHandler
from .signature_validator import SignatureValidator

router = APIRouter()
logger = logging.getLogger('webhook-service')

# Initialize handlers
stripe_handler = StripeHandler(webhook_secret="your_stripe_webhook_secret")
paypal_handler = PayPalHandler(
    client_id="your_paypal_client_id",
    client_secret="your_paypal_client_secret", 
    webhook_id="your_paypal_webhook_id"
)
min_handler = MinHandler(secret_key="your_min_secret_key")

@router.post("/webhooks/stripe", response_model=WebhookResponse)
async def handle_stripe_webhook(
    background_tasks: BackgroundTasks,
    request: Request,
    stripe_signature: Optional[str] = Header(None)
):
    """
    Handle incoming webhooks from Stripe
    """
    try:
        # Get raw payload
        body = await request.body()
        payload = await request.json()
        
        if not stripe_signature:
            raise HTTPException(status_code=400, detail="Missing Stripe signature")
        
        # Process webhook in background
        background_tasks.add_task(
            process_stripe_webhook,
            payload,
            stripe_signature
        )
        
        return WebhookResponse(
            status="accepted",
            message="Webhook received and queued for processing",
            processed=False
        )
        
    except Exception as e:
        logger.error(f"Error handling Stripe webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/webhooks/paypal", response_model=WebhookResponse)
async def handle_paypal_webhook(
    background_tasks: BackgroundTasks,
    request: Request
):
    """
    Handle incoming webhooks from PayPal
    """
    try:
        payload = await request.json()
        headers = dict(request.headers)
        
        # Process webhook in background
        background_tasks.add_task(
            process_paypal_webhook,
            payload,
            headers
        )
        
        return WebhookResponse(
            status="accepted", 
            message="Webhook received and queued for processing",
            processed=False
        )
        
    except Exception as e:
        logger.error(f"Error handling PayPal webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/webhooks/min", response_model=WebhookResponse)
async def handle_min_webhook(
    background_tasks: BackgroundTasks,
    request: Request,
    min_signature: Optional[str] = Header(None)
):
    """
    Handle incoming webhooks from MIN (Merchant Integration Network)
    """
    try:
        payload = await request.json()
        
        if not min_signature:
            raise HTTPException(status_code=400, detail="Missing MIN signature")
        
        # Process webhook in background
        background_tasks.add_task(
            process_min_webhook,
            payload,
            min_signature
        )
        
        return WebhookResponse(
            status="accepted",
            message="Webhook received and queued for processing", 
            processed=False
        )
        
    except Exception as e:
        logger.error(f"Error handling MIN webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/webhooks/custom/{provider}", response_model=WebhookResponse)
async def handle_custom_webhook(
    provider: str,
    background_tasks: BackgroundTasks, 
    request: Request,
    signature: Optional[str] = Header(None)
):
    """
    Handle incoming webhooks from custom providers
    """
    try:
        payload = await request.json()
        headers = dict(request.headers)
        
        # Validate custom provider
        if provider not in ["shopify", "quickbooks", "xero"]:
            raise HTTPException(status_code=400, detail="Unsupported custom provider")
        
        # Process webhook in background
        background_tasks.add_task(
            process_custom_webhook,
            provider,
            payload,
            headers,
            signature
        )
        
        return WebhookResponse(
            status="accepted",
            message="Webhook received and queued for processing",
            processed=False
        )
        
    except Exception as e:
        logger.error(f"Error handling custom webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/webhooks/events", response_model=Dict[str, Any])
async def get_webhook_events(filter: WebhookFilter):
    """
    Retrieve webhook events with filtering
    """
    try:
        # This would typically query a database
        # For now, return mock data
        events = [
            {
                "id": "wh_123",
                "provider": "stripe",
                "event_type": "payment_intent.succeeded", 
                "status": "processed",
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
        
        return {
            "events": events,
            "total": len(events),
            "filter": filter.dict()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving webhook events: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/webhooks/stats", response_model=WebhookStats)
async def get_webhook_stats():
    """
    Get webhook processing statistics
    """
    try:
        # This would typically aggregate from database
        # For now, return mock data
        return WebhookStats(
            total_received=1000,
            total_processed=950,
            total_failed=50,
            total_retried=25,
            by_provider={
                "stripe": 600,
                "paypal": 300,
                "min": 100
            },
            by_event_type={
                "payment_intent.succeeded": 400,
                "invoice.payment_succeeded": 200,
                "charge.refunded": 50
            },
            success_rate=0.95,
            period_start="2024-01-01T00:00:00Z",
            period_end="2024-01-31T23:59:59Z"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving webhook stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/webhooks/retry/{webhook_id}")
async def retry_webhook(webhook_id: str):
    """
    Retry a failed webhook processing
    """
    try:
        # This would retrieve the webhook from database and retry processing
        logger.info(f"Retrying webhook: {webhook_id}")
        
        return {
            "status": "success",
            "message": f"Webhook {webhook_id} queued for retry"
        }
        
    except Exception as e:
        logger.error(f"Error retrying webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Background task functions
async def process_stripe_webhook(payload: Dict[str, Any], signature: str):
    """Process Stripe webhook in background"""
    try:
        result = await stripe_handler.handle_webhook(payload, signature)
        logger.info(f"Stripe webhook processed: {result}")
        
        # Here you would typically save the result to database
        # and trigger any downstream actions
        
    except Exception as e:
        logger.error(f"Background processing failed for Stripe webhook: {e}")

async def process_paypal_webhook(payload: Dict[str, Any], headers: Dict[str, str]):
    """Process PayPal webhook in background"""
    try:
        result = await paypal_handler.handle_webhook(payload, headers)
        logger.info(f"PayPal webhook processed: {result}")
        
    except Exception as e:
        logger.error(f"Background processing failed for PayPal webhook: {e}")

async def process_min_webhook(payload: Dict[str, Any], signature: str):
    """Process MIN webhook in background"""
    try:
        result = await min_handler.handle_webhook(payload, signature)
        logger.info(f"MIN webhook processed: {result}")
        
    except Exception as e:
        logger.error(f"Background processing failed for MIN webhook: {e}")

async def process_custom_webhook(
    provider: str, 
    payload: Dict[str, Any], 
    headers: Dict[str, str],
    signature: Optional[str]
):
    """Process custom webhook in background"""
    try:
        # Custom provider handling logic would go here
        logger.info(f"Custom webhook from {provider} received")
        
        # Validate signature if provided
        if signature:
            validator = SignatureValidator()
            is_valid = await validator.validate_custom_signature(
                provider, payload, signature, headers
            )
            if not is_valid:
                logger.warning(f"Invalid signature for custom webhook from {provider}")
                return
        
        # Process based on provider
        if provider == "shopify":
            await process_shopify_webhook(payload)
        elif provider == "quickbooks":
            await process_quickbooks_webhook(payload)
        elif provider == "xero":
            await process_xero_webhook(payload)
            
    except Exception as e:
        logger.error(f"Background processing failed for custom webhook: {e}")

async def process_shopify_webhook(payload: Dict[str, Any]):
    """Process Shopify webhook"""
    logger.info("Processing Shopify webhook")
    # Implementation for Shopify webhooks

async def process_quickbooks_webhook(payload: Dict[str, Any]):
    """Process QuickBooks webhook"""
    logger.info("Processing QuickBooks webhook")
    # Implementation for QuickBooks webhooks

async def process_xero_webhook(payload: Dict[str, Any]):
    """Process Xero webhook"""
    logger.info("Processing Xero webhook")
    # Implementation for Xero webhooks