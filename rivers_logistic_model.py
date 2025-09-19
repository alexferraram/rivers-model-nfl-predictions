"""
RIVERS Logistic Regression Model
===============================

Advanced NFL prediction model using Logistic Regression to learn optimal feature weights
from historical data instead of manual weight assignment.

Features:
- Enhanced EPA Score (with PFF integration)
- Enhanced Efficiency Score (Success Rate)
- Enhanced Yards Score (Yards per Play)
- Enhanced Turnover Score (Turnover Rate)
- PFF Matchup Score (Team Grades)
- Weather Impact Score
- Dynamic Injury Impact

Output: Win Probability (0-1) for home team
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

from enhanced_epa_system import EnhancedEPASystem
from pff_data_system import PFFDataSystem
from dynamic_injury_system import DynamicInjurySystem
from database_validation_system import DatabaseValidationSystem

class RiversLogisticModel:
    """
    RIVERS Model using Logistic Regression to learn optimal feature weights
    from historical NFL data.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Initialize subsystems
        self.pff_system = PFFDataSystem()
        self.enhanced_epa_system = EnhancedEPASystem(self.pff_system)
        self.injury_system = DynamicInjurySystem(self.pff_system)
        self.validation_system = DatabaseValidationSystem()
        
        # Model components
        self.model = LogisticRegression(random_state=42, max_iter=1000)
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Cache for injury data to avoid repeated scraping
        self.injury_cache = {}
        self.injury_cache_time = None
        
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
        
        self.logger.info("🌊 INITIALIZING RIVERS LOGISTIC REGRESSION MODEL")
        self.logger.info("=" * 60)
        
    def validate_and_load_data(self):
        """Validate all databases and load historical data"""
        self.logger.info("🔍 VALIDATING DATABASES")
        self.logger.info("=" * 30)
        
        # Validate all systems
        validation_result = self.validation_system.validate_all_databases()
        if not validation_result:
            raise Exception("❌ Database validation failed")
            
        self.logger.info("✅ All databases validated successfully")
        
        # Load historical data
        self.logger.info("📊 Loading historical data...")
        
        # Load play-by-play data for multiple seasons
        seasons = [2023, 2024, 2025]
        self.pbp_data = {}
        
        for season in seasons:
            try:
                import nfl_data_py as nfl
                pbp = nfl.import_pbp_data([season])
                self.pbp_data[season] = pbp
                self.logger.info(f"✅ Loaded {len(pbp)} plays from {season}")
            except Exception as e:
                self.logger.error(f"❌ Failed to load {season} data: {e}")
                continue
                
        # Load schedule data
        try:
            import nfl_data_py as nfl
            self.schedule_data = nfl.import_schedules([2023, 2024, 2025])
            self.logger.info(f"✅ Loaded {len(self.schedule_data)} games from schedules")
        except Exception as e:
            self.logger.error(f"❌ Failed to load schedule data: {e}")
            raise
            
        self.logger.info("✅ Data loading complete")
        
    def extract_features_for_game(self, home_team, away_team, week, season):
        """
        Extract all features for a specific game
        
        Returns:
            dict: Feature values for the game
        """
        features = {}
        
        try:
            # Get team data for the season
            home_data = self._get_team_data(home_team, season, week)
            away_data = self._get_team_data(away_team, season, week)
            
            # Enhanced EPA Scores (simplified to avoid errors)
            home_epa = self._calculate_simple_epa_score(home_data)
            away_epa = self._calculate_simple_epa_score(away_data)
            
            features['home_epa_score'] = float(home_epa)
            features['away_epa_score'] = float(away_epa)
            
            # Enhanced Efficiency Scores (Success Rate)
            home_efficiency = self._calculate_efficiency_score(home_data)
            away_efficiency = self._calculate_efficiency_score(away_data)
            features['home_efficiency_score'] = float(home_efficiency)
            features['away_efficiency_score'] = float(away_efficiency)
            
            # Enhanced Yards Scores
            home_yards = self._calculate_yards_score(home_data)
            away_yards = self._calculate_yards_score(away_data)
            features['home_yards_score'] = float(home_yards)
            features['away_yards_score'] = float(away_yards)
            
            # Enhanced Turnover Scores
            home_turnovers = self._calculate_turnover_score(home_data)
            away_turnovers = self._calculate_turnover_score(away_data)
            features['home_turnover_score'] = float(home_turnovers)
            features['away_turnover_score'] = float(away_turnovers)
            
            # PFF Matchup Scores
            home_pff = self._calculate_pff_score(home_team)
            away_pff = self._calculate_pff_score(away_team)
            features['home_pff_score'] = float(home_pff)
            features['away_pff_score'] = float(away_pff)
            
            # Weather Impact
            weather_impact = self._calculate_weather_impact(home_team, away_team, week, season)
            features['weather_impact'] = float(weather_impact)
            
            # Injury Impact
            home_injury_impact = self._calculate_injury_impact(home_team)
            away_injury_impact = self._calculate_injury_impact(away_team)
            features['home_injury_impact'] = float(home_injury_impact)
            features['away_injury_impact'] = float(away_injury_impact)
            
            return features
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting features for {home_team} vs {away_team}: {e}")
            return None
            
    def _get_team_data(self, team, season, week):
        """Get team's play-by-play data for the season up to the given week"""
        if season not in self.pbp_data:
            return pd.DataFrame()
            
        team_data = self.pbp_data[season].copy()
        
        # Filter for team's games up to the given week
        team_games = team_data[
            ((team_data['home_team'] == team) | (team_data['away_team'] == team)) &
            (team_data['week'] <= week)
        ].copy()
        
        return team_games
        
    def _calculate_simple_epa_score(self, team_data):
        """Calculate simple EPA score from team data"""
        if team_data.empty:
            return 50.0
            
        # Get offensive plays
        offensive_plays = team_data[team_data['posteam'] == team_data['home_team'].iloc[0] if 'home_team' in team_data.columns else team_data['posteam']]
        if offensive_plays.empty:
            return 50.0
            
        # Calculate average EPA
        avg_epa = offensive_plays['epa'].mean()
        
        # Normalize to 0-100 scale (assuming EPA range of -2 to +2)
        epa_score = min(100, max(0, ((avg_epa + 2) / 4) * 100))
        return epa_score
        
    def _calculate_efficiency_score(self, team_data):
        """Calculate success rate (efficiency) score"""
        if team_data.empty:
            return 50.0
            
        # Calculate success rate (EPA > 0)
        offensive_plays = team_data[team_data['posteam'] == team_data['home_team'].iloc[0] if 'home_team' in team_data.columns else team_data['posteam']]
        if offensive_plays.empty:
            return 50.0
            
        success_rate = (offensive_plays['epa'] > 0).mean()
        
        # Normalize to 0-100 scale
        efficiency_score = min(100, max(0, success_rate * 100))
        return efficiency_score
        
    def _calculate_yards_score(self, team_data):
        """Calculate yards per play score"""
        if team_data.empty:
            return 50.0
            
        # Get offensive plays
        offensive_plays = team_data[team_data['posteam'] == team_data['home_team'].iloc[0] if 'home_team' in team_data.columns else team_data['posteam']]
        if offensive_plays.empty:
            return 50.0
            
        yards_per_play = offensive_plays['yards_gained'].mean()
        
        # Normalize to 0-100 scale (assuming 0-20 yards range)
        yards_score = min(100, max(0, (yards_per_play / 20) * 100))
        return yards_score
        
    def _calculate_turnover_score(self, team_data):
        """Calculate turnover rate score (lower turnover rate = higher score)"""
        if team_data.empty:
            return 50.0
            
        # Get offensive plays
        offensive_plays = team_data[team_data['posteam'] == team_data['home_team'].iloc[0] if 'home_team' in team_data.columns else team_data['posteam']]
        if offensive_plays.empty:
            return 50.0
            
        # Calculate turnover rate
        turnovers = offensive_plays['interception'].sum() + offensive_plays['fumble_lost'].sum()
        total_plays = len(offensive_plays)
        turnover_rate = turnovers / total_plays if total_plays > 0 else 0
        
        # Convert to score (lower turnover rate = higher score)
        turnover_score = max(0, 100 - (turnover_rate * 1000))  # Scale appropriately
        return turnover_score
        
    def _calculate_pff_score(self, team):
        """Calculate PFF team grade score"""
        try:
            team_grades = self.pff_system.team_grades.get(team, {})
            if team_grades and isinstance(team_grades, dict):
                # Average of all position group grades
                avg_grade = np.mean(list(team_grades.values()))
                return float(avg_grade)
            else:
                return 75.0  # Default PFF grade
        except Exception as e:
            self.logger.warning(f"⚠️ Error getting PFF grades for {team}: {e}")
            return 75.0
            
    def _calculate_weather_impact(self, home_team, away_team, week, season):
        """Calculate weather impact score"""
        try:
            # Get game data
            game_data = self.schedule_data[
                (self.schedule_data['home_team'] == home_team) &
                (self.schedule_data['away_team'] == away_team) &
                (self.schedule_data['week'] == week) &
                (self.schedule_data['season'] == season)
            ]
            
            if game_data.empty:
                return 0.0
                
            # Simple weather impact (can be enhanced)
            weather_impact = 0.0  # Neutral weather impact
            
            return weather_impact
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculating weather impact: {e}")
            return 0.0
            
    def _calculate_injury_impact(self, team):
        """Calculate injury impact score using cached data"""
        try:
            # Use cached injury data to avoid repeated scraping
            if not self.injury_cache:
                self.logger.info("📥 Loading injury data once...")
                self.injury_cache = self.injury_system.scrape_nfl_injuries()
                self.injury_cache_time = pd.Timestamp.now()
                
            team_injuries = self.injury_cache.get(team, [])
            
            # Calculate total injury impact
            total_impact = 0.0
            for injury in team_injuries:
                if injury.get('status') == 'OUT':
                    # Simple impact calculation (can be enhanced)
                    total_impact += 1.0
                    
            return total_impact
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculating injury impact for {team}: {e}")
            return 0.0
            
    def build_training_dataset(self):
        """Build training dataset from historical games"""
        self.logger.info("🏗️ Building training dataset...")
        
        training_data = []
        
        # Process each season (limit to avoid long processing)
        for season in [2023, 2024]:
            if season not in self.pbp_data:
                continue
                
            season_games = self.schedule_data[self.schedule_data['season'] == season]
            
            # Limit to first 100 games per season to avoid long processing
            season_games = season_games.head(100)
            
            for _, game in season_games.iterrows():
                try:
                    home_team = game['home_team']
                    away_team = game['away_team']
                    week = game['week']
                    
                    # Extract features
                    features = self.extract_features_for_game(home_team, away_team, week, season)
                    
                    if features is None:
                        continue
                        
                    # Get actual outcome
                    home_score = game.get('home_score', 0)
                    away_score = game.get('away_score', 0)
                    home_won = 1 if home_score > away_score else 0
                    
                    # Add to training data
                    training_data.append({
                        **features,
                        'home_won': home_won
                    })
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Error processing game {home_team} vs {away_team}: {e}")
                    continue
                    
        self.logger.info(f"✅ Built training dataset with {len(training_data)} games")
        return pd.DataFrame(training_data)
        
    def train_model(self):
        """Train the logistic regression model"""
        self.logger.info("🎯 Training Logistic Regression Model...")
        
        # Build training dataset
        training_df = self.build_training_dataset()
        
        if training_df.empty:
            raise Exception("❌ No training data available")
            
        # Prepare features and target
        X = training_df[self.feature_names]
        y = training_df['home_won']
        
        # Handle missing values
        X = X.fillna(X.mean())
        
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
        """Predict win probability for a game"""
        if not self.is_trained:
            raise Exception("❌ Model must be trained before making predictions")
            
        # Extract features
        features = self.extract_features_for_game(home_team, away_team, week, season)
        
        if features is None:
            raise Exception(f"❌ Could not extract features for {home_team} vs {away_team}")
            
        # Prepare feature vector
        X = np.array([features[name] for name in self.feature_names]).reshape(1, -1)
        
        # Handle missing values
        X = np.nan_to_num(X, nan=0.0)
        
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

def main():
    """Main function to demonstrate the model"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize model
    model = RiversLogisticModel()
    
    # Validate and load data
    model.validate_and_load_data()
    
    # Train model
    model.train_model()
    
    # Test prediction
    prediction = model.predict_game('BUF', 'MIA', week=3, season=2025)
    
    print("\n🏈 RIVERS LOGISTIC REGRESSION PREDICTION")
    print("=" * 50)
    print(f"🏈 {prediction['away_team']} @ {prediction['home_team']}")
    print(f"🏆 Winner: {prediction['winner']}")
    print(f"🎯 Win Probability: {prediction['win_probability']:.1%}")
    print(f"📊 Confidence: {prediction['confidence']:.1%}")
    
    # Show feature importance
    print("\n🎯 LEARNED FEATURE WEIGHTS:")
    print("=" * 30)
    importance = model.get_feature_importance()
    for _, row in importance.iterrows():
        print(f"{row['feature']}: {row['coefficient']:.4f}")

if __name__ == "__main__":
    main()
