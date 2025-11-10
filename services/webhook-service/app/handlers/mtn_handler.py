import hashlib
import hmac
import json
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger('webhook-min-handler')

class MinHandler:
    """
    Handler for MIN (Merchant Integration Network) webhooks
    """
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.supported_events = {
            'payment.completed': self.handle_payment_completed,
            'payment.failed': self.handle_payment_failed,
            'refund.processed': self.handle_refund_processed,
            'dispute.created': self.handle_dispute_created,
            'subscription.updated': self.handle_subscription_updated
        }
    
    def verify_signature(self, payload: str, signature: str) -> bool:
        """
        Verify MIN webhook signature
        """
        try:
            expected_signature = hmac.new(
                self.secret_key.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    async def handle_webhook(self, payload: Dict[str, Any], signature: str) -> Dict[str, Any]:
        """
        Main webhook handler for MIN events
        """
        try:
            # Verify signature
            if not self.verify_signature(json.dumps(payload), signature):
                logger.warning("Invalid MIN webhook signature")
                return {
                    "status": "error",
                    "message": "Invalid signature",
                    "processed": False
                }
            
            event_type = payload.get('event_type')
            event_handler = self.supported_events.get(event_type)
            
            if not event_handler:
                logger.warning(f"Unsupported MIN event type: {event_type}")
                return {
                    "status": "error", 
                    "message": f"Unsupported event type: {event_type}",
                    "processed": False
                }
            
            # Process the event
            result = await event_handler(payload)
            logger.info(f"Processed MIN webhook event: {event_type}")
            
            return {
                "status": "success",
                "message": "Webhook processed successfully",
                "processed": True,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error processing MIN webhook: {e}")
            return {
                "status": "error",
                "message": f"Processing error: {str(e)}",
                "processed": False
            }
    
    async def handle_payment_completed(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle payment completed event
        """
        event_data = payload.get('data', {})
        
        logger.info(f"Processing MIN payment completed: {event_data.get('payment_id')}")
        
        # Extract payment information
        payment_info = {
            'payment_id': event_data.get('payment_id'),
            'amount': event_data.get('amount'),
            'currency': event_data.get('currency'),
            'customer_id': event_data.get('customer_id'),
            'merchant_reference': event_data.get('merchant_reference'),
            'completed_at': event_data.get('completed_at')
        }
        
        # Here you would typically:
        # 1. Update your database with payment status
        # 2. Trigger fulfillment processes
        # 3. Send confirmation emails
        # 4. Update analytics
        
        # Simulate processing
        await self._update_payment_status(payment_info['payment_id'], 'completed')
        await self._trigger_fulfillment(payment_info)
        
        return {
            "action": "payment_processed",
            "payment_id": payment_info['payment_id'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_payment_failed(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle payment failed event
        """
        event_data = payload.get('data', {})
        
        logger.warning(f"Processing MIN payment failed: {event_data.get('payment_id')}")
        
        payment_info = {
            'payment_id': event_data.get('payment_id'),
            'failure_reason': event_data.get('failure_reason'),
            'error_code': event_data.get('error_code'),
            'failed_at': event_data.get('failed_at')
        }
        
        # Update payment status to failed
        await self._update_payment_status(payment_info['payment_id'], 'failed')
        
        # Notify customer service or trigger retry logic
        await self._notify_payment_failure(payment_info)
        
        return {
            "action": "payment_failed",
            "payment_id": payment_info['payment_id'],
            "reason": payment_info['failure_reason'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_refund_processed(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle refund processed event
        """
        event_data = payload.get('data', {})
        
        logger.info(f"Processing MIN refund processed: {event_data.get('refund_id')}")
        
        refund_info = {
            'refund_id': event_data.get('refund_id'),
            'payment_id': event_data.get('payment_id'),
            'amount': event_data.get('amount'),
            'reason': event_data.get('reason'),
            'processed_at': event_data.get('processed_at')
        }
        
        # Update order/refund status
        await self._update_refund_status(refund_info['refund_id'], 'processed')
        
        return {
            "action": "refund_processed",
            "refund_id": refund_info['refund_id'],
            "payment_id": refund_info['payment_id'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_dispute_created(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle dispute created event
        """
        event_data = payload.get('data', {})
        
        logger.warning(f"Processing MIN dispute created: {event_data.get('dispute_id')}")
        
        dispute_info = {
            'dispute_id': event_data.get('dispute_id'),
            'payment_id': event_data.get('payment_id'),
            'reason': event_data.get('reason'),
            'amount': event_data.get('amount'),
            'created_at': event_data.get('created_at')
        }
        
        # Trigger dispute handling workflow
        await self._handle_dispute(dispute_info)
        
        return {
            "action": "dispute_created",
            "dispute_id": dispute_info['dispute_id'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_subscription_updated(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle subscription updated event
        """
        event_data = payload.get('data', {})
        
        logger.info(f"Processing MIN subscription updated: {event_data.get('subscription_id')}")
        
        subscription_info = {
            'subscription_id': event_data.get('subscription_id'),
            'customer_id': event_data.get('customer_id'),
            'status': event_data.get('status'),
            'current_period_end': event_data.get('current_period_end'),
            'updated_at': event_data.get('updated_at')
        }
        
        # Update subscription in database
        await self._update_subscription(subscription_info)
        
        return {
            "action": "subscription_updated",
            "subscription_id": subscription_info['subscription_id'],
            "new_status": subscription_info['status'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Internal helper methods
    async def _update_payment_status(self, payment_id: str, status: str):
        """Update payment status in database"""
        # Implementation would interact with your database
        logger.info(f"Updating payment {payment_id} status to {status}")
        await asyncio.sleep(0.1)  # Simulate DB operation
    
    async def _trigger_fulfillment(self, payment_info: Dict[str, Any]):
        """Trigger order fulfillment process"""
        logger.info(f"Triggering fulfillment for payment {payment_info['payment_id']}")
        # Implementation would trigger your fulfillment workflow
        await asyncio.sleep(0.1)
    
    async def _notify_payment_failure(self, payment_info: Dict[str, Any]):
        """Notify about payment failure"""
        logger.warning(f"Notifying about payment failure: {payment_info}")
        # Implementation would send notifications
        await asyncio.sleep(0.1)
    
    async def _update_refund_status(self, refund_id: str, status: str):
        """Update refund status in database"""
        logger.info(f"Updating refund {refund_id} status to {status}")
        await asyncio.sleep(0.1)
    
    async def _handle_dispute(self, dispute_info: Dict[str, Any]):
        """Handle dispute creation"""
        logger.warning(f"Handling dispute: {dispute_info}")
        # Implementation would trigger dispute resolution workflow
        await asyncio.sleep(0.1)
    
    async def _update_subscription(self, subscription_info: Dict[str, Any]):
        """Update subscription information"""
        logger.info(f"Updating subscription: {subscription_info}")
        await asyncio.sleep(0.1)