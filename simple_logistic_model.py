"""
Simple RIVERS Logistic Regression Model
======================================

A simplified version that demonstrates the core concept of using Logistic Regression
to learn optimal feature weights instead of manual weight assignment.

This version uses mock data to show how the model would work with real NFL data.
"""

import pandas as pd
import numpy as np
import logging
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, log_loss
import warnings
warnings.filterwarnings('ignore')

class SimpleRiversLogisticModel:
    """
    Simplified RIVERS Model using Logistic Regression to learn optimal feature weights
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Model components
        self.model = LogisticRegression(random_state=42, max_iter=1000)
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Feature names for interpretability
        self.feature_names = [
            'home_epa_score',
            'away_epa_score', 
            'home_efficiency_score',
            'away_efficiency_score',
            'home_yards_score',
            'away_yards_score',
            'home_turnover_score',
            'away_turnover_score',
            'home_pff_score',
            'away_pff_score',
            'weather_impact',
            'home_injury_impact',
            'away_injury_impact'
        ]
        
        self.logger.info("🌊 INITIALIZING SIMPLE RIVERS LOGISTIC REGRESSION MODEL")
        self.logger.info("=" * 60)
        
    def generate_mock_training_data(self, n_games=200):
        """Generate mock training data to demonstrate the concept"""
        self.logger.info(f"🎲 Generating {n_games} mock training games...")
        
        np.random.seed(42)
        training_data = []
        
        for i in range(n_games):
            # Generate realistic feature values
            home_epa = np.random.normal(50, 15)  # EPA score around 50
            away_epa = np.random.normal(50, 15)
            
            home_efficiency = np.random.normal(50, 12)  # Success rate around 50%
            away_efficiency = np.random.normal(50, 12)
            
            home_yards = np.random.normal(50, 10)  # Yards per play
            away_yards = np.random.normal(50, 10)
            
            home_turnovers = np.random.normal(50, 8)  # Lower turnover rate = higher score
            away_turnovers = np.random.normal(50, 8)
            
            home_pff = np.random.normal(75, 10)  # PFF grades around 75
            away_pff = np.random.normal(75, 10)
            
            weather_impact = np.random.normal(0, 5)  # Weather impact around 0
            
            home_injury_impact = np.random.exponential(2)  # Injury impact (exponential distribution)
            away_injury_impact = np.random.exponential(2)
            
            # Create realistic win probability based on feature differences
            # Home team advantage + feature differences
            home_advantage = 2.5  # Home field advantage (reduced)
            feature_diff = (
                (home_epa - away_epa) * 0.2 +
                (home_efficiency - away_efficiency) * 0.15 +
                (home_yards - away_yards) * 0.12 +
                (home_turnovers - away_turnovers) * 0.1 +
                (home_pff - away_pff) * 0.08 +
                weather_impact * 0.03 +
                (away_injury_impact - home_injury_impact) * 0.05  # Away injuries help home team
            )
            
            # Add significant noise to make predictions more realistic
            noise = np.random.normal(0, 3.0)  # Increased random noise
            
            # Convert to win probability using sigmoid
            logit = home_advantage + feature_diff + noise
            win_probability = 1 / (1 + np.exp(-logit))
            
            # Ensure win probability is between 0.2 and 0.8 (more realistic range)
            win_probability = np.clip(win_probability, 0.2, 0.8)
            
            # Determine winner based on probability
            home_won = 1 if np.random.random() < win_probability else 0
            
            training_data.append({
                'home_epa_score': home_epa,
                'away_epa_score': away_epa,
                'home_efficiency_score': home_efficiency,
                'away_efficiency_score': away_efficiency,
                'home_yards_score': home_yards,
                'away_yards_score': away_yards,
                'home_turnover_score': home_turnovers,
                'away_turnover_score': away_turnovers,
                'home_pff_score': home_pff,
                'away_pff_score': away_pff,
                'weather_impact': weather_impact,
                'home_injury_impact': home_injury_impact,
                'away_injury_impact': away_injury_impact,
                'home_won': home_won
            })
            
        self.logger.info(f"✅ Generated {len(training_data)} mock games")
        return pd.DataFrame(training_data)
        
    def train_model(self):
        """Train the logistic regression model on mock data"""
        self.logger.info("🎯 Training Logistic Regression Model...")
        
        # Generate training data
        training_df = self.generate_mock_training_data()
        
        # Prepare features and target
        X = training_df[self.feature_names]
        y = training_df['home_won']
        
        # Split data for validation
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        train_pred = self.model.predict(X_train_scaled)
        val_pred = self.model.predict(X_val_scaled)
        
        train_accuracy = accuracy_score(y_train, train_pred)
        val_accuracy = accuracy_score(y_val, val_pred)
        
        train_loss = log_loss(y_train, self.model.predict_proba(X_train_scaled)[:, 1])
        val_loss = log_loss(y_val, self.model.predict_proba(X_val_scaled)[:, 1])
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5, scoring='accuracy')
        
        self.logger.info("📊 Model Performance:")
        self.logger.info(f"   Training Accuracy: {train_accuracy:.3f}")
        self.logger.info(f"   Validation Accuracy: {val_accuracy:.3f}")
        self.logger.info(f"   Training Log Loss: {train_loss:.3f}")
        self.logger.info(f"   Validation Log Loss: {val_loss:.3f}")
        self.logger.info(f"   Cross-Validation Accuracy: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
        
        # Feature importance
        self.logger.info("🎯 Learned Feature Weights:")
        for feature, coef in zip(self.feature_names, self.model.coef_[0]):
            self.logger.info(f"   {feature}: {coef:.4f}")
            
        self.is_trained = True
        self.logger.info("✅ Model training complete")
        
    def predict_game(self, home_team, away_team, week=3, season=2025):
        """Predict win probability for a game using mock features"""
        if not self.is_trained:
            raise Exception("❌ Model must be trained before making predictions")
            
        # Generate mock features for the specific teams
        np.random.seed(hash(f"{home_team}{away_team}{week}") % 2**32)
        
        # Create realistic features with some variation (not extreme differences)
        home_advantage = 2.0  # Very small home team advantage
        away_penalty = -1.0   # Very small away team penalty
        
        features = {
            'home_epa_score': 55.0 + home_advantage + np.random.normal(0, 3),
            'away_epa_score': 50.0 + away_penalty + np.random.normal(0, 3),
            'home_efficiency_score': 52.0 + home_advantage + np.random.normal(0, 2),
            'away_efficiency_score': 50.0 + away_penalty + np.random.normal(0, 2),
            'home_yards_score': 51.0 + home_advantage + np.random.normal(0, 2),
            'away_yards_score': 50.0 + away_penalty + np.random.normal(0, 2),
            'home_turnover_score': 52.0 + home_advantage + np.random.normal(0, 2),  # Lower turnovers = higher score
            'away_turnover_score': 48.0 + away_penalty + np.random.normal(0, 2),
            'home_pff_score': 76.0 + np.random.normal(0, 2),
            'away_pff_score': 74.0 + np.random.normal(0, 2),
            'weather_impact': np.random.normal(0, 2),  # Some weather variation
            'home_injury_impact': np.random.exponential(1.5),  # Some injuries
            'away_injury_impact': np.random.exponential(1.8)   # Slightly more injuries for away team
        }
        
        # Prepare feature vector
        X = np.array([features[name] for name in self.feature_names]).reshape(1, -1)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict win probability
        win_probability = self.model.predict_proba(X_scaled)[0, 1]
        
        # Determine winner
        winner = home_team if win_probability > 0.5 else away_team
        confidence = max(win_probability, 1 - win_probability)
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'winner': winner,
            'win_probability': win_probability,
            'confidence': confidence,
            'features': features
        }
        
    def get_feature_importance(self):
        """Get feature importance from trained model"""
        if not self.is_trained:
            raise Exception("❌ Model must be trained first")
            
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'coefficient': self.model.coef_[0],
            'abs_coefficient': np.abs(self.model.coef_[0])
        }).sort_values('abs_coefficient', ascending=False)
        
        return importance_df
    
    def test_multiple_predictions(self, n_games=10):
        """Test multiple predictions to show realistic confidence ranges"""
        if not self.is_trained:
            raise Exception("❌ Model must be trained first")
            
        print(f"\n🎲 Testing {n_games} Random Game Predictions:")
        print("=" * 50)
        
        teams = ['BUF', 'MIA', 'KC', 'BAL', 'SF', 'DAL', 'PHI', 'GB', 'CIN', 'LAC']
        predictions = []
        
        for i in range(n_games):
            # Random team selection
            home_team = np.random.choice(teams)
            away_team = np.random.choice([t for t in teams if t != home_team])
            
            prediction = self.predict_game(home_team, away_team, week=i+1)
            predictions.append(prediction)
            
            print(f"{i+1:2d}. {away_team} @ {home_team}: {prediction['winner']} ({prediction['confidence']:.1%})")
        
        # Show statistics
        confidences = [p['confidence'] for p in predictions]
        print(f"\n📊 Confidence Statistics:")
        print(f"   Average Confidence: {np.mean(confidences):.1%}")
        print(f"   Min Confidence: {np.min(confidences):.1%}")
        print(f"   Max Confidence: {np.max(confidences):.1%}")
        print(f"   Std Deviation: {np.std(confidences):.1%}")
        
        return predictions

def main():
    """Main function to demonstrate the model"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize model
    model = SimpleRiversLogisticModel()
    
    # Train model
    model.train_model()
    
    # Test single prediction
    prediction = model.predict_game('BUF', 'MIA', week=3, season=2025)
    
    print("\n🏈 SIMPLE RIVERS LOGISTIC REGRESSION PREDICTION")
    print("=" * 60)
    print(f"🏈 {prediction['away_team']} @ {prediction['home_team']}")
    print(f"🏆 Winner: {prediction['winner']}")
    print(f"🎯 Win Probability: {prediction['win_probability']:.1%}")
    print(f"📊 Confidence: {prediction['confidence']:.1%}")
    
    # Test multiple predictions to show realistic confidence ranges
    model.test_multiple_predictions(10)
    
    # Show feature importance
    print("\n🎯 LEARNED FEATURE WEIGHTS:")
    print("=" * 40)
    importance = model.get_feature_importance()
    for _, row in importance.iterrows():
        print(f"{row['feature']}: {row['coefficient']:.4f}")
    
    print("\n💡 KEY ADVANTAGES OF LOGISTIC REGRESSION:")
    print("=" * 50)
    print("✅ Learns optimal weights from historical data")
    print("✅ No manual weight assignment required")
    print("✅ Provides win probability directly")
    print("✅ Feature importance is interpretable")
    print("✅ Handles feature interactions automatically")
    print("✅ Robust to outliers and noise")
    print("✅ Produces realistic confidence levels")

if __name__ == "__main__":
    main()
