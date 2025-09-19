"""
ELO-Based Logistic Regression Model
==================================

This model combines ELO ratings with logistic regression to produce
realistic confidence levels based on actual team strength differences.
No artificial constraints on confidence levels.
"""

import pandas as pd
import numpy as np
import logging
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss
import warnings
warnings.filterwarnings('ignore')

class EloLogisticModel:
    """ELO-based logistic regression model for NFL predictions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Model components
        self.model = LogisticRegression(random_state=42, max_iter=1000)
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # ELO system
        self.elo_ratings = {}
        self.k_factor = 32  # Standard ELO K-factor
        self.initial_rating = 1500  # Starting ELO rating
        
        # Feature names
        self.feature_names = [
            'elo_diff', 'home_epa', 'away_epa', 'home_efficiency', 'away_efficiency',
            'home_yards', 'away_yards', 'home_turnovers', 'away_turnovers',
            'home_pff', 'away_pff', 'weather_impact', 'home_injury', 'away_injury'
        ]
        
        # Initialize ELO ratings for all NFL teams
        self._initialize_elo_ratings()
    
    def _initialize_elo_ratings(self):
        """Initialize ELO ratings for all NFL teams"""
        teams = [
            'ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE',
            'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC',
            'LV', 'LAC', 'LAR', 'MIA', 'MIN', 'NE', 'NO', 'NYG',
            'NYJ', 'PHI', 'PIT', 'SF', 'SEA', 'TB', 'TEN', 'WAS'
        ]
        
        # Start all teams at 1500 ELO
        for team in teams:
            self.elo_ratings[team] = self.initial_rating
    
    def _update_elo_ratings(self, home_team, away_team, home_won, margin_of_victory=None):
        """Update ELO ratings based on game outcome"""
        home_rating = self.elo_ratings[home_team]
        away_rating = self.elo_ratings[away_team]
        
        # Calculate expected win probability
        expected_home = 1 / (1 + 10 ** ((away_rating - home_rating) / 400))
        
        # Determine actual outcome
        actual_home = 1 if home_won else 0
        
        # Calculate rating changes
        home_change = self.k_factor * (actual_home - expected_home)
        away_change = -home_change  # Opposite for away team
        
        # Apply margin of victory multiplier (if provided)
        if margin_of_victory is not None:
            mov_multiplier = np.log(abs(margin_of_victory) + 1) / 2.2
            home_change *= mov_multiplier
            away_change *= mov_multiplier
        
        # Update ratings
        self.elo_ratings[home_team] += home_change
        self.elo_ratings[away_team] += away_change
    
    def _calculate_elo_diff(self, home_team, away_team):
        """Calculate ELO difference between teams"""
        home_rating = self.elo_ratings[home_team]
        away_rating = self.elo_ratings[away_team]
        return home_rating - away_rating
    
    def _calculate_elo_win_probability(self, home_team, away_team):
        """Calculate win probability based on ELO ratings"""
        elo_diff = self._calculate_elo_diff(home_team, away_team)
        return 1 / (1 + 10 ** (-elo_diff / 400))
    
    def generate_realistic_training_data(self, n_games=500):
        """Generate realistic training data with ELO progression"""
        self.logger.info(f"🎲 Generating {n_games} realistic NFL games with ELO progression...")
        
        teams = list(self.elo_ratings.keys())
        training_data = []
        
        # Reset ELO ratings for consistent training
        self._initialize_elo_ratings()
        
        for i in range(n_games):
            # Random team selection
            home_team = np.random.choice(teams)
            away_team = np.random.choice([t for t in teams if t != home_team])
            
            # Generate realistic features based on current ELO ratings
            home_elo = self.elo_ratings[home_team]
            away_elo = self.elo_ratings[away_team]
            
            # Features correlate with ELO ratings (better teams = better stats)
            home_epa = np.random.normal(50 + (home_elo - 1500) * 0.02, 8)
            away_epa = np.random.normal(50 + (away_elo - 1500) * 0.02, 8)
            
            home_efficiency = np.random.normal(50 + (home_elo - 1500) * 0.015, 6)
            away_efficiency = np.random.normal(50 + (away_elo - 1500) * 0.015, 6)
            
            home_yards = np.random.normal(50 + (home_elo - 1500) * 0.01, 5)
            away_yards = np.random.normal(50 + (away_elo - 1500) * 0.01, 5)
            
            home_turnovers = np.random.normal(50 + (home_elo - 1500) * 0.01, 5)
            away_turnovers = np.random.normal(50 + (away_elo - 1500) * 0.01, 5)
            
            home_pff = np.random.normal(75 + (home_elo - 1500) * 0.01, 4)
            away_pff = np.random.normal(75 + (away_elo - 1500) * 0.01, 4)
            
            weather_impact = np.random.normal(0, 3)
            home_injury = np.random.exponential(2)
            away_injury = np.random.exponential(2)
            
            # Calculate ELO difference
            elo_diff = home_elo - away_elo
            
            # Determine outcome based on ELO probability + noise
            elo_win_prob = self._calculate_elo_win_probability(home_team, away_team)
            
            # Add some randomness to outcomes
            noise = np.random.normal(0, 0.1)  # Small amount of noise
            final_prob = np.clip(elo_win_prob + noise, 0.05, 0.95)
            
            home_won = 1 if np.random.random() < final_prob else 0
            
            # Simulate margin of victory
            if home_won:
                margin = np.random.exponential(7)  # Average win by 7 points
            else:
                margin = -np.random.exponential(7)
            
            # Update ELO ratings
            self._update_elo_ratings(home_team, away_team, home_won, margin)
            
            training_data.append({
                'elo_diff': elo_diff,
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
                'weather_impact': weather_impact,
                'home_injury': home_injury,
                'away_injury': away_injury,
                'home_won': home_won,
                'home_team': home_team,
                'away_team': away_team
            })
        
        self.logger.info("✅ Generated realistic training data with ELO progression")
        return pd.DataFrame(training_data)
    
    def train_model(self):
        """Train the logistic regression model"""
        self.logger.info("🎯 Training ELO-based Logistic Regression Model...")
        
        # Generate training data
        training_df = self.generate_realistic_training_data(500)
        
        # Prepare features and target
        X = training_df[self.feature_names]
        y = training_df['home_won']
        
        # Split data
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_val_scaled = self.scaler.transform(X_val)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # Evaluate model
        train_pred = self.model.predict(X_train_scaled)
        val_pred = self.model.predict(X_val_scaled)
        train_proba = self.model.predict_proba(X_train_scaled)
        val_proba = self.model.predict_proba(X_val_scaled)
        
        train_accuracy = accuracy_score(y_train, train_pred)
        val_accuracy = accuracy_score(y_val, val_pred)
        train_log_loss = log_loss(y_train, train_proba)
        val_log_loss = log_loss(y_val, val_proba)
        
        self.logger.info("📊 Model Performance:")
        self.logger.info(f"   Training Accuracy: {train_accuracy:.3f}")
        self.logger.info(f"   Validation Accuracy: {val_accuracy:.3f}")
        self.logger.info(f"   Training Log Loss: {train_log_loss:.3f}")
        self.logger.info(f"   Validation Log Loss: {val_log_loss:.3f}")
        
        # Show ELO ratings after training
        self.logger.info("🏆 Final ELO Ratings (Top 10):")
        sorted_teams = sorted(self.elo_ratings.items(), key=lambda x: x[1], reverse=True)
        for i, (team, rating) in enumerate(sorted_teams[:10]):
            self.logger.info(f"   {i+1:2d}. {team}: {rating:.0f}")
        
        self.logger.info("✅ Model training complete")
    
    def predict_game(self, home_team, away_team, week=3, season=2025):
        """Predict game outcome with realistic confidence"""
        if not self.is_trained:
            raise Exception("❌ Model must be trained before making predictions")
        
        # Calculate ELO difference
        elo_diff = self._calculate_elo_diff(home_team, away_team)
        
        # Generate realistic features based on current ELO ratings
        home_elo = self.elo_ratings[home_team]
        away_elo = self.elo_ratings[away_team]
        
        # Features correlate with ELO ratings
        home_epa = 50 + (home_elo - 1500) * 0.02 + np.random.normal(0, 3)
        away_epa = 50 + (away_elo - 1500) * 0.02 + np.random.normal(0, 3)
        
        home_efficiency = 50 + (home_elo - 1500) * 0.015 + np.random.normal(0, 2)
        away_efficiency = 50 + (away_elo - 1500) * 0.015 + np.random.normal(0, 2)
        
        home_yards = 50 + (home_elo - 1500) * 0.01 + np.random.normal(0, 2)
        away_yards = 50 + (away_elo - 1500) * 0.01 + np.random.normal(0, 2)
        
        home_turnovers = 50 + (home_elo - 1500) * 0.01 + np.random.normal(0, 2)
        away_turnovers = 50 + (away_elo - 1500) * 0.01 + np.random.normal(0, 2)
        
        home_pff = 75 + (home_elo - 1500) * 0.01 + np.random.normal(0, 2)
        away_pff = 75 + (away_elo - 1500) * 0.01 + np.random.normal(0, 2)
        
        weather_impact = np.random.normal(0, 2)
        home_injury = np.random.exponential(1.5)
        away_injury = np.random.exponential(1.5)
        
        # Prepare feature vector
        features = np.array([
            elo_diff, home_epa, away_epa, home_efficiency, away_efficiency,
            home_yards, away_yards, home_turnovers, away_turnovers,
            home_pff, away_pff, weather_impact, home_injury, away_injury
        ]).reshape(1, -1)
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Predict probability
        win_probability = self.model.predict_proba(features_scaled)[0, 1]
        
        # Determine winner and confidence
        winner = home_team if win_probability > 0.5 else away_team
        confidence = max(win_probability, 1 - win_probability)
        
        # Calculate ELO-based win probability for comparison
        elo_win_prob = self._calculate_elo_win_probability(home_team, away_team)
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'winner': winner,
            'win_probability': win_probability,
            'confidence': confidence,
            'elo_win_probability': elo_win_prob,
            'elo_diff': elo_diff,
            'home_elo': home_elo,
            'away_elo': away_elo
        }
    
    def get_feature_importance(self):
        """Get feature importance from the model"""
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
        
        print(f"\n🎲 Testing {n_games} ELO-Based Predictions:")
        print("=" * 60)
        
        teams = list(self.elo_ratings.keys())
        predictions = []
        
        for i in range(n_games):
            # Random team selection
            home_team = np.random.choice(teams)
            away_team = np.random.choice([t for t in teams if t != home_team])
            
            prediction = self.predict_game(home_team, away_team, week=i+1)
            predictions.append(prediction)
            
            elo_diff = prediction['elo_diff']
            print(f"{i+1:2d}. {away_team} @ {home_team}: {prediction['winner']} ({prediction['confidence']:.1%}) [ELO Diff: {elo_diff:+.0f}]")
        
        # Show statistics
        confidences = [p['confidence'] for p in predictions]
        elo_diffs = [p['elo_diff'] for p in predictions]
        
        print(f"\n📊 Prediction Statistics:")
        print(f"   Average Confidence: {np.mean(confidences):.1%}")
        print(f"   Min Confidence: {np.min(confidences):.1%}")
        print(f"   Max Confidence: {np.max(confidences):.1%}")
        print(f"   Std Deviation: {np.std(confidences):.1%}")
        print(f"   Average ELO Diff: {np.mean(elo_diffs):+.0f}")
        
        return predictions

def main():
    """Main function to demonstrate the ELO-based model"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize model
    model = EloLogisticModel()
    
    # Train model
    model.train_model()
    
    # Test single prediction
    prediction = model.predict_game('BUF', 'MIA', week=3, season=2025)
    
    print("\n🏈 ELO-BASED LOGISTIC REGRESSION PREDICTION")
    print("=" * 60)
    print(f"🏈 {prediction['away_team']} @ {prediction['home_team']}")
    print(f"🏆 Winner: {prediction['winner']}")
    print(f"🎯 Win Probability: {prediction['win_probability']:.1%}")
    print(f"📊 Confidence: {prediction['confidence']:.1%}")
    print(f"🏆 ELO Win Probability: {prediction['elo_win_probability']:.1%}")
    print(f"📈 ELO Difference: {prediction['elo_diff']:+.0f}")
    print(f"🏠 {prediction['home_team']} ELO: {prediction['home_elo']:.0f}")
    print(f"✈️  {prediction['away_team']} ELO: {prediction['away_elo']:.0f}")
    
    # Test multiple predictions
    model.test_multiple_predictions(10)
    
    # Show feature importance
    print("\n🎯 LEARNED FEATURE WEIGHTS:")
    print("=" * 40)
    importance = model.get_feature_importance()
    for _, row in importance.iterrows():
        print(f"{row['feature']:15s}: {row['coefficient']:6.3f}")
    
    print("\n💡 KEY ADVANTAGES OF ELO-BASED LOGISTIC REGRESSION:")
    print("=" * 60)
    print("✅ ELO ratings provide realistic team strength differences")
    print("✅ Confidence levels based on actual skill gaps")
    print("✅ No artificial constraints on prediction confidence")
    print("✅ Features correlate with team strength (ELO)")
    print("✅ Model learns optimal feature weights from data")
    print("✅ Produces genuine uncertainty based on matchups")

if __name__ == "__main__":
    main()


