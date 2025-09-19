"""
RNN-based Fraud Detection Model
Implementation of LSTM-based fraud detection as per system specifications
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, Optional
import joblib
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FraudDetectionRNN:
    """
    RNN-based fraud detection model following the system specifications:
    - Input Layer: 50 features (transaction attributes, user behavior, temporal features)
    - Hidden Layers: 3 LSTM layers with 128, 64, and 32 neurons respectively
    - Dropout Layers: 0.3 dropout rate between LSTM layers
    - Output Layer: Single neuron with sigmoid activation
    - Loss Function: Binary Cross-entropy
    - Optimizer: Adam with learning rate = 0.001
    """
    
    def __init__(self, sequence_length: int = 10, n_features: int = 50):
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.model = None
        self.scaler = None
        self.label_encoders = None
        self.feature_names = None
        self.model_version = "v1.0.0"
        self.training_history = None
        
    def build_model(self) -> keras.Model:
        """Build the RNN model architecture as per specifications"""
        logger.info("Building RNN fraud detection model...")
        
        model = keras.Sequential([
            # Input layer - expects sequences of 50 features
            layers.Input(shape=(self.sequence_length, self.n_features)),
            
            # First LSTM layer - 128 neurons, return sequences for next LSTM
            layers.LSTM(128, return_sequences=True, name='lstm_1'),
            layers.Dropout(0.3, name='dropout_1'),
            
            # Second LSTM layer - 64 neurons, return sequences for next LSTM
            layers.LSTM(64, return_sequences=True, name='lstm_2'),
            layers.Dropout(0.3, name='dropout_2'),
            
            # Third LSTM layer - 32 neurons, don't return sequences (final LSTM)
            layers.LSTM(32, return_sequences=False, name='lstm_3'),
            layers.Dropout(0.3, name='dropout_3'),
            
            # Output layer - single neuron with sigmoid activation
            layers.Dense(1, activation='sigmoid', name='output')
        ])
        
        # Compile with Adam optimizer and binary crossentropy loss
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall', 'auc']
        )
        
        self.model = model
        
        # Print model summary
        logger.info("Model architecture:")
        model.summary()
        
        return model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray, y_val: np.ndarray,
              epochs: int = 50, batch_size: int = 256,
              early_stopping_patience: int = 10) -> Dict[str, Any]:
        """Train the RNN model"""
        
        if self.model is None:
            self.build_model()
        
        logger.info(f"Training model with {len(X_train)} samples...")
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=early_stopping_patience,
                restore_best_weights=True,
                verbose=1
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6,
                verbose=1
            ),
            keras.callbacks.ModelCheckpoint(
                filepath='./models/best_fraud_model.h5',
                monitor='val_auc',
                save_best_only=True,
                mode='max',
                verbose=1
            )
        ]
        
        # Create models directory
        os.makedirs('./models', exist_ok=True)
        
        # Train the model
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        self.training_history = history.history
        
        # Evaluate final model
        train_metrics = self.model.evaluate(X_train, y_train, verbose=0)
        val_metrics = self.model.evaluate(X_val, y_val, verbose=0)
        
        results = {
            'training_history': history.history,
            'final_train_metrics': dict(zip(self.model.metrics_names, train_metrics)),
            'final_val_metrics': dict(zip(self.model.metrics_names, val_metrics)),
            'model_version': self.model_version,
            'training_completed': datetime.now().isoformat()
        }
        
        logger.info(f"Training completed. Final validation AUC: {val_metrics[-1]:.4f}")
        
        return results
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions on new data"""
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        
        predictions = self.model.predict(X, verbose=0)
        return predictions.flatten()
    
    def predict_fraud_score(self, transaction_sequence: np.ndarray) -> float:
        """Predict fraud score for a single transaction sequence"""
        if len(transaction_sequence.shape) == 2:
            # Add batch dimension if not present
            transaction_sequence = np.expand_dims(transaction_sequence, axis=0)
        
        score = self.predict(transaction_sequence)[0]
        return float(score)
    
    def save_model(self, model_path: str = './models/fraud_detection_model.h5',
                   metadata_path: str = './models/model_metadata.joblib'):
        """Save the trained model and metadata"""
        if self.model is None:
            raise ValueError("No model to save")
        
        # Save the Keras model
        self.model.save(model_path)
        
        # Save metadata
        metadata = {
            'model_version': self.model_version,
            'sequence_length': self.sequence_length,
            'n_features': self.n_features,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'feature_names': self.feature_names,
            'training_history': self.training_history,
            'saved_at': datetime.now().isoformat()
        }
        
        joblib.dump(metadata, metadata_path)
        
        logger.info(f"Model saved to {model_path}")
        logger.info(f"Metadata saved to {metadata_path}")
    
    def load_model(self, model_path: str = './models/fraud_detection_model.h5',
                   metadata_path: str = './models/model_metadata.joblib'):
        """Load a trained model and metadata"""
        try:
            # Load the Keras model
            self.model = keras.models.load_model(model_path)
            
            # Load metadata
            metadata = joblib.load(metadata_path)
            self.model_version = metadata['model_version']
            self.sequence_length = metadata['sequence_length']
            self.n_features = metadata['n_features']
            self.scaler = metadata['scaler']
            self.label_encoders = metadata['label_encoders']
            self.feature_names = metadata['feature_names']
            self.training_history = metadata['training_history']
            
            logger.info(f"Model loaded from {model_path}")
            logger.info(f"Model version: {self.model_version}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and metadata"""
        if self.model is None:
            return {"status": "No model loaded"}
        
        return {
            "model_version": self.model_version,
            "sequence_length": self.sequence_length,
            "n_features": self.n_features,
            "total_parameters": self.model.count_params(),
            "model_architecture": [layer.name for layer in self.model.layers],
            "feature_names": self.feature_names[:10] if self.feature_names else None,  # First 10 features
            "training_completed": self.training_history is not None
        }

class FraudDetectionPreprocessor:
    """Preprocessor for preparing transaction data for RNN model"""
    
    def __init__(self, model: FraudDetectionRNN):
        self.model = model
        self.transaction_buffer = []  # Buffer to store recent transactions for sequence creation
        
    def prepare_transaction_features(self, transaction: Dict[str, Any]) -> np.ndarray:
        """Prepare features from a single transaction"""
        
        # Extract and engineer features based on transaction data
        features = []
        
        # Basic transaction features
        features.extend([
            float(transaction.get('amount', 0)),
            float(transaction.get('user_id', 0)),
            self._encode_categorical(transaction.get('payment_method', 'unknown')),
            self._encode_categorical(transaction.get('merchant_id', 'unknown')),
            self._encode_categorical(transaction.get('currency', 'NGN')),
        ])
        
        # Time-based features
        timestamp = transaction.get('timestamp', datetime.now())
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        
        features.extend([
            timestamp.hour,
            timestamp.weekday(),
            timestamp.day,
            timestamp.month,
        ])
        
        # Device and location features
        features.extend([
            self._encode_categorical(transaction.get('device_fingerprint', 'unknown')),
            self._encode_ip_address(transaction.get('ip_address')),
        ])
        
        # Pad or truncate to exactly 50 features
        while len(features) < 50:
            features.append(0.0)
        features = features[:50]
        
        return np.array(features, dtype=np.float32)
    
    def _encode_categorical(self, value: str) -> float:
        """Simple categorical encoding"""
        if value is None:
            return 0.0
        return float(hash(str(value)) % 1000) / 1000.0
    
    def _encode_ip_address(self, ip_address: Optional[str]) -> float:
        """Encode IP address to numerical value"""
        if not ip_address:
            return 0.0
        try:
            parts = ip_address.split('.')
            return sum(int(part) * (256 ** (3-i)) for i, part in enumerate(parts)) / (256**4)
        except:
            return 0.0
    
    def add_transaction(self, transaction: Dict[str, Any]) -> Optional[np.ndarray]:
        """Add transaction to buffer and return sequence if ready"""
        
        # Prepare features for this transaction
        features = self.prepare_transaction_features(transaction)
        
        # Add to buffer
        self.transaction_buffer.append(features)
        
        # Keep only the last sequence_length transactions
        if len(self.transaction_buffer) > self.model.sequence_length:
            self.transaction_buffer.pop(0)
        
        # Return sequence if we have enough transactions
        if len(self.transaction_buffer) == self.model.sequence_length:
            sequence = np.array(self.transaction_buffer)
            return np.expand_dims(sequence, axis=0)  # Add batch dimension
        
        return None

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create sample data for testing
    sequence_length = 10
    n_features = 50
    n_samples = 1000
    
    # Generate sample sequences
    X = np.random.random((n_samples, sequence_length, n_features))
    y = np.random.randint(0, 2, n_samples)
    
    # Split data
    split_idx = int(0.8 * n_samples)
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]
    
    # Create and train model
    model = FraudDetectionRNN(sequence_length=sequence_length, n_features=n_features)
    
    # Train for a few epochs (for testing)
    results = model.train(X_train, y_train, X_val, y_val, epochs=5, batch_size=32)
    
    print("Training completed!")
    print(f"Final validation AUC: {results['final_val_metrics']['auc']:.4f}")
    
    # Test prediction
    test_sequence = X_val[:1]
    prediction = model.predict_fraud_score(test_sequence)
    print(f"Sample prediction: {prediction:.4f}")
    
    # Save model
    model.save_model()
    
    # Test loading
    new_model = FraudDetectionRNN()
    if new_model.load_model():
        print("Model loaded successfully!")
        print(new_model.get_model_info())
