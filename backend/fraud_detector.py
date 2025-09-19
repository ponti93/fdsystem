"""
Advanced Fraud Detection Engine
Combines RNN predictions, rule-based scoring, and velocity analysis
as per system specifications
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from sqlalchemy.orm import Session
import json
import hashlib

from ml_models.rnn_fraud_model import FraudDetectionRNN, FraudDetectionPreprocessor
from db_interface import DatabaseManager, FraudRule

logger = logging.getLogger(__name__)

class FraudDetectionEngine:
    """
    Advanced fraud detection engine implementing the mathematical specification:
    Fraud_Score = α × RNN_Score + β × Rule_Score + γ × Velocity_Score
    Where α + β + γ = 1
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.rnn_model = FraudDetectionRNN()
        self.preprocessor = None
        
        # Weighted coefficients (α + β + γ = 1)
        self.alpha = 0.6  # RNN model weight
        self.beta = 0.3   # Rule-based weight  
        self.gamma = 0.1  # Velocity analysis weight
        
        # Decision thresholds
        self.fraud_threshold_high = 0.8   # DECLINE threshold
        self.fraud_threshold_medium = 0.5  # REVIEW threshold
        
        # Load RNN model if available
        self._load_rnn_model()
        
        logger.info("Fraud Detection Engine initialized")
    
    def _load_rnn_model(self):
        """Load the trained RNN model"""
        try:
            if self.rnn_model.load_model():
                self.preprocessor = FraudDetectionPreprocessor(self.rnn_model)
                logger.info("RNN model loaded successfully")
            else:
                logger.warning("RNN model not found, using rule-based detection only")
                # Adjust weights if no RNN model
                self.alpha = 0.0
                self.beta = 0.8
                self.gamma = 0.2
        except Exception as e:
            logger.error(f"Error loading RNN model: {e}")
            self.alpha = 0.0
            self.beta = 0.8
            self.gamma = 0.2
    
    def analyze_transaction(self, transaction: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Main fraud detection analysis combining RNN, rules, and velocity analysis
        """
        logger.info(f"Analyzing transaction: {transaction.get('transaction_id', 'unknown')}")
        
        start_time = datetime.now()
        
        # Initialize scores
        rnn_score = 0.0
        rule_score = 0.0
        velocity_score = 0.0
        risk_factors = []
        
        try:
            # 1. RNN Analysis
            if self.rnn_model.model and self.preprocessor:
                rnn_score = self._get_rnn_score(transaction)
                if rnn_score > 0.5:
                    risk_factors.append({
                        'factor': 'rnn_prediction',
                        'weight': rnn_score,
                        'triggered': True
                    })
            
            # 2. Rule-based Analysis
            rule_score, rule_factors = self._get_rule_score(transaction, db)
            risk_factors.extend(rule_factors)
            
            # 3. Velocity Analysis
            velocity_score, velocity_factors = self._get_velocity_score(transaction, db)
            risk_factors.extend(velocity_factors)
            
            # 4. Calculate final fraud score using the mathematical formula
            final_score = (self.alpha * rnn_score + 
                          self.beta * rule_score + 
                          self.gamma * velocity_score)
            
            # Ensure score is between 0 and 1
            final_score = max(0.0, min(1.0, final_score))
            
            # 5. Make decision
            decision = self._make_decision(final_score)
            
            # 6. Calculate confidence level
            confidence_level = self._calculate_confidence(final_score, risk_factors)
            
            # 7. Processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            result = {
                'transaction_id': transaction.get('transaction_id'),
                'fraud_score': round(final_score, 4),
                'decision': decision,
                'confidence_level': round(confidence_level, 4),
                'risk_factors': risk_factors,
                'component_scores': {
                    'rnn_score': round(rnn_score, 4),
                    'rule_score': round(rule_score, 4),
                    'velocity_score': round(velocity_score, 4)
                },
                'model_version': self.rnn_model.model_version if self.rnn_model.model else 'rule_based_v1.0',
                'processing_time_ms': round(processing_time, 2),
                'processed_at': datetime.now().isoformat()
            }
            
            logger.info(f"Analysis completed: {decision} (score: {final_score:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Error in fraud analysis: {e}")
            # Return safe default
            return {
                'transaction_id': transaction.get('transaction_id'),
                'fraud_score': 0.5,
                'decision': 'REVIEW',
                'confidence_level': 0.0,
                'risk_factors': [{'factor': 'analysis_error', 'weight': 0.5, 'triggered': True}],
                'error': str(e),
                'processed_at': datetime.now().isoformat()
            }
    
    def _get_rnn_score(self, transaction: Dict[str, Any]) -> float:
        """Get fraud score from RNN model"""
        try:
            # Add transaction to preprocessor and get sequence
            sequence = self.preprocessor.add_transaction(transaction)
            
            if sequence is not None:
                # Get prediction from RNN model
                score = self.rnn_model.predict_fraud_score(sequence)
                return float(score)
            else:
                # Not enough transactions for sequence, return neutral score
                return 0.0
                
        except Exception as e:
            logger.error(f"RNN prediction error: {e}")
            return 0.0
    
    def _get_rule_score(self, transaction: Dict[str, Any], db: Session) -> Tuple[float, List[Dict]]:
        """Get fraud score from rule-based analysis"""
        try:
            # Get active fraud rules from database
            rules = self.db_manager.get_active_fraud_rules(db)
            
            total_score = 0.0
            triggered_rules = []
            
            for rule in rules:
                rule_triggered, rule_contribution = self._evaluate_rule(transaction, rule)
                
                if rule_triggered:
                    total_score += rule_contribution
                    triggered_rules.append({
                        'factor': rule.rule_name,
                        'weight': float(rule.weight),
                        'triggered': True,
                        'description': rule.rule_description
                    })
            
            # Normalize score to 0-1 range
            normalized_score = min(total_score, 1.0)
            
            return normalized_score, triggered_rules
            
        except Exception as e:
            logger.error(f"Rule-based analysis error: {e}")
            return 0.0, []
    
    def _evaluate_rule(self, transaction: Dict[str, Any], rule: FraudRule) -> Tuple[bool, float]:
        """Evaluate a single fraud rule against transaction"""
        try:
            rule_logic = rule.rule_logic
            rule_name = rule.rule_name
            weight = float(rule.weight)
            
            amount = float(transaction.get('amount', 0))
            merchant = str(transaction.get('merchant_id', '')).lower()
            timestamp = transaction.get('timestamp', datetime.now())
            
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # High amount rule
            if rule_name == 'high_amount':
                threshold = rule_logic.get('threshold', 500000)
                if amount > threshold:
                    return True, weight
            
            # Round amount rule
            elif rule_name == 'round_amount':
                round_amounts = rule_logic.get('amounts', [])
                if amount in round_amounts:
                    return True, weight
            
            # Very high amount rule
            elif rule_name == 'very_high_amount':
                threshold = rule_logic.get('threshold', 1000000)
                if amount > threshold:
                    return True, weight
            
            # Risky merchant rule
            elif rule_name == 'risky_merchant':
                categories = rule_logic.get('categories', [])
                if any(category in merchant for category in categories):
                    return True, weight
            
            # Unusual time rule
            elif rule_name == 'unusual_time':
                start_hour = rule_logic.get('start_hour', 23)
                end_hour = rule_logic.get('end_hour', 6)
                hour = timestamp.hour
                
                if start_hour > end_hour:  # Spans midnight
                    if hour >= start_hour or hour <= end_hour:
                        return True, weight
                else:
                    if start_hour <= hour <= end_hour:
                        return True, weight
            
            return False, 0.0
            
        except Exception as e:
            logger.error(f"Rule evaluation error for {rule.rule_name}: {e}")
            return False, 0.0
    
    def _get_velocity_score(self, transaction: Dict[str, Any], db: Session) -> Tuple[float, List[Dict]]:
        """Analyze transaction velocity patterns"""
        try:
            user_id = transaction.get('user_id')
            if not user_id:
                return 0.0, []
            
            # Get user's recent transaction history
            recent_transactions = self.db_manager.get_user_transaction_history(
                db, user_id, days=1  # Last 24 hours
            )
            
            velocity_factors = []
            velocity_score = 0.0
            
            if len(recent_transactions) > 0:
                # Check transaction frequency
                frequency_score = self._analyze_frequency(recent_transactions)
                if frequency_score > 0:
                    velocity_score += frequency_score
                    velocity_factors.append({
                        'factor': 'high_frequency',
                        'weight': frequency_score,
                        'triggered': True,
                        'details': f'{len(recent_transactions)} transactions in 24h'
                    })
                
                # Check amount patterns
                amount_score = self._analyze_amount_patterns(recent_transactions, transaction)
                if amount_score > 0:
                    velocity_score += amount_score
                    velocity_factors.append({
                        'factor': 'unusual_amount_pattern',
                        'weight': amount_score,
                        'triggered': True
                    })
                
                # Check time patterns
                time_score = self._analyze_time_patterns(recent_transactions)
                if time_score > 0:
                    velocity_score += time_score
                    velocity_factors.append({
                        'factor': 'unusual_time_pattern',
                        'weight': time_score,
                        'triggered': True
                    })
            
            # Normalize velocity score
            velocity_score = min(velocity_score, 1.0)
            
            return velocity_score, velocity_factors
            
        except Exception as e:
            logger.error(f"Velocity analysis error: {e}")
            return 0.0, []
    
    def _analyze_frequency(self, transactions: List[Dict]) -> float:
        """Analyze transaction frequency for velocity scoring"""
        # More than 5 transactions in 24 hours is suspicious
        if len(transactions) > 5:
            return min((len(transactions) - 5) * 0.1, 0.5)
        return 0.0
    
    def _analyze_amount_patterns(self, recent_transactions: List[Dict], current_transaction: Dict) -> float:
        """Analyze amount patterns for anomalies"""
        if len(recent_transactions) < 2:
            return 0.0
        
        current_amount = float(current_transaction.get('amount', 0))
        recent_amounts = [float(t['amount']) for t in recent_transactions]
        
        # Check if current amount is significantly different from recent pattern
        avg_recent = sum(recent_amounts) / len(recent_amounts)
        
        if avg_recent > 0:
            ratio = current_amount / avg_recent
            if ratio > 5 or ratio < 0.2:  # 5x higher or 80% lower
                return min(abs(ratio - 1) * 0.1, 0.3)
        
        return 0.0
    
    def _analyze_time_patterns(self, transactions: List[Dict]) -> float:
        """Analyze time patterns for velocity scoring"""
        if len(transactions) < 3:
            return 0.0
        
        # Check for rapid-fire transactions (within 5 minutes of each other)
        timestamps = [t['timestamp'] for t in transactions]
        timestamps.sort()
        
        rapid_count = 0
        for i in range(1, len(timestamps)):
            time_diff = (timestamps[i] - timestamps[i-1]).total_seconds()
            if time_diff < 300:  # Less than 5 minutes
                rapid_count += 1
        
        if rapid_count > 2:
            return min(rapid_count * 0.1, 0.2)
        
        return 0.0
    
    def _make_decision(self, fraud_score: float) -> str:
        """Make fraud decision based on score thresholds"""
        if fraud_score >= self.fraud_threshold_high:
            return 'DECLINE'
        elif fraud_score >= self.fraud_threshold_medium:
            return 'REVIEW'
        else:
            return 'APPROVE'
    
    def _calculate_confidence(self, fraud_score: float, risk_factors: List[Dict]) -> float:
        """Calculate confidence level for the fraud decision"""
        # Base confidence on score extremity and number of risk factors
        score_confidence = abs(fraud_score - 0.5) * 2  # 0 at middle, 1 at extremes
        factor_confidence = min(len(risk_factors) * 0.1, 0.5)  # More factors = higher confidence
        
        total_confidence = min(score_confidence + factor_confidence, 1.0)
        return total_confidence
    
    def update_user_profile(self, user_id: int, transaction: Dict[str, Any], 
                          fraud_result: Dict[str, Any], db: Session):
        """Update user risk profile based on transaction analysis"""
        try:
            user = self.db_manager.get_user(db, user_id)
            if not user:
                return
            
            current_profile = user.risk_profile or {}
            
            # Update transaction count
            current_profile['transaction_count'] = current_profile.get('transaction_count', 0) + 1
            
            # Update average amount
            current_avg = current_profile.get('avg_amount', 0)
            current_count = current_profile['transaction_count']
            new_amount = float(transaction.get('amount', 0))
            
            new_avg = ((current_avg * (current_count - 1)) + new_amount) / current_count
            current_profile['avg_amount'] = round(new_avg, 2)
            
            # Update risk indicators
            fraud_score = fraud_result.get('fraud_score', 0)
            decision = fraud_result.get('decision', 'APPROVE')
            
            # Track fraud history
            fraud_history = current_profile.get('fraud_history', [])
            fraud_history.append({
                'timestamp': datetime.now().isoformat(),
                'fraud_score': fraud_score,
                'decision': decision
            })
            
            # Keep only last 10 fraud assessments
            current_profile['fraud_history'] = fraud_history[-10:]
            
            # Calculate risk level based on recent fraud scores
            recent_scores = [f['fraud_score'] for f in fraud_history[-5:]]
            avg_recent_score = sum(recent_scores) / len(recent_scores) if recent_scores else 0
            
            if avg_recent_score > 0.7:
                current_profile['risk_level'] = 'high'
            elif avg_recent_score > 0.4:
                current_profile['risk_level'] = 'medium'
            else:
                current_profile['risk_level'] = 'low'
            
            # Update last transaction time
            current_profile['last_transaction'] = datetime.now().isoformat()
            
            # Save updated profile
            self.db_manager.update_user_risk_profile(db, user_id, current_profile)
            
            logger.info(f"Updated risk profile for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the fraud detection model"""
        return {
            'engine_version': '2.0.0',
            'rnn_model_loaded': self.rnn_model.model is not None,
            'rnn_model_info': self.rnn_model.get_model_info() if self.rnn_model.model else None,
            'weights': {
                'alpha': self.alpha,
                'beta': self.beta,
                'gamma': self.gamma
            },
            'thresholds': {
                'high': self.fraud_threshold_high,
                'medium': self.fraud_threshold_medium
            }
        }

# Global fraud detection engine instance
fraud_engine = FraudDetectionEngine()

def analyze_transaction_fraud(transaction: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Convenience function to analyze transaction fraud"""
    return fraud_engine.analyze_transaction(transaction, db)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test the fraud detection engine
    sample_transaction = {
        'transaction_id': 'TEST_001',
        'user_id': 1,
        'amount': 750000,
        'merchant_id': 'CASINO_ROYAL',
        'timestamp': datetime.now(),
        'payment_method': 'card',
        'ip_address': '192.168.1.100'
    }
    
    # This would need a real database session in practice
    print("Fraud Detection Engine initialized successfully!")
    print("Model info:", fraud_engine.get_model_info())
