import hashlib
import hmac
import json
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import aiohttp

logger = logging.getLogger('webhook-paypal-handler')

class PayPalHandler:
    """
    Handler for PayPal webhooks
    """
    
    def __init__(self, client_id: str, client_secret: str, webhook_id: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.webhook_id = webhook_id
        self.base_url = "https://api.sandbox.paypal.com"  # Use https://api.paypal.com for production
        
        self.supported_events = {
            'PAYMENT.CAPTURE.COMPLETED': self.handle_payment_capture_completed,
            'PAYMENT.CAPTURE.DENIED': self.handle_payment_capture_denied,
            'PAYMENT.CAPTURE.REFUNDED': self.handle_payment_capture_refunded,
            'PAYMENT.CAPTURE.REVERSED': self.handle_payment_capture_reversed,
            'CHECKOUT.ORDER.COMPLETED': self.handle_checkout_order_completed,
            'BILLING.SUBSCRIPTION.ACTIVATED': self.handle_subscription_activated,
            'BILLING.SUBSCRIPTION.CANCELLED': self.handle_subscription_cancelled,
        }
    
    async def verify_signature(self, headers: Dict[str, str], body: str) -> bool:
        """
        Verify PayPal webhook signature
        """
        try:
            # Get access token for PayPal API
            access_token = await self._get_access_token()
            
            # Verify webhook signature with PayPal API
            verification_url = f"{self.base_url}/v1/notifications/verify-webhook-signature"
            
            verification_data = {
                "transmission_id": headers.get('PAYPAL-TRANSMISSION-ID'),
                "transmission_time": headers.get('PAYPAL-TRANSMISSION-TIME'),
                "cert_url": headers.get('PAYPAL-CERT-URL'),
                "auth_algo": headers.get('PAYPAL-AUTH-ALGO'),
                "transmission_sig": headers.get('PAYPAL-TRANSMISSION-SIG'),
                "webhook_id": self.webhook_id,
                "webhook_event": json.loads(body)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    verification_url,
                    json=verification_data,
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json'
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('verification_status') == 'SUCCESS'
                    else:
                        logger.error(f"PayPal verification API error: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"PayPal signature verification failed: {e}")
            return False
    
    async def _get_access_token(self) -> str:
        """
        Get access token from PayPal API
        """
        auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/v1/oauth2/token",
                data={'grant_type': 'client_credentials'},
                auth=auth
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['access_token']
                else:
                    raise Exception(f"Failed to get PayPal access token: {response.status}")
    
    async def handle_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Main webhook handler for PayPal events
        """
        try:
            # Verify signature
            body_str = json.dumps(payload)
            if not await self.verify_signature(headers, body_str):
                logger.warning("Invalid PayPal webhook signature")
                return {
                    "status": "error",
                    "message": "Invalid signature",
                    "processed": False
                }
            
            event_type = payload.get('event_type')
            event_handler = self.supported_events.get(event_type)
            
            if not event_handler:
                logger.warning(f"Unsupported PayPal event type: {event_type}")
                return {
                    "status": "error",
                    "message": f"Unsupported event type: {event_type}",
                    "processed": False
                }
            
            # Process the event
            result = await event_handler(payload)
            logger.info(f"Processed PayPal webhook event: {event_type}")
            
            return {
                "status": "success",
                "message": "Webhook processed successfully",
                "processed": True,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error processing PayPal webhook: {e}")
            return {
                "status": "error",
                "message": f"Processing error: {str(e)}",
                "processed": False
            }
    
    async def handle_payment_capture_completed(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle payment capture completed event
        """
        resource = payload.get('resource', {})
        
        logger.info(f"Processing PayPal payment capture completed: {resource.get('id')}")
        
        capture_info = {
            'capture_id': resource.get('id'),
            'order_id': resource.get('supplementary_data', {}).get('related_ids', {}).get('order_id'),
            'amount': resource.get('amount', {}).get('value'),
            'currency': resource.get('amount', {}).get('currency_code'),
            'status': resource.get('status'),
            'create_time': resource.get('create_time'),
            'update_time': resource.get('update_time')
        }
        
        # Update order status to paid
        await self._update_order_status(capture_info['order_id'], 'paid')
        
        # Trigger fulfillment
        await self._trigger_order_fulfillment(capture_info)
        
        return {
            "action": "payment_captured",
            "capture_id": capture_info['capture_id'],
            "order_id": capture_info['order_id'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_payment_capture_denied(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle payment capture denied event
        """
        resource = payload.get('resource', {})
        
        logger.warning(f"Processing PayPal payment capture denied: {resource.get('id')}")
        
        capture_info = {
            'capture_id': resource.get('id'),
            'order_id': resource.get('supplementary_data', {}).get('related_ids', {}).get('order_id'),
            'reason': resource.get('details', [{}])[0].get('description', 'Unknown reason'),
            'create_time': resource.get('create_time')
        }
        
        # Update order status to payment_failed
        await self._update_order_status(capture_info['order_id'], 'payment_failed')
        
        # Notify customer
        await self._notify_payment_denied(capture_info)
        
        return {
            "action": "payment_denied",
            "capture_id": capture_info['capture_id'],
            "reason": capture_info['reason'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_payment_capture_refunded(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle payment capture refunded event
        """
        resource = payload.get('resource', {})
        
        logger.info(f"Processing PayPal payment capture refunded: {resource.get('id')}")
        
        refund_info = {
            'refund_id': resource.get('id'),
            'capture_id': resource.get('capture_id'),
            'amount': resource.get('amount', {}).get('value'),
            'currency': resource.get('amount', {}).get('currency_code'),
            'status': resource.get('status'),
            'create_time': resource.get('create_time')
        }
        
        # Update order status to refunded
        await self._update_refund_status(refund_info)
        
        return {
            "action": "payment_refunded",
            "refund_id": refund_info['refund_id'],
            "capture_id": refund_info['capture_id'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_checkout_order_completed(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle checkout order completed event
        """
        resource = payload.get('resource', {})
        
        logger.info(f"Processing PayPal checkout order completed: {resource.get('id')}")
        
        order_info = {
            'order_id': resource.get('id'),
            'status': resource.get('status'),
            'amount': resource.get('purchase_units', [{}])[0].get('amount', {}).get('value'),
            'currency': resource.get('purchase_units', [{}])[0].get('amount', {}).get('currency_code'),
            'create_time': resource.get('create_time'),
            'update_time': resource.get('update_time')
        }
        
        # Order is completed, ready for capture
        await self._process_order_completion(order_info)
        
        return {
            "action": "order_completed",
            "order_id": order_info['order_id'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_subscription_activated(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle subscription activated event
        """
        resource = payload.get('resource', {})
        
        logger.info(f"Processing PayPal subscription activated: {resource.get('id')}")
        
        subscription_info = {
            'subscription_id': resource.get('id'),
            'status': resource.get('status'),
            'start_time': resource.get('start_time'),
            'billing_info': resource.get('billing_info', {})
        }
        
        # Activate subscription in system
        await self._activate_subscription(subscription_info)
        
        return {
            "action": "subscription_activated",
            "subscription_id": subscription_info['subscription_id'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def handle_subscription_cancelled(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle subscription cancelled event
        """
        resource = payload.get('resource', {})
        
        logger.info(f"Processing PayPal subscription cancelled: {resource.get('id')}")
        
        subscription_info = {
            'subscription_id': resource.get('id'),
            'status': resource.get('status'),
            'cancelled_time': datetime.utcnow().isoformat()
        }
        
        # Cancel subscription in system
        await self._cancel_subscription(subscription_info)
        
        return {
            "action": "subscription_cancelled",
            "subscription_id": subscription_info['subscription_id'],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # Internal helper methods
    async def _update_order_status(self, order_id: str, status: str):
        """Update order status in database"""
        logger.info(f"Updating order {order_id} status to {status}")
        await asyncio.sleep(0.1)
    
    async def _trigger_order_fulfillment(self, capture_info: Dict[str, Any]):
        """Trigger order fulfillment process"""
        logger.info(f"Triggering fulfillment for capture {capture_info['capture_id']}")
        await asyncio.sleep(0.1)
    
    async def _notify_payment_denied(self, capture_info: Dict[str, Any]):
        """Notify about payment denial"""
        logger.warning(f"Notifying about payment denial: {capture_info}")
        await asyncio.sleep(0.1)
    
    async def _update_refund_status(self, refund_info: Dict[str, Any]):
        """Update refund status"""
        logger.info(f"Updating refund status: {refund_info}")
        await asyncio.sleep(0.1)
    
    async def _process_order_completion(self, order_info: Dict[str, Any]):
        """Process order completion"""
        logger.info(f"Processing order completion: {order_info}")
        await asyncio.sleep(0.1)
    
    async def _activate_subscription(self, subscription_info: Dict[str, Any]):
        """Activate subscription"""
        logger.info(f"Activating subscription: {subscription_info}")
        await asyncio.sleep(0.1)
    
    async def _cancel_subscription(self, subscription_info: Dict[str, Any]):
        """Cancel subscription"""
        logger.info(f"Cancelling subscription: {subscription_info}")
        await asyncio.sleep(0.1)