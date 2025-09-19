"""
Database Interface Module
Handles all database operations for the fraud detection system
"""

from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, TIMESTAMP, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import JSONB, INET
from datetime import datetime
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/fraud_detection_db")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    last_login = Column(TIMESTAMP)
    risk_profile = Column(JSONB)
    status = Column(String(20), default='active')
    
    # Relationships
    transactions = relationship("Transaction", back_populates="user")

class Transaction(Base):
    __tablename__ = "transactions"
    
    transaction_id = Column(String(50), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    amount = Column(DECIMAL(15, 2), nullable=False, index=True)
    currency = Column(String(3), default='NGN')
    transaction_type = Column(String(50))
    merchant_id = Column(String(100))
    timestamp = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    payment_method = Column(String(50))
    ip_address = Column(INET)
    device_fingerprint = Column(String(255))
    location_data = Column(JSONB)
    transaction_status = Column(String(20))
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    fraud_assessments = relationship("FraudAssessment", back_populates="transaction")

class FraudAssessment(Base):
    __tablename__ = "fraud_assessments"
    
    assessment_id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(50), ForeignKey("transactions.transaction_id"), nullable=False)
    fraud_score = Column(DECIMAL(5, 4), nullable=False, index=True)
    risk_factors = Column(JSONB)
    model_version = Column(String(20))
    decision = Column(String(20), nullable=False, index=True)
    confidence_level = Column(DECIMAL(5, 4))
    processed_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    transaction = relationship("Transaction", back_populates="fraud_assessments")

class FraudRule(Base):
    __tablename__ = "fraud_rules"
    
    rule_id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(100), nullable=False)
    rule_description = Column(Text)
    rule_logic = Column(JSONB)
    weight = Column(DECIMAL(3, 2))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

class DatabaseManager:
    """Database manager for fraud detection system"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")
    
    def get_db(self) -> Session:
        """Get database session"""
        db = self.SessionLocal()
        try:
            return db
        except Exception as e:
            db.close()
            raise e
    
    def close_db(self, db: Session):
        """Close database session"""
        db.close()
    
    # User operations
    def create_user(self, db: Session, email: str, phone_number: Optional[str] = None,
                   risk_profile: Optional[Dict] = None) -> User:
        """Create a new user"""
        user = User(
            email=email,
            phone_number=phone_number,
            risk_profile=risk_profile or {}
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Created user: {email}")
        return user
    
    def get_user(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.user_id == user_id).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    def update_user_risk_profile(self, db: Session, user_id: int, risk_profile: Dict) -> bool:
        """Update user risk profile"""
        user = self.get_user(db, user_id)
        if user:
            user.risk_profile = risk_profile
            db.commit()
            return True
        return False
    
    # Transaction operations
    def save_transaction(self, db: Session, transaction_data: Dict[str, Any]) -> Transaction:
        """Save a transaction to database"""
        transaction = Transaction(**transaction_data)
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        logger.info(f"Saved transaction: {transaction.transaction_id}")
        return transaction
    
    def get_transaction(self, db: Session, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID"""
        return db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    
    def get_user_transactions(self, db: Session, user_id: int, limit: int = 100) -> List[Transaction]:
        """Get user's recent transactions"""
        return db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).order_by(Transaction.timestamp.desc()).limit(limit).all()
    
    def get_recent_transactions(self, db: Session, limit: int = 100) -> List[Transaction]:
        """Get recent transactions"""
        return db.query(Transaction).order_by(
            Transaction.timestamp.desc()
        ).limit(limit).all()
    
    # Fraud assessment operations
    def save_fraud_assessment(self, db: Session, assessment_data: Dict[str, Any]) -> FraudAssessment:
        """Save fraud assessment to database"""
        assessment = FraudAssessment(**assessment_data)
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        logger.info(f"Saved fraud assessment for transaction: {assessment.transaction_id}")
        return assessment
    
    def get_fraud_assessment(self, db: Session, transaction_id: str) -> Optional[FraudAssessment]:
        """Get fraud assessment for a transaction"""
        return db.query(FraudAssessment).filter(
            FraudAssessment.transaction_id == transaction_id
        ).first()
    
    def get_fraud_assessments_by_decision(self, db: Session, decision: str, limit: int = 100) -> List[FraudAssessment]:
        """Get fraud assessments by decision type"""
        return db.query(FraudAssessment).filter(
            FraudAssessment.decision == decision
        ).order_by(FraudAssessment.processed_at.desc()).limit(limit).all()
    
    # Fraud rules operations
    def get_active_fraud_rules(self, db: Session) -> List[FraudRule]:
        """Get all active fraud rules"""
        return db.query(FraudRule).filter(FraudRule.is_active == True).all()
    
    def create_fraud_rule(self, db: Session, rule_data: Dict[str, Any]) -> FraudRule:
        """Create a new fraud rule"""
        rule = FraudRule(**rule_data)
        db.add(rule)
        db.commit()
        db.refresh(rule)
        logger.info(f"Created fraud rule: {rule.rule_name}")
        return rule
    
    def update_fraud_rule(self, db: Session, rule_id: int, rule_data: Dict[str, Any]) -> bool:
        """Update a fraud rule"""
        rule = db.query(FraudRule).filter(FraudRule.rule_id == rule_id).first()
        if rule:
            for key, value in rule_data.items():
                setattr(rule, key, value)
            db.commit()
            return True
        return False
    
    def deactivate_fraud_rule(self, db: Session, rule_id: int) -> bool:
        """Deactivate a fraud rule"""
        return self.update_fraud_rule(db, rule_id, {'is_active': False})
    
    # Statistics and analytics
    def get_transaction_stats(self, db: Session) -> Dict[str, Any]:
        """Get transaction statistics"""
        total_transactions = db.query(Transaction).count()
        
        # Get fraud assessment stats
        assessments = db.query(FraudAssessment).all()
        approved = len([a for a in assessments if a.decision == 'APPROVE'])
        declined = len([a for a in assessments if a.decision == 'DECLINE'])
        review = len([a for a in assessments if a.decision == 'REVIEW'])
        
        avg_fraud_score = sum(float(a.fraud_score) for a in assessments) / len(assessments) if assessments else 0
        
        return {
            'total_transactions': total_transactions,
            'total_assessments': len(assessments),
            'approved': approved,
            'declined': declined,
            'review': review,
            'approval_rate': round((approved / len(assessments) * 100), 1) if assessments else 0,
            'average_fraud_score': round(avg_fraud_score, 3)
        }
    
    def get_user_transaction_history(self, db: Session, user_id: int, days: int = 30) -> List[Dict]:
        """Get user transaction history for velocity analysis"""
        from sqlalchemy import and_, func
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        transactions = db.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.timestamp >= cutoff_date
            )
        ).order_by(Transaction.timestamp.desc()).all()
        
        return [
            {
                'transaction_id': t.transaction_id,
                'amount': float(t.amount),
                'timestamp': t.timestamp,
                'merchant_id': t.merchant_id,
                'payment_method': t.payment_method
            }
            for t in transactions
        ]
    
    def execute_query(self, db: Session, query: str) -> List[Dict]:
        """Execute custom database query"""
        try:
            result = db.execute(query)
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return []

# Initialize database manager
db_manager = DatabaseManager()

# Dependency for FastAPI
def get_database():
    """Dependency to get database session"""
    db = db_manager.get_db()
    try:
        yield db
    finally:
        db_manager.close_db(db)

# Initialize database (create tables)
def init_database():
    """Initialize database with tables and sample data"""
    try:
        db_manager.create_tables()
        
        # Create sample data if tables are empty
        db = db_manager.get_db()
        try:
            # Check if we have users
            user_count = db.query(User).count()
            if user_count == 0:
                logger.info("Creating sample users...")
                
                sample_users = [
                    {
                        'email': 'test_user_001@example.com',
                        'phone_number': '+2348012345678',
                        'risk_profile': {'risk_level': 'low', 'transaction_count': 150, 'avg_amount': 75000}
                    },
                    {
                        'email': 'test_user_002@example.com', 
                        'phone_number': '+2348012345679',
                        'risk_profile': {'risk_level': 'medium', 'transaction_count': 50, 'avg_amount': 200000}
                    },
                    {
                        'email': 'test_user_003@example.com',
                        'phone_number': '+2348012345680', 
                        'risk_profile': {'risk_level': 'high', 'transaction_count': 10, 'avg_amount': 800000}
                    },
                    {
                        'email': 'admin@fraudsystem.com',
                        'phone_number': '+2348012345681',
                        'risk_profile': {'risk_level': 'admin', 'role': 'administrator'}
                    }
                ]
                
                for user_data in sample_users:
                    db_manager.create_user(db, **user_data)
            
            # Check if we have fraud rules
            rule_count = db.query(FraudRule).count()
            if rule_count == 0:
                logger.info("Creating default fraud rules...")
                
                default_rules = [
                    {
                        'rule_name': 'high_amount',
                        'rule_description': 'High transaction amount rule',
                        'rule_logic': {'threshold': 500000, 'currency': 'NGN'},
                        'weight': 0.6,
                        'is_active': True
                    },
                    {
                        'rule_name': 'round_amount',
                        'rule_description': 'Suspicious round amounts',
                        'rule_logic': {'amounts': [100000, 200000, 500000, 1000000, 2000000]},
                        'weight': 0.3,
                        'is_active': True
                    },
                    {
                        'rule_name': 'very_high_amount',
                        'rule_description': 'Very high transaction amounts',
                        'rule_logic': {'threshold': 1000000, 'currency': 'NGN'},
                        'weight': 0.5,
                        'is_active': True
                    },
                    {
                        'rule_name': 'risky_merchant',
                        'rule_description': 'Risky merchant categories',
                        'rule_logic': {'categories': ['casino', 'gambling', 'crypto', 'betting']},
                        'weight': 0.4,
                        'is_active': True
                    },
                    {
                        'rule_name': 'unusual_time',
                        'rule_description': 'Unusual transaction times',
                        'rule_logic': {'start_hour': 23, 'end_hour': 6},
                        'weight': 0.2,
                        'is_active': True
                    },
                    {
                        'rule_name': 'velocity_check',
                        'rule_description': 'Transaction velocity analysis',
                        'rule_logic': {'max_transactions': 5, 'time_window': 300},
                        'weight': 0.7,
                        'is_active': True
                    }
                ]
                
                for rule_data in default_rules:
                    db_manager.create_fraud_rule(db, rule_data)
                    
        finally:
            db_manager.close_db(db)
            
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_database()
    print("Database initialized successfully!")
