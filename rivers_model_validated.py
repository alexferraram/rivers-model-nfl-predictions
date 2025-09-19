"""
RIVERS Model - Validated NFL Predictions
Enhanced model with dynamic injury system and database validation
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
from database_validation_system import DatabaseValidationSystem
from enhanced_epa_system import EnhancedEPASystem

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RiversModelValidated:
    """
    RIVERS Model - Enhanced NFL prediction model with dynamic injury system
    Includes comprehensive database validation before predictions
    """
    
    def __init__(self):
        logger.info("🌊 INITIALIZING RIVERS MODEL")
        logger.info("=" * 60)
        
        # Initialize data systems
        self.pff_system = PFFDataSystem()
        self.injury_system = DynamicInjurySystem(self.pff_system)
        self.weather_system = WeatherDataSystem()
        self.validator = DatabaseValidationSystem()
        self.enhanced_epa_system = EnhancedEPASystem(self.pff_system)
        
        # RIVERS Model weights (balanced to 100% total)
        self.weights = {
            'enhanced_epa': 0.26,        # EPA enhanced with PFF player grades (26%)
            'enhanced_efficiency': 0.25,  # Efficiency enhanced with PFF execution grades (25%)
            'enhanced_turnovers': 0.18,   # Turnovers enhanced with PFF ball security (18%)
            'enhanced_yards': 0.16,      # Yards enhanced with PFF YAC/air yards (16%)
            'pff_matchups': 0.09,        # PFF-based matchup analysis (9%)
            'weather': 0.01,            # Weather conditions (1%)
            'home_field': 0.05          # Home field advantage (5%)
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
        
        # Data storage
        self.pbp_data = None
        self.schedules = None
        
        # Validation status
        self.validation_passed = False
        
        # Initialize model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the model with validation"""
        logger.info("🔍 VALIDATING DATABASES BEFORE INITIALIZATION")
        
        # Validate all databases
        validation_results = self.validator.validate_all_databases()
        
        if validation_results['overall_status'] == 'FAIL':
            logger.error("❌ DATABASE VALIDATION FAILED - CANNOT PROCEED")
            self.validation_passed = False
            return
        
        logger.info("✅ DATABASE VALIDATION PASSED - LOADING DATA")
        self.validation_passed = True
        
        # Load historical data
        self.load_historical_data()
    
    def load_historical_data(self):
        """Load historical data (2023-2025 seasons)"""
        if not self.validation_passed:
            logger.error("❌ Cannot load data - validation failed")
            return
            
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
    
    def calculate_team_score(self, team_abbr: str, week: int = 3, opponent_abbr: str = None) -> Dict:
        """
        Calculate team score with dynamic injury impact
        """
        if not self.validation_passed:
            logger.error("❌ Cannot calculate scores - validation failed")
            return {'final_score': 50.0, 'base_score': 50.0, 'injury_adjustment': 0.0}
            
        try:
            # Get progressive weights for current week
            week_weights = self.progressive_weights.get(week, self.progressive_weights[17])
            
            # Calculate traditional metrics
            epa_result = self._calculate_enhanced_epa_score(team_abbr, week_weights)
            epa_score = epa_result['final_score']
            efficiency_score = self._calculate_enhanced_efficiency_score(team_abbr, week_weights)
            yards_score = self._calculate_enhanced_yards_score(team_abbr, week_weights)
            turnover_score = self._calculate_enhanced_turnover_score(team_abbr, week_weights)
            
            # Calculate PFF matchup score (matchup-specific if opponent provided)
            pff_matchup_score = self._calculate_pff_matchup_score(team_abbr, opponent_abbr)
            
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
                'epa_details': epa_result,
                'efficiency_score': efficiency_score,
                'yards_score': yards_score,
                'turnover_score': turnover_score,
                'pff_matchup_score': pff_matchup_score,
                'weather_score': weather_score,
                'injury_details': injury_impact
            }
            
        except Exception as e:
            logger.error(f"Error calculating team score for {team_abbr}: {e}")
            return {'final_score': 50.0, 'base_score': 50.0, 'injury_adjustment': 0.0}
    
    def _calculate_enhanced_epa_score(self, team_abbr: str, week_weights: Dict) -> Dict:
        """Calculate enhanced EPA score with full PFF integration"""
        try:
            # Use the new enhanced EPA system
            epa_result = self.enhanced_epa_system.calculate_enhanced_epa_score(
                team_abbr, self.pbp_data, week_weights
            )
            
            # Log detailed EPA analysis
            logger.info(f"📊 {team_abbr} Enhanced EPA Analysis:")
            logger.info(f"   Final Score: {epa_result['final_score']:.2f}")
            logger.info(f"   Weighted EPA: {epa_result['weighted_epa']:.4f}")
            
            # Log situational EPA
            if epa_result['situational_epa']:
                logger.info(f"   Situational EPA:")
                for situation, epa in epa_result['situational_epa'].items():
                    logger.info(f"     {situation}: {epa:.4f}")
            
            # Log advanced metrics
            if epa_result['advanced_metrics']:
                logger.info(f"   Advanced Metrics:")
                for metric, value in epa_result['advanced_metrics'].items():
                    logger.info(f"     {metric}: {value:.4f}")
            
            # Log PFF adjustments
            if epa_result['pff_adjustments']:
                pff_adj = epa_result['pff_adjustments']
                logger.info(f"   PFF Adjustments:")
                logger.info(f"     Team Grades Available: {pff_adj.get('team_grades_available', False)}")
                logger.info(f"     Player Grades Available: {pff_adj.get('player_grades_available', False)}")
                logger.info(f"     Offensive Grade: {pff_adj.get('offensive_grade', 50)}")
                logger.info(f"     Defensive Grade: {pff_adj.get('defensive_grade', 50)}")
            
            return epa_result
            
        except Exception as e:
            logger.error(f"Error calculating enhanced EPA score: {e}")
            return {'final_score': 50.0, 'weighted_epa': 0.0, 'situational_epa': {}, 
                   'advanced_metrics': {}, 'pff_adjustments': {}}
    
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
    
    def _calculate_pff_matchup_score(self, team_abbr: str, opponent_abbr: str = None) -> float:
        """Calculate PFF-based matchup score comparing specific offensive vs defensive matchups"""
        try:
            team_name = self._get_team_full_name(team_abbr)
            team_grades = self.pff_system.team_grades.get(team_name, {})
            
            if not team_grades:
                return 50.0
            
            # If no opponent specified, return overall team grade
            if not opponent_abbr:
                overall_grade = team_grades.get('overall', None)
                if overall_grade and overall_grade != 75.0:  # 75.0 is the default mock value
                    return overall_grade
                else:
                    # Calculate from components if no overall grade
                    offensive_data = team_grades.get('offense', {})
                    defensive_data = team_grades.get('defense', {})
                    special_teams_data = team_grades.get('special_teams', {})
                    
                    offensive_score = (
                        offensive_data.get('passing', 50) * 0.4 +
                        offensive_data.get('rushing', 50) * 0.3 +
                        offensive_data.get('receiving', 50) * 0.2 +
                        offensive_data.get('pass_blocking', 50) * 0.1
                    )
                    
                    defensive_score = (
                        defensive_data.get('pass_rush', 50) * 0.3 +
                        defensive_data.get('run_defense', 50) * 0.25 +
                        defensive_data.get('coverage', 50) * 0.25 +
                        defensive_data.get('tackling', 50) * 0.2
                    )
                    
                    special_teams_score = special_teams_data.get('overall', 50)
                    
                    return (offensive_score + defensive_score + special_teams_score) / 3
            
            # Calculate matchup-specific score
            opponent_name = self._get_team_full_name(opponent_abbr)
            opponent_grades = self.pff_system.team_grades.get(opponent_name, {})
            
            if not opponent_grades:
                return 50.0
            
            # Extract grades for both teams using the correct flat structure
            # Expected format: Team Name - Record - PF - PG - Overall Grade - Offensive Overall Grade - Passing Grade - Pass Blocking Grade - Receiving Grade - Running Grade - Run Blocking Grade - Defensive Overall Grade - Run Defense Grade - Tackling Grade - Pass Rush Grade - Pass Coverage Grade - Special Teams Grade
            
            # Map nested structure to flat format
            team_overall = team_grades.get('overall', 50)
            team_offensive_overall = team_grades.get('offense', {}).get('overall', 50)  # Will calculate from components
            team_passing = team_grades.get('offense', {}).get('passing', 50)
            team_pass_blocking = team_grades.get('offense', {}).get('pass_blocking', 50)
            team_receiving = team_grades.get('offense', {}).get('receiving', 50)
            team_running = team_grades.get('offense', {}).get('rushing', 50)
            team_run_blocking = team_grades.get('offense', {}).get('run_blocking', 50)
            team_defensive_overall = team_grades.get('defense', {}).get('overall', 50)  # Will calculate from components
            team_run_defense = team_grades.get('defense', {}).get('run_defense', 50)
            team_tackling = team_grades.get('defense', {}).get('tackling', 50)
            team_pass_rush = team_grades.get('defense', {}).get('pass_rush', 50)
            team_pass_coverage = team_grades.get('defense', {}).get('coverage', 50)
            team_special_teams = team_grades.get('special_teams', {}).get('overall', 50)  # Will calculate from components
            
            opponent_overall = opponent_grades.get('overall', 50)
            opponent_offensive_overall = opponent_grades.get('offense', {}).get('overall', 50)
            opponent_passing = opponent_grades.get('offense', {}).get('passing', 50)
            opponent_pass_blocking = opponent_grades.get('offense', {}).get('pass_blocking', 50)
            opponent_receiving = opponent_grades.get('offense', {}).get('receiving', 50)
            opponent_running = opponent_grades.get('offense', {}).get('rushing', 50)
            opponent_run_blocking = opponent_grades.get('offense', {}).get('run_blocking', 50)
            opponent_defensive_overall = opponent_grades.get('defense', {}).get('overall', 50)
            opponent_run_defense = opponent_grades.get('defense', {}).get('run_defense', 50)
            opponent_tackling = opponent_grades.get('defense', {}).get('tackling', 50)
            opponent_pass_rush = opponent_grades.get('defense', {}).get('pass_rush', 50)
            opponent_pass_coverage = opponent_grades.get('defense', {}).get('coverage', 50)
            opponent_special_teams = opponent_grades.get('special_teams', {}).get('overall', 50)
            
            # Calculate overall grades from components if not available
            if team_offensive_overall == 50:  # Default value means not found
                team_offense_components = [
                    team_passing, team_pass_blocking, team_receiving, 
                    team_running, team_run_blocking
                ]
                team_offensive_overall = sum(team_offense_components) / len(team_offense_components)
            
            if team_defensive_overall == 50:  # Default value means not found
                team_defense_components = [
                    team_pass_rush, team_run_defense, team_tackling, team_pass_coverage
                ]
                team_defensive_overall = sum(team_defense_components) / len(team_defense_components)
            
            if team_special_teams == 50:  # Default value means not found
                team_st_components = [
                    team_grades.get('special_teams', {}).get('kicking', 50),
                    team_grades.get('special_teams', {}).get('punting', 50),
                    team_grades.get('special_teams', {}).get('return', 50)
                ]
                team_special_teams = sum(team_st_components) / len(team_st_components)
            
            if opponent_offensive_overall == 50:  # Default value means not found
                opponent_offense_components = [
                    opponent_passing, opponent_pass_blocking, opponent_receiving, 
                    opponent_running, opponent_run_blocking
                ]
                opponent_offensive_overall = sum(opponent_offense_components) / len(opponent_offense_components)
            
            if opponent_defensive_overall == 50:  # Default value means not found
                opponent_defense_components = [
                    opponent_pass_rush, opponent_run_defense, opponent_tackling, opponent_pass_coverage
                ]
                opponent_defensive_overall = sum(opponent_defense_components) / len(opponent_defense_components)
            
            if opponent_special_teams == 50:  # Default value means not found
                opponent_st_components = [
                    opponent_grades.get('special_teams', {}).get('kicking', 50),
                    opponent_grades.get('special_teams', {}).get('punting', 50),
                    opponent_grades.get('special_teams', {}).get('return', 50)
                ]
                opponent_special_teams = sum(opponent_st_components) / len(opponent_st_components)
            
            # NEW PFF Matchup Calculation using Sigmoid Functions
            # PFF Matchup Component (worth 9% total)
            
            # Sigmoid function: sig(x) = 1 / (1 + e^(-x))
            def sigmoid(x, k=10):
                return 1 / (1 + np.exp(-x / k))
            
            # Sensitivity parameters
            k = 10  # for most categories (≈10 PFF points → ~73/27 split)
            k_spec = 8  # slightly sharper for special teams
            
            # Extract PFF grades (using calculated overall grades if not available)
            OFF_A = team_offensive_overall
            DEF_A = team_defensive_overall
            PASS_A = team_passing
            PBLK_A = team_pass_blocking
            RUN_A = team_running
            RDEF_A = team_run_defense
            PRSH_A = team_pass_rush
            COV_A = team_pass_coverage
            SPEC_A = team_special_teams
            
            OFF_B = opponent_offensive_overall
            DEF_B = opponent_defensive_overall
            PASS_B = opponent_passing
            PBLK_B = opponent_pass_blocking
            RUN_B = opponent_running
            RDEF_B = opponent_run_defense
            PRSH_B = opponent_pass_rush
            COV_B = opponent_pass_coverage
            SPEC_B = opponent_special_teams
            
            # Symmetric category share calculations
            # Overall Offense vs Defense
            S_over = 0.5 * (
                sigmoid(OFF_A - DEF_B, k) + 
                (1 - sigmoid(OFF_B - DEF_A, k))
            )
            
            # Passing vs Coverage
            S_pass = 0.5 * (
                sigmoid(PASS_A - COV_B, k) + 
                (1 - sigmoid(PASS_B - COV_A, k))
            )
            
            # Pass Blocking vs Pass Rush
            S_pblk = 0.5 * (
                sigmoid(PBLK_A - PRSH_B, k) + 
                (1 - sigmoid(PBLK_B - PRSH_A, k))
            )
            
            # Rushing vs Run Defense
            S_run = 0.5 * (
                sigmoid(RUN_A - RDEF_B, k) + 
                (1 - sigmoid(RUN_B - RDEF_A, k))
            )
            
            # Special Teams (single head-to-head)
            S_spec = sigmoid(SPEC_A - SPEC_B, k_spec)
            
            # Optional cap: clamp each S_* to [0.35, 0.65] to prevent single facet domination
            S_over = max(0.35, min(0.65, S_over))
            S_pass = max(0.35, min(0.65, S_pass))
            S_pblk = max(0.35, min(0.65, S_pblk))
            S_run = max(0.35, min(0.65, S_run))
            S_spec = max(0.35, min(0.65, S_spec))
            
            # Weights inside the 9% (sum to 1) - "passing-tilted" set
            w_over = 0.25
            w_pass = 0.25
            w_pblk = 0.20
            w_run = 0.20
            w_spec = 0.10
            
            # Aggregate Team A share of this component
            S_A = (w_over * S_over + 
                   w_pass * S_pass + 
                   w_pblk * S_pblk + 
                   w_run * S_run + 
                   w_spec * S_spec)
            
            # Convert to model points (block = 9%)
            # Return as percentage (0-100 scale)
            points_A_from_matchups = S_A * 100
            
            return points_A_from_matchups
            
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
        if not self.validation_passed:
            logger.error("❌ Cannot predict games - validation failed")
            return {
                'home_team': home_team,
                'away_team': away_team,
                'home_score': 50.0,
                'away_score': 50.0,
                'score_difference': 0.0,
                'winner': 'TIE',
                'confidence': 0.5,
                'home_details': {},
                'away_details': {},
                'error': 'Validation failed'
            }
            
        try:
            # Calculate team scores with matchup-specific PFF calculations
            home_score_data = self.calculate_team_score(home_team, week, away_team)
            away_score_data = self.calculate_team_score(away_team, week, home_team)
            
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
                'away_details': {},
                'error': str(e)
            }
    
    def get_week3_schedule(self) -> List[Dict]:
        """Get Week 3 NFL schedule"""
        return [
            {'home': 'BUF', 'away': 'MIA', 'time': 'Thursday 8:15 PM'},
            {'home': 'CAR', 'away': 'ATL', 'time': 'Sunday 1:00 PM'},
            {'home': 'CLE', 'away': 'GB', 'time': 'Sunday 1:00 PM'},
            {'home': 'JAX', 'away': 'HOU', 'time': 'Sunday 1:00 PM'},
            {'home': 'MIN', 'away': 'CIN', 'time': 'Sunday 1:00 PM'},
            {'home': 'NE', 'away': 'PIT', 'time': 'Sunday 1:00 PM'},
            {'home': 'PHI', 'away': 'LA', 'time': 'Sunday 1:00 PM'},
            {'home': 'TB', 'away': 'NYJ', 'time': 'Sunday 1:00 PM'},
            {'home': 'TEN', 'away': 'IND', 'time': 'Sunday 1:00 PM'},
            {'home': 'WAS', 'away': 'LV', 'time': 'Sunday 1:00 PM'},
            {'home': 'LAC', 'away': 'DEN', 'time': 'Sunday 4:05 PM'},
            {'home': 'SEA', 'away': 'NO', 'time': 'Sunday 4:05 PM'},
            {'home': 'CHI', 'away': 'DAL', 'time': 'Sunday 4:25 PM'},
            {'home': 'SF', 'away': 'ARI', 'time': 'Sunday 4:25 PM'},
            {'home': 'NYG', 'away': 'KC', 'time': 'Sunday 4:25 PM'},
            {'home': 'BAL', 'away': 'DET', 'time': 'Monday 8:15 PM'}
        ]
    
    def display_prediction(self, prediction: Dict):
        """Display prediction with winner, confidence, and injury details only"""
        home_team = prediction['home_team']
        away_team = prediction['away_team']
        winner = prediction['winner']
        confidence = prediction['confidence']
        
        print(f"\n{'='*60}")
        print(f"🏈 {away_team} @ {home_team}")
        print(f"{'='*60}")
        print(f"🏆 Winner: {winner}")
        print(f"🎯 Confidence: {confidence*100:.1f}%")
        
        # Display injury impacts
        home_injuries = prediction['home_details'].get('injury_details', {})
        away_injuries = prediction['away_details'].get('injury_details', {})
        
        print(f"\n🏥 Injury Report:")
        
        if home_injuries.get('total_impact', 0) > 0:
            print(f"   {home_team} Impact: -{home_injuries['total_impact']:.2f}% win probability")
            for injury in home_injuries.get('injuries', []):
                print(f"     • {injury['player']} ({injury['position']}) - {injury['status']}: -{injury['impact']:.2f}%")
        else:
            print(f"   {home_team}: No significant injuries")
        
        if away_injuries.get('total_impact', 0) > 0:
            print(f"   {away_team} Impact: -{away_injuries['total_impact']:.2f}% win probability")
            for injury in away_injuries.get('injuries', []):
                print(f"     • {injury['player']} ({injury['position']}) - {injury['status']}: -{injury['impact']:.2f}%")
        else:
            print(f"   {away_team}: No significant injuries")
        
        print(f"{'='*60}")
    
    def generate_week3_predictions(self):
        """Generate Week 3 predictions with validation"""
        if not self.validation_passed:
            logger.error("❌ Cannot generate predictions - validation failed")
            print("\n🚨 VALIDATION FAILED - CANNOT GENERATE PREDICTIONS")
            print("Please fix the failing systems before generating predictions.")
            return
        
        print("\n🌊 RIVERS MODEL - WEEK 3 NFL PREDICTIONS")
        print("=" * 60)
        print("Enhanced model with dynamic injury system")
        print("✅ All databases validated successfully")
        print("=" * 60)
        
        # Get Week 3 schedule
        week3_games = self.get_week3_schedule()
        
        print(f"\n📅 WEEK 3 NFL SCHEDULE - {len(week3_games)} GAMES")
        print("=" * 60)
        
        # Generate predictions for all games
        predictions = []
        for game in week3_games:
            prediction = self.predict_game(game['home'], game['away'], week=3)
            predictions.append(prediction)
            self.display_prediction(prediction)
        
        # Summary statistics
        print(f"\n📊 WEEK 3 PREDICTION SUMMARY")
        print("=" * 60)
        
        home_wins = sum(1 for p in predictions if p['winner'] == p['home_team'])
        away_wins = sum(1 for p in predictions if p['winner'] == p['away_team'])
        avg_confidence = np.mean([p['confidence'] for p in predictions])
        
        print(f"Home Team Wins: {home_wins}/{len(predictions)} ({home_wins/len(predictions):.1%})")
        print(f"Away Team Wins: {away_wins}/{len(predictions)} ({away_wins/len(predictions):.1%})")
        print(f"Average Confidence: {avg_confidence*100:.1f}%")
        
        print(f"\n✅ RIVERS MODEL WEEK 3 PREDICTIONS COMPLETE")
        
        return predictions

if __name__ == "__main__":
    # Initialize RIVERS Model with validation
    rivers_model = RiversModelValidated()
    
    # Generate Week 3 predictions
    rivers_model.generate_week3_predictions()

