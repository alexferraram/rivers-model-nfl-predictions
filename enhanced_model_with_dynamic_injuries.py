"""
Enhanced Model with Dynamic Injury System
Integrates dynamic injury penalties that directly affect win probability
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import nfl_data_py as nfl
from pff_data_system import PFFDataSystem
from dynamic_injury_system import DynamicInjurySystem
from weather_data_system import WeatherDataSystem

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedModelWithDynamicInjuries:
    """
    Enhanced NFL prediction model with dynamic injury system
    """
    
    def __init__(self):
        self.pbp_data = None
        self.schedules = None
        self.pff_system = PFFDataSystem()
        self.injury_system = DynamicInjurySystem(self.pff_system)
        self.weather_system = WeatherDataSystem()
        
        # Updated weights (removed 5% injury weight, redistributed)
        self.weights = {
            'enhanced_epa': 0.26,        # EPA enhanced with PFF player grades (increased from 0.24)
            'enhanced_efficiency': 0.26,  # Efficiency enhanced with PFF execution grades (increased from 0.24)
            'enhanced_yards': 0.21,      # Yards enhanced with PFF YAC/air yards (increased from 0.19)
            'enhanced_turnovers': 0.21,   # Turnovers enhanced with PFF ball security (increased from 0.19)
            'pff_matchups': 0.08,        # PFF-based matchup analysis
            'weather': 0.01             # Weather conditions (reduced weight)
        }
        
        # Progressive weighting system (2023 diminishes to 0% by week 4, 2024 by week 9)
        self.progressive_weights = {
            2: {'current': 0.92, '2024': 0.06, '2023': 0.02},
            3: {'current': 0.94, '2024': 0.05, '2023': 0.01},
            4: {'current': 0.96, '2024': 0.04, '2023': 0.00},
            5: {'current': 0.97, '2024': 0.03, '2023': 0.00},
            6: {'current': 0.98, '2024': 0.02, '2023': 0.00},
            7: {'current': 0.99, '2024': 0.01, '2023': 0.00},
            8: {'current': 0.995, '2024': 0.005, '2023': 0.00},
            9: {'current': 1.00, '2024': 0.00, '2023': 0.00},
            10: {'current': 1.00, '2024': 0.00, '2023': 0.00},
            11: {'current': 1.00, '2024': 0.00, '2023': 0.00},
            12: {'current': 1.00, '2024': 0.00, '2023': 0.00},
            13: {'current': 1.00, '2024': 0.00, '2023': 0.00},
            14: {'current': 1.00, '2024': 0.00, '2023': 0.00},
            15: {'current': 1.00, '2024': 0.00, '2023': 0.00},
            16: {'current': 1.00, '2024': 0.00, '2023': 0.00},
            17: {'current': 1.00, '2024': 0.00, '2023': 0.00}
        }
        
        # Load data
        self.load_historical_data()
    
    def load_historical_data(self):
        """Load historical data (2023-2025 seasons)"""
        try:
            logger.info("Loading historical data...")
            seasons = [2023, 2024, 2025]  # Removed 2022
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
            
            self.schedules = nfl.import_schedules([2025])
            logger.info(f"✅ Loaded {len(self.schedules)} games from 2025 schedule")
            
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
    
    def calculate_enhanced_team_score(self, team_abbr: str, week: int = 3) -> Dict:
        """
        Calculate enhanced team score with dynamic injury impact
        """
        try:
            # Get progressive weights for current week
            week_weights = self.progressive_weights.get(week, self.progressive_weights[17])
            
            # Calculate traditional metrics
            epa_score = self._calculate_enhanced_epa_score(team_abbr, week_weights)
            efficiency_score = self._calculate_enhanced_efficiency_score(team_abbr, week_weights)
            yards_score = self._calculate_enhanced_yards_score(team_abbr, week_weights)
            turnover_score = self._calculate_enhanced_turnover_score(team_abbr, week_weights)
            
            # Calculate PFF matchup score
            pff_matchup_score = self._calculate_pff_matchup_score(team_abbr)
            
            # Calculate weather score
            weather_score = self._calculate_weather_score(team_abbr)
            
            # Calculate base score using traditional weights
            base_score = (
                epa_score * self.weights['enhanced_epa'] +
                efficiency_score * self.weights['enhanced_efficiency'] +
                yards_score * self.weights['enhanced_yards'] +
                turnover_score * self.weights['enhanced_turnovers'] +
                pff_matchup_score * self.weights['pff_matchups'] +
                weather_score * self.weights['weather']
            )
            
            # Calculate dynamic injury impact
            injury_impact = self.injury_system.calculate_dynamic_injury_impact(team_abbr)
            injury_adjustment = injury_impact['total_impact']
            
            # Apply injury adjustment directly to base score
            final_score = base_score - injury_adjustment
            
            return {
                'final_score': final_score,
                'base_score': base_score,
                'injury_adjustment': injury_adjustment,
                'epa_score': epa_score,
                'efficiency_score': efficiency_score,
                'yards_score': yards_score,
                'turnover_score': turnover_score,
                'pff_matchup_score': pff_matchup_score,
                'weather_score': weather_score,
                'injury_details': injury_impact
            }
            
        except Exception as e:
            logger.error(f"Error calculating enhanced team score for {team_abbr}: {e}")
            return {'final_score': 50.0, 'base_score': 50.0, 'injury_adjustment': 0.0}
    
    def _calculate_enhanced_epa_score(self, team_abbr: str, week_weights: Dict) -> float:
        """Calculate enhanced EPA score with PFF integration"""
        try:
            # Filter data for team
            team_data = self.pbp_data[self.pbp_data['posteam'] == team_abbr].copy()
            
            if team_data.empty:
                return 50.0
            
            # Calculate EPA by season
            epa_by_season = {}
            for season in [2023, 2024, 2025]:
                season_data = team_data[team_data['season'] == season]
                if not season_data.empty:
                    epa_by_season[season] = season_data['epa'].mean()
            
            # Apply progressive weights
            weighted_epa = 0
            total_weight = 0
            
            for season, epa in epa_by_season.items():
                if season == 2025:
                    weight = week_weights['current']
                elif season == 2024:
                    weight = week_weights['2024']
                elif season == 2023:
                    weight = week_weights['2023']
                else:
                    continue
                
                weighted_epa += epa * weight
                total_weight += weight
            
            if total_weight == 0:
                return 50.0
            
            final_epa = weighted_epa / total_weight
            
            # Normalize to 0-100 scale
            # EPA typically ranges from -0.5 to +0.5, so scale accordingly
            normalized_epa = max(0, min(100, 50 + (final_epa * 100)))
            
            return normalized_epa
            
        except Exception as e:
            logger.error(f"Error calculating enhanced EPA score: {e}")
            return 50.0
    
    def _calculate_enhanced_efficiency_score(self, team_abbr: str, week_weights: Dict) -> float:
        """Calculate enhanced efficiency score with PFF integration"""
        try:
            team_data = self.pbp_data[self.pbp_data['posteam'] == team_abbr].copy()
            
            if team_data.empty:
                return 50.0
            
            # Calculate success rate by season
            success_by_season = {}
            for season in [2023, 2024, 2025]:
                season_data = team_data[team_data['season'] == season]
                if not season_data.empty:
                    success_rate = (season_data['success'] == 1).mean()
                    success_by_season[season] = success_rate
            
            # Apply progressive weights
            weighted_success = 0
            total_weight = 0
            
            for season, success in success_by_season.items():
                if season == 2025:
                    weight = week_weights['current']
                elif season == 2024:
                    weight = week_weights['2024']
                elif season == 2023:
                    weight = week_weights['2023']
                else:
                    continue
                
                weighted_success += success * weight
                total_weight += weight
            
            if total_weight == 0:
                return 50.0
            
            final_success = weighted_success / total_weight
            
            # Normalize to 0-100 scale
            normalized_success = final_success * 100
            
            return normalized_success
            
        except Exception as e:
            logger.error(f"Error calculating enhanced efficiency score: {e}")
            return 50.0
    
    def _calculate_enhanced_yards_score(self, team_abbr: str, week_weights: Dict) -> float:
        """Calculate enhanced yards score with PFF integration"""
        try:
            team_data = self.pbp_data[self.pbp_data['posteam'] == team_abbr].copy()
            
            if team_data.empty:
                return 50.0
            
            # Calculate yards per play by season
            yards_by_season = {}
            for season in [2023, 2024, 2025]:
                season_data = team_data[team_data['season'] == season]
                if not season_data.empty:
                    yards_per_play = season_data['yards_gained'].mean()
                    yards_by_season[season] = yards_per_play
            
            # Apply progressive weights
            weighted_yards = 0
            total_weight = 0
            
            for season, yards in yards_by_season.items():
                if season == 2025:
                    weight = week_weights['current']
                elif season == 2024:
                    weight = week_weights['2024']
                elif season == 2023:
                    weight = week_weights['2023']
                else:
                    continue
                
                weighted_yards += yards * weight
                total_weight += weight
            
            if total_weight == 0:
                return 50.0
            
            final_yards = weighted_yards / total_weight
            
            # Normalize to 0-100 scale (yards per play typically 0-20)
            normalized_yards = max(0, min(100, (final_yards / 20) * 100))
            
            return normalized_yards
            
        except Exception as e:
            logger.error(f"Error calculating enhanced yards score: {e}")
            return 50.0
    
    def _calculate_enhanced_turnover_score(self, team_abbr: str, week_weights: Dict) -> float:
        """Calculate enhanced turnover score with PFF integration"""
        try:
            team_data = self.pbp_data[self.pbp_data['posteam'] == team_abbr].copy()
            
            if team_data.empty:
                return 50.0
            
            # Calculate turnover rate by season
            turnover_by_season = {}
            for season in [2023, 2024, 2025]:
                season_data = team_data[team_data['season'] == season]
                if not season_data.empty:
                    turnover_rate = (season_data['interception'] == 1).mean() + (season_data['fumble_lost'] == 1).mean()
                    turnover_by_season[season] = turnover_rate
            
            # Apply progressive weights
            weighted_turnover = 0
            total_weight = 0
            
            for season, turnover in turnover_by_season.items():
                if season == 2025:
                    weight = week_weights['current']
                elif season == 2024:
                    weight = week_weights['2024']
                elif season == 2023:
                    weight = week_weights['2023']
                else:
                    continue
                
                weighted_turnover += turnover * weight
                total_weight += weight
            
            if total_weight == 0:
                return 50.0
            
            final_turnover = weighted_turnover / total_weight
            
            # Normalize to 0-100 scale (lower turnover rate = higher score)
            normalized_turnover = max(0, min(100, 100 - (final_turnover * 1000)))
            
            return normalized_turnover
            
        except Exception as e:
            logger.error(f"Error calculating enhanced turnover score: {e}")
            return 50.0
    
    def _calculate_pff_matchup_score(self, team_abbr: str) -> float:
        """Calculate PFF-based matchup score"""
        try:
            team_name = self._get_team_full_name(team_abbr)
            team_grades = self.pff_system.team_pff_grades.get(team_name, {})
            
            if not team_grades:
                return 50.0
            
            # Calculate overall PFF score
            offensive_score = (
                team_grades.get('overall_offense', 50) * 0.3 +
                team_grades.get('passing_offense', 50) * 0.25 +
                team_grades.get('rushing_offense', 50) * 0.2 +
                team_grades.get('receiving_offense', 50) * 0.15 +
                team_grades.get('pass_blocking_offense', 50) * 0.1
            )
            
            defensive_score = (
                team_grades.get('overall_defense', 50) * 0.3 +
                team_grades.get('pass_rush_defense', 50) * 0.25 +
                team_grades.get('run_defense', 50) * 0.2 +
                team_grades.get('coverage_defense', 50) * 0.15 +
                team_grades.get('tackling_defense', 50) * 0.1
            )
            
            overall_score = (offensive_score + defensive_score) / 2
            return overall_score
            
        except Exception as e:
            logger.error(f"Error calculating PFF matchup score: {e}")
            return 50.0
    
    def _calculate_weather_score(self, team_abbr: str) -> float:
        """Calculate weather score"""
        try:
            # For now, return neutral weather score
            # In real implementation, would get actual weather data
            return 50.0
            
        except Exception as e:
            logger.error(f"Error calculating weather score: {e}")
            return 50.0
    
    def _get_team_full_name(self, team_abbr: str) -> str:
        """Convert team abbreviation to full name"""
        team_mapping = {
            'BUF': 'Buffalo Bills', 'MIA': 'Miami Dolphins', 'PHI': 'Philadelphia Eagles',
            'DAL': 'Dallas Cowboys', 'NYG': 'New York Giants', 'WAS': 'Washington Commanders',
            'CHI': 'Chicago Bears', 'DET': 'Detroit Lions', 'GB': 'Green Bay Packers',
            'MIN': 'Minnesota Vikings', 'ATL': 'Atlanta Falcons', 'CAR': 'Carolina Panthers',
            'NO': 'New Orleans Saints', 'TB': 'Tampa Bay Buccaneers', 'ARI': 'Arizona Cardinals',
            'LAR': 'Los Angeles Rams', 'SF': 'San Francisco 49ers', 'SEA': 'Seattle Seahawks',
            'BAL': 'Baltimore Ravens', 'CIN': 'Cincinnati Bengals', 'CLE': 'Cleveland Browns',
            'PIT': 'Pittsburgh Steelers', 'HOU': 'Houston Texans', 'IND': 'Indianapolis Colts',
            'JAX': 'Jacksonville Jaguars', 'TEN': 'Tennessee Titans', 'DEN': 'Denver Broncos',
            'KC': 'Kansas City Chiefs', 'LV': 'Las Vegas Raiders', 'LAC': 'Los Angeles Chargers',
            'NE': 'New England Patriots', 'NYJ': 'New York Jets'
        }
        return team_mapping.get(team_abbr, f"{team_abbr} Team")
    
    def predict_game(self, home_team: str, away_team: str, week: int = 3) -> Dict:
        """
        Predict game outcome with dynamic injury system
        """
        try:
            # Calculate team scores
            home_score_data = self.calculate_enhanced_team_score(home_team, week)
            away_score_data = self.calculate_enhanced_team_score(away_team, week)
            
            home_score = home_score_data['final_score']
            away_score = away_score_data['final_score']
            
            # Calculate score difference
            score_diff = home_score - away_score
            
            # Calculate win probability using sigmoid function
            win_prob = 1 / (1 + np.exp(-score_diff / 10))
            
            # Determine winner
            if home_score > away_score:
                winner = home_team
                confidence = win_prob
            else:
                winner = away_team
                confidence = 1 - win_prob
            
            return {
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'score_difference': score_diff,
                'winner': winner,
                'confidence': confidence,
                'home_details': home_score_data,
                'away_details': away_score_data
            }
            
        except Exception as e:
            logger.error(f"Error predicting game: {e}")
            return {
                'home_team': home_team,
                'away_team': away_team,
                'home_score': 50.0,
                'away_score': 50.0,
                'score_difference': 0.0,
                'winner': 'TIE',
                'confidence': 0.5,
                'home_details': {},
                'away_details': {}
            }
    
    def display_prediction(self, prediction: Dict):
        """Display prediction with injury details"""
        home_team = prediction['home_team']
        away_team = prediction['away_team']
        home_score = prediction['home_score']
        away_score = prediction['away_score']
        winner = prediction['winner']
        confidence = prediction['confidence']
        
        print(f"\n🏈 {away_team} @ {home_team}")
        print(f"📊 Score: {away_team} {away_score:.1f} - {home_team} {home_score:.1f}")
        print(f"🏆 Winner: {winner}")
        print(f"🎯 Confidence: {confidence:.1%}")
        
        # Display injury impacts
        home_injuries = prediction['home_details'].get('injury_details', {})
        away_injuries = prediction['away_details'].get('injury_details', {})
        
        if home_injuries.get('total_impact', 0) > 0:
            print(f"\n🏥 {home_team} Injury Impact: -{home_injuries['total_impact']:.2f}% win probability")
            for injury in home_injuries.get('injuries', []):
                print(f"   {injury['player']} ({injury['position']}) - {injury['status']}: -{injury['impact']:.2f}%")
        
        if away_injuries.get('total_impact', 0) > 0:
            print(f"\n🏥 {away_team} Injury Impact: -{away_injuries['total_impact']:.2f}% win probability")
            for injury in away_injuries.get('injuries', []):
                print(f"   {injury['player']} ({injury['position']}) - {injury['status']}: -{injury['impact']:.2f}%")

if __name__ == "__main__":
    # Test the enhanced model
    model = EnhancedModelWithDynamicInjuries()
    
    print("🔍 Testing Enhanced Model with Dynamic Injuries")
    print("=" * 60)
    
    # Test a game prediction
    prediction = model.predict_game('BUF', 'MIA', week=3)
    model.display_prediction(prediction)
    
    print("\n✅ Enhanced Model Test Complete")




