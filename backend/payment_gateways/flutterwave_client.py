"""
Flutterwave Payment Gateway Client
Comprehensive integration with Flutterwave API v3
"""

import os
import requests
import hashlib
import hmac
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class FlutterwaveClient:
    """Flutterwave API v3 client for payment processing and fraud detection integration"""
    
    def __init__(self):
        self.secret_key = os.getenv('FLUTTERWAVE_SECRET_KEY')
        self.public_key = os.getenv('FLUTTERWAVE_PUBLIC_KEY')
        self.encryption_key = os.getenv('FLUTTERWAVE_ENCRYPTION_KEY')
        self.base_url = 'https://api.flutterwave.com/v3'
        
        if not all([self.secret_key, self.public_key, self.encryption_key]):
            logger.warning("Flutterwave credentials not fully configured")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get standard headers for Flutterwave API requests"""
        return {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
    
    def create_payment_link(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a payment link for testing fraud detection"""
        
        payload = {
            "tx_ref": f"FDS-{uuid.uuid4().hex[:10]}",
            "amount": transaction_data.get('amount', 100000),
            "currency": transaction_data.get('currency', 'NGN'),
            "redirect_url": "https://your-domain.com/payment/callback",
            "payment_options": "card,banktransfer,ussd",
            "customer": {
                "email": transaction_data.get('email', 'test@fraudsystem.com'),
                "phone_number": transaction_data.get('phone', '+2348012345678'),
                "name": transaction_data.get('customer_name', 'Test Customer')
            },
            "customizations": {
                "title": "Fraud Detection System Test",
                "description": f"Test payment for fraud detection - {transaction_data.get('merchant_id', 'Test Merchant')}",
                "logo": "https://your-logo-url.com/logo.png"
            },
            "meta": {
                "fraud_detection": True,
                "merchant_id": transaction_data.get('merchant_id', 'TEST_MERCHANT'),
                "user_id": transaction_data.get('user_id', 1),
                "payment_method": transaction_data.get('payment_method', 'card')
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/payments",
                json=payload,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Payment link created: {result.get('data', {}).get('link')}")
                return {
                    'status': 'success',
                    'payment_link': result.get('data', {}).get('link'),
                    'tx_ref': payload['tx_ref'],
                    'data': result.get('data', {})
                }
            else:
                logger.error(f"Failed to create payment link: {response.text}")
                return {
                    'status': 'error',
                    'message': response.text
                }
                
        except Exception as e:
            logger.error(f"Error creating payment link: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def verify_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Verify a transaction status"""
        
        try:
            response = requests.get(
                f"{self.base_url}/transactions/{transaction_id}/verify",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'status': 'success',
                    'data': result.get('data', {})
                }
            else:
                return {
                    'status': 'error',
                    'message': response.text
                }
                
        except Exception as e:
            logger.error(f"Error verifying transaction: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """Verify Flutterwave webhook signature"""
        
        if not signature or not self.encryption_key:
            return False
        
        # Flutterwave uses the secret hash for webhook verification
        expected_signature = os.getenv('FLUTTERWAVE_WEBHOOK_HASH')
        return signature == expected_signature
    
    def process_webhook_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process Flutterwave webhook payload for fraud detection"""
        
        try:
            event_type = payload.get('event')
            data = payload.get('data', {})
            
            # Extract transaction information
            transaction_info = {
                'transaction_id': data.get('tx_ref'),
                'flw_ref': data.get('flw_ref'),
                'amount': data.get('amount'),
                'currency': data.get('currency', 'NGN'),
                'status': data.get('status'),
                'payment_type': data.get('payment_type'),
                'created_at': data.get('created_at'),
                'customer': data.get('customer', {}),
                'card': data.get('card', {}),
                'meta': data.get('meta', {}),
                'event_type': event_type
            }
            
            # Add fraud detection specific data
            fraud_indicators = self._extract_fraud_indicators(data)
            transaction_info.update(fraud_indicators)
            
            return {
                'status': 'success',
                'transaction_info': transaction_info,
                'requires_fraud_check': event_type in ['charge.completed', 'transfer.completed']
            }
            
        except Exception as e:
            logger.error(f"Error processing webhook payload: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _extract_fraud_indicators(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract fraud detection indicators from Flutterwave transaction data"""
        
        indicators = {}
        
        # Card information
        card_info = data.get('card', {})
        if card_info:
            indicators.update({
                'card_type': card_info.get('type'),
                'card_country': card_info.get('country'),
                'card_issuer': card_info.get('issuer'),
                'card_bin': card_info.get('first_6digits'),
                'card_last4': card_info.get('last_4digits')
            })
        
        # Customer information
        customer = data.get('customer', {})
        if customer:
            indicators.update({
                'customer_email': customer.get('email'),
                'customer_phone': customer.get('phone_number'),
                'customer_name': customer.get('name')
            })
        
        # Transaction metadata
        meta = data.get('meta', {})
        if meta:
            indicators.update({
                'merchant_id': meta.get('merchant_id'),
                'user_id': meta.get('user_id'),
                'payment_method': meta.get('payment_method')
            })
        
        # Risk indicators
        indicators.update({
            'ip_address': data.get('ip'),
            'device_fingerprint': data.get('device_fingerprint'),
            'narration': data.get('narration'),
            'processor_response': data.get('processor_response'),
            'auth_model': data.get('auth_model')
        })
        
        return indicators
    
    def get_transaction_timeline(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction timeline for fraud analysis"""
        
        try:
            response = requests.get(
                f"{self.base_url}/transactions/{transaction_id}/events",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'status': 'success',
                    'timeline': result.get('data', [])
                }
            else:
                return {
                    'status': 'error',
                    'message': response.text
                }
                
        except Exception as e:
            logger.error(f"Error getting transaction timeline: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def create_test_webhook_payload(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a test webhook payload for development/testing"""
        
        return {
            "event": "charge.completed",
            "data": {
                "id": 12345678,
                "tx_ref": f"FDS-{uuid.uuid4().hex[:10]}",
                "flw_ref": f"FLW-{uuid.uuid4().hex[:10]}",
                "device_fingerprint": f"device_{uuid.uuid4().hex[:8]}",
                "amount": transaction_data.get('amount', 100000),
                "currency": transaction_data.get('currency', 'NGN'),
                "charged_amount": transaction_data.get('amount', 100000),
                "app_fee": transaction_data.get('amount', 100000) * 0.015,  # 1.5% fee
                "merchant_fee": 0,
                "processor_response": "Approved by Financial Institution",
                "auth_model": "PIN",
                "ip": transaction_data.get('ip_address', '192.168.1.100'),
                "narration": f"Payment to {transaction_data.get('merchant_id', 'Test Merchant')}",
                "status": "successful",
                "payment_type": transaction_data.get('payment_method', 'card'),
                "created_at": datetime.now().isoformat(),
                "account_id": 123456,
                "customer": {
                    "id": transaction_data.get('user_id', 1),
                    "name": "Test Customer",
                    "phone_number": "+2348012345678",
                    "email": "test@example.com",
                    "created_at": datetime.now().isoformat()
                },
                "card": {
                    "first_6digits": "539983",
                    "last_4digits": "1234",
                    "issuer": "MASTERCARD CREDIT",
                    "country": "NG",
                    "type": "MASTERCARD",
                    "expiry": "12/26"
                },
                "meta": {
                    "merchant_id": transaction_data.get('merchant_id', 'TEST_MERCHANT'),
                    "user_id": transaction_data.get('user_id', 1),
                    "payment_method": transaction_data.get('payment_method', 'card'),
                    "fraud_detection": True
                }
            }
        }

# Global Flutterwave client instance
flutterwave_client = FlutterwaveClient()

if __name__ == "__main__":
    # Test the Flutterwave client
    client = FlutterwaveClient()
    
    # Test payment link creation
    test_transaction = {
        'amount': 50000,
        'currency': 'NGN',
        'email': 'test@fraudsystem.com',
        'merchant_id': 'TEST_MERCHANT',
        'user_id': 1
    }
    
    result = client.create_payment_link(test_transaction)
    print("Payment link creation result:", result)
    
    # Test webhook payload creation
    webhook_payload = client.create_test_webhook_payload(test_transaction)
    print("Test webhook payload:", json.dumps(webhook_payload, indent=2))
