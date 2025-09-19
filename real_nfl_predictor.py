#!/usr/bin/env python3
"""
Real NFL Game Winner Prediction Model
Uses actual NFL data to predict winners of upcoming games.
"""

import pandas as pd
import numpy as np
import nfl_data_py as nfl
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
import logging
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealNFLPredictor:
    """Real NFL Game Winner Prediction Model"""
    
    def __init__(self, model_type='random_forest'):
        """
        Initialize the NFL prediction model
        
        Args:
            model_type (str): Type of model to use ('random_forest', 'gradient_boosting', 'logistic_regression')
        """
        self.model_type = model_type
        self.model = None
        self.feature_names = None
        self.is_trained = False
        self.teams_data = None
        
        # Initialize model based on type
        if model_type == 'random_forest':
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
        elif model_type == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=8,
                random_state=42
            )
        elif model_type == 'logistic_regression':
            self.model = LogisticRegression(
                random_state=42,
                max_iter=2000
            )
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    def load_nfl_data(self, seasons=[2022, 2023, 2024]):
        """
        Load real NFL data from nfl_data_py
        
        Args:
            seasons (list): List of seasons to load data for
            
        Returns:
            dict: Dictionary containing all loaded data
        """
        logger.info(f"Loading NFL data for seasons: {seasons}")
        
        data = {}
        
        try:
            # Load play-by-play data
            logger.info("Loading play-by-play data...")
            data['pbp'] = nfl.import_pbp_data(seasons)
            logger.info(f"Loaded {len(data['pbp'])} plays")
            
            # Load team stats
            logger.info("Loading team stats...")
            data['team_stats'] = nfl.import_team_desc()
            logger.info(f"Loaded {len(data['team_stats'])} team records")
            
            # Load schedules
            logger.info("Loading schedules...")
            data['schedules'] = nfl.import_schedules(seasons)
            logger.info(f"Loaded {len(data['schedules'])} games")
            
            # Load player stats
            logger.info("Loading player stats...")
            data['player_stats'] = nfl.import_seasonal_data(seasons)
            logger.info(f"Loaded {len(data['player_stats'])} player-season records")
            
            # Load rosters (if available)
            try:
                logger.info("Loading rosters...")
                data['rosters'] = nfl.import_rosters(seasons)
                logger.info(f"Loaded {len(data['rosters'])} roster records")
            except AttributeError:
                logger.info("Rosters not available in this version, skipping...")
                data['rosters'] = pd.DataFrame()
            
            logger.info("✅ Successfully loaded all NFL data!")
            return data
            
        except Exception as e:
            logger.error(f"Error loading NFL data: {e}")
            return {}
    
    def create_game_features(self, data):
        """
        Create comprehensive game features from NFL data
        
        Args:
            data (dict): Dictionary containing NFL data
            
        Returns:
            pd.DataFrame: Game features with target variable
        """
        logger.info("Creating comprehensive game features...")
        
        pbp_data = data['pbp']
        schedules = data['schedules']
        
        # Filter for regular season games only
        schedules = schedules[schedules['game_type'] == 'REG'].copy()
        
        # Create game-level features
        game_features = []
        
        for _, game in schedules.iterrows():
            try:
                # Get game data
                game_id = game['game_id']
                home_team = game['home_team']
                away_team = game['away_team']
                
                # Filter play-by-play data for this game
                game_pbp = pbp_data[pbp_data['game_id'] == game_id].copy()
                
                if game_pbp.empty:
                    continue
                
                # Calculate team statistics
                home_stats = self._calculate_team_stats(game_pbp, home_team, 'home')
                away_stats = self._calculate_team_stats(game_pbp, away_team, 'away')
                
                # Create feature row
                feature_row = {
                    'game_id': game_id,
                    'season': game['season'],
                    'week': game['week'],
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_score': game['home_score'],
                    'away_score': game['away_score'],
                    'home_win': 1 if game['home_score'] > game['away_score'] else 0,
                    **home_stats,
                    **away_stats
                }
                
                game_features.append(feature_row)
                
            except Exception as e:
                logger.warning(f"Error processing game {game_id}: {e}")
                continue
        
        # Convert to DataFrame
        features_df = pd.DataFrame(game_features)
        
        if features_df.empty:
            logger.error("No game features could be created")
            return pd.DataFrame()
        
        logger.info(f"Created features for {len(features_df)} games")
        logger.info(f"Features: {len(features_df.columns)} total columns")
        
        return features_df
    
    def _calculate_team_stats(self, game_pbp, team, side):
        """
        Calculate team statistics for a game
        
        Args:
            game_pbp (pd.DataFrame): Play-by-play data for the game
            team (str): Team abbreviation
            side (str): 'home' or 'away'
            
        Returns:
            dict: Team statistics
        """
        # Filter plays for this team
        team_plays = game_pbp[game_pbp['posteam'] == team].copy()
        
        if team_plays.empty:
            return self._get_empty_stats(side)
        
        # Basic offensive stats
        stats = {
            f'{side}_total_plays': len(team_plays),
            f'{side}_total_yards': team_plays['yards_gained'].sum(),
            f'{side}_yards_per_play': team_plays['yards_gained'].mean() if len(team_plays) > 0 else 0,
            f'{side}_first_downs': len(team_plays[team_plays['first_down'] == 1]),
            f'{side}_touchdowns': team_plays['touchdown'].sum(),
            f'{side}_turnovers': team_plays['interception'].sum() + team_plays['fumble_lost'].sum(),
        }
        
        # Passing stats
        pass_plays = team_plays[team_plays['play_type'] == 'pass'].copy()
        if not pass_plays.empty:
            stats[f'{side}_pass_attempts'] = len(pass_plays)
            stats[f'{side}_pass_completions'] = pass_plays['complete_pass'].sum()
            stats[f'{side}_pass_yards'] = pass_plays['passing_yards'].sum()
            stats[f'{side}_pass_touchdowns'] = pass_plays['pass_touchdown'].sum()
            stats[f'{side}_pass_interceptions'] = pass_plays['interception'].sum()
            stats[f'{side}_completion_rate'] = pass_plays['complete_pass'].mean()
            stats[f'{side}_yards_per_pass'] = pass_plays['passing_yards'].mean()
        else:
            stats.update({
                f'{side}_pass_attempts': 0,
                f'{side}_pass_completions': 0,
                f'{side}_pass_yards': 0,
                f'{side}_pass_touchdowns': 0,
                f'{side}_pass_interceptions': 0,
                f'{side}_completion_rate': 0,
                f'{side}_yards_per_pass': 0,
            })
        
        # Rushing stats
        rush_plays = team_plays[team_plays['play_type'] == 'run'].copy()
        if not rush_plays.empty:
            stats[f'{side}_rush_attempts'] = len(rush_plays)
            stats[f'{side}_rush_yards'] = rush_plays['rushing_yards'].sum()
            stats[f'{side}_rush_touchdowns'] = rush_plays['rush_touchdown'].sum()
            stats[f'{side}_yards_per_rush'] = rush_plays['rushing_yards'].mean()
        else:
            stats.update({
                f'{side}_rush_attempts': 0,
                f'{side}_rush_yards': 0,
                f'{side}_rush_touchdowns': 0,
                f'{side}_yards_per_rush': 0,
            })
        
        # Situational stats
        third_down_plays = team_plays[team_plays['down'] == 3].copy()
        if not third_down_plays.empty:
            stats[f'{side}_third_down_conversions'] = len(third_down_plays[third_down_plays['first_down'] == 1])
            stats[f'{side}_third_down_attempts'] = len(third_down_plays)
            stats[f'{side}_third_down_rate'] = stats[f'{side}_third_down_conversions'] / stats[f'{side}_third_down_attempts']
        else:
            stats.update({
                f'{side}_third_down_conversions': 0,
                f'{side}_third_down_attempts': 0,
                f'{side}_third_down_rate': 0,
            })
        
        # Red zone stats
        redzone_plays = team_plays[team_plays['yardline_100'] <= 20].copy()
        if not redzone_plays.empty:
            stats[f'{side}_redzone_touchdowns'] = redzone_plays['touchdown'].sum()
            stats[f'{side}_redzone_attempts'] = len(redzone_plays)
            stats[f'{side}_redzone_rate'] = stats[f'{side}_redzone_touchdowns'] / stats[f'{side}_redzone_attempts'] if stats[f'{side}_redzone_attempts'] > 0 else 0
        else:
            stats.update({
                f'{side}_redzone_touchdowns': 0,
                f'{side}_redzone_attempts': 0,
                f'{side}_redzone_rate': 0,
            })
        
        return stats
    
    def _get_empty_stats(self, side):
        """Get empty stats for teams with no plays"""
        stats = {}
        for stat_type in ['total_plays', 'total_yards', 'yards_per_play', 'first_downs', 'touchdowns', 'turnovers',
                         'pass_attempts', 'pass_completions', 'pass_yards', 'pass_touchdowns', 'pass_interceptions',
                         'completion_rate', 'yards_per_pass', 'rush_attempts', 'rush_yards', 'rush_touchdowns',
                         'yards_per_rush', 'third_down_conversions', 'third_down_attempts', 'third_down_rate',
                         'redzone_touchdowns', 'redzone_attempts', 'redzone_rate']:
            stats[f'{side}_{stat_type}'] = 0
        return stats
    
    def prepare_ml_data(self, features_df):
        """
        Prepare data for machine learning
        
        Args:
            features_df (pd.DataFrame): Game features
            
        Returns:
            tuple: (X, y) features and target variable
        """
        logger.info("Preparing data for machine learning...")
        
        # Select feature columns (exclude metadata)
        exclude_cols = ['game_id', 'season', 'week', 'home_team', 'away_team', 'home_score', 'away_score', 'home_win']
        feature_cols = [col for col in features_df.columns if col not in exclude_cols]
        
        X = features_df[feature_cols].copy()
        y = features_df['home_win'].copy()
        
        # Handle missing values
        X = X.fillna(0)
        
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        logger.info(f"Prepared ML data: {X.shape[0]} games, {X.shape[1]} features")
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
    
    def predict_game_winner(self, home_team_stats, away_team_stats):
        """
        Predict the winner of a specific game
        
        Args:
            home_team_stats (dict): Home team statistics
            away_team_stats (dict): Away team statistics
            
        Returns:
            dict: Prediction results
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")
        
        # Create feature vector
        features = {}
        for stat_name, home_value in home_team_stats.items():
            features[f'home_{stat_name}'] = home_value
        for stat_name, away_value in away_team_stats.items():
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
        
        winner = "Home Team" if prediction == 1 else "Away Team"
        confidence = max(probabilities) * 100
        
        return {
            'predicted_winner': winner,
            'confidence': confidence,
            'home_win_probability': probabilities[1],
            'away_win_probability': probabilities[0],
            'prediction': prediction
        }
    
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
            
            # Filter for upcoming games
            today = datetime.now().date()
            upcoming_games = schedules[schedules['gameday'] >= today].copy()
            
            # Sort by date
            upcoming_games = upcoming_games.sort_values('gameday')
            
            logger.info(f"Found {len(upcoming_games)} upcoming games")
            return upcoming_games
            
        except Exception as e:
            logger.error(f"Error loading upcoming games: {e}")
            return pd.DataFrame()
    
    def save_model(self, filepath):
        """Save the trained model"""
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
        """Load a trained model"""
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.model_type = model_data['model_type']
        self.feature_names = model_data['feature_names']
        self.is_trained = model_data['is_trained']
        
        logger.info(f"Model loaded from {filepath}")

def main():
    """Main function to train model and predict upcoming games"""
    logger.info("🏈 Real NFL Game Winner Prediction Starting...")
    
    # Create model
    predictor = RealNFLPredictor(model_type='random_forest')
    
    # Load NFL data
    logger.info("Loading NFL data...")
    data = predictor.load_nfl_data(seasons=[2022, 2023, 2024])
    
    if not data:
        logger.error("Failed to load NFL data. Exiting.")
        return
    
    # Create game features
    logger.info("Creating game features...")
    game_features = predictor.create_game_features(data)
    
    if game_features.empty:
        logger.error("Failed to create game features. Exiting.")
        return
    
    # Prepare ML data
    X, y = predictor.prepare_ml_data(game_features)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"Training set: {X_train.shape[0]} games")
    logger.info(f"Test set: {X_test.shape[0]} games")
    
    # Train model
    predictor.train(X_train, y_train)
    
    # Evaluate model
    y_pred = predictor.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    logger.info(f"Test Accuracy: {accuracy:.3f}")
    logger.info("\nClassification Report:")
    logger.info(classification_report(y_test, y_pred))
    
    # Get feature importance
    if hasattr(predictor.model, 'feature_importances_'):
        feature_importance = dict(zip(predictor.feature_names, predictor.model.feature_importances_))
        logger.info("\nTop 10 Most Important Features:")
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        for feature, importance in sorted_features[:10]:
            logger.info(f"  {feature}: {importance:.4f}")
    
    # Save model
    os.makedirs('models', exist_ok=True)
    predictor.save_model('models/real_nfl_model.pkl')
    
    # Get upcoming games
    logger.info("\n🎯 Loading upcoming games...")
    upcoming_games = predictor.get_upcoming_games(weeks_ahead=2)
    
    if not upcoming_games.empty:
        logger.info(f"\n📅 Upcoming Games ({len(upcoming_games)} games):")
        
        for _, game in upcoming_games.head(10).iterrows():
            logger.info(f"\n🏟️  {game['away_team']} @ {game['home_team']}")
            logger.info(f"   Date: {game['gameday']}")
            logger.info(f"   Time: {game['gametime']}")
            
            # For demo purposes, create sample stats
            # In a real implementation, you'd get current team stats
            home_stats = {
                'yards_per_play': 5.5,
                'third_down_rate': 0.42,
                'redzone_rate': 0.65,
                'turnovers': 1.2,
                'completion_rate': 0.68,
                'yards_per_pass': 7.2,
                'yards_per_rush': 4.1
            }
            
            away_stats = {
                'yards_per_play': 5.3,
                'third_down_rate': 0.38,
                'redzone_rate': 0.58,
                'turnovers': 1.5,
                'completion_rate': 0.65,
                'yards_per_pass': 6.8,
                'yards_per_rush': 3.9
            }
            
            # Make prediction
            prediction = predictor.predict_game_winner(home_stats, away_stats)
            
            logger.info(f"   🏆 Predicted Winner: {prediction['predicted_winner']}")
            logger.info(f"   📊 Confidence: {prediction['confidence']:.1f}%")
            logger.info(f"   🏠 Home Win Probability: {prediction['home_win_probability']:.3f}")
            logger.info(f"   ✈️  Away Win Probability: {prediction['away_win_probability']:.3f}")
    
    logger.info("\n✅ Real NFL prediction model completed successfully!")
    logger.info("The model is now ready to predict winners of upcoming NFL games!")

if __name__ == "__main__":
    main()
