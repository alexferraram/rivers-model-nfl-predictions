#!/usr/bin/env python3
"""
Predict Upcoming NFL Games
Uses the trained model to predict winners of upcoming games.
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

class UpcomingGamesPredictor:
    """Predict upcoming NFL games using trained model"""
    
    def __init__(self, model_path='models/real_nfl_model.pkl'):
        """
        Initialize predictor with trained model
        
        Args:
            model_path (str): Path to trained model
        """
        self.model_path = model_path
        self.model = None
        self.feature_names = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model"""
        try:
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.feature_names = model_data['feature_names']
            logger.info(f"✅ Model loaded from {self.model_path}")
            logger.info(f"Features: {len(self.feature_names)}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
    
    def get_upcoming_games(self, weeks_ahead=1):
        """
        Get upcoming NFL games
        
        Args:
            weeks_ahead (int): Number of weeks ahead to look
            
        Returns:
            pd.DataFrame: Upcoming games
        """
        logger.info(f"Loading upcoming games for next {weeks_ahead} weeks...")
        
        try:
            # Load current season schedule
            current_year = datetime.now().year
            schedules = nfl.import_schedules([current_year])
            
            # Filter for regular season games
            schedules = schedules[schedules['game_type'] == 'REG'].copy()
            
            # Convert gameday to datetime for comparison
            schedules['gameday'] = pd.to_datetime(schedules['gameday'])
            
            # Filter for upcoming games
            today = datetime.now().date()
            upcoming_games = schedules[schedules['gameday'].dt.date >= today].copy()
            
            # Sort by date
            upcoming_games = upcoming_games.sort_values('gameday')
            
            logger.info(f"Found {len(upcoming_games)} upcoming games")
            return upcoming_games
            
        except Exception as e:
            logger.error(f"Error loading upcoming games: {e}")
            return pd.DataFrame()
    
    def get_team_current_stats(self, team, season=2024):
        """
        Get current season stats for a team
        
        Args:
            team (str): Team abbreviation
            season (int): Season year
            
        Returns:
            dict: Team statistics
        """
        try:
            # Load play-by-play data for current season
            pbp_data = nfl.import_pbp_data([season])
            
            # Filter for team's games
            team_games = pbp_data[pbp_data['posteam'] == team].copy()
            
            if team_games.empty:
                return self._get_default_stats()
            
            # Calculate current season stats
            stats = {
                'yards_per_play': team_games['yards_gained'].mean(),
                'third_down_rate': len(team_games[(team_games['down'] == 3) & (team_games['first_down'] == 1)]) / max(len(team_games[team_games['down'] == 3]), 1),
                'redzone_rate': len(team_games[(team_games['yardline_100'] <= 20) & (team_games['touchdown'] == 1)]) / max(len(team_games[team_games['yardline_100'] <= 20]), 1),
                'turnovers': (team_games['interception'].sum() + team_games['fumble_lost'].sum()) / len(team_games['game_id'].unique()),
                'completion_rate': team_games[team_games['play_type'] == 'pass']['complete_pass'].mean(),
                'yards_per_pass': team_games[team_games['play_type'] == 'pass']['passing_yards'].mean(),
                'yards_per_rush': team_games[team_games['play_type'] == 'run']['rushing_yards'].mean()
            }
            
            # Fill NaN values with defaults
            for key, value in stats.items():
                if pd.isna(value):
                    stats[key] = self._get_default_stats()[key]
            
            return stats
            
        except Exception as e:
            logger.warning(f"Error getting stats for {team}: {e}")
            return self._get_default_stats()
    
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
    
    def predict_game(self, home_team, away_team):
        """
        Predict the winner of a specific game
        
        Args:
            home_team (str): Home team abbreviation
            away_team (str): Away team abbreviation
            
        Returns:
            dict: Prediction results
        """
        if not self.model:
            logger.error("Model not loaded")
            return {}
        
        logger.info(f"Predicting: {away_team} @ {home_team}")
        
        # Get current team stats
        home_stats = self.get_team_current_stats(home_team)
        away_stats = self.get_team_current_stats(away_team)
        
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
            'away_stats': away_stats
        }
    
    def predict_upcoming_games(self, weeks_ahead=1):
        """
        Predict all upcoming games
        
        Args:
            weeks_ahead (int): Number of weeks ahead to predict
            
        Returns:
            list: List of predictions
        """
        logger.info(f"🎯 Predicting upcoming games for next {weeks_ahead} weeks...")
        
        # Get upcoming games
        upcoming_games = self.get_upcoming_games(weeks_ahead)
        
        if upcoming_games.empty:
            logger.warning("No upcoming games found")
            return []
        
        predictions = []
        
        for _, game in upcoming_games.iterrows():
            try:
                prediction = self.predict_game(
                    game['home_team'], 
                    game['away_team']
                )
                
                prediction['game_date'] = game['gameday']
                prediction['week'] = game['week']
                prediction['stadium'] = game.get('stadium', 'Unknown')
                
                predictions.append(prediction)
                
            except Exception as e:
                logger.warning(f"Error predicting game {game['home_team']} vs {game['away_team']}: {e}")
                continue
        
        return predictions

def main():
    """Main function to predict upcoming games"""
    logger.info("🏈 NFL Upcoming Games Predictor Starting...")
    
    # Create predictor
    predictor = UpcomingGamesPredictor()
    
    if not predictor.model:
        logger.error("Failed to load model. Exiting.")
        return
    
    # Predict upcoming games
    predictions = predictor.predict_upcoming_games(weeks_ahead=2)
    
    if not predictions:
        logger.warning("No predictions made")
        return
    
    # Display predictions
    logger.info(f"\n📅 NFL Game Predictions ({len(predictions)} games):")
    logger.info("=" * 80)
    
    for i, pred in enumerate(predictions, 1):
        logger.info(f"\n🏟️  Game {i}: {pred['away_team']} @ {pred['home_team']}")
        logger.info(f"   📅 Date: {pred['game_date'].strftime('%Y-%m-%d')}")
        logger.info(f"   🏆 Predicted Winner: {pred['predicted_winner']}")
        logger.info(f"   📊 Confidence: {pred['confidence']:.1f}%")
        logger.info(f"   🏠 Home Win Probability: {pred['home_win_probability']:.3f}")
        logger.info(f"   ✈️  Away Win Probability: {pred['away_win_probability']:.3f}")
        logger.info(f"   🏟️  Stadium: {pred['stadium']}")
        
        # Show key stats comparison
        logger.info(f"   📈 Key Stats Comparison:")
        logger.info(f"      {pred['home_team']} YPP: {pred['home_stats']['yards_per_play']:.1f}, 3rd Down: {pred['home_stats']['third_down_rate']:.1%}")
        logger.info(f"      {pred['away_team']} YPP: {pred['away_stats']['yards_per_play']:.1f}, 3rd Down: {pred['away_stats']['third_down_rate']:.1%}")
    
    logger.info("\n✅ Predictions completed!")
    logger.info("These predictions are based on current season performance and historical patterns.")
    logger.info("Remember: NFL games are unpredictable and anything can happen!")

if __name__ == "__main__":
    main()





