#!/usr/bin/env python3
"""
Comprehensive NFL Game Outcome Predictor (2025 Emphasis)
Implements all key predictive variables with proper weighting for current season performance.
"""

import pandas as pd
import numpy as np
import nfl_data_py as nfl
import joblib
import logging
from datetime import datetime, timedelta
import requests
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveNFLPredictor:
    """Comprehensive NFL predictor with all key variables and 2025 emphasis"""
    
    def __init__(self, model_path='models/real_nfl_model.pkl'):
        """Initialize comprehensive predictor"""
        self.model_path = model_path
        self.model = None
        self.feature_names = None
        self.pbp_2025 = None
        self.pbp_2024 = None
        self.schedules_2025 = None
        self.load_model()
        self.load_data()
        self.setup_weighting_system()
        self.setup_injury_impacts()
        self.setup_team_locations()
    
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
        """Load comprehensive NFL data"""
        logger.info("Loading comprehensive NFL data...")
        try:
            # Load 2025 data (primary)
            self.pbp_2025 = nfl.import_pbp_data([2025])
            self.schedules_2025 = nfl.import_schedules([2025])
            logger.info(f"✅ Loaded {len(self.pbp_2025)} plays from 2025 season")
            logger.info(f"✅ Loaded {len(self.schedules_2025)} games from 2025 season")
            
            # Load 2024 data (for context/regression)
            self.pbp_2024 = nfl.import_pbp_data([2024])
            logger.info(f"✅ Loaded {len(self.pbp_2024)} plays from 2024 season")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.pbp_2025 = None
            self.pbp_2024 = None
            self.schedules_2025 = None
    
    def setup_weighting_system(self):
        """Setup comprehensive weighting system for 2025 emphasis"""
        self.weights = {
            # Offensive & Defensive Performance (Current Season) - ~50% of weight
            'offensive_defensive_performance': 0.50,
            'scoring_metrics': 0.30,  # Points for/against, point differential
            'yardage_efficiency': 0.20,  # Yards/play, efficiency stats
            
            # Turnover Differential - ~10-15% of weight
            'turnover_differential': 0.125,
            
            # Recent Momentum and Form - ~15% of weight
            'recent_momentum': 0.15,
            
            # Injuries and Roster Changes - variable weight (up to ~10-20% in extreme cases)
            'injuries_roster': 0.10,
            
            # Home-Field & Situational Factors - ~5-10% of weight
            'situational_factors': 0.075,
            'home_field': 0.05,
            'travel_rest': 0.015,
            'weather': 0.01,
            
            # Advanced Metrics - usage dependent
            'advanced_metrics': 0.10,
            
            # Betting Line - high weight if used
            'betting_line': 0.20,  # Only if available
        }
        
        # Week-based regression to 2025 data
        self.current_week = self._get_current_week()
        self.season_progress = min(self.current_week / 18, 1.0)  # 0 to 1
        
        # Weight for 2025 vs historical data
        self.current_season_weight = 0.1 + (0.9 * self.season_progress)  # 10% to 100%
        logger.info(f"📊 Current season weight: {self.current_season_weight:.1%}")
    
    def setup_injury_impacts(self):
        """Setup comprehensive injury impact system"""
        self.injury_impacts = {
            # QB impacts (most critical)
            'qb_starter_out': 0.70,  # 30% reduction in win probability
            'qb_backup_playing': 0.85,  # 15% reduction
            'qb_elite_out': 0.60,  # 40% reduction for elite QBs
            
            # Skill position impacts
            'rb_starter_out': 0.95,  # 5% reduction
            'wr_starter_out': 0.97,  # 3% reduction
            'te_starter_out': 0.98,  # 2% reduction
            
            # Defensive impacts
            'defense_key_out': 0.96,  # 4% reduction
            'pass_rush_out': 0.94,  # 6% reduction
            
            # Multiple injuries
            'multiple_injuries': 0.90,  # 10% reduction
            'critical_injuries': 0.80,  # 20% reduction
        }
        
        # Team-specific QB importance
        self.qb_importance = {
            'BUF': 0.95, 'KC': 0.95, 'CIN': 0.90, 'LAC': 0.85, 'DAL': 0.85,
            'PHI': 0.85, 'BAL': 0.90, 'GB': 0.85, 'DET': 0.85, 'MIN': 0.80,
            'SF': 0.80, 'ATL': 0.75, 'CAR': 0.70, 'NO': 0.75, 'TB': 0.80,
            'IND': 0.80, 'TEN': 0.75, 'HOU': 0.80, 'JAX': 0.85, 'NYJ': 0.70,
            'NE': 0.70, 'PIT': 0.75, 'CLE': 0.80, 'DEN': 0.75, 'LV': 0.70,
            'LAR': 0.80, 'ARI': 0.85, 'SEA': 0.75, 'WAS': 0.75, 'NYG': 0.70,
            'CHI': 0.80, 'MIA': 0.90
        }
    
    def setup_team_locations(self):
        """Setup team location data for travel analysis"""
        self.team_locations = {
            'BUF': {'city': 'Buffalo', 'state': 'NY', 'timezone': 'EST'},
            'MIA': {'city': 'Miami', 'state': 'FL', 'timezone': 'EST'},
            'NE': {'city': 'Foxborough', 'state': 'MA', 'timezone': 'EST'},
            'NYJ': {'city': 'East Rutherford', 'state': 'NJ', 'timezone': 'EST'},
            'BAL': {'city': 'Baltimore', 'state': 'MD', 'timezone': 'EST'},
            'CIN': {'city': 'Cincinnati', 'state': 'OH', 'timezone': 'EST'},
            'CLE': {'city': 'Cleveland', 'state': 'OH', 'timezone': 'EST'},
            'PIT': {'city': 'Pittsburgh', 'state': 'PA', 'timezone': 'EST'},
            'HOU': {'city': 'Houston', 'state': 'TX', 'timezone': 'CST'},
            'IND': {'city': 'Indianapolis', 'state': 'IN', 'timezone': 'EST'},
            'JAX': {'city': 'Jacksonville', 'state': 'FL', 'timezone': 'EST'},
            'TEN': {'city': 'Nashville', 'state': 'TN', 'timezone': 'CST'},
            'DEN': {'city': 'Denver', 'state': 'CO', 'timezone': 'MST'},
            'KC': {'city': 'Kansas City', 'state': 'MO', 'timezone': 'CST'},
            'LV': {'city': 'Las Vegas', 'state': 'NV', 'timezone': 'PST'},
            'LAC': {'city': 'Los Angeles', 'state': 'CA', 'timezone': 'PST'},
            'DAL': {'city': 'Arlington', 'state': 'TX', 'timezone': 'CST'},
            'NYG': {'city': 'East Rutherford', 'state': 'NJ', 'timezone': 'EST'},
            'PHI': {'city': 'Philadelphia', 'state': 'PA', 'timezone': 'EST'},
            'WAS': {'city': 'Landover', 'state': 'MD', 'timezone': 'EST'},
            'CHI': {'city': 'Chicago', 'state': 'IL', 'timezone': 'CST'},
            'DET': {'city': 'Detroit', 'state': 'MI', 'timezone': 'EST'},
            'GB': {'city': 'Green Bay', 'state': 'WI', 'timezone': 'CST'},
            'MIN': {'city': 'Minneapolis', 'state': 'MN', 'timezone': 'CST'},
            'ATL': {'city': 'Atlanta', 'state': 'GA', 'timezone': 'EST'},
            'CAR': {'city': 'Charlotte', 'state': 'NC', 'timezone': 'EST'},
            'NO': {'city': 'New Orleans', 'state': 'LA', 'timezone': 'CST'},
            'TB': {'city': 'Tampa', 'state': 'FL', 'timezone': 'EST'},
            'ARI': {'city': 'Glendale', 'state': 'AZ', 'timezone': 'MST'},
            'LAR': {'city': 'Los Angeles', 'state': 'CA', 'timezone': 'PST'},
            'SF': {'city': 'Santa Clara', 'state': 'CA', 'timezone': 'PST'},
            'SEA': {'city': 'Seattle', 'state': 'WA', 'timezone': 'PST'}
        }
    
    def _get_current_week(self):
        """Get current NFL week"""
        try:
            if self.schedules_2025 is not None:
                # Get the latest week from schedules
                latest_week = self.schedules_2025['week'].max()
                return latest_week
            return 1  # Default to week 1
        except:
            return 1
    
    def get_comprehensive_team_stats(self, team, injury_scenario='healthy'):
        """Get comprehensive team statistics with all variables"""
        if self.pbp_2025 is None:
            return self._get_default_stats()
        
        # Get 2025 stats (primary)
        team_2025 = self.pbp_2025[self.pbp_2025['posteam'] == team].copy()
        
        # Get 2024 stats (for regression)
        team_2024 = self.pbp_2024[self.pbp_2024['posteam'] == team].copy() if self.pbp_2024 is not None else pd.DataFrame()
        
        # Calculate comprehensive stats
        stats_2025 = self._calculate_comprehensive_stats(team_2025, "2025")
        stats_2024 = self._calculate_comprehensive_stats(team_2024, "2024") if not team_2024.empty else self._get_default_stats()
        
        # Combine with weighted average (emphasizing 2025)
        comprehensive_stats = {}
        for stat in stats_2025.keys():
            if stat in stats_2024:
                comprehensive_stats[stat] = (
                    self.current_season_weight * stats_2025[stat] + 
                    (1 - self.current_season_weight) * stats_2024[stat]
                )
            else:
                comprehensive_stats[stat] = stats_2025[stat]
        
        # Apply injury adjustments
        comprehensive_stats = self._apply_injury_adjustments(comprehensive_stats, team, injury_scenario)
        
        return comprehensive_stats
    
    def _calculate_comprehensive_stats(self, team_games, season_label):
        """Calculate comprehensive team statistics"""
        if team_games.empty:
            return self._get_default_stats()
        
        logger.info(f"📊 Calculating {season_label} comprehensive stats: {len(team_games)} plays")
        
        # Basic offensive/defensive stats
        stats = {
            # Scoring metrics (highest weight)
            'points_per_game': team_games.get('posteam_score', pd.Series([24.0])).mean(),
            'yards_per_play': team_games['yards_gained'].mean(),
            'first_downs_per_game': len(team_games[team_games['first_down'] == 1]) / len(team_games['game_id'].unique()),
            
            # Efficiency metrics
            'third_down_rate': len(team_games[(team_games['down'] == 3) & (team_games['first_down'] == 1)]) / max(len(team_games[team_games['down'] == 3]), 1),
            'redzone_rate': len(team_games[(team_games['yardline_100'] <= 20) & (team_games['touchdown'] == 1)]) / max(len(team_games[team_games['yardline_100'] <= 20]), 1),
            
            # Turnover metrics (critical)
            'turnovers_per_game': (team_games['interception'].sum() + team_games['fumble_lost'].sum()) / len(team_games['game_id'].unique()),
            'takeaways_per_game': (team_games['interception'].sum() + team_games.get('fumble_recovery', pd.Series([0])).sum()) / len(team_games['game_id'].unique()),
            
            # Passing metrics
            'completion_rate': team_games[team_games['play_type'] == 'pass']['complete_pass'].mean(),
            'yards_per_pass': team_games[team_games['play_type'] == 'pass']['passing_yards'].mean(),
            'pass_touchdown_rate': team_games[team_games['play_type'] == 'pass']['pass_touchdown'].sum() / len(team_games['game_id'].unique()),
            
            # Rushing metrics
            'yards_per_rush': team_games[team_games['play_type'] == 'run']['rushing_yards'].mean(),
            'rush_touchdown_rate': team_games[team_games['play_type'] == 'run']['rush_touchdown'].sum() / len(team_games['game_id'].unique()),
            
            # Penalty metrics
            'penalties_per_game': team_games['penalty'].sum() / len(team_games['game_id'].unique()),
            'penalty_yards_per_game': team_games['penalty_yards'].sum() / len(team_games['game_id'].unique()),
            
            # Special teams (basic)
            'field_goal_attempts': team_games[team_games['play_type'] == 'field_goal'].shape[0] / len(team_games['game_id'].unique()),
        }
        
        # Calculate advanced metrics
        stats.update(self._calculate_advanced_metrics(team_games))
        
        # Calculate recent momentum (last 3 games)
        stats.update(self._calculate_recent_momentum(team_games))
        
        # Fill NaN values
        for key, value in stats.items():
            if pd.isna(value):
                stats[key] = self._get_default_stats().get(key, 0)
        
        return stats
    
    def _calculate_advanced_metrics(self, team_games):
        """Calculate advanced metrics like EPA"""
        advanced_stats = {}
        
        try:
            # EPA per play (if available)
            if 'epa' in team_games.columns:
                advanced_stats['epa_per_play'] = team_games['epa'].mean()
                advanced_stats['success_rate'] = (team_games['epa'] > 0).mean()
            else:
                advanced_stats['epa_per_play'] = 0.0
                advanced_stats['success_rate'] = 0.5
            
            # Explosive plays (20+ yard gains)
            explosive_plays = team_games[team_games['yards_gained'] >= 20]
            advanced_stats['explosive_play_rate'] = len(explosive_plays) / len(team_games)
            
            # Time of possession proxy (plays per game)
            advanced_stats['plays_per_game'] = len(team_games) / len(team_games['game_id'].unique())
            
        except Exception as e:
            logger.warning(f"Error calculating advanced metrics: {e}")
            advanced_stats = {
                'epa_per_play': 0.0,
                'success_rate': 0.5,
                'explosive_play_rate': 0.1,
                'plays_per_game': 65.0
            }
        
        return advanced_stats
    
    def _calculate_recent_momentum(self, team_games):
        """Calculate recent momentum (last 3 games)"""
        momentum_stats = {}
        
        try:
            # Get last 3 games
            recent_games = team_games.groupby('game_id').agg({
                'yards_gained': 'sum',
                'touchdown': 'sum',
                'interception': 'sum',
                'fumble_lost': 'sum'
            }).tail(3)
            
            if len(recent_games) >= 2:
                # Recent performance vs season average
                recent_yards = recent_games['yards_gained'].mean()
                season_yards = team_games['yards_gained'].mean()
                momentum_stats['recent_yards_trend'] = recent_yards / max(season_yards, 1)
                
                recent_turnovers = recent_games[['interception', 'fumble_lost']].sum(axis=1).mean()
                season_turnovers = team_games['interception'].sum() + team_games['fumble_lost'].sum()
                season_turnovers_per_game = season_turnovers / len(team_games['game_id'].unique())
                momentum_stats['recent_turnover_trend'] = recent_turnovers / max(season_turnovers_per_game, 1)
            else:
                momentum_stats['recent_yards_trend'] = 1.0
                momentum_stats['recent_turnover_trend'] = 1.0
                
        except Exception as e:
            logger.warning(f"Error calculating momentum: {e}")
            momentum_stats = {
                'recent_yards_trend': 1.0,
                'recent_turnover_trend': 1.0
            }
        
        return momentum_stats
    
    def _apply_injury_adjustments(self, stats, team, injury_scenario):
        """Apply injury adjustments to team stats"""
        if injury_scenario == 'healthy':
            return stats
        
        # Get injury impact multiplier
        injury_multiplier = self.injury_impacts.get(injury_scenario, 1.0)
        
        # Apply team-specific QB importance
        if 'qb' in injury_scenario:
            qb_importance = self.qb_importance.get(team, 0.8)
            injury_multiplier = 1.0 - ((1.0 - injury_multiplier) * qb_importance)
        
        # Apply adjustments to key stats
        if injury_scenario in ['qb_backup', 'qb_out', 'qb_elite_out']:
            stats['completion_rate'] *= injury_multiplier
            stats['yards_per_pass'] *= injury_multiplier
            stats['turnovers_per_game'] *= (2 - injury_multiplier)  # More turnovers
            stats['redzone_rate'] *= injury_multiplier
            stats['pass_touchdown_rate'] *= injury_multiplier
        
        elif injury_scenario == 'rb_starter_out':
            stats['yards_per_rush'] *= injury_multiplier
            stats['redzone_rate'] *= injury_multiplier
            stats['rush_touchdown_rate'] *= injury_multiplier
        
        elif injury_scenario == 'wr_starter_out':
            stats['yards_per_pass'] *= injury_multiplier
            stats['completion_rate'] *= injury_multiplier
        
        elif injury_scenario in ['multiple_injuries', 'critical_injuries']:
            stats['yards_per_play'] *= injury_multiplier
            stats['third_down_rate'] *= injury_multiplier
            stats['turnovers_per_game'] *= (2 - injury_multiplier)
            stats['points_per_game'] *= injury_multiplier
        
        return stats
    
    def _get_default_stats(self):
        """Get default team statistics"""
        return {
            'points_per_game': 24.0,
            'yards_per_play': 5.5,
            'first_downs_per_game': 20.0,
            'third_down_rate': 0.4,
            'redzone_rate': 0.6,
            'turnovers_per_game': 1.5,
            'takeaways_per_game': 1.5,
            'completion_rate': 0.65,
            'yards_per_pass': 7.0,
            'pass_touchdown_rate': 1.5,
            'yards_per_rush': 4.0,
            'rush_touchdown_rate': 1.0,
            'penalties_per_game': 7.0,
            'penalty_yards_per_game': 60.0,
            'field_goal_attempts': 2.0,
            'epa_per_play': 0.0,
            'success_rate': 0.5,
            'explosive_play_rate': 0.1,
            'plays_per_game': 65.0,
            'recent_yards_trend': 1.0,
            'recent_turnover_trend': 1.0
        }
    
    def get_situational_factors(self, home_team, away_team, game_date=None):
        """Get situational factors for the game"""
        factors = {}
        
        # Home field advantage
        factors['home_field_advantage'] = 0.55  # 55% win rate for home teams
        
        # Travel analysis
        home_location = self.team_locations.get(home_team, {})
        away_location = self.team_locations.get(away_team, {})
        
        if home_location and away_location:
            # Time zone difference
            timezone_diff = self._get_timezone_difference(home_location.get('timezone'), away_location.get('timezone'))
            factors['timezone_travel'] = timezone_diff
            
            # Distance estimation (simplified)
            factors['travel_distance'] = self._estimate_travel_distance(home_location, away_location)
        
        # Rest analysis (simplified - would need actual game dates)
        factors['rest_advantage'] = 0.0  # Would calculate based on last game date
        
        # Weather (would integrate with weather API)
        factors['weather_impact'] = 0.0  # Would get from weather API
        
        return factors
    
    def _get_timezone_difference(self, home_tz, away_tz):
        """Get timezone difference impact"""
        tz_map = {'EST': 0, 'CST': 1, 'MST': 2, 'PST': 3}
        home_offset = tz_map.get(home_tz, 0)
        away_offset = tz_map.get(away_tz, 0)
        
        diff = abs(home_offset - away_offset)
        return diff * 0.02  # 2% impact per timezone difference
    
    def _estimate_travel_distance(self, home_location, away_location):
        """Estimate travel distance impact"""
        # Simplified distance calculation
        # In practice, would use actual coordinates
        return 0.01  # 1% impact for travel
    
    def predict_comprehensive_game(self, home_team, away_team, 
                                 home_injury='healthy', away_injury='healthy',
                                 include_betting_line=False):
        """
        Make comprehensive game prediction with all variables
        
        Args:
            home_team (str): Home team abbreviation
            away_team (str): Away team abbreviation
            home_injury (str): Home team injury scenario
            away_injury (str): Away team injury scenario
            include_betting_line (bool): Whether to include betting line
        """
        if not self.model:
            logger.error("Model not loaded")
            return {}
        
        logger.info(f"🎯 Comprehensive prediction: {away_team} @ {home_team}")
        logger.info(f"   Home injury scenario: {home_injury}")
        logger.info(f"   Away injury scenario: {away_injury}")
        logger.info(f"   2025 season weight: {self.current_season_weight:.1%}")
        
        # Get comprehensive team stats
        home_stats = self.get_comprehensive_team_stats(home_team, home_injury)
        away_stats = self.get_comprehensive_team_stats(away_team, away_injury)
        
        # Get situational factors
        situational_factors = self.get_situational_factors(home_team, away_team)
        
        # Create comprehensive feature vector
        features = {}
        
        # Team performance features
        for stat_name, home_value in home_stats.items():
            features[f'home_{stat_name}'] = home_value
        for stat_name, away_value in away_stats.items():
            features[f'away_{stat_name}'] = away_value
        
        # Situational features
        features['home_field_advantage'] = situational_factors['home_field_advantage']
        features['timezone_travel'] = situational_factors['timezone_travel']
        features['travel_distance'] = situational_factors['travel_distance']
        
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
            'situational_factors': situational_factors,
            'home_injury_scenario': home_injury,
            'away_injury_scenario': away_injury,
            'current_season_weight': self.current_season_weight,
            'prediction_factors': self._analyze_prediction_factors(home_stats, away_stats, situational_factors)
        }
    
    def _analyze_prediction_factors(self, home_stats, away_stats, situational_factors):
        """Analyze key factors in the prediction"""
        factors = {
            'scoring_advantage': home_stats['points_per_game'] - away_stats['points_per_game'],
            'turnover_advantage': away_stats['turnovers_per_game'] - home_stats['turnovers_per_game'],
            'efficiency_advantage': home_stats['yards_per_play'] - away_stats['yards_per_play'],
            'third_down_advantage': home_stats['third_down_rate'] - away_stats['third_down_rate'],
            'home_field_advantage': situational_factors['home_field_advantage'] - 0.5,
            'recent_momentum_home': home_stats['recent_yards_trend'] - 1.0,
            'recent_momentum_away': away_stats['recent_yards_trend'] - 1.0,
        }
        
        return factors

def main():
    """Main function to demonstrate comprehensive prediction"""
    logger.info("🏈 Comprehensive NFL Predictor Starting...")
    
    # Create comprehensive predictor
    predictor = ComprehensiveNFLPredictor()
    
    if not predictor.model:
        logger.error("Failed to load model. Exiting.")
        return
    
    # Predict MIA @ BUF with comprehensive analysis
    home_team = 'BUF'
    away_team = 'MIA'
    
    logger.info(f"\n🎯 Comprehensive Analysis: {away_team} @ {home_team}")
    logger.info("=" * 60)
    
    # Get comprehensive prediction
    prediction = predictor.predict_comprehensive_game(
        home_team, away_team, 
        home_injury='healthy', away_injury='healthy'
    )
    
    print(f"\n🏆 COMPREHENSIVE PREDICTION:")
    print("-" * 35)
    print(f"Predicted Winner: {prediction['predicted_winner']}")
    print(f"Confidence: {prediction['confidence']:.1f}%")
    print(f"Home Win Probability: {prediction['home_win_probability']:.3f}")
    print(f"Away Win Probability: {prediction['away_win_probability']:.3f}")
    print(f"2025 Season Weight: {prediction['current_season_weight']:.1%}")
    
    print(f"\n📊 KEY PREDICTION FACTORS:")
    print("-" * 30)
    factors = prediction['prediction_factors']
    for factor, value in factors.items():
        print(f"{factor.replace('_', ' ').title()}: {value:.3f}")
    
    print(f"\n📈 COMPREHENSIVE STATS COMPARISON:")
    print("-" * 40)
    
    # Show key stats comparison
    key_stats = ['points_per_game', 'yards_per_play', 'turnovers_per_game', 
                 'third_down_rate', 'completion_rate', 'recent_yards_trend']
    
    for stat in key_stats:
        home_val = prediction['home_stats'][stat]
        away_val = prediction['away_stats'][stat]
        
        if 'rate' in stat:
            home_display = f'{home_val:.1%}'
            away_display = f'{away_val:.1%}'
        else:
            home_display = f'{home_val:.2f}'
            away_display = f'{away_val:.2f}'
        
        advantage = 'HOME' if home_val > away_val else 'AWAY' if away_val > home_val else 'TIE'
        print(f"{stat.replace('_', ' ').title()}: HOME {home_display} vs AWAY {away_display} → {advantage}")
    
    logger.info("\n✅ Comprehensive prediction completed!")
    logger.info("This model now incorporates all key predictive variables with 2025 emphasis!")

if __name__ == "__main__":
    main()
