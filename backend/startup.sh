#!/bin/bash

# Startup script for Fraud Detection System
echo "🚀 Starting Fraud Detection System..."

# Create models directory if it doesn't exist
mkdir -p ./models

# Check if model exists, if not train it
if [ ! -f "./models/fraud_detection_model.h5" ]; then
    echo "📊 No pre-trained model found, training new model..."
    python -c "
from ml_models.rnn_fraud_model import RNNFraudModel
from ml_models.dataset_handler import FraudDatasetHandler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Initialize model
    model = RNNFraudModel()
    
    # Load and prepare dataset
    dataset_handler = FraudDatasetHandler()
    training_data = dataset_handler.load_training_data()
    
    if training_data:
        logger.info('Training model with dataset...')
        results = model.train(
            X_train=training_data['X_train'],
            y_train=training_data['y_train'],
            X_val=training_data['X_val'],
            y_val=training_data['y_val']
        )
        
        # Save the trained model
        model.save_model('./models/fraud_detection_model.h5')
        logger.info('Model training completed and saved successfully!')
    else:
        logger.warning('No training data available, using rule-based detection only')
        
except Exception as e:
    logger.error(f'Error during model training: {e}')
    logger.info('Continuing with rule-based detection only')
"
else
    echo "✅ Pre-trained model found, skipping training"
fi

# Start the FastAPI application
echo "🌐 Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
