"""
Transaction Processing Module
Handles incoming transaction data, validation, and fraud analysis routing
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
import logging
import json
from ipaddress import ip_address, AddressValueError

from db_interface import DatabaseManager, get_database
from fraud_detector import analyze_transaction_fraud

logger = logging.getLogger(__name__)

class TransactionProcessor:
    """Handles transaction processing workflow"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        
    def receive_transaction(self, transaction_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Main entry point for processing incoming transactions
        1. Validates transaction data
        2. Saves to database
        3. Routes for fraud analysis
        4. Updates transaction status
        5. Returns analysis results
        """
        try:
            # 1. Validate transaction
            validation_result = self.validate_transaction(transaction_data)
            if not validation_result['valid']:
                return {
                    'status': 'error',
                    'error': validation_result['error'],
                    'transaction_id': transaction_data.get('transaction_id')
                }
            
            # 2. Prepare transaction for database
            processed_transaction = self._prepare_transaction(transaction_data)
            
            # 3. Save transaction to database
            saved_transaction = self.db_manager.save_transaction(db, processed_transaction)
            
            # 4. Perform fraud analysis
            fraud_result = analyze_transaction_fraud(processed_transaction, db)
            
            # 5. Save fraud assessment
            assessment_data = {
                'transaction_id': saved_transaction.transaction_id,
                'fraud_score': fraud_result['fraud_score'],
                'risk_factors': fraud_result.get('risk_factors', []),
                'model_version': fraud_result.get('model_version', 'unknown'),
                'decision': fraud_result['decision'],
                'confidence_level': fraud_result.get('confidence_level', 0.0)
            }
            
            fraud_assessment = self.db_manager.save_fraud_assessment(db, assessment_data)
            
            # 6. Update transaction status based on decision
            self._update_transaction_status(saved_transaction.transaction_id, fraud_result['decision'], db)
            
            # 7. Prepare response
            response = {
                'status': 'success',
                'transaction_id': saved_transaction.transaction_id,
                'user_id': saved_transaction.user_id,
                'amount': float(saved_transaction.amount),
                'currency': saved_transaction.currency,
                'timestamp': saved_transaction.timestamp.isoformat(),
                'fraud_analysis': fraud_result,
                'assessment_id': fraud_assessment.assessment_id
            }
            
            logger.info(f"Transaction processed successfully: {saved_transaction.transaction_id}")
            return response
            
        except Exception as e:
            logger.error(f"Transaction processing error: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'transaction_id': transaction_data.get('transaction_id')
            }
    
    def validate_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform basic transaction validation"""
        errors = []
        
        # Required fields
        required_fields = ['amount', 'user_id', 'currency']
        for field in required_fields:
            if field not in transaction_data or transaction_data[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Amount validation
        try:
            amount = float(transaction_data.get('amount', 0))
            if amount <= 0:
                errors.append("Amount must be greater than 0")
            elif amount > 50000000:  # 50M NGN max
                errors.append("Amount exceeds maximum limit")
        except (ValueError, TypeError):
            errors.append("Invalid amount format")
        
        # Currency validation
        currency = transaction_data.get('currency', '').upper()
        valid_currencies = ['NGN', 'USD', 'EUR', 'GBP']
        if currency not in valid_currencies:
            errors.append(f"Unsupported currency: {currency}")
        
        # User ID validation
        try:
            user_id = int(transaction_data.get('user_id', 0))
            if user_id <= 0:
                errors.append("Invalid user ID")
        except (ValueError, TypeError):
            errors.append("User ID must be a number")
        
        # IP address validation (if provided)
        ip_addr = transaction_data.get('ip_address')
        if ip_addr:
            try:
                ip_address(ip_addr)
            except AddressValueError:
                errors.append("Invalid IP address format")
        
        # Email validation (if provided)
        email = transaction_data.get('email')
        if email and '@' not in email:
            errors.append("Invalid email format")
        
        if errors:
            return {'valid': False, 'error': '; '.join(errors)}
        
        return {'valid': True}
    
    def _prepare_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare transaction data for database storage"""
        
        # Generate transaction ID if not provided
        transaction_id = transaction_data.get('transaction_id')
        if not transaction_id:
            transaction_id = f"TXN_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8]}"
        
        # Prepare the transaction dict
        prepared_transaction = {
            'transaction_id': transaction_id,
            'user_id': int(transaction_data['user_id']),
            'amount': float(transaction_data['amount']),
            'currency': transaction_data.get('currency', 'NGN').upper(),
            'transaction_type': transaction_data.get('transaction_type', 'payment'),
            'merchant_id': transaction_data.get('merchant_id', transaction_data.get('merchant', 'Unknown')),
            'payment_method': transaction_data.get('payment_method', 'card'),
            'ip_address': transaction_data.get('ip_address'),
            'device_fingerprint': transaction_data.get('device_fingerprint', self._generate_device_fingerprint(transaction_data)),
            'location_data': self._prepare_location_data(transaction_data),
            'transaction_status': 'pending'
        }
        
        # Add timestamp
        if 'timestamp' in transaction_data:
            if isinstance(transaction_data['timestamp'], str):
                prepared_transaction['timestamp'] = datetime.fromisoformat(transaction_data['timestamp'].replace('Z', '+00:00'))
            else:
                prepared_transaction['timestamp'] = transaction_data['timestamp']
        else:
            prepared_transaction['timestamp'] = datetime.now()
        
        return prepared_transaction
    
    def _generate_device_fingerprint(self, transaction_data: Dict[str, Any]) -> str:
        """Generate device fingerprint from available data"""
        fingerprint_data = {
            'user_agent': transaction_data.get('user_agent', ''),
            'ip_address': transaction_data.get('ip_address', ''),
            'device_id': transaction_data.get('device_id', ''),
            'screen_resolution': transaction_data.get('screen_resolution', ''),
            'timezone': transaction_data.get('timezone', '')
        }
        
        # Create hash of fingerprint data
        fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
        return f"fp_{hash(fingerprint_string) % 1000000:06d}"
    
    def _prepare_location_data(self, transaction_data: Dict[str, Any]) -> Optional[Dict]:
        """Prepare location data as JSONB"""
        location_fields = ['country', 'state', 'city', 'latitude', 'longitude', 'postal_code']
        location_data = {}
        
        for field in location_fields:
            if field in transaction_data:
                location_data[field] = transaction_data[field]
        
        # Add billing address if provided
        billing_address = transaction_data.get('billing_address')
        if billing_address:
            location_data['billing_address'] = billing_address
        
        return location_data if location_data else None
    
    def _update_transaction_status(self, transaction_id: str, decision: str, db: Session):
        """Update transaction status based on fraud decision"""
        status_mapping = {
            'APPROVE': 'approved',
            'DECLINE': 'declined', 
            'REVIEW': 'under_review'
        }
        
        new_status = status_mapping.get(decision, 'pending')
        
        try:
            transaction = self.db_manager.get_transaction(db, transaction_id)
            if transaction:
                transaction.transaction_status = new_status
                db.commit()
                logger.info(f"Updated transaction {transaction_id} status to {new_status}")
        except Exception as e:
            logger.error(f"Error updating transaction status: {e}")
    
    def route_for_analysis(self, transaction: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Route transaction for fraud analysis"""
        return analyze_transaction_fraud(transaction, db)
    
    def update_transaction_status(self, transaction_id: str, status: str, db: Session) -> bool:
        """Update transaction status"""
        try:
            transaction = self.db_manager.get_transaction(db, transaction_id)
            if transaction:
                transaction.transaction_status = status
                db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating transaction status: {e}")
            return False
    
    def get_transaction_details(self, transaction_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Get detailed transaction information including fraud assessment"""
        try:
            transaction = self.db_manager.get_transaction(db, transaction_id)
            if not transaction:
                return None
            
            # Get fraud assessment
            fraud_assessment = self.db_manager.get_fraud_assessment(db, transaction_id)
            
            # Prepare response
            result = {
                'transaction_id': transaction.transaction_id,
                'user_id': transaction.user_id,
                'amount': float(transaction.amount),
                'currency': transaction.currency,
                'transaction_type': transaction.transaction_type,
                'merchant_id': transaction.merchant_id,
                'timestamp': transaction.timestamp.isoformat(),
                'payment_method': transaction.payment_method,
                'ip_address': str(transaction.ip_address) if transaction.ip_address else None,
                'device_fingerprint': transaction.device_fingerprint,
                'location_data': transaction.location_data,
                'transaction_status': transaction.transaction_status
            }
            
            if fraud_assessment:
                result['fraud_assessment'] = {
                    'assessment_id': fraud_assessment.assessment_id,
                    'fraud_score': float(fraud_assessment.fraud_score),
                    'risk_factors': fraud_assessment.risk_factors,
                    'model_version': fraud_assessment.model_version,
                    'decision': fraud_assessment.decision,
                    'confidence_level': float(fraud_assessment.confidence_level) if fraud_assessment.confidence_level else None,
                    'processed_at': fraud_assessment.processed_at.isoformat()
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting transaction details: {e}")
            return None
    
    def get_user_transaction_summary(self, user_id: int, db: Session, limit: int = 50) -> Dict[str, Any]:
        """Get transaction summary for a user"""
        try:
            transactions = self.db_manager.get_user_transactions(db, user_id, limit)
            
            if not transactions:
                return {
                    'user_id': user_id,
                    'total_transactions': 0,
                    'total_amount': 0,
                    'transactions': []
                }
            
            total_amount = sum(float(t.amount) for t in transactions)
            
            transaction_list = []
            for t in transactions:
                # Get fraud assessment for each transaction
                fraud_assessment = self.db_manager.get_fraud_assessment(db, t.transaction_id)
                
                tx_data = {
                    'transaction_id': t.transaction_id,
                    'amount': float(t.amount),
                    'currency': t.currency,
                    'merchant_id': t.merchant_id,
                    'timestamp': t.timestamp.isoformat(),
                    'status': t.transaction_status
                }
                
                if fraud_assessment:
                    tx_data['fraud_score'] = float(fraud_assessment.fraud_score)
                    tx_data['decision'] = fraud_assessment.decision
                
                transaction_list.append(tx_data)
            
            return {
                'user_id': user_id,
                'total_transactions': len(transactions),
                'total_amount': round(total_amount, 2),
                'transactions': transaction_list
            }
            
        except Exception as e:
            logger.error(f"Error getting user transaction summary: {e}")
            return {'user_id': user_id, 'error': str(e)}

# Global transaction processor instance
transaction_processor = TransactionProcessor()

def process_transaction(transaction_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Convenience function to process a transaction"""
    return transaction_processor.receive_transaction(transaction_data, db)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test transaction processor
    sample_transaction = {
        'user_id': 1,
        'amount': 150000,
        'currency': 'NGN',
        'merchant_id': 'TEST_MERCHANT',
        'payment_method': 'card',
        'ip_address': '192.168.1.100'
    }
    
    processor = TransactionProcessor()
    validation = processor.validate_transaction(sample_transaction)
    
    print("Transaction Processor initialized successfully!")
    print("Sample validation result:", validation)
