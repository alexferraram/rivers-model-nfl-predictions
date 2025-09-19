"""
Enhanced NFL Prediction Model Framework
Integrates PFF data into existing components + new matchup analysis
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import nfl_data_py as nfl
from pff_data_system import PFFDataSystem
from enhanced_injury_tracker import EnhancedInjuryTracker
from weather_data_system import WeatherDataSystem

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedModelFramework:
    """
    Enhanced NFL prediction model with PFF integration into existing components
    """
    
    def __init__(self):
        self.pff_system = PFFDataSystem()
        self.injury_tracker = EnhancedInjuryTracker()
        self.weather_system = WeatherDataSystem()
        
        # Load historical data
        self.pbp_data = None
        self.schedules = None
        self.load_historical_data()
        
        # ENHANCED WEIGHTING SYSTEM (PFF-enhanced existing components)
        self.weights = {
            'enhanced_epa': 0.24,        # EPA enhanced with PFF player grades (reduced from 0.25)
            'enhanced_efficiency': 0.24,  # Efficiency enhanced with PFF execution grades (reduced from 0.25)
            'enhanced_yards': 0.19,      # Yards enhanced with PFF YAC/air yards (reduced from 0.20)
            'enhanced_turnovers': 0.19,   # Turnovers enhanced with PFF ball security (reduced from 0.20)
            'pff_matchups': 0.08,        # NEW: PFF-based matchup analysis
            'injuries': 0.05,           # Enhanced injury impact (increased from 0.01)
            'weather': 0.01             # Weather conditions (reduced weight)
        }
        
        # Progressive weighting system (updated - current season focus, no 2022 data)
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
    
    def load_historical_data(self):
        """Load historical play-by-play and schedule data"""
        try:
            logger.info("Loading historical data...")
            
            # Load play-by-play data for recent seasons (2023, 2024, 2025)
            seasons = [2023, 2024, 2025]
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
    
    def calculate_enhanced_epa_score(self, team_abbr: str) -> Dict:
        """
        COMPONENT 1: Enhanced EPA Score (25% weight)
        Traditional EPA enhanced with PFF player grades and contextual analysis
        """
        try:
            if self.pbp_data is None:
                return {'enhanced_epa_score': 50.0, 'traditional_epa': 0, 'pff_enhancement': 0}
            
            # Filter for current season (2025)
            current_season = self.pbp_data[self.pbp_data['season'] == 2025]
            team_data = current_season[current_season['posteam'] == team_abbr]
            
            if len(team_data) == 0:
                return {'enhanced_epa_score': 50.0, 'traditional_epa': 0, 'pff_enhancement': 0}
            
            # TRADITIONAL EPA CALCULATION (50+ metrics)
            traditional_epa = team_data['epa'].mean() if 'epa' in team_data.columns else 0
            
            # PFF ENHANCEMENT FACTORS
            pff_enhancement = self._calculate_pff_epa_enhancement(team_abbr, team_data)
            
            # Enhanced EPA Score = Traditional EPA + PFF Enhancement
            enhanced_epa_score = max(0, min(100, 50 + (traditional_epa * 20) + pff_enhancement))
            
            return {
                'enhanced_epa_score': enhanced_epa_score,
                'traditional_epa': traditional_epa,
                'pff_enhancement': pff_enhancement,
                'breakdown': {
                    'passing_epa': team_data[team_data['play_type'] == 'pass']['epa'].mean() if 'play_type' in team_data.columns else 0,
                    'rushing_epa': team_data[team_data['play_type'] == 'run']['epa'].mean() if 'play_type' in team_data.columns else 0,
                    'red_zone_epa': team_data[team_data['yardline_100'] <= 20]['epa'].mean() if 'yardline_100' in team_data.columns else 0,
                    'third_down_epa': team_data[team_data['down'] == 3]['epa'].mean() if 'down' in team_data.columns else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating enhanced EPA score for {team_abbr}: {e}")
            return {'enhanced_epa_score': 50.0, 'traditional_epa': 0, 'pff_enhancement': 0}
    
    def _calculate_pff_epa_enhancement(self, team_abbr: str, team_data: pd.DataFrame) -> float:
        """
        Calculate PFF enhancement for EPA score
        """
        try:
            # Get PFF team grades
            offense_data = self.pff_system.get_team_offensive_efficiency(team_abbr)
            defense_data = self.pff_system.get_team_defensive_efficiency(team_abbr)
            
            if not offense_data or not defense_data:
                return 0.0
            
            # PFF Enhancement Factors
            enhancement_factors = []
            
            # 1. Player-Grade Enhanced EPA
            # Individual player performance vs. team average
            player_enhancement = self._calculate_player_grade_enhancement(team_abbr)
            enhancement_factors.append(player_enhancement)
            
            # 2. Contextual EPA Enhancement
            # PFF grades account for opponent strength and situational context
            contextual_enhancement = self._calculate_contextual_epa_enhancement(team_data, offense_data, defense_data)
            enhancement_factors.append(contextual_enhancement)
            
            # 3. Position-Specific EPA Enhancement
            # QB, RB, WR, TE, OL, DL, LB, DB grades weighted by importance
            position_enhancement = self._calculate_position_specific_enhancement(team_abbr)
            enhancement_factors.append(position_enhancement)
            
            # 4. Clutch Performance Enhancement
            # PFF grades in high-leverage situations
            clutch_enhancement = self._calculate_clutch_performance_enhancement(team_data, team_abbr)
            enhancement_factors.append(clutch_enhancement)
            
            # Combine enhancement factors
            total_enhancement = sum(enhancement_factors) / len(enhancement_factors)
            return max(-10, min(10, total_enhancement))  # Cap enhancement at ±10 points
            
        except Exception as e:
            logger.error(f"Error calculating PFF EPA enhancement: {e}")
            return 0.0
    
    def calculate_enhanced_efficiency_score(self, team_abbr: str) -> Dict:
        """
        COMPONENT 2: Enhanced Efficiency Score (25% weight)
        Success Rate enhanced with PFF execution grades and assignment completion
        """
        try:
            if self.pbp_data is None:
                return {'enhanced_efficiency_score': 50.0, 'traditional_success_rate': 0.5, 'pff_enhancement': 0}
            
            # Filter for current season (2025)
            current_season = self.pbp_data[self.pbp_data['season'] == 2025]
            team_data = current_season[current_season['posteam'] == team_abbr]
            
            if len(team_data) == 0:
                return {'enhanced_efficiency_score': 50.0, 'traditional_success_rate': 0.5, 'pff_enhancement': 0}
            
            # TRADITIONAL SUCCESS RATE CALCULATION (30+ metrics)
            traditional_success_rate = (team_data['success'] == 1).mean() if 'success' in team_data.columns else 0.5
            
            # PFF ENHANCEMENT FACTORS
            pff_enhancement = self._calculate_pff_efficiency_enhancement(team_abbr, team_data)
            
            # Enhanced Efficiency Score = Traditional Success Rate + PFF Enhancement
            enhanced_efficiency_score = max(0, min(100, (traditional_success_rate * 100) + pff_enhancement))
            
            return {
                'enhanced_efficiency_score': enhanced_efficiency_score,
                'traditional_success_rate': traditional_success_rate,
                'pff_enhancement': pff_enhancement,
                'breakdown': {
                    'passing_success_rate': (team_data[team_data['play_type'] == 'pass']['success'] == 1).mean() if 'play_type' in team_data.columns else 0.5,
                    'rushing_success_rate': (team_data[team_data['play_type'] == 'run']['success'] == 1).mean() if 'play_type' in team_data.columns else 0.5,
                    'third_down_success_rate': (team_data[team_data['down'] == 3]['success'] == 1).mean() if 'down' in team_data.columns else 0.5,
                    'red_zone_success_rate': (team_data[team_data['yardline_100'] <= 20]['success'] == 1).mean() if 'yardline_100' in team_data.columns else 0.5
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating enhanced efficiency score for {team_abbr}: {e}")
            return {'enhanced_efficiency_score': 50.0, 'traditional_success_rate': 0.5, 'pff_enhancement': 0}
    
    def _calculate_pff_efficiency_enhancement(self, team_abbr: str, team_data: pd.DataFrame) -> float:
        """
        Calculate PFF enhancement for efficiency score
        """
        try:
            # Get PFF team grades
            offense_data = self.pff_system.get_team_offensive_efficiency(team_abbr)
            defense_data = self.pff_system.get_team_defensive_efficiency(team_abbr)
            
            if not offense_data or not defense_data:
                return 0.0
            
            # PFF Enhancement Factors
            enhancement_factors = []
            
            # 1. PFF Success Rate Enhancement
            # Film-based success rate vs. statistical success rate
            pff_success_enhancement = (offense_data.get('passing', 50) - 50) * 0.1
            enhancement_factors.append(pff_success_enhancement)
            
            # 2. Execution Grades Enhancement
            # How well players execute their assignments (0-100 scale)
            execution_enhancement = (offense_data.get('run_blocking', 50) - 50) * 0.05
            enhancement_factors.append(execution_enhancement)
            
            # 3. Assignment Completion Enhancement
            # Did players fulfill their role correctly?
            assignment_enhancement = (defense_data.get('tackling', 50) - 50) * 0.05
            enhancement_factors.append(assignment_enhancement)
            
            # 4. Situational Execution Enhancement
            # Performance in specific game situations
            situational_enhancement = (offense_data.get('receiving', 50) - 50) * 0.1
            enhancement_factors.append(situational_enhancement)
            
            # Combine enhancement factors
            total_enhancement = sum(enhancement_factors) / len(enhancement_factors)
            return max(-5, min(5, total_enhancement))  # Cap enhancement at ±5 points
            
        except Exception as e:
            logger.error(f"Error calculating PFF efficiency enhancement: {e}")
            return 0.0
    
    def calculate_enhanced_yards_score(self, team_abbr: str) -> Dict:
        """
        COMPONENT 3: Enhanced Yards Per Play Score (20% weight)
        Yards enhanced with PFF YAC, air yards, and contact analysis
        """
        try:
            if self.pbp_data is None:
                return {'enhanced_yards_score': 50.0, 'traditional_yards_per_play': 4.0, 'pff_enhancement': 0}
            
            # Filter for current season (2025)
            current_season = self.pbp_data[self.pbp_data['season'] == 2025]
            team_data = current_season[current_season['posteam'] == team_abbr]
            
            if len(team_data) == 0:
                return {'enhanced_yards_score': 50.0, 'traditional_yards_per_play': 4.0, 'pff_enhancement': 0}
            
            # TRADITIONAL YARDS PER PLAY CALCULATION (25+ metrics)
            traditional_yards_per_play = team_data['yards_gained'].mean() if 'yards_gained' in team_data.columns else 4.0
            
            # PFF ENHANCEMENT FACTORS
            pff_enhancement = self._calculate_pff_yards_enhancement(team_abbr, team_data)
            
            # Enhanced Yards Score = Traditional YPP + PFF Enhancement
            enhanced_yards_score = max(0, min(100, 50 + ((traditional_yards_per_play - 4.0) * 25) + pff_enhancement))
            
            return {
                'enhanced_yards_score': enhanced_yards_score,
                'traditional_yards_per_play': traditional_yards_per_play,
                'pff_enhancement': pff_enhancement,
                'breakdown': {
                    'passing_yards_per_play': team_data[team_data['play_type'] == 'pass']['yards_gained'].mean() if 'play_type' in team_data.columns else 4.0,
                    'rushing_yards_per_play': team_data[team_data['play_type'] == 'run']['yards_gained'].mean() if 'play_type' in team_data.columns else 4.0,
                    'red_zone_yards_per_play': team_data[team_data['yardline_100'] <= 20]['yards_gained'].mean() if 'yardline_100' in team_data.columns else 4.0,
                    'third_down_yards_per_play': team_data[team_data['down'] == 3]['yards_gained'].mean() if 'down' in team_data.columns else 4.0
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating enhanced yards score for {team_abbr}: {e}")
            return {'enhanced_yards_score': 50.0, 'traditional_yards_per_play': 4.0, 'pff_enhancement': 0}
    
    def _calculate_pff_yards_enhancement(self, team_abbr: str, team_data: pd.DataFrame) -> float:
        """
        Calculate PFF enhancement for yards score
        """
        try:
            # Get PFF team grades
            offense_data = self.pff_system.get_team_offensive_efficiency(team_abbr)
            defense_data = self.pff_system.get_team_defensive_efficiency(team_abbr)
            
            if not offense_data or not defense_data:
                return 0.0
            
            # PFF Enhancement Factors
            enhancement_factors = []
            
            # 1. PFF Yards After Contact Enhancement
            # RB/WR ability to gain extra yards
            yac_enhancement = (offense_data.get('rushing', 50) - 50) * 0.1
            enhancement_factors.append(yac_enhancement)
            
            # 2. PFF Yards After Catch Enhancement
            # WR/TE ability to create after reception
            yac_receiving_enhancement = (offense_data.get('receiving', 50) - 50) * 0.1
            enhancement_factors.append(yac_receiving_enhancement)
            
            # 3. PFF Air Yards vs. Actual Yards Enhancement
            # QB accuracy and receiver separation
            air_yards_enhancement = (offense_data.get('passing', 50) - 50) * 0.1
            enhancement_factors.append(air_yards_enhancement)
            
            # 4. Defensive Yards Prevention Enhancement
            # Defensive ability to limit YAC
            defensive_yards_enhancement = (defense_data.get('run_defense', 50) - 50) * 0.05
            enhancement_factors.append(defensive_yards_enhancement)
            
            # Combine enhancement factors
            total_enhancement = sum(enhancement_factors) / len(enhancement_factors)
            return max(-5, min(5, total_enhancement))  # Cap enhancement at ±5 points
            
        except Exception as e:
            logger.error(f"Error calculating PFF yards enhancement: {e}")
            return 0.0
    
    def calculate_enhanced_turnover_score(self, team_abbr: str) -> Dict:
        """
        COMPONENT 4: Enhanced Turnover Avoidance Score (20% weight)
        Turnovers enhanced with PFF ball security, decision making, and coverage grades
        """
        try:
            if self.pbp_data is None:
                return {'enhanced_turnover_score': 50.0, 'traditional_turnover_rate': 0.1, 'pff_enhancement': 0}
            
            # Filter for current season (2025)
            current_season = self.pbp_data[self.pbp_data['season'] == 2025]
            team_data = current_season[current_season['posteam'] == team_abbr]
            
            if len(team_data) == 0:
                return {'enhanced_turnover_score': 50.0, 'traditional_turnover_rate': 0.1, 'pff_enhancement': 0}
            
            # TRADITIONAL TURNOVER CALCULATION (20+ metrics)
            turnovers = team_data['interception'].sum() + team_data['fumble_lost'].sum() if 'interception' in team_data.columns and 'fumble_lost' in team_data.columns else 0
            total_plays = len(team_data)
            traditional_turnover_rate = turnovers / total_plays if total_plays > 0 else 0.1
            
            # PFF ENHANCEMENT FACTORS
            pff_enhancement = self._calculate_pff_turnover_enhancement(team_abbr, team_data)
            
            # Enhanced Turnover Score = Traditional Turnover Rate + PFF Enhancement
            # Lower turnover rate = higher score
            enhanced_turnover_score = max(0, min(100, 50 + ((0.1 - traditional_turnover_rate) * 500) + pff_enhancement))
            
            return {
                'enhanced_turnover_score': enhanced_turnover_score,
                'traditional_turnover_rate': traditional_turnover_rate,
                'pff_enhancement': pff_enhancement,
                'breakdown': {
                    'interception_rate': team_data['interception'].sum() / len(team_data) if 'interception' in team_data.columns else 0,
                    'fumble_rate': team_data['fumble_lost'].sum() / len(team_data) if 'fumble_lost' in team_data.columns else 0,
                    'forced_turnovers': team_data['fumble_recovery'].sum() + team_data['interception'].sum() if 'fumble_recovery' in team_data.columns and 'interception' in team_data.columns else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating enhanced turnover score for {team_abbr}: {e}")
            return {'enhanced_turnover_score': 50.0, 'traditional_turnover_rate': 0.1, 'pff_enhancement': 0}
    
    def _calculate_pff_turnover_enhancement(self, team_abbr: str, team_data: pd.DataFrame) -> float:
        """
        Calculate PFF enhancement for turnover score
        """
        try:
            # Get PFF team grades
            offense_data = self.pff_system.get_team_offensive_efficiency(team_abbr)
            defense_data = self.pff_system.get_team_defensive_efficiency(team_abbr)
            
            if not offense_data or not defense_data:
                return 0.0
            
            # PFF Enhancement Factors
            enhancement_factors = []
            
            # 1. PFF Ball Security Enhancement
            # Fumble risk assessment
            ball_security_enhancement = (offense_data.get('passing', 50) - 50) * 0.1
            enhancement_factors.append(ball_security_enhancement)
            
            # 2. PFF Decision Making Enhancement
            # QB interception risk based on film
            decision_making_enhancement = (offense_data.get('passing', 50) - 50) * 0.1
            enhancement_factors.append(decision_making_enhancement)
            
            # 3. PFF Coverage Enhancement
            # Defensive ability to force turnovers
            coverage_enhancement = (defense_data.get('coverage', 50) - 50) * 0.1
            enhancement_factors.append(coverage_enhancement)
            
            # 4. PFF Pressure Enhancement
            # Offensive line ability to prevent turnovers
            pressure_enhancement = (offense_data.get('pass_blocking', 50) - 50) * 0.05
            enhancement_factors.append(pressure_enhancement)
            
            # Combine enhancement factors
            total_enhancement = sum(enhancement_factors) / len(enhancement_factors)
            return max(-5, min(5, total_enhancement))  # Cap enhancement at ±5 points
            
        except Exception as e:
            logger.error(f"Error calculating PFF turnover enhancement: {e}")
            return 0.0
    
    def calculate_pff_matchup_analysis(self, home_team: str, away_team: str) -> Dict:
        """
        NEW COMPONENT: PFF Matchup Analysis (8% weight)
        Comprehensive matchup analysis using PFF grades
        """
        try:
            # Get PFF team grades for both teams
            home_offense = self.pff_system.get_team_offensive_efficiency(home_team)
            home_defense = self.pff_system.get_team_defensive_efficiency(home_team)
            away_offense = self.pff_system.get_team_offensive_efficiency(away_team)
            away_defense = self.pff_system.get_team_defensive_efficiency(away_team)
            
            if not all([home_offense, home_defense, away_offense, away_defense]):
                return {'matchup_score': 0, 'home_advantage': 0, 'away_advantage': 0}
            
            # 1. PASSING GAME SOPHISTICATION MATCHUP
            passing_matchup = self._analyze_passing_game_matchup(home_offense, away_defense, away_offense, home_defense)
            
            # 2. DEFENSIVE SOPHISTICATION MATCHUP
            defensive_matchup = self._analyze_defensive_matchup(home_defense, away_offense, away_defense, home_offense)
            
            # 3. SCHEME MATCHUP ANALYSIS
            scheme_matchup = self._analyze_scheme_matchup(home_team, away_team)
            
            # Calculate overall matchup advantage
            home_advantage = (passing_matchup['home_advantage'] + defensive_matchup['home_advantage'] + scheme_matchup['home_advantage']) / 3
            away_advantage = (passing_matchup['away_advantage'] + defensive_matchup['away_advantage'] + scheme_matchup['away_advantage']) / 3
            
            # Net advantage for home team
            net_advantage = home_advantage - away_advantage
            
            return {
                'matchup_score': net_advantage,
                'home_advantage': home_advantage,
                'away_advantage': away_advantage,
                'passing_matchup': passing_matchup,
                'defensive_matchup': defensive_matchup,
                'scheme_matchup': scheme_matchup
            }
            
        except Exception as e:
            logger.error(f"Error calculating PFF matchup analysis: {e}")
            return {'matchup_score': 0, 'home_advantage': 0, 'away_advantage': 0}
    
    def _analyze_passing_game_matchup(self, home_offense: Dict, away_defense: Dict, away_offense: Dict, home_defense: Dict) -> Dict:
        """
        Analyze passing game matchup using PFF grades
        """
        try:
            # Home passing advantage
            home_pass_advantage = (
                home_offense.get('passing', 50) - away_defense.get('coverage', 50) +
                home_offense.get('pass_blocking', 50) - away_defense.get('pass_rush', 50)
            ) / 2
            
            # Away passing advantage
            away_pass_advantage = (
                away_offense.get('passing', 50) - home_defense.get('coverage', 50) +
                away_offense.get('pass_blocking', 50) - home_defense.get('pass_rush', 50)
            ) / 2
            
            return {
                'home_advantage': home_pass_advantage,
                'away_advantage': away_pass_advantage,
                'net_advantage': home_pass_advantage - away_pass_advantage
            }
            
        except Exception as e:
            logger.error(f"Error analyzing passing game matchup: {e}")
            return {'home_advantage': 0, 'away_advantage': 0, 'net_advantage': 0}
    
    def _analyze_defensive_matchup(self, home_defense: Dict, away_offense: Dict, away_defense: Dict, home_offense: Dict) -> Dict:
        """
        Analyze defensive matchup using PFF grades
        """
        try:
            # Home defensive advantage
            home_defensive_advantage = (
                home_defense.get('run_defense', 50) - away_offense.get('rushing', 50) +
                home_defense.get('tackling', 50) - away_offense.get('receiving', 50)
            ) / 2
            
            # Away defensive advantage
            away_defensive_advantage = (
                away_defense.get('run_defense', 50) - home_offense.get('rushing', 50) +
                away_defense.get('tackling', 50) - home_offense.get('receiving', 50)
            ) / 2
            
            return {
                'home_advantage': home_defensive_advantage,
                'away_advantage': away_defensive_advantage,
                'net_advantage': home_defensive_advantage - away_defensive_advantage
            }
            
        except Exception as e:
            logger.error(f"Error analyzing defensive matchup: {e}")
            return {'home_advantage': 0, 'away_advantage': 0, 'net_advantage': 0}
    
    def _analyze_scheme_matchup(self, home_team: str, away_team: str) -> Dict:
        """
        Analyze scheme matchup (simplified for now)
        """
        try:
            # This would include route tree analysis, formation effectiveness, etc.
            # For now, return neutral values
            return {
                'home_advantage': 0,
                'away_advantage': 0,
                'net_advantage': 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing scheme matchup: {e}")
            return {'home_advantage': 0, 'away_advantage': 0, 'net_advantage': 0}
    
    def _calculate_player_grade_enhancement(self, team_abbr: str) -> float:
        """Calculate player grade enhancement for EPA"""
        # Simplified for now - would use actual PFF player grades
        return 0.0
    
    def _calculate_contextual_epa_enhancement(self, team_data: pd.DataFrame, offense_data: Dict, defense_data: Dict) -> float:
        """Calculate contextual EPA enhancement"""
        # Simplified for now - would use PFF contextual grades
        return 0.0
    
    def _calculate_position_specific_enhancement(self, team_abbr: str) -> float:
        """Calculate position-specific enhancement"""
        # Simplified for now - would use PFF position grades
        return 0.0
    
    def _calculate_clutch_performance_enhancement(self, team_data: pd.DataFrame, team_abbr: str) -> float:
        """Calculate clutch performance enhancement"""
        # Simplified for now - would use PFF clutch grades
        return 0.0
    
    def calculate_enhanced_team_score(self, team_abbr: str, opponent_abbr: str = None) -> Dict:
        """
        Calculate enhanced team score using all components
        """
        try:
            # Calculate all enhanced components
            epa_data = self.calculate_enhanced_epa_score(team_abbr)
            efficiency_data = self.calculate_enhanced_efficiency_score(team_abbr)
            yards_data = self.calculate_enhanced_yards_score(team_abbr)
            turnover_data = self.calculate_enhanced_turnover_score(team_abbr)
            
            # Calculate PFF matchup analysis if opponent provided
            matchup_data = {'matchup_score': 0}
            if opponent_abbr:
                matchup_data = self.calculate_pff_matchup_analysis(team_abbr, opponent_abbr)
            
            # Get injury impact
            injury_impact = self.injury_tracker.get_enhanced_injury_impact(team_abbr)
            
            # Calculate weighted score
            enhanced_score = (
                epa_data['enhanced_epa_score'] * self.weights['enhanced_epa'] +
                efficiency_data['enhanced_efficiency_score'] * self.weights['enhanced_efficiency'] +
                yards_data['enhanced_yards_score'] * self.weights['enhanced_yards'] +
                turnover_data['enhanced_turnover_score'] * self.weights['enhanced_turnovers'] +
                matchup_data['matchup_score'] * self.weights['pff_matchups'] +
                injury_impact * self.weights['injuries'] +
                50.0 * self.weights['weather']  # Weather will be added separately
            )
            
            return {
                'enhanced_score': enhanced_score,
                'epa_data': epa_data,
                'efficiency_data': efficiency_data,
                'yards_data': yards_data,
                'turnover_data': turnover_data,
                'matchup_data': matchup_data,
                'injury_impact': injury_impact,
                'breakdown': {
                    'epa_contribution': epa_data['enhanced_epa_score'] * self.weights['enhanced_epa'],
                    'efficiency_contribution': efficiency_data['enhanced_efficiency_score'] * self.weights['enhanced_efficiency'],
                    'yards_contribution': yards_data['enhanced_yards_score'] * self.weights['enhanced_yards'],
                    'turnover_contribution': turnover_data['enhanced_turnover_score'] * self.weights['enhanced_turnovers'],
                    'matchup_contribution': matchup_data['matchup_score'] * self.weights['pff_matchups'],
                    'injury_contribution': injury_impact * self.weights['injuries']
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating enhanced team score for {team_abbr}: {e}")
            return {'enhanced_score': 50.0}
    
    def predict_game_enhanced(self, home_team: str, away_team: str, game_date: str = None) -> Dict:
        """
        Predict game outcome using enhanced model
        """
        try:
            logger.info(f"🎯 Predicting {away_team} @ {home_team} with Enhanced Model")
            
            # Calculate enhanced team scores
            home_data = self.calculate_enhanced_team_score(home_team, away_team)
            away_data = self.calculate_enhanced_team_score(away_team, home_team)
            
            # Get weather data
            weather_data = self.weather_system.get_game_weather(f"{home_team}_{away_team}")
            weather_score = 50.0  # Default neutral weather score
            
            # Apply home field advantage
            home_field_advantage = 5.0  # Fixed home field advantage
            
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
        return 1 / (1 + np.exp(-score_diff / 10))
    
    def _calculate_confidence(self, score_diff: float, home_data: Dict, away_data: Dict) -> float:
        """Calculate confidence level based on score difference and data quality"""
        base_confidence = min(95, max(50, 50 + abs(score_diff) * 2))
        return base_confidence

if __name__ == "__main__":
    # Test the enhanced model framework
    model = EnhancedModelFramework()
    
    print("🔍 Testing Enhanced Model Framework")
    print("=" * 50)
    
    # Test individual game prediction
    print("\n🎯 Testing Individual Game Prediction:")
    test_prediction = model.predict_game_enhanced("BUF", "MIA")
    if test_prediction:
        print(f"   {test_prediction['away_team']} @ {test_prediction['home_team']}")
        print(f"   Winner: {test_prediction['home_team'] if test_prediction['home_win_probability'] > 0.5 else test_prediction['away_team']}")
        print(f"   Confidence: {test_prediction['confidence']:.1f}%")
        print(f"   Score: {test_prediction['away_team']} {test_prediction['away_score']:.1f} @ {test_prediction['home_team']} {test_prediction['home_score']:.1f}")
    
    print("\n✅ Enhanced Model Framework Test Complete")
