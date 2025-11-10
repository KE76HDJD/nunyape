import hashlib
import hmac
import json
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger('webhook-stripe-handler')

class StripeHandler:
    """
    Handler for Stripe webhooks
    """
    
    def __init__(self, webhook_secret: str):
        self.webhook_secret = webhook_secret
        self.supported_events = {
            'payment_intent.succeeded': self.handle_payment_intent_succeeded,
            'payment_intent.payment_failed': self.handle_payment_intent_failed,
            'charge.succeeded': self.handle_charge_succeeded,
            'charge.failed': self.handle_charge_failed,
            'charge.refunded': self.handle_charge_refunded,
            'customer.subscription.created': self.handle_subscription_created,
            'customer.subscription.updated': self.handle_subscription_updated,
            'customer.subscription.deleted': self.handle_subscription_deleted,
            'invoice.payment_succeeded': self.handle_invoice_payment_succeeded,
            'invoice.payment_failed': self.handle_invoice_payment_failed,
        }
    
    def verify_signature(self, payload: str, signature: str) -> bool:
        """
        Verify Stripe webhook signature
        """
        try:
            # Compute the signature
            computed_signature = hmac.new(
                self.webhook_secret.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(computed_signature, signature)
            
        except Exception as e:
            logger.error(f"Stripe signature verification failed: {e}")
            return False
    
    async def handle_webhook(self, payload: Dict[str, Any], signature: str) -> Dict[str, Any]:
        """
        Main webhook handler for Stripe events
        """
        try:
            # Verify signature
            if not self.verify_signature(json.dumps(payload), signature):
                logger.warning("Invalid Stripe webhook signature")
                return {
                    "status": "error",
                    "message": "Invalid signature",
                    "processed": False
                }
            
            event_type = payload.get('type')
            event_handler = self.supported_events.get(event_type)
            
            if not event_handler:
                logger.warning(f"Unsupported Stripe event type: {event_type}")
                return {
                    "status": "error",
                    "message": f"Unsupported event type: {event_type}",
                    "processed": False
                }
            
            # Process the event
            result = await event_handler(payload)
            logger.info(f"Processed Stripe webhook event: {event_type}")
            
            return {
                "status": "success",
                "message": "Webhook processed successfully",
                "processed": True,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error processing Stripe webhook: {e}")
            return {
                "status": "error",
                "message": f"Processing error: {str(e)}",
                "processed": False
            }
    
    async def handle_payment_intent_succeeded(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle payment intent succeeded event
        """
        data = payload.get('data', {})
        payment_intent = data.get('object', {})
        
        logger.info(f"Processing Stripe payment intent succeeded: {payment_intent.get('id')}")
        
        payment_info = {
            'payment_intent_id': payment_intent.get('id'),
            'amount': payment_intent.get('amount'),
            'currency': payment_intent.get('currency'),
            'customer_id': payment_intent.get('customer'),
            'status': payment_intent.get('status'),
            'metadata': payment_intent.get('metadata', {})
        }
        
        # Update order status
        await self._update_order_status(payment_info['metadata'].get('order_id'), 'paid')
        
        # Trigger fulfillment
        await self._trigger_fulfillment(payment_info)
        
        return {
            "action": "payment_succeeded",
            "payment_intent_id": payment_info['payment_intent_id'],
            "amount": payment_info['amount'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_payment_intent_failed(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle payment intent failed event
        """
        data = payload.get('data', {})
        payment_intent = data.get('object', {})
        
        logger.warning(f"Processing Stripe payment intent failed: {payment_intent.get('id')}")
        
        payment_info = {
            'payment_intent_id': payment_intent.get('id'),
            'failure_message': payment_intent.get('last_payment_error', {}).get('message'),
            'failure_code': payment_intent.get('last_payment_error', {}).get('code'),
            'customer_id': payment_intent.get('customer'),
            'metadata': payment_intent.get('metadata', {})
        }
        
        # Update order status to payment_failed
        await self._update_order_status(payment_info['metadata'].get('order_id'), 'payment_failed')
        
        # Notify customer
        await self._notify_payment_failure(payment_info)
        
        return {
            "action": "payment_failed",
            "payment_intent_id": payment_info['payment_intent_id'],
            "reason": payment_info['failure_message'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_charge_succeeded(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle charge succeeded event
        """
        data = payload.get('data', {})
        charge = data.get('object', {})
        
        logger.info(f"Processing Stripe charge succeeded: {charge.get('id')}")
        
        charge_info = {
            'charge_id': charge.get('id'),
            'amount': charge.get('amount'),
            'currency': charge.get('currency'),
            'customer_id': charge.get('customer'),
            'payment_intent_id': charge.get('payment_intent'),
            'billing_details': charge.get('billing_details', {}),
            'metadata': charge.get('metadata', {})
        }
        
        # Log charge success for analytics
        await self._log_charge_success(charge_info)
        
        return {
            "action": "charge_succeeded",
            "charge_id": charge_info['charge_id'],
            "payment_intent_id": charge_info['payment_intent_id'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_charge_failed(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle charge failed event
        """
        data = payload.get('data', {})
        charge = data.get('object', {})
        
        logger.warning(f"Processing Stripe charge failed: {charge.get('id')}")
        
        charge_info = {
            'charge_id': charge.get('id'),
            'failure_message': charge.get('failure_message'),
            'failure_code': charge.get('failure_code'),
            'customer_id': charge.get('customer'),
            'payment_intent_id': charge.get('payment_intent')
        }
        
        # Log charge failure
        await self._log_charge_failure(charge_info)
        
        return {
            "action": "charge_failed",
            "charge_id": charge_info['charge_id'],
            "reason": charge_info['failure_message'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_charge_refunded(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle charge refunded event
        """
        data = payload.get('data', {})
        charge = data.get('object', {})
        
        logger.info(f"Processing Stripe charge refunded: {charge.get('id')}")
        
        refund_info = {
            'charge_id': charge.get('id'),
            'amount_refunded': charge.get('amount_refunded'),
            'refunds': charge.get('refunds', {}).get('data', []),
            'metadata': charge.get('metadata', {})
        }
        
        # Update order status to refunded
        await self._update_refund_status(refund_info)
        
        return {
            "action": "charge_refunded",
            "charge_id": refund_info['charge_id'],
            "amount_refunded": refund_info['amount_refunded'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_subscription_created(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle subscription created event
        """
        data = payload.get('data', {})
        subscription = data.get('object', {})
        
        logger.info(f"Processing Stripe subscription created: {subscription.get('id')}")
        
        subscription_info = {
            'subscription_id': subscription.get('id'),
            'customer_id': subscription.get('customer'),
            'status': subscription.get('status'),
            'current_period_start': subscription.get('current_period_start'),
            'current_period_end': subscription.get('current_period_end'),
            'items': subscription.get('items', {}).get('data', [])
        }
        
        # Create subscription in system
        await self._create_subscription(subscription_info)
        
        return {
            "action": "subscription_created",
            "subscription_id": subscription_info['subscription_id'],
            "status": subscription_info['status'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_subscription_updated(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle subscription updated event
        """
        data = payload.get('data', {})
        subscription = data.get('object', {})
        
        logger.info(f"Processing Stripe subscription updated: {subscription.get('id')}")
        
        subscription_info = {
            'subscription_id': subscription.get('id'),
            'status': subscription.get('status'),
            'current_period_start': subscription.get('current_period_start'),
            'current_period_end': subscription.get('current_period_end'),
            'cancel_at_period_end': subscription.get('cancel_at_period_end')
        }
        
        # Update subscription in system
        await self._update_subscription(subscription_info)
        
        return {
            "action": "subscription_updated",
            "subscription_id": subscription_info['subscription_id'],
            "new_status": subscription_info['status'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_subscription_deleted(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle subscription deleted event
        """
        data = payload.get('data', {})
        subscription = data.get('object', {})
        
        logger.info(f"Processing Stripe subscription deleted: {subscription.get('id')}")
        
        subscription_info = {
            'subscription_id': subscription.get('id'),
            'status': subscription.get('status'),
            'canceled_at': subscription.get('canceled_at')
        }
        
        # Cancel subscription in system
        await self._cancel_subscription(subscription_info)
        
        return {
            "action": "subscription_deleted",
            "subscription_id": subscription_info['subscription_id'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_invoice_payment_succeeded(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle invoice payment succeeded event
        """
        data = payload.get('data', {})
        invoice = data.get('object', {})
        
        logger.info(f"Processing Stripe invoice payment succeeded: {invoice.get('id')}")
        
        invoice_info = {
            'invoice_id': invoice.get('id'),
            'subscription_id': invoice.get('subscription'),
            'amount_paid': invoice.get('amount_paid'),
            'customer_id': invoice.get('customer'),
            'period_start': invoice.get('period_start'),
            'period_end': invoice.get('period_end')
        }
        
        # Process successful invoice payment
        await self._process_invoice_payment(invoice_info)
        
        return {
            "action": "invoice_payment_succeeded",
            "invoice_id": invoice_info['invoice_id'],
            "subscription_id": invoice_info['subscription_id'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_invoice_payment_failed(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle invoice payment failed event
        """
        data = payload.get('data', {})
        invoice = data.get('object', {})
        
        logger.warning(f"Processing Stripe invoice payment failed: {invoice.get('id')}")
        
        invoice_info = {
            'invoice_id': invoice.get('id'),
            'subscription_id': invoice.get('subscription'),
            'attempt_count': invoice.get('attempt_count'),
            'next_payment_attempt': invoice.get('next_payment_attempt'),
            'customer_id': invoice.get('customer')
        }
        
        # Handle failed invoice payment
        await self._handle_invoice_payment_failure(invoice_info)
        
        return {
            "action": "invoice_payment_failed",
            "invoice_id": invoice_info['invoice_id'],
            "subscription_id": invoice_info['subscription_id'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Internal helper methods
    async def _update_order_status(self, order_id: str, status: str):
        """Update order status in database"""
        logger.info(f"Updating order {order_id} status to {status}")
        await asyncio.sleep(0.1)
    
    async def _trigger_fulfillment(self, payment_info: Dict[str, Any]):
        """Trigger fulfillment process"""
        logger.info(f"Triggering fulfillment for payment {payment_info['payment_intent_id']}")
        await asyncio.sleep(0.1)
    
    async def _notify_payment_failure(self, payment_info: Dict[str, Any]):
        """Notify about payment failure"""
        logger.warning(f"Notifying about payment failure: {payment_info}")
        await asyncio.sleep(0.1)
    
    async def _log_charge_success(self, charge_info: Dict[str, Any]):
        """Log charge success"""
        logger.info(f"Logging charge success: {charge_info['charge_id']}")
        await asyncio.sleep(0.1)
    
    async def _log_charge_failure(self, charge_info: Dict[str, Any]):
        """Log charge failure"""
        logger.warning(f"Logging charge failure: {charge_info}")
        await asyncio.sleep(0.1)
    
    async def _update_refund_status(self, refund_info: Dict[str, Any]):
        """Update refund status"""
        logger.info(f"Updating refund status: {refund_info}")
        await asyncio.sleep(0.1)
    
    async def _create_subscription(self, subscription_info: Dict[str, Any]):
        """Create subscription"""
        logger.info(f"Creating subscription: {subscription_info}")
        await asyncio.sleep(0.1)
    
    async def _update_subscription(self, subscription_info: Dict[str, Any]):
        """Update subscription"""
        logger.info(f"Updating subscription: {subscription_info}")
        await asyncio.sleep(0.1)
    
    async def _cancel_subscription(self, subscription_info: Dict[str, Any]):
        """Cancel subscription"""
        logger.info(f"Cancelling subscription: {subscription_info}")
        await asyncio.sleep(0.1)
    
    async def _process_invoice_payment(self, invoice_info: Dict[str, Any]):
        """Process invoice payment"""
        logger.info(f"Processing invoice payment: {invoice_info}")
        await asyncio.sleep(0.1)
    
    async def _handle_invoice_payment_failure(self, invoice_info: Dict[str, Any]):
        """Handle invoice payment failure"""
        logger.warning(f"Handling invoice payment failure: {invoice_info}")
        await asyncio.sleep(0.1)