"""
API Handler Module
Handles payment gateway webhooks and external API integrations
"""

import hmac
import hashlib
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
import logging
import os
from dotenv import load_dotenv

from transaction_processor import process_transaction
from db_interface import get_database
from payment_gateways.flutterwave_client import flutterwave_client

load_dotenv()
logger = logging.getLogger(__name__)

class PaymentGatewayHandler:
    """Handles payment gateway integrations and webhooks"""
    
    def __init__(self):
        # Paystack configuration
        self.paystack_secret_key = os.getenv('PAYSTACK_SECRET_KEY')
        self.paystack_public_key = os.getenv('PAYSTACK_PUBLIC_KEY')
        self.paystack_base_url = 'https://api.paystack.co'
        
        # Flutterwave configuration
        self.flutterwave_secret_key = os.getenv('FLUTTERWAVE_SECRET_KEY')
        self.flutterwave_public_key = os.getenv('FLUTTERWAVE_PUBLIC_KEY')
        self.flutterwave_encryption_key = os.getenv('FLUTTERWAVE_ENCRYPTION_KEY')
        self.flutterwave_base_url = 'https://api.flutterwave.com/v3'
        
        logger.info("Payment gateway handler initialized")
    
    def process_webhook(self, payload: Dict[str, Any], headers: Dict[str, str], 
                       gateway: str) -> Dict[str, Any]:
        """Process webhook from payment gateway"""
        try:
            if gateway.lower() == 'paystack':
                return self._process_paystack_webhook(payload, headers)
            elif gateway.lower() == 'flutterwave':
                return self._process_flutterwave_webhook(payload, headers)
            else:
                return {'status': 'error', 'message': 'Unsupported gateway'}
                
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _process_paystack_webhook(self, payload: Dict[str, Any], 
                                 headers: Dict[str, str]) -> Dict[str, Any]:
        """Process Paystack webhook"""
        
        # Verify webhook signature
        signature = headers.get('x-paystack-signature')
        if not self._verify_paystack_signature(json.dumps(payload), signature):
            logger.warning("Invalid Paystack webhook signature")
            return {'status': 'error', 'message': 'Invalid signature'}
        
        event = payload.get('event')
        data = payload.get('data', {})
        
        logger.info(f"Processing Paystack webhook: {event}")
        
        if event == 'charge.success':
            return self._handle_successful_payment(data, 'paystack')
        elif event == 'charge.failed':
            return self._handle_failed_payment(data, 'paystack')
        elif event == 'transfer.success':
            return self._handle_successful_transfer(data, 'paystack')
        elif event == 'transfer.failed':
            return self._handle_failed_transfer(data, 'paystack')
        else:
            logger.info(f"Unhandled Paystack event: {event}")
            return {'status': 'ignored', 'message': f'Event {event} not handled'}
    
    def _process_flutterwave_webhook(self, payload: Dict[str, Any], 
                                   headers: Dict[str, str]) -> Dict[str, Any]:
        """Process Flutterwave webhook using enhanced client"""
        
        # Verify webhook signature
        signature = headers.get('verif-hash')
        if not flutterwave_client.verify_webhook_signature(json.dumps(payload), signature):
            logger.warning("Invalid Flutterwave webhook signature")
            return {'status': 'error', 'message': 'Invalid signature'}
        
        # Process webhook payload
        processing_result = flutterwave_client.process_webhook_payload(payload)
        
        if processing_result['status'] != 'success':
            return processing_result
        
        transaction_info = processing_result['transaction_info']
        event_type = transaction_info['event_type']
        
        logger.info(f"Processing Flutterwave webhook: {event_type}")
        
        if processing_result['requires_fraud_check']:
            return self._handle_flutterwave_fraud_check(transaction_info)
        else:
            logger.info(f"No fraud check required for event: {event_type}")
            return {'status': 'ignored', 'message': f'Event {event_type} not processed'}
    
    def _verify_paystack_signature(self, payload: str, signature: str) -> bool:
        """Verify Paystack webhook signature"""
        if not signature or not self.paystack_secret_key:
            return False
        
        expected_signature = hmac.new(
            self.paystack_secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def _verify_flutterwave_signature(self, payload: str, signature: str) -> bool:
        """Verify Flutterwave webhook signature"""
        if not signature:
            return False
        
        # Flutterwave uses a simple hash verification
        expected_signature = os.getenv('FLUTTERWAVE_WEBHOOK_HASH')
        return signature == expected_signature
    
    def _handle_successful_payment(self, data: Dict[str, Any], gateway: str) -> Dict[str, Any]:
        """Handle successful payment webhook"""
        try:
            # Extract transaction data from webhook payload
            transaction_data = self._extract_transaction_data(data, gateway)
            
            # Process through fraud detection
            db = next(get_database())
            try:
                result = process_transaction(transaction_data, db)
                
                # Log the result
                logger.info(f"Processed {gateway} payment: {result.get('transaction_id')} - {result.get('fraud_analysis', {}).get('decision')}")
                
                return {
                    'status': 'success',
                    'message': 'Payment processed successfully',
                    'transaction_id': result.get('transaction_id'),
                    'fraud_decision': result.get('fraud_analysis', {}).get('decision'),
                    'fraud_score': result.get('fraud_analysis', {}).get('fraud_score')
                }
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error handling successful payment: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _handle_failed_payment(self, data: Dict[str, Any], gateway: str) -> Dict[str, Any]:
        """Handle failed payment webhook"""
        try:
            transaction_id = self._get_transaction_id(data, gateway)
            logger.info(f"Payment failed for transaction: {transaction_id}")
            
            # You might want to update transaction status or send notifications
            return {
                'status': 'success',
                'message': 'Failed payment logged',
                'transaction_id': transaction_id
            }
            
        except Exception as e:
            logger.error(f"Error handling failed payment: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _handle_successful_transfer(self, data: Dict[str, Any], gateway: str) -> Dict[str, Any]:
        """Handle successful transfer webhook"""
        try:
            # Similar to payment handling but for transfers/withdrawals
            transaction_data = self._extract_transfer_data(data, gateway)
            
            db = next(get_database())
            try:
                result = process_transaction(transaction_data, db)
                
                logger.info(f"Processed {gateway} transfer: {result.get('transaction_id')}")
                
                return {
                    'status': 'success',
                    'message': 'Transfer processed successfully',
                    'transaction_id': result.get('transaction_id')
                }
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error handling successful transfer: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _handle_failed_transfer(self, data: Dict[str, Any], gateway: str) -> Dict[str, Any]:
        """Handle failed transfer webhook"""
        try:
            transaction_id = self._get_transaction_id(data, gateway)
            logger.info(f"Transfer failed for transaction: {transaction_id}")
            
            return {
                'status': 'success',
                'message': 'Failed transfer logged',
                'transaction_id': transaction_id
            }
            
        except Exception as e:
            logger.error(f"Error handling failed transfer: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _handle_flutterwave_fraud_check(self, transaction_info: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Flutterwave transaction fraud check"""
        try:
            # Convert Flutterwave transaction info to our standard format
            transaction_data = {
                'transaction_id': transaction_info.get('transaction_id'),
                'user_id': self._extract_user_id_from_email(transaction_info.get('customer_email')),
                'amount': transaction_info.get('amount', 0),
                'currency': transaction_info.get('currency', 'NGN'),
                'transaction_type': 'payment',
                'merchant_id': transaction_info.get('merchant_id', 'FLUTTERWAVE'),
                'payment_method': transaction_info.get('payment_type', 'card'),
                'ip_address': transaction_info.get('ip_address'),
                'timestamp': datetime.now(),
                'device_fingerprint': transaction_info.get('device_fingerprint'),
                'email': transaction_info.get('customer_email'),
                'phone': transaction_info.get('customer_phone'),
                # Add Flutterwave specific fraud indicators
                'card_type': transaction_info.get('card_type'),
                'card_country': transaction_info.get('card_country'),
                'card_issuer': transaction_info.get('card_issuer'),
                'processor_response': transaction_info.get('processor_response'),
                'auth_model': transaction_info.get('auth_model')
            }
            
            # Process through fraud detection
            db = next(get_database())
            try:
                result = process_transaction(transaction_data, db)
                
                logger.info(f"Processed Flutterwave transaction: {result.get('transaction_id')} - {result.get('fraud_analysis', {}).get('decision')}")
                
                return {
                    'status': 'success',
                    'message': 'Flutterwave transaction processed successfully',
                    'transaction_id': result.get('transaction_id'),
                    'fraud_decision': result.get('fraud_analysis', {}).get('decision'),
                    'fraud_score': result.get('fraud_analysis', {}).get('fraud_score'),
                    'flw_ref': transaction_info.get('flw_ref')
                }
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error handling Flutterwave fraud check: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _extract_transaction_data(self, data: Dict[str, Any], gateway: str) -> Dict[str, Any]:
        """Extract transaction data from webhook payload"""
        
        if gateway == 'paystack':
            return {
                'transaction_id': data.get('reference'),
                'user_id': self._extract_user_id_from_email(data.get('customer', {}).get('email')),
                'amount': data.get('amount', 0) / 100,  # Paystack amounts are in kobo
                'currency': data.get('currency', 'NGN'),
                'transaction_type': 'payment',
                'merchant_id': 'PAYSTACK',
                'payment_method': data.get('channel'),
                'ip_address': data.get('ip_address'),
                'timestamp': datetime.now(),
                'device_fingerprint': data.get('metadata', {}).get('device_id'),
                'email': data.get('customer', {}).get('email'),
                'phone': data.get('customer', {}).get('phone')
            }
            
        elif gateway == 'flutterwave':
            return {
                'transaction_id': data.get('tx_ref'),
                'user_id': self._extract_user_id_from_email(data.get('customer', {}).get('email')),
                'amount': data.get('amount', 0),
                'currency': data.get('currency', 'NGN'),
                'transaction_type': 'payment',
                'merchant_id': 'FLUTTERWAVE',
                'payment_method': data.get('payment_type'),
                'ip_address': data.get('ip'),
                'timestamp': datetime.now(),
                'device_fingerprint': data.get('device_fingerprint'),
                'email': data.get('customer', {}).get('email'),
                'phone': data.get('customer', {}).get('phone_number')
            }
        
        return {}
    
    def _extract_transfer_data(self, data: Dict[str, Any], gateway: str) -> Dict[str, Any]:
        """Extract transfer data from webhook payload"""
        
        if gateway == 'paystack':
            return {
                'transaction_id': data.get('transfer_code') or data.get('reference'),
                'user_id': self._extract_user_id_from_account(data.get('recipient')),
                'amount': data.get('amount', 0) / 100,  # Paystack amounts are in kobo
                'currency': data.get('currency', 'NGN'),
                'transaction_type': 'transfer',
                'merchant_id': 'PAYSTACK_TRANSFER',
                'payment_method': 'bank_transfer',
                'timestamp': datetime.now()
            }
            
        elif gateway == 'flutterwave':
            return {
                'transaction_id': data.get('reference'),
                'user_id': self._extract_user_id_from_account(data.get('account_number')),
                'amount': data.get('amount', 0),
                'currency': data.get('currency', 'NGN'),
                'transaction_type': 'transfer',
                'merchant_id': 'FLUTTERWAVE_TRANSFER',
                'payment_method': 'bank_transfer',
                'timestamp': datetime.now()
            }
        
        return {}
    
    def _get_transaction_id(self, data: Dict[str, Any], gateway: str) -> str:
        """Extract transaction ID from webhook data"""
        if gateway == 'paystack':
            return data.get('reference', 'unknown')
        elif gateway == 'flutterwave':
            return data.get('tx_ref', data.get('reference', 'unknown'))
        return 'unknown'
    
    def _extract_user_id_from_email(self, email: Optional[str]) -> int:
        """Extract or create user ID from email"""
        if not email:
            return 1  # Default user
        
        # In a real implementation, you'd look up the user by email
        # For now, we'll create a simple hash-based ID
        return abs(hash(email)) % 10000 + 1
    
    def _extract_user_id_from_account(self, account_info: Optional[str]) -> int:
        """Extract user ID from account information"""
        if not account_info:
            return 1  # Default user
        
        # Simple hash-based ID
        return abs(hash(str(account_info))) % 10000 + 1

class AdminAPIHandler:
    """Handles admin API operations"""
    
    def __init__(self):
        self.db_manager = None  # Will be injected
    
    def authenticate_request(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate API request authentication"""
        # This is a simplified implementation
        # In production, you'd validate JWT tokens properly
        
        if not token:
            return None
        
        # For demo purposes, accept any token that starts with 'admin_'
        if token.startswith('admin_'):
            return {
                'user_id': 1,
                'role': 'admin',
                'permissions': ['read', 'write', 'admin']
            }
        elif token.startswith('analyst_'):
            return {
                'user_id': 2,
                'role': 'analyst',
                'permissions': ['read']
            }
        
        return None
    
    def format_response(self, data: Any, status: str = 'success', 
                       message: Optional[str] = None) -> Dict[str, Any]:
        """Standardize API responses"""
        response = {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        if message:
            response['message'] = message
        
        return response
    
    def handle_error(self, error: Exception, context: str = '') -> Dict[str, Any]:
        """Handle and format API errors"""
        logger.error(f"API Error in {context}: {error}")
        
        return {
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': str(error),
            'context': context
        }

# Global instances
payment_handler = PaymentGatewayHandler()
admin_handler = AdminAPIHandler()

def process_payment_webhook(payload: Dict[str, Any], headers: Dict[str, str], 
                          gateway: str) -> Dict[str, Any]:
    """Convenience function to process payment webhooks"""
    return payment_handler.process_webhook(payload, headers, gateway)

def authenticate_admin_request(token: str) -> Optional[Dict[str, Any]]:
    """Convenience function for admin authentication"""
    return admin_handler.authenticate_request(token)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test payment gateway handler
    sample_paystack_payload = {
        'event': 'charge.success',
        'data': {
            'reference': 'TEST_REF_123',
            'amount': 15000000,  # 150,000 NGN in kobo
            'currency': 'NGN',
            'channel': 'card',
            'customer': {
                'email': 'test@example.com',
                'phone': '+2348012345678'
            },
            'ip_address': '192.168.1.100'
        }
    }
    
    print("API handlers initialized successfully!")
    print("Sample transaction data extraction:")
    print(payment_handler._extract_transaction_data(sample_paystack_payload['data'], 'paystack'))
