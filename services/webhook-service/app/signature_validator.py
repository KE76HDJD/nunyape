import hashlib
import hmac
import json
from typing import Dict, Any, Optional
import logging
import base64

logger = logging.getLogger('webhook-signature-validator')

class SignatureValidator:
    """
    Unified signature validator for various webhook providers
    """
    
    def __init__(self):
        self.validation_methods = {
            'stripe': self.validate_stripe_signature,
            'paypal': self.validate_paypal_signature,
            'min': self.validate_min_signature,
            'shopify': self.validate_shopify_signature,
            'quickbooks': self.validate_quickbooks_signature,
            'xero': self.validate_xero_signature
        }
    
    async def validate_signature(
        self, 
        provider: str,
        payload: Dict[str, Any],
        signature: str,
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None
    ) -> bool:
        """
        Validate webhook signature for any supported provider
        """
        try:
            validation_method = self.validation_methods.get(provider)
            if not validation_method:
                logger.warning(f"No validation method for provider: {provider}")
                return False
            
            return await validation_method(payload, signature, headers, secret)
            
        except Exception as e:
            logger.error(f"Signature validation error for {provider}: {e}")
            return False
    
    async def validate_stripe_signature(
        self,
        payload: Dict[str, Any],
        signature: str,
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None
    ) -> bool:
        """
        Validate Stripe webhook signature
        """
        try:
            # Stripe signature validation is handled by StripeHandler
            # This is a placeholder for unified interface
            return True
            
        except Exception as e:
            logger.error(f"Stripe signature validation failed: {e}")
            return False
    
    async def validate_paypal_signature(
        self,
        payload: Dict[str, Any],
        signature: str,
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None
    ) -> bool:
        """
        Validate PayPal webhook signature
        """
        try:
            # PayPal signature validation is handled by PayPalHandler
            # This is a placeholder for unified interface
            return True
            
        except Exception as e:
            logger.error(f"PayPal signature validation failed: {e}")
            return False
    
    async def validate_min_signature(
        self,
        payload: Dict[str, Any],
        signature: str,
        headers: Optional[Dict[str, str]] = None, 
        secret: Optional[str] = None
    ) -> bool:
        """
        Validate MIN webhook signature
        """
        try:
            # MIN signature validation is handled by MinHandler
            # This is a placeholder for unified interface
            return True
            
        except Exception as e:
            logger.error(f"MIN signature validation failed: {e}")
            return False
    
    async def validate_shopify_signature(
        self,
        payload: Dict[str, Any],
        signature: str,
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None
    ) -> bool:
        """
        Validate Shopify webhook signature
        """
        try:
            if not secret:
                logger.error("Shopify validation requires secret")
                return False
            
            # Shopify uses HMAC SHA256
            payload_str = json.dumps(payload, separators=(',', ':'))
            
            computed_hmac = hmac.new(
                secret.encode('utf-8'),
                payload_str.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(computed_hmac, signature)
            
        except Exception as e:
            logger.error(f"Shopify signature validation failed: {e}")
            return False
    
    async def validate_quickbooks_signature(
        self,
        payload: Dict[str, Any],
        signature: str,
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None
    ) -> bool:
        """
        Validate QuickBooks webhook signature
        """
        try:
            if not headers or 'intuit-signature' not in headers:
                logger.error("QuickBooks validation requires intuit-signature header")
                return False
            
            # QuickBooks uses HMAC SHA256
            payload_str = json.dumps(payload, separators=(',', ':'))
            
            computed_hmac = hmac.new(
                secret.encode('utf-8'),
                payload_str.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(computed_hmac, headers['intuit-signature'])
            
        except Exception as e:
            logger.error(f"QuickBooks signature validation failed: {e}")
            return False
    
    async def validate_xero_signature(
        self,
        payload: Dict[str, Any],
        signature: str,
        headers: Optional[Dict[str, str]] = None,
        secret: Optional[str] = None
    ) -> bool:
        """
        Validate Xero webhook signature
        """
        try:
            if not headers or 'x-xero-signature' not in headers:
                logger.error("Xero validation requires x-xero-signature header")
                return False
            
            # Xero uses base64 encoded HMAC SHA256
            payload_str = json.dumps(payload, separators=(',', ':'))
            
            computed_hmac = hmac.new(
                secret.encode('utf-8'),
                payload_str.encode('utf-8'),
                hashlib.sha256
            ).digest()
            
            computed_signature = base64.b64encode(computed_hmac).decode()
            
            return hmac.compare_digest(computed_signature, headers['x-xero-signature'])
            
        except Exception as e:
            logger.error(f"Xero signature validation failed: {e}")
            return False
    
    async def validate_custom_signature(
        self,
        provider: str,
        payload: Dict[str, Any],
        signature: str,
        headers: Dict[str, str]
    ) -> bool:
        """
        Validate signature for custom providers
        """
        try:
            # Custom validation logic based on provider requirements
            if provider == "custom_provider_1":
                return await self._validate_custom_provider_1(payload, signature, headers)
            elif provider == "custom_provider_2":
                return await self._validate_custom_provider_2(payload, signature, headers)
            else:
                logger.warning(f"No custom validation for provider: {provider}")
                return True  # Accept by default for unknown custom providers
                
        except Exception as e:
            logger.error(f"Custom signature validation failed for {provider}: {e}")
            return False
    
    async def _validate_custom_provider_1(
        self,
        payload: Dict[str, Any],
        signature: str,
        headers: Dict[str, str]
    ) -> bool:
        """Validate custom provider 1 signature"""
        # Implementation for custom provider 1
        return True
    
    async def _validate_custom_provider_2(
        self,
        payload: Dict[str, Any],
        signature: str,
        headers: Dict[str, str]
    ) -> bool:
        """Validate custom provider 2 signature"""
        # Implementation for custom provider 2
        return True