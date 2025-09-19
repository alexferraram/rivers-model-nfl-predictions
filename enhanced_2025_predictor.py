#!/usr/bin/env python3
"""
Enhanced 2025 NFL Predictor
Gives more weight to current season performance and uses 2025 data.
"""

import pandas as pd
import numpy as np
import nfl_data_py as nfl
import joblib
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Enhanced2025Predictor:
    """Enhanced predictor that prioritizes 2025 season data"""
    
    def __init__(self, model_path='models/real_nfl_model.pkl'):
        """Initialize predictor with trained model"""
        self.model_path = model_path
        self.model = None
        self.feature_names = None
        self.pbp_2025 = None
        self.pbp_2024 = None
        self.load_model()
        self.load_data()
    
    def load_model(self):
        """Load the trained model"""
        try:
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.feature_names = model_data['feature_names']
            logger.info(f"✅ Model loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
    
    def load_data(self):
        """Load both 2024 and 2025 data"""
        logger.info("Loading NFL data for enhanced prediction...")
        try:
            # Load 2025 data (current season - most important)
            self.pbp_2025 = nfl.import_pbp_data([2025])
            logger.info(f"✅ Loaded {len(self.pbp_2025)} plays from 2025 season")
            
            # Load 2024 data (for context)
            self.pbp_2024 = nfl.import_pbp_data([2024])
            logger.info(f"✅ Loaded {len(self.pbp_2024)} plays from 2024 season")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.pbp_2025 = None
            self.pbp_2024 = None
    
    def get_enhanced_team_stats(self, team, current_season_weight=0.7):
        """
        Get team stats with enhanced weighting for current season
        
        Args:
            team (str): Team abbreviation
            current_season_weight (float): Weight for 2025 data (0.7 = 70% weight)
        """
        if self.pbp_2025 is None:
            return self._get_default_stats()
        
        # Get 2025 stats (current season)
        team_2025 = self.pbp_2025[self.pbp_2025['posteam'] == team].copy()
        
        # Get 2024 stats (previous season for context)
        team_2024 = self.pbp_2024[self.pbp_2024['posteam'] == team].copy() if self.pbp_2024 is not None else pd.DataFrame()
        
        # Calculate 2025 stats
        stats_2025 = self._calculate_stats(team_2025, "2025")
        
        # Calculate 2024 stats
        stats_2024 = self._calculate_stats(team_2024, "2024") if not team_2024.empty else self._get_default_stats()
        
        # Combine with weighted average (favoring 2025)
        enhanced_stats = {}
        for stat in stats_2025.keys():
            if stat in stats_2024:
                enhanced_stats[stat] = (
                    current_season_weight * stats_2025[stat] + 
                    (1 - current_season_weight) * stats_2024[stat]
                )
            else:
                enhanced_stats[stat] = stats_2025[stat]
        
        return enhanced_stats
    
    def _calculate_stats(self, team_games, season_label):
        """Calculate team statistics from game data"""
        if team_games.empty:
            return self._get_default_stats()
        
        logger.info(f"📊 Calculating {season_label} stats: {len(team_games)} plays")
        
        stats = {
            'yards_per_play': team_games['yards_gained'].mean(),
            'third_down_rate': len(team_games[(team_games['down'] == 3) & (team_games['first_down'] == 1)]) / max(len(team_games[team_games['down'] == 3]), 1),
            'redzone_rate': len(team_games[(team_games['yardline_100'] <= 20) & (team_games['touchdown'] == 1)]) / max(len(team_games[team_games['yardline_100'] <= 20]), 1),
            'turnovers': (team_games['interception'].sum() + team_games['fumble_lost'].sum()) / len(team_games['game_id'].unique()),
            'completion_rate': team_games[team_games['play_type'] == 'pass']['complete_pass'].mean(),
            'yards_per_pass': team_games[team_games['play_type'] == 'pass']['passing_yards'].mean(),
            'yards_per_rush': team_games[team_games['play_type'] == 'run']['rushing_yards'].mean()
        }
        
        # Fill NaN values
        for key, value in stats.items():
            if pd.isna(value):
                stats[key] = self._get_default_stats()[key]
        
        return stats
    
    def _get_default_stats(self):
        """Get default team statistics"""
        return {
            'yards_per_play': 5.5,
            'third_down_rate': 0.4,
            'redzone_rate': 0.6,
            'turnovers': 1.5,
            'completion_rate': 0.65,
            'yards_per_pass': 7.0,
            'yards_per_rush': 4.0
        }
    
    def predict_game_enhanced(self, home_team, away_team, current_season_weight=0.7):
        """
        Predict game with enhanced current season weighting
        
        Args:
            home_team (str): Home team abbreviation
            away_team (str): Away team abbreviation
            current_season_weight (float): Weight for current season data
        """
        if not self.model:
            logger.error("Model not loaded")
            return {}
        
        logger.info(f"🎯 Enhanced prediction: {away_team} @ {home_team}")
        logger.info(f"📊 Using {current_season_weight:.1%} weight for 2025 season data")
        
        # Get enhanced team stats
        home_stats = self.get_enhanced_team_stats(home_team, current_season_weight)
        away_stats = self.get_enhanced_team_stats(away_team, current_season_weight)
        
        # Create feature vector
        features = {}
        for stat_name, home_value in home_stats.items():
            features[f'home_{stat_name}'] = home_value
        for stat_name, away_value in away_stats.items():
            features[f'away_{stat_name}'] = away_value
        
        # Convert to DataFrame
        X = pd.DataFrame([features])
        
        # Ensure all required features are present
        for feature in self.feature_names:
            if feature not in X.columns:
                X[feature] = 0
        
        # Reorder columns to match training data
        X = X[self.feature_names]
        
        # Make prediction
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        winner = home_team if prediction == 1 else away_team
        confidence = max(probabilities) * 100
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'predicted_winner': winner,
            'confidence': confidence,
            'home_win_probability': probabilities[1],
            'away_win_probability': probabilities[0],
            'home_stats': home_stats,
            'away_stats': away_stats,
            'current_season_weight': current_season_weight
        }
    
    def compare_prediction_methods(self, home_team, away_team):
        """Compare predictions with different season weightings"""
        logger.info(f"🔍 Comparing prediction methods for {away_team} @ {home_team}")
        
        methods = [
            ("2024 Only", 0.0),
            ("Balanced", 0.5),
            ("2025 Focused", 0.7),
            ("2025 Heavy", 0.9)
        ]
        
        results = []
        
        for method_name, weight in methods:
            prediction = self.predict_game_enhanced(home_team, away_team, weight)
            results.append({
                'method': method_name,
                'weight': weight,
                'winner': prediction['predicted_winner'],
                'confidence': prediction['confidence'],
                'home_prob': prediction['home_win_probability']
            })
        
        return results

def main():
    """Main function to demonstrate enhanced prediction"""
    logger.info("🏈 Enhanced 2025 NFL Predictor Starting...")
    
    # Create enhanced predictor
    predictor = Enhanced2025Predictor()
    
    if not predictor.model:
        logger.error("Failed to load model. Exiting.")
        return
    
    # Predict MIA @ BUF with different weightings
    home_team = 'BUF'
    away_team = 'MIA'
    
    logger.info(f"\n🎯 Enhanced Prediction Analysis: {away_team} @ {home_team}")
    logger.info("=" * 60)
    
    # Compare different methods
    results = predictor.compare_prediction_methods(home_team, away_team)
    
    print("\n📊 PREDICTION COMPARISON:")
    print("-" * 50)
    for result in results:
        print(f"{result['method']:<15} | Winner: {result['winner']:<3} | Confidence: {result['confidence']:.1f}% | Home Prob: {result['home_prob']:.3f}")
    
    # Get detailed enhanced prediction
    enhanced_pred = predictor.predict_game_enhanced(home_team, away_team, current_season_weight=0.7)
    
    print(f"\n🏆 ENHANCED PREDICTION (70% 2025 Weight):")
    print("-" * 45)
    print(f"Predicted Winner: {enhanced_pred['predicted_winner']}")
    print(f"Confidence: {enhanced_pred['confidence']:.1f}%")
    print(f"Home Win Probability: {enhanced_pred['home_win_probability']:.3f}")
    print(f"Away Win Probability: {enhanced_pred['away_win_probability']:.3f}")
    
    print(f"\n📈 KEY STATS (70% 2025 Season Weight):")
    print("-" * 40)
    print(f"{home_team} Stats:")
    for stat, value in enhanced_pred['home_stats'].items():
        if 'rate' in stat:
            print(f"  {stat.replace('_', ' ').title()}: {value:.1%}")
        else:
            print(f"  {stat.replace('_', ' ').title()}: {value:.2f}")
    
    print(f"\n{away_team} Stats:")
    for stat, value in enhanced_pred['away_stats'].items():
        if 'rate' in stat:
            print(f"  {stat.replace('_', ' ').title()}: {value:.1%}")
        else:
            print(f"  {stat.replace('_', ' ').title()}: {value:.2f}")
    
    logger.info("\n✅ Enhanced prediction completed!")
    logger.info("This model now prioritizes current 2025 season performance!")

if __name__ == "__main__":
    main()





