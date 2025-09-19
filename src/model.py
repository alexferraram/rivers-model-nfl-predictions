"""
NFL Prediction Model

This module contains the machine learning model for predicting NFL game outcomes.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib
import logging
from typing import Dict, Tuple, List, Optional

logger = logging.getLogger(__name__)


class NFLPredictionModel:
    """Machine learning model for NFL game outcome prediction."""
    
    def __init__(self, model_type: str = 'random_forest'):
        """
        Initialize the prediction model.
        
        Args:
            model_type: Type of model to use ('random_forest', 'gradient_boosting', 'logistic_regression')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = None
        self.is_trained = False
        
        # Initialize model based on type
        if model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
        elif model_type == 'logistic_regression':
            self.model = LogisticRegression(
                random_state=42,
                max_iter=1000
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2) -> Dict:
        """
        Train the model.
        
        Args:
            X: Feature matrix
            y: Target variable
            test_size: Proportion of data to use for testing
            
        Returns:
            Dictionary containing training results
        """
        logger.info(f"Training {self.model_type} model...")
        
        # Store feature columns
        self.feature_columns = list(X.columns)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features (important for logistic regression)
        if self.model_type == 'logistic_regression':
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
        else:
            X_train_scaled = X_train
            X_test_scaled = X_test
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        # Cross-validation score
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5)
        
        results = {
            'accuracy': accuracy,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'classification_report': classification_report(y_test, y_pred),
            'confusion_matrix': confusion_matrix(y_test, y_pred),
            'feature_importance': self._get_feature_importance(),
            'predictions': y_pred,
            'probabilities': y_pred_proba,
            'y_test': y_test
        }
        
        self.is_trained = True
        logger.info(f"Model training complete. Accuracy: {accuracy:.3f}")
        
        return results
    
    def predict(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make predictions on new data.
        
        Args:
            X: Feature matrix
            
        Returns:
            Tuple of (predictions, probabilities)
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Scale features if needed
        if self.model_type == 'logistic_regression':
            X_scaled = self.scaler.transform(X)
        else:
            X_scaled = X
        
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)[:, 1]
        
        return predictions, probabilities
    
    def predict_game(self, home_team_stats: Dict, away_team_stats: Dict) -> Dict:
        """
        Predict the outcome of a specific game.
        
        Args:
            home_team_stats: Dictionary of home team statistics
            away_team_stats: Dictionary of away team statistics
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Create feature vector
        features = {}
        
        # Add home team features
        for key, value in home_team_stats.items():
            features[f'home_{key}'] = value
        
        # Add away team features
        for key, value in away_team_stats.items():
            features[f'away_{key}'] = value
        
        # Add differential features
        features['yards_per_play_diff'] = home_team_stats.get('yards_per_play', 0) - away_team_stats.get('yards_per_play', 0)
        features['first_down_rate_diff'] = home_team_stats.get('first_down_rate', 0) - away_team_stats.get('first_down_rate', 0)
        features['turnover_rate_diff'] = home_team_stats.get('turnover_rate', 0) - away_team_stats.get('turnover_rate', 0)
        features['fg_percentage_diff'] = home_team_stats.get('fg_percentage', 0) - away_team_stats.get('fg_percentage', 0)
        features['touchdown_diff'] = home_team_stats.get('touchdowns', 0) - away_team_stats.get('touchdowns', 0)
        
        # Convert to DataFrame
        feature_df = pd.DataFrame([features])
        
        # Ensure all required features are present
        for col in self.feature_columns:
            if col not in feature_df.columns:
                feature_df[col] = 0
        
        # Reorder columns to match training data
        feature_df = feature_df[self.feature_columns]
        
        # Make prediction
        prediction, probability = self.predict(feature_df)
        
        return {
            'home_win_probability': probability[0],
            'away_win_probability': 1 - probability[0],
            'predicted_winner': 'home' if prediction[0] == 1 else 'away',
            'confidence': max(probability[0], 1 - probability[0])
        }
    
    def _get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores."""
        if not self.is_trained:
            return {}
        
        if hasattr(self.model, 'feature_importances_'):
            importance_dict = dict(zip(self.feature_columns, self.model.feature_importances_))
            return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
        else:
            return {}
    
    def save_model(self, filepath: str):
        """Save the trained model."""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'model_type': self.model_type,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model."""
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_columns = model_data['feature_columns']
        self.model_type = model_data['model_type']
        self.is_trained = model_data['is_trained']
        
        logger.info(f"Model loaded from {filepath}")
    
    def optimize_hyperparameters(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """
        Optimize hyperparameters using grid search.
        
        Args:
            X: Feature matrix
            y: Target variable
            
        Returns:
            Dictionary with optimization results
        """
        logger.info("Optimizing hyperparameters...")
        
        # Define parameter grids for different models
        if self.model_type == 'random_forest':
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15, None],
                'min_samples_split': [2, 5, 10]
            }
        elif self.model_type == 'gradient_boosting':
            param_grid = {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 6, 9]
            }
        elif self.model_type == 'logistic_regression':
            param_grid = {
                'C': [0.1, 1, 10, 100],
                'penalty': ['l1', 'l2'],
                'solver': ['liblinear', 'saga']
            }
        else:
            raise ValueError(f"Hyperparameter optimization not supported for {self.model_type}")
        
        # Perform grid search
        grid_search = GridSearchCV(
            self.model, param_grid, cv=5, scoring='accuracy', n_jobs=-1
        )
        
        # Scale features if needed
        if self.model_type == 'logistic_regression':
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = X
        
        grid_search.fit(X_scaled, y)
        
        # Update model with best parameters
        self.model = grid_search.best_estimator_
        
        results = {
            'best_params': grid_search.best_params_,
            'best_score': grid_search.best_score_,
            'cv_results': grid_search.cv_results_
        }
        
        logger.info(f"Hyperparameter optimization complete. Best score: {grid_search.best_score_:.3f}")
        
        return results






