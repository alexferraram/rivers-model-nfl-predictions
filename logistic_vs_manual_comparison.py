"""
Comparison: Logistic Regression vs Manual Weighting
=================================================

This script demonstrates the key differences between:
1. Manual weight assignment (current RIVERS model)
2. Logistic Regression (learned weights)

Shows realistic NFL predictions with proper uncertainty.
"""

import pandas as pd
import numpy as np
import logging
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings
warnings.filterwarnings('ignore')

class ManualWeightModel:
    """Simulates the current RIVERS model with manual weights"""
    
    def __init__(self):
        # Manual weights (like current RIVERS model)
        self.weights = {
            'enhanced_epa': 0.24,
            'enhanced_efficiency': 0.24,
            'enhanced_yards': 0.21,
            'enhanced_turnovers': 0.17,
            'pff_matchups': 0.13,
            'weather': 0.01
        }
        
    def predict_game(self, home_features, away_features):
        """Predict using manual weights"""
        # Calculate weighted scores
        home_score = (
            home_features['epa'] * self.weights['enhanced_epa'] +
            home_features['efficiency'] * self.weights['enhanced_efficiency'] +
            home_features['yards'] * self.weights['enhanced_yards'] +
            home_features['turnovers'] * self.weights['enhanced_turnovers'] +
            home_features['pff'] * self.weights['pff_matchups'] +
            home_features['weather'] * self.weights['weather']
        )
        
        away_score = (
            away_features['epa'] * self.weights['enhanced_epa'] +
            away_features['efficiency'] * self.weights['enhanced_efficiency'] +
            away_features['yards'] * self.weights['enhanced_yards'] +
            away_features['turnovers'] * self.weights['enhanced_turnovers'] +
            away_features['pff'] * self.weights['pff_matchups'] +
            away_features['weather'] * self.weights['weather']
        )
        
        # Add home field advantage
        home_score += 3.0
        
        # Convert to win probability (simplified)
        score_diff = home_score - away_score
        win_probability = 1 / (1 + np.exp(-score_diff * 0.1))
        
        winner = "HOME" if win_probability > 0.5 else "AWAY"
        confidence = max(win_probability, 1 - win_probability)
        
        return {
            'winner': winner,
            'win_probability': win_probability,
            'confidence': confidence,
            'method': 'Manual Weights'
        }

class LogisticRegressionModel:
    """Uses Logistic Regression to learn optimal weights"""
    
    def __init__(self):
        self.model = LogisticRegression(random_state=42, max_iter=1000)
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def train_model(self, training_data):
        """Train on historical data"""
        X = training_data[['home_epa', 'away_epa', 'home_efficiency', 'away_efficiency', 
                          'home_yards', 'away_yards', 'home_turnovers', 'away_turnovers',
                          'home_pff', 'away_pff', 'weather', 'home_injury', 'away_injury']]
        y = training_data['home_won']
        
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        val_pred = self.model.predict(X_val_scaled)
        accuracy = accuracy_score(y_val, val_pred)
        
        print(f"📊 Logistic Regression Accuracy: {accuracy:.1%}")
        self.is_trained = True
        
    def predict_game(self, home_features, away_features):
        """Predict using learned weights"""
        if not self.is_trained:
            raise Exception("Model not trained")
            
        # Prepare feature vector
        X = np.array([
            home_features['epa'], away_features['epa'],
            home_features['efficiency'], away_features['efficiency'],
            home_features['yards'], away_features['yards'],
            home_features['turnovers'], away_features['turnovers'],
            home_features['pff'], away_features['pff'],
            home_features['weather'],
            home_features['injury'], away_features['injury']
        ]).reshape(1, -1)
        
        X_scaled = self.scaler.transform(X)
        win_probability = self.model.predict_proba(X_scaled)[0, 1]
        
        winner = "HOME" if win_probability > 0.5 else "AWAY"
        confidence = max(win_probability, 1 - win_probability)
        
        return {
            'winner': winner,
            'win_probability': win_probability,
            'confidence': confidence,
            'method': 'Logistic Regression'
        }

def generate_realistic_game_data(n_games=100):
    """Generate realistic NFL game data"""
    np.random.seed(42)
    games = []
    
    for i in range(n_games):
        # Generate realistic team features
        home_epa = np.random.normal(50, 12)
        away_epa = np.random.normal(50, 12)
        
        home_efficiency = np.random.normal(50, 10)
        away_efficiency = np.random.normal(50, 10)
        
        home_yards = np.random.normal(50, 8)
        away_yards = np.random.normal(50, 8)
        
        home_turnovers = np.random.normal(50, 8)
        away_turnovers = np.random.normal(50, 8)
        
        home_pff = np.random.normal(75, 8)
        away_pff = np.random.normal(75, 8)
        
        weather = np.random.normal(0, 3)
        
        home_injury = np.random.exponential(2)
        away_injury = np.random.exponential(2)
        
        # Create realistic outcome with noise
        home_advantage = 2.5
        feature_diff = (
            (home_epa - away_epa) * 0.15 +
            (home_efficiency - away_efficiency) * 0.12 +
            (home_yards - away_yards) * 0.08 +
            (home_turnovers - away_turnovers) * 0.06 +
            (home_pff - away_pff) * 0.05 +
            weather * 0.02 +
            (away_injury - home_injury) * 0.03
        )
        
        noise = np.random.normal(0, 2.5)
        logit = home_advantage + feature_diff + noise
        win_probability = 1 / (1 + np.exp(-logit))
        win_probability = np.clip(win_probability, 0.2, 0.8)
        
        home_won = 1 if np.random.random() < win_probability else 0
        
        games.append({
            'home_epa': home_epa,
            'away_epa': away_epa,
            'home_efficiency': home_efficiency,
            'away_efficiency': away_efficiency,
            'home_yards': home_yards,
            'away_yards': away_yards,
            'home_turnovers': home_turnovers,
            'away_turnovers': away_turnovers,
            'home_pff': home_pff,
            'away_pff': away_pff,
            'weather': weather,
            'home_injury': home_injury,
            'away_injury': away_injury,
            'home_won': home_won
        })
    
    return pd.DataFrame(games)

def compare_models():
    """Compare manual weights vs logistic regression"""
    print("🏈 NFL PREDICTION MODEL COMPARISON")
    print("=" * 50)
    
    # Generate training data
    print("📊 Generating realistic NFL game data...")
    training_data = generate_realistic_game_data(200)
    
    # Initialize models
    manual_model = ManualWeightModel()
    logistic_model = LogisticRegressionModel()
    
    # Train logistic regression
    print("🎯 Training Logistic Regression model...")
    logistic_model.train_model(training_data)
    
    # Test predictions
    print("\n🎲 Testing Predictions on Sample Games:")
    print("-" * 50)
    
    # Sample games
    sample_games = [
        {
            'home': {'epa': 65, 'efficiency': 62, 'yards': 58, 'turnovers': 68, 'pff': 78, 'weather': 0, 'injury': 1.5},
            'away': {'epa': 45, 'efficiency': 48, 'yards': 52, 'turnovers': 45, 'pff': 72, 'weather': 0, 'injury': 2.5}
        },
        {
            'home': {'epa': 55, 'efficiency': 52, 'yards': 51, 'turnovers': 52, 'pff': 76, 'weather': 0, 'injury': 1.8},
            'away': {'epa': 50, 'efficiency': 50, 'yards': 50, 'turnovers': 48, 'pff': 74, 'weather': 0, 'injury': 2.0}
        },
        {
            'home': {'epa': 48, 'efficiency': 45, 'yards': 47, 'turnovers': 45, 'pff': 70, 'weather': 0, 'injury': 2.2},
            'away': {'epa': 62, 'efficiency': 65, 'yards': 63, 'turnovers': 68, 'pff': 80, 'weather': 0, 'injury': 1.2}
        }
    ]
    
    for i, game in enumerate(sample_games, 1):
        print(f"\nGame {i}:")
        
        # Manual model prediction
        manual_pred = manual_model.predict_game(game['home'], game['away'])
        print(f"  Manual Weights:     {manual_pred['winner']} ({manual_pred['confidence']:.1%})")
        
        # Logistic regression prediction
        logistic_pred = logistic_model.predict_game(game['home'], game['away'])
        print(f"  Logistic Regression: {logistic_pred['winner']} ({logistic_pred['confidence']:.1%})")
    
    # Show learned weights
    print(f"\n🎯 LEARNED FEATURE WEIGHTS (Logistic Regression):")
    print("-" * 50)
    feature_names = ['home_epa', 'away_epa', 'home_efficiency', 'away_efficiency', 
                    'home_yards', 'away_yards', 'home_turnovers', 'away_turnovers',
                    'home_pff', 'away_pff', 'weather', 'home_injury', 'away_injury']
    
    for feature, coef in zip(feature_names, logistic_model.model.coef_[0]):
        print(f"  {feature:15s}: {coef:6.3f}")
    
    print(f"\n💡 KEY DIFFERENCES:")
    print("-" * 30)
    print("✅ Manual Weights: Fixed, requires expert tuning")
    print("✅ Logistic Regression: Learned from data automatically")
    print("✅ Manual Weights: Composite score approach")
    print("✅ Logistic Regression: Direct win probability")
    print("✅ Manual Weights: Static over time")
    print("✅ Logistic Regression: Improves with more data")

if __name__ == "__main__":
    compare_models()


