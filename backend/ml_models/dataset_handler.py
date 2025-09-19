"""
IEEE-CIS Fraud Detection Dataset Handler
Handles downloading, preprocessing, and feature engineering for the IEEE-CIS dataset
"""

import pandas as pd
import numpy as np
import os
import requests
from typing import Tuple, Optional, Dict, Any
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import logging

logger = logging.getLogger(__name__)

class IEEEFraudDatasetHandler:
    """Handler for IEEE-CIS Fraud Detection Dataset"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.train_transaction = None
        self.train_identity = None
        self.test_transaction = None
        self.test_identity = None
        self.processed_features = None
        self.target = None
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Dataset URLs (you would need to download these from Kaggle)
        self.dataset_info = {
            "train_transaction": "train_transaction.csv",
            "train_identity": "train_identity.csv", 
            "test_transaction": "test_transaction.csv",
            "test_identity": "test_identity.csv"
        }
    
    def load_dataset(self) -> bool:
        """Load the IEEE-CIS fraud detection dataset"""
        try:
            # Load training data
            train_tx_path = os.path.join(self.data_dir, self.dataset_info["train_transaction"])
            train_id_path = os.path.join(self.data_dir, self.dataset_info["train_identity"])
            
            if os.path.exists(train_tx_path):
                logger.info("Loading IEEE-CIS fraud detection dataset...")
                self.train_transaction = pd.read_csv(train_tx_path)
                logger.info(f"Loaded train_transaction: {self.train_transaction.shape}")
                
                if os.path.exists(train_id_path):
                    self.train_identity = pd.read_csv(train_id_path)
                    logger.info(f"Loaded train_identity: {self.train_identity.shape}")
                
                return True
            else:
                logger.warning("IEEE-CIS dataset not found. Please download from Kaggle.")
                return False
                
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            return False
    
    def create_sample_dataset(self) -> pd.DataFrame:
        """Create a sample dataset with IEEE-CIS like structure for development"""
        logger.info("Creating sample IEEE-CIS like dataset for development...")
        
        np.random.seed(42)
        n_samples = 10000
        
        # Create sample transaction data
        data = {
            'TransactionID': range(1, n_samples + 1),
            'isFraud': np.random.choice([0, 1], n_samples, p=[0.965, 0.035]),  # ~3.5% fraud rate
            'TransactionDT': np.random.randint(0, 15724800, n_samples),  # Time delta
            'TransactionAmt': np.random.lognormal(4, 1.5, n_samples),  # Log-normal distribution
            
            # Payment type features
            'ProductCD': np.random.choice(['W', 'C', 'R', 'H', 'S'], n_samples),
            'card1': np.random.randint(1000, 20000, n_samples),
            'card2': np.random.choice([100, 200, 300, 400, 500], n_samples),
            'card3': np.random.randint(100, 200, n_samples),
            'card4': np.random.choice(['visa', 'mastercard', 'american express', 'discover'], n_samples),
            'card5': np.random.randint(100, 300, n_samples),
            'card6': np.random.choice(['debit', 'credit'], n_samples),
            
            # Address features
            'addr1': np.random.randint(100, 500, n_samples),
            'addr2': np.random.randint(10, 100, n_samples),
            
            # Distance features
            'dist1': np.random.exponential(50, n_samples),
            'dist2': np.random.exponential(50, n_samples),
            
            # Email domain features
            'P_emaildomain': np.random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', None], 
                                            n_samples, p=[0.3, 0.2, 0.15, 0.1, 0.25]),
            'R_emaildomain': np.random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', None], 
                                            n_samples, p=[0.3, 0.2, 0.15, 0.1, 0.25]),
            
            # Device info
            'DeviceType': np.random.choice(['desktop', 'mobile'], n_samples, p=[0.6, 0.4]),
            'DeviceInfo': np.random.choice(['Windows', 'iOS', 'Android', 'MacOS'], n_samples),
        }
        
        # Add C features (anonymized features)
        for i in range(1, 15):
            data[f'C{i}'] = np.random.normal(0, 1, n_samples)
        
        # Add D features (time-based features)
        for i in range(1, 16):
            data[f'D{i}'] = np.random.exponential(1, n_samples)
        
        # Add M features (match features)
        for i in range(1, 10):
            data[f'M{i}'] = np.random.choice(['T', 'F', None], n_samples, p=[0.3, 0.3, 0.4])
        
        # Add V features (Vesta engineered features)
        for i in range(1, 340):
            if i <= 11:  # V1-V11 are categorical
                data[f'V{i}'] = np.random.choice([0, 1, 2, 3, None], n_samples, p=[0.2, 0.2, 0.2, 0.2, 0.2])
            else:  # V12+ are numerical
                data[f'V{i}'] = np.random.normal(0, 1, n_samples)
        
        df = pd.DataFrame(data)
        
        # Make fraud transactions more extreme in some features
        fraud_mask = df['isFraud'] == 1
        df.loc[fraud_mask, 'TransactionAmt'] *= np.random.uniform(2, 5, fraud_mask.sum())
        df.loc[fraud_mask, 'C1'] += np.random.normal(2, 0.5, fraud_mask.sum())
        
        return df
    
    def preprocess_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Preprocess features for the RNN model"""
        logger.info("Preprocessing features for RNN model...")
        
        # Separate target variable
        if 'isFraud' in df.columns:
            target = df['isFraud'].values
            features_df = df.drop(['isFraud', 'TransactionID'], axis=1)
        else:
            target = None
            features_df = df.drop(['TransactionID'], axis=1, errors='ignore')
        
        # Handle categorical variables
        categorical_columns = features_df.select_dtypes(include=['object']).columns
        label_encoders = {}
        
        for col in categorical_columns:
            le = LabelEncoder()
            features_df[col] = features_df[col].fillna('unknown')
            features_df[col] = le.fit_transform(features_df[col].astype(str))
            label_encoders[col] = le
        
        # Handle missing values
        features_df = features_df.fillna(0)
        
        # Select top 50 features (as per specification)
        numeric_columns = features_df.select_dtypes(include=[np.number]).columns
        
        # Calculate feature importance (correlation with target if available)
        if target is not None:
            correlations = []
            for col in numeric_columns:
                corr = abs(np.corrcoef(features_df[col], target)[0, 1])
                correlations.append((col, corr if not np.isnan(corr) else 0))
            
            # Sort by correlation and select top 50
            correlations.sort(key=lambda x: x[1], reverse=True)
            top_features = [col for col, _ in correlations[:50]]
        else:
            # If no target, select first 50 numeric columns
            top_features = numeric_columns[:50].tolist()
        
        # Ensure we have exactly 50 features
        while len(top_features) < 50:
            top_features.append(f'feature_{len(top_features)}')
            features_df[f'feature_{len(top_features)-1}'] = 0
        
        top_features = top_features[:50]
        
        # Select and scale features
        X = features_df[top_features].values
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        logger.info(f"Processed features shape: {X_scaled.shape}")
        
        return X_scaled, target, label_encoders, scaler, top_features
    
    def prepare_rnn_sequences(self, X: np.ndarray, y: Optional[np.ndarray] = None, 
                            sequence_length: int = 10) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """Prepare sequences for RNN training"""
        logger.info(f"Preparing RNN sequences with length {sequence_length}...")
        
        # For transaction data, we'll create sequences by grouping consecutive transactions
        # In a real scenario, you'd group by user_id or card_id
        
        sequences_X = []
        sequences_y = []
        
        for i in range(len(X) - sequence_length + 1):
            sequences_X.append(X[i:i + sequence_length])
            if y is not None:
                sequences_y.append(y[i + sequence_length - 1])  # Predict the last transaction in sequence
        
        X_sequences = np.array(sequences_X)
        y_sequences = np.array(sequences_y) if y is not None else None
        
        logger.info(f"Created {len(X_sequences)} sequences of shape {X_sequences.shape}")
        
        return X_sequences, y_sequences
    
    def get_training_data(self, test_size: float = 0.2, sequence_length: int = 10) -> Dict[str, Any]:
        """Get preprocessed training data ready for RNN model"""
        
        # Try to load real dataset, fallback to sample
        if not self.load_dataset():
            logger.info("Using sample dataset for development")
            df = self.create_sample_dataset()
        else:
            # Merge transaction and identity data if available
            df = self.train_transaction.copy()
            if self.train_identity is not None:
                df = df.merge(self.train_identity, on='TransactionID', how='left')
        
        # Preprocess features
        X, y, label_encoders, scaler, feature_names = self.preprocess_features(df)
        
        # Create sequences for RNN
        X_seq, y_seq = self.prepare_rnn_sequences(X, y, sequence_length)
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X_seq, y_seq, test_size=test_size, random_state=42, stratify=y_seq
        )
        
        return {
            'X_train': X_train,
            'X_val': X_val,
            'y_train': y_train,
            'y_val': y_val,
            'label_encoders': label_encoders,
            'scaler': scaler,
            'feature_names': feature_names,
            'sequence_length': sequence_length
        }

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize dataset handler
    handler = IEEEFraudDatasetHandler()
    
    # Get training data
    data = handler.get_training_data()
    
    print(f"Training data shape: {data['X_train'].shape}")
    print(f"Validation data shape: {data['X_val'].shape}")
    print(f"Feature names: {data['feature_names'][:10]}...")  # Show first 10 features
    print(f"Fraud rate in training: {data['y_train'].mean():.3f}")
