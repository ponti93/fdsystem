from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import uvicorn
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import os
import uuid
from dotenv import load_dotenv

# Import our custom modules
from db_interface import get_database, init_database, db_manager
from transaction_processor import process_transaction, transaction_processor
from fraud_detector import fraud_engine
from api_handlers import process_payment_webhook, authenticate_admin_request, admin_handler
from ml_models.dataset_handler import IEEEFraudDatasetHandler
from ml_models.rnn_fraud_model import FraudDetectionRNN, FraudDetectionPreprocessor
from payment_gateways.flutterwave_client import flutterwave_client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Advanced Fraud Detection System",
    description="Real-time fraud detection system with RNN-based ML models, rule-based analysis, and payment gateway integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()


# Helper function for consistent response formatting
def format_response(data: Any, status: str = "success") -> Dict[str, Any]:
    """Format API responses consistently"""
    return {
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and load ML models on startup"""
    try:
        logger.info("Initializing fraud detection system...")

        # Initialize database
        init_database()

        # Create models directory if it doesn't exist
        os.makedirs("./models", exist_ok=True)

        # Try to load ML model
        try:
            if fraud_engine.rnn_model.load_model():
                fraud_engine.preprocessor = FraudDetectionPreprocessor(fraud_engine.rnn_model)
                logger.info("RNN fraud detection model loaded successfully")
            else:
                logger.info("No pre-trained model found, using rule-based detection")
        except Exception as e:
            logger.warning(f"Could not load existing model: {e}. Using rule-based detection.")

        logger.info("Fraud detection system initialized successfully")

    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise


# Authentication dependency
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    user = authenticate_admin_request(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user


# Public endpoints
@app.get("/api/info")
def api_info():
    """API information endpoint"""
    return {
        "message": "Advanced Fraud Detection System API",
        "version": "2.0.0",
        "features": [
            "RNN-based fraud detection",
            "Real-time transaction processing",
            "Payment gateway integration",
            "Advanced analytics and reporting",
            "Rule-based fraud detection",
            "Velocity analysis"
        ],
        "endpoints": {
            "transactions": "/api/transactions",
            "stats": "/api/stats",
            "webhooks": "/api/webhooks",
            "admin": "/api/admin",
            "ml": "/api/ml",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected",
        "ml_model": "loaded" if fraud_engine.rnn_model.model else "not_loaded"
    }


# Transaction endpoints
@app.post("/api/transactions")
def create_transaction(transaction: Dict[str, Any], db: Session = Depends(get_database)):
    """Create and analyze a new transaction"""
    try:
        result = process_transaction(transaction, db)
        return admin_handler.format_response(result)
    except Exception as e:
        return admin_handler.handle_error(e, "create_transaction")


@app.get("/api/transactions")
def get_transactions(limit: int = 100, db: Session = Depends(get_database)):
    """Get recent transactions"""
    try:
        transactions = db_manager.get_recent_transactions(db, limit)

        formatted_transactions = []
        for tx in transactions:
            fraud_assessment = db_manager.get_fraud_assessment(db, tx.transaction_id)

            tx_data = {
                "transaction_id": tx.transaction_id,
                "user_id": tx.user_id,
                "amount": float(tx.amount),
                "currency": tx.currency,
                "merchant_id": tx.merchant_id,
                "timestamp": tx.timestamp.isoformat(),
                "status": tx.transaction_status,
                "payment_method": tx.payment_method
            }

            if fraud_assessment:
                tx_data["fraud_assessment"] = {
                    "fraud_score": float(fraud_assessment.fraud_score),
                    "decision": fraud_assessment.decision,
                    "risk_factors": fraud_assessment.risk_factors,
                    "confidence_level": float(fraud_assessment.confidence_level) if fraud_assessment.confidence_level else None
                }

            formatted_transactions.append(tx_data)

        return admin_handler.format_response(formatted_transactions)
    except Exception as e:
        return admin_handler.handle_error(e, "get_transactions")


@app.get("/api/transactions/{transaction_id}")
def get_transaction(transaction_id: str, db: Session = Depends(get_database)):
    """Get a specific transaction with fraud assessment"""
    try:
        result = transaction_processor.get_transaction_details(transaction_id, db)
        if not result:
            raise HTTPException(status_code=404, detail="Transaction not found")

        return admin_handler.format_response(result)
    except HTTPException:
        raise
    except Exception as e:
        return admin_handler.handle_error(e, "get_transaction")



@app.get("/api/stats")
def get_stats(db: Session = Depends(get_database)):
    """Get comprehensive system statistics"""
    try:
        stats = db_manager.get_transaction_stats(db)
        
        # Add model information
        stats['model_info'] = fraud_engine.get_model_info()
        stats['timestamp'] = datetime.now().isoformat()
        
        return admin_handler.format_response(stats)
    except Exception as e:
        return admin_handler.handle_error(e, "get_stats")

# Test endpoints (for development)
@app.post("/api/test-scenarios")
def run_test_scenarios(db: Session = Depends(get_database)):
    """Run predefined test scenarios"""
    try:
        scenarios = [
            {'amount': 50000, 'user_id': 1, 'merchant_id': 'Coffee Shop', 'description': 'Normal transaction'},
            {'amount': 150000, 'user_id': 2, 'merchant_id': 'Electronics Store', 'description': 'Medium amount'},
            {'amount': 600000, 'user_id': 3, 'merchant_id': 'Luxury Store', 'description': 'High amount'},
            {'amount': 1000000, 'user_id': 1, 'merchant_id': 'Car Dealer', 'description': 'Round amount (1M)'},
            {'amount': 100000, 'user_id': 2, 'merchant_id': 'Casino Resort', 'description': 'Risky merchant'},
            {'amount': 2000000, 'user_id': 3, 'merchant_id': 'Real Estate', 'description': 'Very high amount'}
        ]
        
        results = []
        for scenario in scenarios:
            result = process_transaction(scenario, db)
            result['description'] = scenario['description']
            results.append(result)
        
        return admin_handler.format_response({
            'message': f'Generated {len(results)} test transactions',
            'results': results
        })
    except Exception as e:
        return admin_handler.handle_error(e, "run_test_scenarios")

# Webhook endpoints
@app.post("/api/webhooks/paystack")
async def paystack_webhook(request: Request, x_paystack_signature: str = Header(None)):
    """Handle Paystack webhook"""
    try:
        payload = await request.json()
        headers = {'x-paystack-signature': x_paystack_signature}
        
        result = process_payment_webhook(payload, headers, 'paystack')
        return admin_handler.format_response(result)
    except Exception as e:
        return admin_handler.handle_error(e, "paystack_webhook")

@app.post("/api/webhooks/flutterwave")
async def flutterwave_webhook(request: Request, verif_hash: str = Header(None)):
    """Handle Flutterwave webhook"""
    try:
        payload = await request.json()
        headers = {'verif-hash': verif_hash}
        
        result = process_payment_webhook(payload, headers, 'flutterwave')
        return admin_handler.format_response(result)
    except Exception as e:
        return admin_handler.handle_error(e, "flutterwave_webhook")

# Admin endpoints (require authentication)
@app.get("/api/admin/users")
def get_users(current_user: dict = Depends(get_current_user), db: Session = Depends(get_database)):
    """Get all users (admin only)"""
    try:
        if 'admin' not in current_user.get('permissions', []):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        from db_interface import User
        users = db.query(User).all()
        user_list = []
        
        for user in users:
            user_data = {
                'user_id': user.user_id,
                'email': user.email,
                'phone_number': user.phone_number,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'risk_profile': user.risk_profile,
                'status': user.status
            }
            user_list.append(user_data)
        
        return admin_handler.format_response(user_list)
    except HTTPException:
        raise
    except Exception as e:
        return admin_handler.handle_error(e, "get_users")

@app.get("/api/admin/fraud-rules")
def get_fraud_rules(current_user: dict = Depends(get_current_user), db: Session = Depends(get_database)):
    """Get all fraud rules (admin only)"""
    try:
        if 'admin' not in current_user.get('permissions', []):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        rules = db_manager.get_active_fraud_rules(db)
        rule_list = []
        
        for rule in rules:
            rule_data = {
                'rule_id': rule.rule_id,
                'rule_name': rule.rule_name,
                'rule_description': rule.rule_description,
                'rule_logic': rule.rule_logic,
                'weight': float(rule.weight) if rule.weight else None,
                'is_active': rule.is_active,
                'created_at': rule.created_at.isoformat()
            }
            rule_list.append(rule_data)
        
        return admin_handler.format_response(rule_list)
    except HTTPException:
        raise
    except Exception as e:
        return admin_handler.handle_error(e, "get_fraud_rules")

@app.post("/api/admin/fraud-rules")
def create_fraud_rule(rule_data: Dict[str, Any], current_user: dict = Depends(get_current_user), 
                     db: Session = Depends(get_database)):
    """Create a new fraud rule (admin only)"""
    try:
        if 'admin' not in current_user.get('permissions', []):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        rule = db_manager.create_fraud_rule(db, rule_data)
        
        return admin_handler.format_response({
            'rule_id': rule.rule_id,
            'message': 'Fraud rule created successfully'
        })
    except HTTPException:
        raise
    except Exception as e:
        return admin_handler.handle_error(e, "create_fraud_rule")

@app.get("/api/admin/analytics")
def get_analytics(current_user: dict = Depends(get_current_user), db: Session = Depends(get_database)):
    """Get advanced analytics (admin only)"""
    try:
        if 'read' not in current_user.get('permissions', []):
            raise HTTPException(status_code=403, detail="Read access required")
        
        # Get comprehensive analytics
        stats = db_manager.get_transaction_stats(db)
        
        # Add fraud trend analysis
        from db_interface import FraudAssessment
        fraud_assessments = db.query(FraudAssessment).order_by(
            FraudAssessment.processed_at.desc()
        ).limit(1000).all()
        
        # Calculate trends
        decisions = [a.decision for a in fraud_assessments]
        fraud_scores = [float(a.fraud_score) for a in fraud_assessments]
        
        analytics = {
            **stats,
            'fraud_trends': {
                'recent_avg_score': sum(fraud_scores[:100]) / min(100, len(fraud_scores)) if fraud_scores else 0,
                'decision_distribution': {
                    'APPROVE': decisions.count('APPROVE'),
                    'DECLINE': decisions.count('DECLINE'),
                    'REVIEW': decisions.count('REVIEW')
                },
                'high_risk_transactions': len([s for s in fraud_scores if s > 0.7]),
                'total_analyzed': len(fraud_assessments)
            },
            'model_performance': fraud_engine.get_model_info()
        }
        
        return admin_handler.format_response(analytics)
    except HTTPException:
        raise
    except Exception as e:
        return admin_handler.handle_error(e, "get_analytics")

# ML Model endpoints
@app.get("/api/ml/model-info")
def get_model_info():
    """Get ML model information"""
    try:
        return admin_handler.format_response(fraud_engine.get_model_info())
    except Exception as e:
        return admin_handler.handle_error(e, "get_model_info")

@app.post("/api/ml/train-model")
def train_model(current_user: dict = Depends(get_current_user)):
    """Train the RNN fraud detection model (admin only)"""
    try:
        if 'admin' not in current_user.get('permissions', []):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Initialize dataset handler
        dataset_handler = IEEEFraudDatasetHandler()
        
        # Get training data (will use sample data if real dataset not available)
        training_data = dataset_handler.get_training_data()
        
        # Train the model
        model = FraudDetectionRNN()
        results = model.train(
            training_data['X_train'],
            training_data['y_train'],
            training_data['X_val'],
            training_data['y_val'],
            epochs=10,  # Reduced for demo
            batch_size=256
        )
        
        # Save the trained model
        model.scaler = training_data['scaler']
        model.label_encoders = training_data['label_encoders']
        model.feature_names = training_data['feature_names']
        model.save_model()
        
        # Debug: Log the training results structure
        logger.info(f"Training results keys: {list(results.keys())}")
        if 'final_val_metrics' in results:
            logger.info(f"Final validation metrics: {results['final_val_metrics']}")
        
        # Update the fraud engine with the new model
        fraud_engine.rnn_model = model
        fraud_engine.preprocessor = FraudDetectionPreprocessor(model)
        logger.info("Fraud engine updated with newly trained model")
        
        return admin_handler.format_response({
            'message': 'Model training completed successfully',
            'training_results': {
                'final_val_auc': results.get('final_val_metrics', {}).get('auc', 'N/A'),
                'final_val_accuracy': results.get('final_val_metrics', {}).get('accuracy', 'N/A'),
                'training_samples': len(training_data['X_train']),
                'validation_samples': len(training_data['X_val']),
                'model_saved': True,
                'model_loaded_in_engine': True
            }
        })
    except HTTPException:
        raise
    except Exception as e:
        return admin_handler.handle_error(e, "train_model")

@app.delete("/api/admin/transactions")
def clear_transactions(current_user: dict = Depends(get_current_user), db: Session = Depends(get_database)):
    """Clear all transactions (admin only - for testing)"""
    try:
        if 'admin' not in current_user.get('permissions', []):
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Delete all fraud assessments first (due to foreign key constraint)
        from db_interface import FraudAssessment, Transaction
        assessment_count = db.query(FraudAssessment).count()
        db.query(FraudAssessment).delete()
        
        # Delete all transactions
        transaction_count = db.query(Transaction).count()
        db.query(Transaction).delete()
        
        db.commit()
        
        return admin_handler.format_response({
            'message': f'Cleared {transaction_count} transactions and {assessment_count} fraud assessments'
        })
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        return admin_handler.handle_error(e, "clear_transactions")

# Flutterwave Integration Endpoints
@app.post("/api/flutterwave/create-payment-link")
def create_flutterwave_payment_link(transaction_data: Dict[str, Any]):
    """Create a Flutterwave payment link for testing"""
    try:
        # Simulate payment link creation (in real scenario, this would call Flutterwave API)
        tx_ref = f"FLW_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # For testing, we'll create a mock payment link
        payment_link = f"https://checkout.flutterwave.com/v3/hosted/pay/{tx_ref}"
        
        result = {
            'status': 'success',
            'payment_link': payment_link,
            'tx_ref': tx_ref,
            'message': 'Payment link created successfully (Test Mode)',
            'amount': transaction_data.get('amount'),
            'currency': transaction_data.get('currency', 'NGN'),
            'customer': {
                'email': transaction_data.get('email'),
                'phone': transaction_data.get('phone'),
                'name': transaction_data.get('customer_name')
            }
        }
        
        logger.info(f"Created Flutterwave payment link: {tx_ref}")
        return format_response(result)
        
    except Exception as e:
        logger.error(f"Error creating payment link: {e}")
        return format_response({'error': str(e)}, 'error')

@app.post("/api/flutterwave/test-webhook")
def test_flutterwave_webhook(transaction_data: Dict[str, Any]):
    """Simulate Flutterwave webhook for testing"""
    try:
        # Create realistic webhook payload
        tx_ref = f"FLW_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        webhook_payload = {
            "event": "charge.completed",
            "data": {
                "id": 12345678,
                "tx_ref": tx_ref,
                "flw_ref": f"FLW-{uuid.uuid4().hex[:10]}",
                "device_fingerprint": f"device_{uuid.uuid4().hex[:8]}",
                "amount": transaction_data.get('amount', 100000),
                "currency": transaction_data.get('currency', 'NGN'),
                "charged_amount": transaction_data.get('amount', 100000) * 0.015,
                "app_fee": transaction_data.get('amount', 100000) * 0.015,
                "merchant_fee": 0,
                "processor_response": "Approved by Financial Institution",
                "auth_model": "PIN",
                "ip": transaction_data.get('ip_address', '192.168.1.100'),
                "narration": f"Payment to {transaction_data.get('merchant_id', 'Test Merchant')}",
                "status": "successful",
                "payment_type": transaction_data.get('payment_method', 'card'),
                "created_at": datetime.now().isoformat(),
                "customer": {
                    "id": transaction_data.get('user_id', 1),
                    "name": transaction_data.get('customer_name', 'Test Customer'),
                    "phone_number": transaction_data.get('phone', '+2348012345678'),
                    "email": transaction_data.get('email', 'test@example.com'),
                    "created_at": datetime.now().isoformat()
                },
                "card": {
                    "first_6digits": "539983",
                    "last_4digits": "0002",
                    "issuer": "MASTERCARD CREDIT",
                    "country": "NG",
                    "type": "MASTERCARD",
                    "expiry": "12/26"
                },
                "meta": {
                    "merchant_id": transaction_data.get('merchant_id', 'TEST_MERCHANT'),
                    "user_id": transaction_data.get('user_id', 1),
                    "payment_method": transaction_data.get('payment_method', 'card')
                }
            }
        }
        
        # Process the webhook through fraud detection using the real ML engine
        flw_transaction = {
            'transaction_id': tx_ref,
            'user_id': transaction_data.get('user_id', 1),
            'amount': transaction_data.get('amount', 100000),
            'currency': transaction_data.get('currency', 'NGN'),
            'merchant_id': transaction_data.get('merchant_id', 'FLUTTERWAVE'),
            'payment_method': 'card',
            'ip_address': transaction_data.get('ip_address', '192.168.1.100'),
            'email': transaction_data.get('email', 'test@example.com'),
            'phone': transaction_data.get('phone', '+2348012345678')
        }
        
        # Process through the advanced ML fraud detection
        db = next(get_database())
        try:
            fraud_result = process_transaction(flw_transaction, db)
            
            logger.info(f"Processed Flutterwave webhook: {tx_ref} - {fraud_result.get('fraud_analysis', {}).get('decision')}")
            
            return format_response({
                'message': 'Flutterwave webhook processed successfully',
                'webhook_payload': webhook_payload,
                'fraud_analysis': fraud_result.get('fraud_analysis'),
                'transaction_id': fraud_result.get('transaction_id'),
                'processing_result': fraud_result
            })
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error processing Flutterwave webhook: {e}")
        return format_response({'error': str(e)}, 'error')

@app.get("/api/flutterwave/verify/{transaction_id}")
def verify_flutterwave_transaction(transaction_id: str):
    """Verify a Flutterwave transaction"""
    try:
        # In real implementation, this would call Flutterwave API
        # For testing, we'll return mock verification data
        
        result = {
            'status': 'success',
            'data': {
                'tx_ref': transaction_id,
                'status': 'successful',
                'amount': 100000,
                'currency': 'NGN',
                'customer': {
                    'email': 'test@example.com'
                },
                'verification_status': 'verified'
            }
        }
        
        return format_response(result)
    except Exception as e:
        logger.error(f"Error verifying transaction: {e}")
        return format_response({'error': str(e)}, 'error')

# Catch-all route for React Router (SPA routing)
@app.get("/{full_path:path}")
def serve_react_app(full_path: str):
    """Serve React app for all non-API routes (SPA routing support)"""
    # Skip API routes
    if full_path.startswith("api/") or full_path.startswith("docs"):
        raise HTTPException(status_code=404, detail="Not Found")
    
    # Check if static directory exists
    if os.path.exists("./static"):
        # Serve index.html for all other routes (React Router will handle routing)
        from fastapi.responses import FileResponse
        return FileResponse("./static/index.html")
    else:
        raise HTTPException(status_code=404, detail="Frontend not available")

# Mount static files for assets (CSS, JS, images) - this should be LAST
# Check if static directory exists (for Docker deployment)
import os
if os.path.exists("./static"):
    # Mount static assets directory - React expects /static/js/... and /static/css/...
    app.mount("/static", StaticFiles(directory="static"), name="static_assets")
    print("📱 Frontend will be served from: http://localhost:8000")
    print("📁 Static assets mounted at: /static")
else:
    print("📱 Frontend static files not found - running in API-only mode")

if __name__ == "__main__":
    print("🚀 Starting Advanced Fraud Detection System")
    print("📊 Backend API available at: http://localhost:8000/api")
    print("📚 API docs available at: http://localhost:8000/docs")
    print("🔐 Use 'admin_token123' for admin access or 'analyst_token123' for analyst access")
    uvicorn.run(app, host="0.0.0.0", port=8000)
