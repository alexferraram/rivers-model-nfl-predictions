"""
PFF-Enhanced NFL Predictor
Integrates PFF Premium data for sophisticated predictions
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import nfl_data_py as nfl
from pff_data_system import PFFDataSystem
from enhanced_injury_tracker import EnhancedInjuryTracker
from weather_data_system import WeatherDataSystem

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PFFEnhancedPredictor:
    """
    Enhanced NFL predictor with PFF Premium data integration
    """
    
    def __init__(self):
        self.pff_system = PFFDataSystem()
        self.injury_tracker = EnhancedInjuryTracker()
        self.weather_system = WeatherDataSystem()
        
        # Load historical data
        self.pbp_data = None
        self.schedules = None
        self.load_historical_data()
        
        # Enhanced weighting system with PFF integration
        self.weights = {
            'pff_offense': 0.25,      # PFF offensive grades
            'pff_defense': 0.25,      # PFF defensive grades
            'pff_matchups': 0.15,     # PFF matchup advantages
            'traditional_epa': 0.15,  # Traditional EPA metrics
            'efficiency': 0.10,       # Success rate and efficiency
            'injuries': 0.05,        # Enhanced injury impact
            'weather': 0.02,         # Weather conditions
            'home_field': 0.03       # Home field advantage
        }
        
        # Progressive weighting system
        self.progressive_weights = {
            2: {'current': 0.85, '2024': 0.10, '2023': 0.05},
            3: {'current': 0.80, '2024': 0.15, '2023': 0.05},
            4: {'current': 0.75, '2024': 0.20, '2023': 0.05},
            5: {'current': 0.70, '2024': 0.25, '2023': 0.05},
            6: {'current': 0.65, '2024': 0.30, '2023': 0.05},
            7: {'current': 0.60, '2024': 0.35, '2023': 0.05},
            8: {'current': 0.55, '2024': 0.40, '2023': 0.05},
            9: {'current': 0.50, '2024': 0.45, '2023': 0.05},
            10: {'current': 0.45, '2024': 0.50, '2023': 0.05},
            11: {'current': 0.40, '2024': 0.55, '2023': 0.05},
            12: {'current': 0.35, '2024': 0.60, '2023': 0.05},
            13: {'current': 0.30, '2024': 0.65, '2023': 0.05},
            14: {'current': 0.25, '2024': 0.70, '2023': 0.05},
            15: {'current': 0.20, '2024': 0.75, '2023': 0.05},
            16: {'current': 0.15, '2024': 0.80, '2023': 0.05},
            17: {'current': 0.10, '2024': 0.85, '2023': 0.05}
        }
    
    def load_historical_data(self):
        """Load historical play-by-play and schedule data"""
        try:
            logger.info("Loading historical data...")
            
            # Load play-by-play data for multiple seasons
            seasons = [2022, 2023, 2024, 2025]
            pbp_list = []
            
            for season in seasons:
                try:
                    pbp = nfl.import_pbp_data([season])
                    pbp_list.append(pbp)
                    logger.info(f"✅ Loaded {len(pbp)} plays from {season}")
                except Exception as e:
                    logger.warning(f"Could not load {season} data: {e}")
            
            if pbp_list:
                self.pbp_data = pd.concat(pbp_list, ignore_index=True)
                logger.info(f"✅ Total historical data: {len(self.pbp_data):,} plays")
            else:
                logger.error("❌ No historical data loaded")
                return
            
            # Load schedules
            self.schedules = nfl.import_schedules([2025])
            logger.info(f"✅ Loaded {len(self.schedules)} games from 2025 schedule")
            
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
    
    def calculate_pff_team_score(self, team_abbr: str) -> Dict:
        """
        Calculate team score based on PFF grades
        """
        try:
            # Get PFF team grades
            offense_data = self.pff_system.get_team_offensive_efficiency(team_abbr)
            defense_data = self.pff_system.get_team_defensive_efficiency(team_abbr)
            
            if not offense_data or not defense_data:
                return {'pff_score': 50.0, 'offense_score': 50.0, 'defense_score': 50.0}
            
            # Calculate offensive score (weighted average)
            offense_score = (
                offense_data.get('passing', 50) * 0.35 +
                offense_data.get('rushing', 50) * 0.25 +
                offense_data.get('receiving', 50) * 0.20 +
                offense_data.get('pass_blocking', 50) * 0.10 +
                offense_data.get('run_blocking', 50) * 0.10
            )
            
            # Calculate defensive score (weighted average)
            defense_score = (
                defense_data.get('pass_rush', 50) * 0.30 +
                defense_data.get('run_defense', 50) * 0.25 +
                defense_data.get('coverage', 50) * 0.25 +
                defense_data.get('tackling', 50) * 0.20
            )
            
            # Overall PFF score
            pff_score = (offense_score * 0.6 + defense_score * 0.4)
            
            return {
                'pff_score': pff_score,
                'offense_score': offense_score,
                'defense_score': defense_score,
                'offense_data': offense_data,
                'defense_data': defense_data
            }
            
        except Exception as e:
            logger.error(f"Error calculating PFF team score for {team_abbr}: {e}")
            return {'pff_score': 50.0, 'offense_score': 50.0, 'defense_score': 50.0}
    
    def calculate_matchup_advantage(self, home_team: str, away_team: str) -> Dict:
        """
        Calculate matchup advantages using PFF data
        """
        try:
            matchup_data = self.pff_system.analyze_matchup_advantages(home_team, away_team)
            
            if not matchup_data:
                return {'home_advantage': 0, 'away_advantage': 0, 'net_advantage': 0}
            
            # Calculate net advantage
            home_advantage = matchup_data['home_overall_advantage']
            away_advantage = matchup_data['away_overall_advantage']
            net_advantage = home_advantage - away_advantage
            
            return {
                'home_advantage': home_advantage,
                'away_advantage': away_advantage,
                'net_advantage': net_advantage,
                'matchup_data': matchup_data
            }
            
        except Exception as e:
            logger.error(f"Error calculating matchup advantage: {e}")
            return {'home_advantage': 0, 'away_advantage': 0, 'net_advantage': 0}
    
    def calculate_traditional_metrics(self, team_abbr: str) -> Dict:
        """
        Calculate traditional EPA and efficiency metrics
        """
        try:
            if self.pbp_data is None:
                return {'epa_score': 50.0, 'efficiency_score': 50.0, 'yards_score': 50.0}
            
            # Filter for current season (2025)
            current_season = self.pbp_data[self.pbp_data['season'] == 2025]
            team_data = current_season[current_season['posteam'] == team_abbr]
            
            if len(team_data) == 0:
                return {'epa_score': 50.0, 'efficiency_score': 50.0, 'yards_score': 50.0}
            
            # Calculate EPA metrics
            epa_per_play = team_data['epa'].mean() if 'epa' in team_data.columns else 0
            success_rate = (team_data['success'] == 1).mean() if 'success' in team_data.columns else 0.5
            
            # Calculate yards per play
            yards_per_play = team_data['yards_gained'].mean() if 'yards_gained' in team_data.columns else 4.0
            
            # Normalize scores to 0-100 scale
            epa_score = max(0, min(100, 50 + (epa_per_play * 20)))
            efficiency_score = max(0, min(100, success_rate * 100))
            yards_score = max(0, min(100, 50 + ((yards_per_play - 4.0) * 25)))
            
            return {
                'epa_score': epa_score,
                'efficiency_score': efficiency_score,
                'yards_score': yards_score,
                'raw_epa': epa_per_play,
                'raw_success_rate': success_rate,
                'raw_yards_per_play': yards_per_play
            }
            
        except Exception as e:
            logger.error(f"Error calculating traditional metrics for {team_abbr}: {e}")
            return {'epa_score': 50.0, 'efficiency_score': 50.0, 'yards_score': 50.0}
    
    def calculate_enhanced_team_score(self, team_abbr: str, opponent_abbr: str = None) -> Dict:
        """
        Calculate enhanced team score using PFF data and traditional metrics
        """
        try:
            # Get PFF scores
            pff_data = self.calculate_pff_team_score(team_abbr)
            
            # Get traditional metrics
            traditional_data = self.calculate_traditional_metrics(team_abbr)
            
            # Get injury impact
            injury_impact = self.injury_tracker.get_enhanced_injury_impact(team_abbr)
            
            # Get matchup advantage if opponent provided
            matchup_advantage = 0
            if opponent_abbr:
                matchup_data = self.calculate_matchup_advantage(team_abbr, opponent_abbr)
                matchup_advantage = matchup_data['net_advantage']
            
            # Calculate weighted score
            enhanced_score = (
                pff_data['pff_score'] * self.weights['pff_offense'] +
                pff_data['pff_score'] * self.weights['pff_defense'] +
                matchup_advantage * self.weights['pff_matchups'] +
                traditional_data['epa_score'] * self.weights['traditional_epa'] +
                traditional_data['efficiency_score'] * self.weights['efficiency'] +
                injury_impact * self.weights['injuries'] +
                50.0 * self.weights['weather'] +  # Weather will be added separately
                50.0 * self.weights['home_field']  # Home field will be added separately
            )
            
            return {
                'enhanced_score': enhanced_score,
                'pff_data': pff_data,
                'traditional_data': traditional_data,
                'injury_impact': injury_impact,
                'matchup_advantage': matchup_advantage,
                'breakdown': {
                    'pff_offense': pff_data['offense_score'] * self.weights['pff_offense'],
                    'pff_defense': pff_data['defense_score'] * self.weights['pff_defense'],
                    'pff_matchups': matchup_advantage * self.weights['pff_matchups'],
                    'traditional_epa': traditional_data['epa_score'] * self.weights['traditional_epa'],
                    'efficiency': traditional_data['efficiency_score'] * self.weights['efficiency'],
                    'injuries': injury_impact * self.weights['injuries']
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating enhanced team score for {team_abbr}: {e}")
            return {'enhanced_score': 50.0, 'pff_data': {}, 'traditional_data': {}, 'injury_impact': 0}
    
    def predict_game_enhanced(self, home_team: str, away_team: str, game_date: str = None) -> Dict:
        """
        Predict game outcome using enhanced PFF-integrated model
        """
        try:
            logger.info(f"🎯 Predicting {away_team} @ {home_team} with PFF Enhanced Model")
            
            # Calculate enhanced team scores
            home_data = self.calculate_enhanced_team_score(home_team, away_team)
            away_data = self.calculate_enhanced_team_score(away_team, home_team)
            
            # Get weather data
            weather_data = self.weather_system.get_game_weather(f"{home_team}_{away_team}")
            weather_score = 50.0  # Default neutral weather score
            
            # Apply home field advantage
            home_field_advantage = 3.0  # Reduced from previous model
            
            # Calculate final scores
            home_final_score = (
                home_data['enhanced_score'] + 
                home_field_advantage + 
                weather_score
            )
            away_final_score = away_data['enhanced_score'] + weather_score
            
            # Calculate win probability
            score_diff = home_final_score - away_final_score
            home_win_prob = self._calculate_win_probability(score_diff)
            away_win_prob = 1 - home_win_prob
            
            # Determine confidence level
            confidence = self._calculate_confidence(score_diff, home_data, away_data)
            
            return {
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_final_score,
                'away_score': away_final_score,
                'home_win_probability': home_win_prob,
                'away_win_probability': away_win_prob,
                'confidence': confidence,
                'score_difference': score_diff,
                'home_data': home_data,
                'away_data': away_data,
                'weather_data': weather_data,
                'weather_score': weather_score,
                'home_field_advantage': home_field_advantage
            }
            
        except Exception as e:
            logger.error(f"Error predicting game {away_team} @ {home_team}: {e}")
            return {}
    
    def _calculate_win_probability(self, score_diff: float) -> float:
        """Calculate win probability from score difference"""
        # Use sigmoid function for win probability
        return 1 / (1 + np.exp(-score_diff / 10))
    
    def _calculate_confidence(self, score_diff: float, home_data: Dict, away_data: Dict) -> float:
        """Calculate confidence level based on score difference and data quality"""
        # Base confidence from score difference
        base_confidence = min(95, max(50, 50 + abs(score_diff) * 2))
        
        # Adjust for data quality
        data_quality_factor = 1.0
        if home_data.get('pff_data', {}).get('pff_score', 50) > 0:
            data_quality_factor += 0.1
        if away_data.get('pff_data', {}).get('pff_score', 50) > 0:
            data_quality_factor += 0.1
        
        return min(95, base_confidence * data_quality_factor)
    
    def predict_week_enhanced(self, week: int = 3) -> List[Dict]:
        """
        Predict all games for a given week using enhanced PFF model
        """
        try:
            logger.info(f"🎯 Predicting Week {week} with PFF Enhanced Model")
            
            if self.schedules is None:
                logger.error("No schedule data available")
                return []
            
            # Filter games for the week
            week_games = self.schedules[self.schedules['week'] == week]
            
            if len(week_games) == 0:
                logger.error(f"No games found for week {week}")
                return []
            
            predictions = []
            
            for _, game in week_games.iterrows():
                home_team = game['home_team']
                away_team = game['away_team']
                game_date = game['gameday']
                
                prediction = self.predict_game_enhanced(home_team, away_team, game_date)
                if prediction:
                    predictions.append(prediction)
            
            logger.info(f"✅ Generated {len(predictions)} predictions for Week {week}")
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting week {week}: {e}")
            return []
    
    def display_enhanced_predictions(self, predictions: List[Dict]):
        """Display enhanced predictions with PFF data"""
        if not predictions:
            print("No predictions to display")
            return
        
        print(f"\n🎯 PFF-ENHANCED NFL PREDICTIONS:")
        print("=" * 80)
        
        for i, pred in enumerate(predictions, 1):
            home_team = pred['home_team']
            away_team = pred['away_team']
            home_score = pred['home_score']
            away_score = pred['away_score']
            confidence = pred['confidence']
            home_win_prob = pred['home_win_probability']
            
            winner = home_team if home_win_prob > 0.5 else away_team
            
            print(f"\n🏟️  Game {i}: {away_team} @ {home_team}")
            print(f"   🏆 Predicted Winner: {winner}")
            print(f"   📊 Confidence: {confidence:.1f}%")
            print(f"   🏠 Home Win Probability: {home_win_prob:.3f}")
            print(f"   ✈️  Away Win Probability: {1-home_win_prob:.3f}")
            
            # PFF Data
            home_pff = pred['home_data']['pff_data']
            away_pff = pred['away_data']['pff_data']
            print(f"\n📊 PFF GRADES:")
            print(f"   {home_team}: Overall {home_pff.get('pff_score', 0):.1f} (Off: {home_pff.get('offense_score', 0):.1f}, Def: {home_pff.get('defense_score', 0):.1f})")
            print(f"   {away_team}: Overall {away_pff.get('pff_score', 0):.1f} (Off: {away_pff.get('offense_score', 0):.1f}, Def: {away_pff.get('defense_score', 0):.1f})")
            
            # Enhanced Injury Data
            home_injury = pred['home_data']['injury_impact']
            away_injury = pred['away_data']['injury_impact']
            print(f"\n🏥 ENHANCED INJURY IMPACTS:")
            print(f"   {home_team}: {home_injury:.1f} points")
            print(f"   {away_team}: {away_injury:.1f} points")
            
            # Score Breakdown
            print(f"\n📊 SCORE BREAKDOWN:")
            print(f"   {home_team}: {home_score:.1f}")
            print(f"   {away_team}: {away_score:.1f}")
            print(f"   Score Difference: {pred['score_difference']:+.1f}")
            
            # Key Variables
            home_traditional = pred['home_data']['traditional_data']
            away_traditional = pred['away_data']['traditional_data']
            print(f"\n🔑 KEY VARIABLES:")
            print(f"   EPA: {home_team} {home_traditional.get('raw_epa', 0):.1f} vs {away_team} {away_traditional.get('raw_epa', 0):.1f}")
            print(f"   Success Rate: {home_team} {home_traditional.get('raw_success_rate', 0):.1%} vs {away_team} {away_traditional.get('raw_success_rate', 0):.1%}")
            print(f"   Yards/Play: {home_team} {home_traditional.get('raw_yards_per_play', 0):.2f} vs {away_team} {away_traditional.get('raw_yards_per_play', 0):.2f}")

if __name__ == "__main__":
    # Test the PFF Enhanced Predictor
    predictor = PFFEnhancedPredictor()
    
    print("🔍 Testing PFF Enhanced Predictor")
    print("=" * 50)
    
    # Test individual game prediction
    print("\n🎯 Testing Individual Game Prediction:")
    test_prediction = predictor.predict_game_enhanced("BUF", "MIA")
    if test_prediction:
        print(f"   {test_prediction['away_team']} @ {test_prediction['home_team']}")
        print(f"   Winner: {test_prediction['home_team'] if test_prediction['home_win_probability'] > 0.5 else test_prediction['away_team']}")
        print(f"   Confidence: {test_prediction['confidence']:.1f}%")
        print(f"   Score: {test_prediction['away_team']} {test_prediction['away_score']:.1f} @ {test_prediction['home_team']} {test_prediction['home_score']:.1f}")
    
    # Test week predictions
    print("\n🎯 Testing Week 3 Predictions:")
    week_predictions = predictor.predict_week_enhanced(3)
    if week_predictions:
        predictor.display_enhanced_predictions(week_predictions[:3])  # Show first 3 games
    
    print("\n✅ PFF Enhanced Predictor Test Complete")
