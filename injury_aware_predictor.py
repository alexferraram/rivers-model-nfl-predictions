#!/usr/bin/env python3
"""
Injury-Aware NFL Predictor
Includes injury impacts, especially for quarterbacks and key players.
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

class InjuryAwarePredictor:
    """NFL predictor that accounts for injuries and key player impacts"""
    
    def __init__(self, model_path='models/real_nfl_model.pkl'):
        """Initialize predictor with trained model"""
        self.model_path = model_path
        self.model = None
        self.feature_names = None
        self.pbp_2025 = None
        self.qb_data = None
        self.load_model()
        self.load_data()
        self.setup_injury_impacts()
    
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
        """Load NFL data and identify QBs"""
        logger.info("Loading NFL data for injury-aware prediction...")
        try:
            # Load 2025 data
            self.pbp_2025 = nfl.import_pbp_data([2025])
            logger.info(f"✅ Loaded {len(self.pbp_2025)} plays from 2025 season")
            
            # Extract QB data
            self.qb_data = self.pbp_2025[self.pbp_2025['passer_player_name'].notna()].copy()
            logger.info(f"✅ Identified {len(self.qb_data['passer_player_name'].unique())} QBs")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.pbp_2025 = None
            self.qb_data = None
    
    def setup_injury_impacts(self):
        """Setup injury impact multipliers"""
        self.injury_impacts = {
            'QB_STARTER_OUT': 0.85,      # Starting QB out - major impact
            'QB_BACKUP_PLAYING': 0.92,   # Backup QB playing - moderate impact
            'RB_STARTER_OUT': 0.95,      # Starting RB out - minor impact
            'WR_STARTER_OUT': 0.97,      # Starting WR out - minor impact
            'TE_STARTER_OUT': 0.98,      # Starting TE out - minor impact
            'DEFENSE_KEY_OUT': 0.96,     # Key defensive player out - minor impact
            'MULTIPLE_INJURIES': 0.90,   # Multiple key players out - moderate impact
        }
        
        # Team-specific QB importance (higher = more impact if QB is out)
        self.qb_importance = {
            'BUF': 0.95,  # Josh Allen is crucial
            'MIA': 0.90,  # Tua is important
            'KC': 0.95,   # Mahomes is crucial
            'CIN': 0.90,  # Burrow is important
            'LAC': 0.85,  # Herbert is important
            'DAL': 0.85,  # Dak is important
            'PHI': 0.85,  # Hurts is important
            'SF': 0.80,   # Purdy is good but system helps
            'BAL': 0.90,  # Jackson is crucial
            'GB': 0.85,   # Love is developing
            'DET': 0.85,  # Goff is solid
            'MIN': 0.80,  # Cousins is solid
            'ATL': 0.75,  # Cousins is solid
            'CAR': 0.70,  # Young is developing
            'NO': 0.75,   # Carr is solid
            'TB': 0.80,   # Mayfield is solid
            'IND': 0.80,  # Richardson is developing
            'TEN': 0.75,  # Levis is developing
            'HOU': 0.80,  # Stroud is developing
            'JAX': 0.85,  # Lawrence is solid
            'NYJ': 0.70,  # Rodgers is aging
            'NE': 0.70,   # Maye is rookie
            'PIT': 0.75,  # Fields is developing
            'CLE': 0.80,  # Watson is solid
            'DEN': 0.75,  # Nix is rookie
            'LV': 0.70,   # O'Connell is developing
            'LAR': 0.80,  # Stafford is solid
            'ARI': 0.85,  # Murray is solid
            'SEA': 0.75,  # Geno is solid
            'WAS': 0.75,  # Daniels is rookie
            'NYG': 0.70,  # Jones is struggling
            'CHI': 0.80,  # Williams is rookie
        }
    
    def get_team_qb_info(self, team):
        """Get QB information for a team"""
        if self.qb_data is None:
            return None
        
        team_qbs = self.qb_data[self.qb_data['posteam'] == team].copy()
        
        if team_qbs.empty:
            return None
        
        # Get QB stats
        qb_stats = team_qbs.groupby('passer_player_name').agg({
            'passing_yards': 'sum',
            'complete_pass': 'sum',
            'pass_attempt': 'sum',
            'pass_touchdown': 'sum',
            'interception': 'sum',
            'game_id': 'nunique'
        }).reset_index()
        
        # Calculate efficiency
        qb_stats['completion_rate'] = qb_stats['complete_pass'] / qb_stats['pass_attempt']
        qb_stats['yards_per_attempt'] = qb_stats['passing_yards'] / qb_stats['pass_attempt']
        qb_stats['td_int_ratio'] = qb_stats['pass_touchdown'] / (qb_stats['interception'] + 1)
        
        # Sort by attempts (most used QB)
        qb_stats = qb_stats.sort_values('pass_attempt', ascending=False)
        
        return qb_stats.iloc[0] if not qb_stats.empty else None
    
    def simulate_injury_scenarios(self, team):
        """Simulate different injury scenarios for a team"""
        scenarios = {
            'healthy': 1.0,
            'qb_backup': self.injury_impacts['QB_BACKUP_PLAYING'],
            'qb_out': self.injury_impacts['QB_STARTER_OUT'] * self.qb_importance.get(team, 0.8),
            'rb_out': self.injury_impacts['RB_STARTER_OUT'],
            'wr_out': self.injury_impacts['WR_STARTER_OUT'],
            'multiple_injuries': self.injury_impacts['MULTIPLE_INJURIES'],
        }
        
        return scenarios
    
    def get_team_stats_with_injuries(self, team, injury_scenario='healthy'):
        """Get team stats adjusted for injuries"""
        if self.pbp_2025 is None:
            return self._get_default_stats()
        
        team_games = self.pbp_2025[self.pbp_2025['posteam'] == team].copy()
        
        if team_games.empty:
            return self._get_default_stats()
        
        # Calculate base stats
        stats = {
            'yards_per_play': team_games['yards_gained'].mean(),
            'third_down_rate': len(team_games[(team_games['down'] == 3) & (team_games['first_down'] == 1)]) / max(len(team_games[team_games['down'] == 3]), 1),
            'redzone_rate': len(team_games[(team_games['yardline_100'] <= 20) & (team_games['touchdown'] == 1)]) / max(len(team_games[team_games['yardline_100'] <= 20]), 1),
            'turnovers': (team_games['interception'].sum() + team_games['fumble_lost'].sum()) / len(team_games['game_id'].unique()),
            'completion_rate': team_games[team_games['play_type'] == 'pass']['complete_pass'].mean(),
            'yards_per_pass': team_games[team_games['play_type'] == 'pass']['passing_yards'].mean(),
            'yards_per_rush': team_games[team_games['play_type'] == 'run']['rushing_yards'].mean()
        }
        
        # Apply injury adjustments
        injury_scenarios = self.simulate_injury_scenarios(team)
        injury_multiplier = injury_scenarios.get(injury_scenario, 1.0)
        
        # Apply injury impact to key stats
        if injury_scenario in ['qb_backup', 'qb_out']:
            stats['completion_rate'] *= injury_multiplier
            stats['yards_per_pass'] *= injury_multiplier
            stats['turnovers'] *= (2 - injury_multiplier)  # More turnovers with backup QB
            stats['redzone_rate'] *= injury_multiplier
        
        elif injury_scenario == 'rb_out':
            stats['yards_per_rush'] *= injury_multiplier
            stats['redzone_rate'] *= injury_multiplier
        
        elif injury_scenario == 'wr_out':
            stats['yards_per_pass'] *= injury_multiplier
            stats['completion_rate'] *= injury_multiplier
        
        elif injury_scenario == 'multiple_injuries':
            stats['yards_per_play'] *= injury_multiplier
            stats['third_down_rate'] *= injury_multiplier
            stats['turnovers'] *= (2 - injury_multiplier)
        
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
    
    def predict_game_with_injuries(self, home_team, away_team, 
                                 home_injury='healthy', away_injury='healthy'):
        """
        Predict game accounting for injuries
        
        Args:
            home_team (str): Home team abbreviation
            away_team (str): Away team abbreviation
            home_injury (str): Home team injury scenario
            away_injury (str): Away team injury scenario
        """
        if not self.model:
            logger.error("Model not loaded")
            return {}
        
        logger.info(f"🏥 Injury-aware prediction: {away_team} @ {home_team}")
        logger.info(f"   Home team injury scenario: {home_injury}")
        logger.info(f"   Away team injury scenario: {away_injury}")
        
        # Get QB info
        home_qb = self.get_team_qb_info(home_team)
        away_qb = self.get_team_qb_info(away_team)
        
        # Get team stats with injury adjustments
        home_stats = self.get_team_stats_with_injuries(home_team, home_injury)
        away_stats = self.get_team_stats_with_injuries(away_team, away_injury)
        
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
            'home_injury_scenario': home_injury,
            'away_injury_scenario': away_injury,
            'home_qb_info': home_qb,
            'away_qb_info': away_qb
        }
    
    def analyze_injury_impact(self, home_team, away_team):
        """Analyze how different injury scenarios affect the prediction"""
        logger.info(f"🔍 Analyzing injury impact for {away_team} @ {home_team}")
        
        scenarios = ['healthy', 'qb_backup', 'qb_out', 'rb_out', 'wr_out', 'multiple_injuries']
        results = []
        
        for home_scenario in scenarios:
            for away_scenario in scenarios:
                prediction = self.predict_game_with_injuries(
                    home_team, away_team, home_scenario, away_scenario
                )
                
                results.append({
                    'home_injury': home_scenario,
                    'away_injury': away_scenario,
                    'winner': prediction['predicted_winner'],
                    'confidence': prediction['confidence'],
                    'home_prob': prediction['home_win_probability']
                })
        
        return results

def main():
    """Main function to demonstrate injury-aware prediction"""
    logger.info("🏈 Injury-Aware NFL Predictor Starting...")
    
    # Create injury-aware predictor
    predictor = InjuryAwarePredictor()
    
    if not predictor.model:
        logger.error("Failed to load model. Exiting.")
        return
    
    # Analyze MIA @ BUF with different injury scenarios
    home_team = 'BUF'
    away_team = 'MIA'
    
    logger.info(f"\n🏥 Injury Impact Analysis: {away_team} @ {home_team}")
    logger.info("=" * 60)
    
    # Get QB information
    home_qb = predictor.get_team_qb_info(home_team)
    away_qb = predictor.get_team_qb_info(away_team)
    
    print(f"\n📊 QUARTERBACK INFORMATION:")
    print("-" * 35)
    if home_qb is not None:
        print(f"{home_team} QB: {home_qb['passer_player_name']}")
        print(f"  Completion Rate: {home_qb['completion_rate']:.1%}")
        print(f"  Yards Per Attempt: {home_qb['yards_per_attempt']:.1f}")
        print(f"  TD/INT Ratio: {home_qb['td_int_ratio']:.1f}")
        print(f"  Games Played: {home_qb['game_id']}")
    
    if away_qb is not None:
        print(f"\n{away_team} QB: {away_qb['passer_player_name']}")
        print(f"  Completion Rate: {away_qb['completion_rate']:.1%}")
        print(f"  Yards Per Attempt: {away_qb['yards_per_attempt']:.1f}")
        print(f"  TD/INT Ratio: {away_qb['td_int_ratio']:.1f}")
        print(f"  Games Played: {away_qb['game_id']}")
    
    # Test different injury scenarios
    scenarios_to_test = [
        ('healthy', 'healthy', 'Both teams healthy'),
        ('healthy', 'qb_backup', f'{away_team} backup QB'),
        ('qb_backup', 'healthy', f'{home_team} backup QB'),
        ('healthy', 'qb_out', f'{away_team} starting QB out'),
        ('qb_out', 'healthy', f'{home_team} starting QB out'),
        ('multiple_injuries', 'healthy', f'{home_team} multiple injuries'),
        ('healthy', 'multiple_injuries', f'{away_team} multiple injuries'),
    ]
    
    print(f"\n🎯 INJURY SCENARIO ANALYSIS:")
    print("-" * 40)
    
    for home_injury, away_injury, description in scenarios_to_test:
        prediction = predictor.predict_game_with_injuries(
            home_team, away_team, home_injury, away_injury
        )
        
        print(f"{description}:")
        print(f"  Winner: {prediction['predicted_winner']}")
        print(f"  Confidence: {prediction['confidence']:.1f}%")
        print(f"  Home Win Prob: {prediction['home_win_probability']:.3f}")
        print()
    
    # Get baseline prediction
    baseline = predictor.predict_game_with_injuries(home_team, away_team, 'healthy', 'healthy')
    
    print(f"🏆 BASELINE PREDICTION (Both Healthy):")
    print("-" * 40)
    print(f"Predicted Winner: {baseline['predicted_winner']}")
    print(f"Confidence: {baseline['confidence']:.1f}%")
    print(f"Home Win Probability: {baseline['home_win_probability']:.3f}")
    print(f"Away Win Probability: {baseline['away_win_probability']:.3f}")
    
    logger.info("\n✅ Injury-aware prediction completed!")
    logger.info("The model now accounts for QB and key player injuries!")

if __name__ == "__main__":
    main()





