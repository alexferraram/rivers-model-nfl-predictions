#!/usr/bin/env python3
"""
NFL Prediction Model Demo
Demonstrates the model structure and capabilities without requiring external data packages.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NFLPredictionModelDemo:
    """Demo version of the NFL Prediction Model"""
    
    def __init__(self, model_type='random_forest'):
        """
        Initialize the NFL prediction model demo
        
        Args:
            model_type (str): Type of model to use ('random_forest', 'gradient_boosting', 'logistic_regression')
        """
        self.model_type = model_type
        self.model = None
        self.feature_names = None
        self.is_trained = False
        
        # Initialize model based on type
        if model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
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
            raise ValueError(f"Unsupported model type: {model_type}")
    
    def create_demo_data(self, n_games=1000):
        """
        Create demo NFL game data for testing
        
        Args:
            n_games (int): Number of games to generate
            
        Returns:
            tuple: (X, y) features and labels
        """
        logger.info(f"Creating demo data for {n_games} games...")
        
        np.random.seed(42)
        
        # Create realistic NFL game features
        data = {
            # Basic team stats
            'home_offense_yards_per_play': np.random.normal(5.5, 1.0, n_games),
            'away_offense_yards_per_play': np.random.normal(5.5, 1.0, n_games),
            'home_defense_yards_per_play': np.random.normal(5.5, 1.0, n_games),
            'away_defense_yards_per_play': np.random.normal(5.5, 1.0, n_games),
            
            # Situational stats
            'home_third_down_rate': np.random.normal(0.4, 0.1, n_games),
            'away_third_down_rate': np.random.normal(0.4, 0.1, n_games),
            'home_redzone_td_rate': np.random.normal(0.6, 0.15, n_games),
            'away_redzone_td_rate': np.random.normal(0.6, 0.15, n_games),
            
            # Player stats
            'home_passing_yards_per_game': np.random.normal(250, 50, n_games),
            'away_passing_yards_per_game': np.random.normal(250, 50, n_games),
            'home_rushing_yards_per_game': np.random.normal(120, 30, n_games),
            'away_rushing_yards_per_game': np.random.normal(120, 30, n_games),
            
            # Fantasy stats (simulated)
            'home_fantasy_points_per_game': np.random.normal(150, 25, n_games),
            'away_fantasy_points_per_game': np.random.normal(150, 25, n_games),
            'home_fantasy_efficiency': np.random.normal(1.0, 0.2, n_games),
            'away_fantasy_efficiency': np.random.normal(1.0, 0.2, n_games),
            
            # Opportunity metrics
            'home_yards_over_expected': np.random.normal(0, 200, n_games),
            'away_yards_over_expected': np.random.normal(0, 200, n_games),
            'home_target_share': np.random.normal(0.2, 0.05, n_games),
            'away_target_share': np.random.normal(0.2, 0.05, n_games),
            
            # Efficiency metrics
            'home_success_rate': np.random.normal(0.5, 0.1, n_games),
            'away_success_rate': np.random.normal(0.5, 0.1, n_games),
            'home_explosive_play_rate': np.random.normal(0.1, 0.03, n_games),
            'away_explosive_play_rate': np.random.normal(0.1, 0.03, n_games),
            
            # Tendencies
            'home_pass_rate': np.random.normal(0.6, 0.1, n_games),
            'away_pass_rate': np.random.normal(0.6, 0.1, n_games),
            
            # Injury impact
            'home_key_injuries': np.random.poisson(1.5, n_games),
            'away_key_injuries': np.random.poisson(1.5, n_games),
        }
        
        # Create DataFrame
        X = pd.DataFrame(data)
        
        # Create target variable (home team wins)
        # Simple heuristic: home team wins if they have better stats
        home_advantage = np.random.normal(0.05, 0.02, n_games)  # Home field advantage
        home_offense_advantage = (X['home_offense_yards_per_play'] - X['away_offense_yards_per_play']) / 10
        home_defense_advantage = (X['away_defense_yards_per_play'] - X['home_defense_yards_per_play']) / 10
        home_fantasy_advantage = (X['home_fantasy_points_per_game'] - X['away_fantasy_points_per_game']) / 100
        
        # Combine advantages
        total_advantage = home_advantage + home_offense_advantage + home_defense_advantage + home_fantasy_advantage
        
        # Create binary target (1 = home wins, 0 = away wins)
        y = (total_advantage > 0).astype(int)
        
        logger.info(f"Created demo data: {X.shape[0]} games, {X.shape[1]} features")
        logger.info(f"Home team win rate: {y.mean():.3f}")
        
        return X, y
    
    def train(self, X, y):
        """
        Train the model
        
        Args:
            X (pd.DataFrame): Feature matrix
            y (pd.Series): Target variable
        """
        logger.info(f"Training {self.model_type} model...")
        
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        # Train the model
        self.model.fit(X, y)
        self.is_trained = True
        
        logger.info("Model training completed!")
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X, y, cv=5, scoring='accuracy')
        logger.info(f"Cross-validation accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    
    def predict(self, X):
        """
        Make predictions
        
        Args:
            X (pd.DataFrame): Feature matrix
            
        Returns:
            np.array: Predictions
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        return self.model.predict(X)
    
    def predict_proba(self, X):
        """
        Get prediction probabilities
        
        Args:
            X (pd.DataFrame): Feature matrix
            
        Returns:
            np.array: Prediction probabilities
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        return self.model.predict_proba(X)
    
    def get_feature_importance(self):
        """
        Get feature importance
        
        Returns:
            dict: Feature importance scores
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before getting feature importance")
        
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            return dict(zip(self.feature_names, importance))
        else:
            logger.warning("Model does not support feature importance")
            return {}
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate model performance
        
        Args:
            X_test (pd.DataFrame): Test features
            y_test (pd.Series): Test labels
            
        Returns:
            dict: Evaluation metrics
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before evaluation")
        
        # Make predictions
        y_pred = self.predict(X_test)
        y_proba = self.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Test Accuracy: {accuracy:.3f}")
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test, y_pred))
        
        return {
            'accuracy': accuracy,
            'predictions': y_pred,
            'probabilities': y_proba,
            'classification_report': classification_report(y_test, y_pred)
        }
    
    def save_model(self, filepath):
        """
        Save the trained model
        
        Args:
            filepath (str): Path to save the model
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        model_data = {
            'model': self.model,
            'model_type': self.model_type,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """
        Load a trained model
        
        Args:
            filepath (str): Path to load the model from
        """
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.model_type = model_data['model_type']
        self.feature_names = model_data['feature_names']
        self.is_trained = model_data['is_trained']
        
        logger.info(f"Model loaded from {filepath}")

def main():
    """Main demo function"""
    logger.info("🏈 NFL Prediction Model Demo Starting...")
    
    # Create model
    model = NFLPredictionModelDemo(model_type='random_forest')
    
    # Create demo data
    X, y = model.create_demo_data(n_games=1000)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"Training set: {X_train.shape[0]} games")
    logger.info(f"Test set: {X_test.shape[0]} games")
    
    # Train model
    model.train(X_train, y_train)
    
    # Evaluate model
    results = model.evaluate(X_test, y_test)
    
    # Get feature importance
    feature_importance = model.get_feature_importance()
    if feature_importance:
        logger.info("\nTop 10 Most Important Features:")
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        for feature, importance in sorted_features[:10]:
            logger.info(f"  {feature}: {importance:.4f}")
    
    # Save model
    os.makedirs('models', exist_ok=True)
    model.save_model('models/demo_nfl_model.pkl')
    
    # Demo prediction
    logger.info("\n🎯 Demo Prediction:")
    sample_game = X_test.iloc[0:1].copy()
    prediction = model.predict(sample_game)[0]
    probability = model.predict_proba(sample_game)[0]
    
    winner = "Home Team" if prediction == 1 else "Away Team"
    confidence = max(probability) * 100
    
    logger.info(f"Predicted Winner: {winner}")
    logger.info(f"Confidence: {confidence:.1f}%")
    logger.info(f"Home Team Win Probability: {probability[1]:.3f}")
    logger.info(f"Away Team Win Probability: {probability[0]:.3f}")
    
    logger.info("\n✅ Demo completed successfully!")
    logger.info("This demonstrates the structure and capabilities of your comprehensive NFL prediction model.")
    logger.info("With real data from nflverse, nfldata, dynastyprocess, and ffopportunity,")
    logger.info("the model will have 200+ fantasy-enhanced features for even better predictions!")

if __name__ == "__main__":
    main()





