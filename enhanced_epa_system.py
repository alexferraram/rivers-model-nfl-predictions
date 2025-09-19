"""
Enhanced EPA System with Full PFF Integration
Implements player-grade weighted EPA, position-specific adjustments, and matchup-based modifications
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from pff_data_system import PFFDataSystem

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedEPASystem:
    """
    Enhanced EPA calculation system with full PFF integration
    """
    
    def __init__(self, pff_system: PFFDataSystem):
        self.pff_system = pff_system
        
        # PFF grade thresholds for player quality multipliers
        self.pff_multipliers = {
            'elite': (85.0, 1.2),        # Elite players: 20% EPA boost
            'above_average': (75.0, 1.1), # Above average: 10% EPA boost
            'average': (65.0, 1.0),       # Average: No adjustment
            'below_average': (55.0, 0.9), # Below average: 10% EPA reduction
            'poor': (45.0, 0.8)          # Poor: 20% EPA reduction
        }
        
        # Position-specific EPA weights
        self.position_weights = {
            'QB': 1.0,      # Quarterback - highest impact
            'RB': 0.8,      # Running back - high impact
            'WR': 0.7,      # Wide receiver - high impact
            'TE': 0.6,      # Tight end - medium-high impact
            'OT': 0.5,      # Offensive tackle - medium impact
            'OG': 0.4,      # Offensive guard - medium impact
            'C': 0.4,       # Center - medium impact
            'DE': 0.6,      # Defensive end - medium-high impact
            'DT': 0.5,      # Defensive tackle - medium impact
            'LB': 0.5,      # Linebacker - medium impact
            'CB': 0.6,      # Cornerback - medium-high impact
            'S': 0.5,       # Safety - medium impact
            'K': 0.2,       # Kicker - low impact
            'P': 0.1,       # Punter - low impact
            'LS': 0.1       # Long snapper - low impact
        }
        
        # Situational EPA weights
        self.situational_weights = {
            'red_zone': 1.5,        # Red zone plays are high leverage
            'third_down': 1.3,      # Third down plays are critical
            'two_minute': 1.2,      # Two-minute drill plays
            'goal_line': 2.0,       # Goal line plays are highest leverage
            'normal': 1.0           # Normal situation
        }
    
    def calculate_enhanced_epa_score(self, team_abbr: str, pbp_data: pd.DataFrame, 
                                    week_weights: Dict, opponent_team: str = None) -> Dict:
        """
        Calculate enhanced EPA score with full PFF integration
        
        Args:
            team_abbr: Team abbreviation
            pbp_data: Play-by-play data
            week_weights: Progressive weighting for seasons
            opponent_team: Opponent team abbreviation for matchup analysis
            
        Returns:
            Dict with detailed EPA breakdown
        """
        try:
            # Get team data
            team_data = pbp_data[pbp_data['posteam'] == team_abbr].copy()
            
            if team_data.empty:
                return self._get_default_epa_result()
            
            # Calculate base EPA by season
            base_epa_by_season = self._calculate_base_epa_by_season(team_data)
            
            # Apply PFF enhancements
            enhanced_epa_by_season = {}
            for season, base_epa in base_epa_by_season.items():
                enhanced_epa = self._apply_pff_enhancements(
                    team_abbr, season, base_epa, team_data, opponent_team
                )
                enhanced_epa_by_season[season] = enhanced_epa
            
            # Apply progressive weights
            weighted_epa = self._apply_progressive_weights(enhanced_epa_by_season, week_weights)
            
            # Calculate situational breakdowns
            situational_epa = self._calculate_situational_epa(team_data, team_abbr)
            
            # Calculate advanced metrics
            advanced_metrics = self._calculate_advanced_epa_metrics(team_data, team_abbr)
            
            # Normalize to 0-100 scale
            normalized_epa = max(0, min(100, 50 + (weighted_epa * 100)))
            
            return {
                'final_score': normalized_epa,
                'weighted_epa': weighted_epa,
                'base_epa_by_season': base_epa_by_season,
                'enhanced_epa_by_season': enhanced_epa_by_season,
                'situational_epa': situational_epa,
                'advanced_metrics': advanced_metrics,
                'pff_adjustments': self._get_pff_adjustment_summary(team_abbr)
            }
            
        except Exception as e:
            logger.error(f"Error calculating enhanced EPA score for {team_abbr}: {e}")
            return self._get_default_epa_result()
    
    def _calculate_base_epa_by_season(self, team_data: pd.DataFrame) -> Dict:
        """Calculate base EPA by season"""
        epa_by_season = {}
        for season in [2023, 2024, 2025]:
            season_data = team_data[team_data['season'] == season]
            if not season_data.empty:
                epa_by_season[season] = season_data['epa'].mean()
        return epa_by_season
    
    def _apply_pff_enhancements(self, team_abbr: str, season: int, base_epa: float, 
                               team_data: pd.DataFrame, opponent_team: str = None) -> float:
        """Apply PFF enhancements to base EPA with robust error handling"""
        try:
            # Get team name for PFF data
            team_name = self._get_team_full_name(team_abbr)
            
            # Ensure PFF data is available
            if not hasattr(self.pff_system, 'team_grades') or not self.pff_system.team_grades:
                logger.warning(f"PFF team grades not available for {team_abbr}, using base EPA")
                return base_epa
            
            if not hasattr(self.pff_system, 'player_grades') or not self.pff_system.player_grades:
                logger.warning(f"PFF player grades not available for {team_abbr}, using base EPA")
                return base_epa
            
            # Get PFF team grades with fallback
            team_grades = self.pff_system.team_grades.get(team_name, {})
            if not team_grades:
                logger.warning(f"No PFF team grades found for {team_name}, using default")
                team_grades = {
                    'overall': 75.0, 'overall_offense': 75.0, 'overall_defense': 75.0,
                    'offense': {'passing': 75.0, 'rushing': 75.0, 'receiving': 75.0, 'pass_blocking': 75.0, 'run_blocking': 75.0},
                    'defense': {'pass_rush': 75.0, 'run_defense': 75.0, 'coverage': 75.0, 'tackling': 75.0}
                }
            
            # Get PFF player grades with fallback
            player_grades = self.pff_system.player_grades.get(team_name, {})
            if not player_grades:
                logger.warning(f"No PFF player grades found for {team_name}, using default")
                player_grades = {
                    'QB': {'Starting QB': 75.0}, 'RB': {'Starting RB': 75.0}, 'WR': {'WR1': 75.0},
                    'TE': {'Starting TE': 75.0}, 'OT': {'LT': 75.0}, 'OG': {'LG': 75.0}, 'C': {'Starting C': 75.0},
                    'DE': {'DE1': 75.0}, 'DT': {'DT1': 75.0}, 'LB': {'LB1': 75.0}, 'CB': {'CB1': 75.0}, 'S': {'S1': 75.0}
                }
            
            # Calculate PFF adjustments
            pff_adjustment = 0.0
            
            # 1. Team-level PFF adjustment
            try:
                offensive_grade = team_grades.get('offense', {}).get('passing', 75.0)
                pff_adjustment += (offensive_grade - 75.0) * 0.001  # Small adjustment per grade point
            except Exception as e:
                logger.warning(f"Error calculating team-level PFF adjustment: {e}")
            
            # 2. Player-grade weighted EPA
            try:
                player_adjustment = self._calculate_player_grade_adjustment(
                    team_data, player_grades, season
                )
                pff_adjustment += player_adjustment
            except Exception as e:
                logger.warning(f"Error calculating player-grade adjustment: {e}")
            
            # 3. Matchup-based adjustment
            try:
                if opponent_team:
                    matchup_adjustment = self._calculate_matchup_adjustment(
                        team_name, opponent_team
                    )
                    pff_adjustment += matchup_adjustment
            except Exception as e:
                logger.warning(f"Error calculating matchup adjustment: {e}")
            
            # Apply PFF adjustment to base EPA
            enhanced_epa = base_epa + pff_adjustment
            
            return enhanced_epa
            
        except Exception as e:
            logger.error(f"Error applying PFF enhancements: {e}")
            return base_epa
    
    def _calculate_player_grade_adjustment(self, team_data: pd.DataFrame, 
                                          player_grades: Dict, season: int) -> float:
        """Calculate player-grade weighted EPA adjustment"""
        try:
            season_data = team_data[team_data['season'] == season]
            if season_data.empty:
                return 0.0
            
            total_adjustment = 0.0
            play_count = len(season_data)
            
            # For each position group, calculate weighted adjustment
            for position, players in player_grades.items():
                if not players:
                    continue
                
                # Get average PFF grade for position
                avg_grade = np.mean(list(players.values()))
                
                # Calculate multiplier based on grade
                multiplier = self._get_pff_multiplier(avg_grade)
                
                # Get position weight
                position_weight = self.position_weights.get(position, 0.5)
                
                # Calculate adjustment
                adjustment = (multiplier - 1.0) * position_weight * 0.1
                total_adjustment += adjustment
            
            return total_adjustment / len(player_grades) if player_grades else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating player grade adjustment: {e}")
            return 0.0
    
    def _get_pff_multiplier(self, grade: float) -> float:
        """Get PFF multiplier based on grade"""
        for threshold, multiplier in self.pff_multipliers.values():
            if grade >= threshold:
                return multiplier
        return 0.8  # Default for very poor grades
    
    def _calculate_matchup_adjustment(self, team_name: str, opponent_team: str) -> float:
        """Calculate matchup-based EPA adjustment"""
        try:
            # Get team grades
            team_grades = self.pff_system.team_grades.get(team_name, {})
            opponent_name = self._get_team_full_name(opponent_team)
            opponent_grades = self.pff_system.team_grades.get(opponent_name, {})
            
            if not team_grades or not opponent_grades:
                return 0.0
            
            # Calculate offensive vs defensive matchup
            team_offense = team_grades.get('offense', {})
            opponent_defense = opponent_grades.get('defense', {})
            
            # Passing matchup
            team_passing = team_offense.get('passing', 50)
            opponent_coverage = opponent_defense.get('coverage', 50)
            passing_advantage = (team_passing - opponent_coverage) * 0.0005
            
            # Rushing matchup
            team_rushing = team_offense.get('rushing', 50)
            opponent_run_defense = opponent_defense.get('run_defense', 50)
            rushing_advantage = (team_rushing - opponent_run_defense) * 0.0005
            
            # Pass blocking vs pass rush
            team_pass_blocking = team_offense.get('pass_blocking', 50)
            opponent_pass_rush = opponent_defense.get('pass_rush', 50)
            blocking_advantage = (team_pass_blocking - opponent_pass_rush) * 0.0005
            
            total_adjustment = passing_advantage + rushing_advantage + blocking_advantage
            
            return total_adjustment
            
        except Exception as e:
            logger.error(f"Error calculating matchup adjustment: {e}")
            return 0.0
    
    def _apply_progressive_weights(self, epa_by_season: Dict, week_weights: Dict) -> float:
        """Apply progressive weights to EPA by season"""
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
        
        return weighted_epa / total_weight if total_weight > 0 else 0.0
    
    def _calculate_situational_epa(self, team_data: pd.DataFrame, team_abbr: str) -> Dict:
        """Calculate situational EPA breakdown"""
        try:
            situational_epa = {}
            
            # Red zone success rate (inside 20-yard line) - percentage of successful plays
            red_zone_data = team_data[
                (team_data['yardline_100'] <= 20) & 
                (team_data['yardline_100'] > 0)
            ]
            situational_epa['red_zone'] = (red_zone_data['epa'] > 0).mean() if not red_zone_data.empty else 0.0
            
            # Third down success rate - percentage of successful plays
            third_down_data = team_data[team_data['down'] == 3]
            situational_epa['third_down'] = (third_down_data['epa'] > 0).mean() if not third_down_data.empty else 0.0
            
            # Two-minute drill success rate - percentage of successful plays
            two_minute_data = team_data[
                (team_data['quarter_seconds_remaining'] <= 120) |
                (team_data['game_seconds_remaining'] <= 120)
            ]
            situational_epa['two_minute'] = (two_minute_data['epa'] > 0).mean() if not two_minute_data.empty else 0.0
            
            # Goal line success rate - percentage of successful plays
            goal_line_data = team_data[team_data['yardline_100'] <= 5]
            situational_epa['goal_line'] = (goal_line_data['epa'] > 0).mean() if not goal_line_data.empty else 0.0
            
            # Normal situation success rate - percentage of successful plays
            normal_data = team_data[
                (team_data['yardline_100'] > 20) & 
                (team_data['down'] != 3) &
                (team_data['quarter_seconds_remaining'] > 120)
            ]
            situational_epa['normal'] = (normal_data['epa'] > 0).mean() if not normal_data.empty else 0.0
            
            return situational_epa
            
        except Exception as e:
            logger.error(f"Error calculating situational EPA: {e}")
            return {}
    
    def _calculate_advanced_epa_metrics(self, team_data: pd.DataFrame, team_abbr: str) -> Dict:
        """Calculate advanced EPA metrics"""
        try:
            advanced_metrics = {}
            
            # Air EPA vs YAC EPA
            passing_plays = team_data[
                (team_data['play_type'] == 'pass') & 
                (team_data['air_epa'].notna()) & 
                (team_data['yac_epa'].notna())
            ]
            
            if not passing_plays.empty:
                advanced_metrics['air_epa'] = passing_plays['air_epa'].mean()
                advanced_metrics['yac_epa'] = passing_plays['yac_epa'].mean()
                advanced_metrics['air_epa_ratio'] = advanced_metrics['air_epa'] / (
                    advanced_metrics['air_epa'] + advanced_metrics['yac_epa']
                ) if (advanced_metrics['air_epa'] + advanced_metrics['yac_epa']) != 0 else 0.5
            
            # QB EPA
            qb_plays = team_data[
                (team_data['play_type'] == 'pass') & 
                (team_data['qb_epa'].notna())
            ]
            advanced_metrics['qb_epa'] = qb_plays['qb_epa'].mean() if not qb_plays.empty else 0.0
            
            # Cumulative EPA trends
            advanced_metrics['epa_per_game'] = team_data.groupby('game_id')['epa'].sum().mean()
            advanced_metrics['epa_per_drive'] = team_data.groupby('drive')['epa'].sum().mean()
            
            return advanced_metrics
            
        except Exception as e:
            logger.error(f"Error calculating advanced EPA metrics: {e}")
            return {}
    
    def _get_pff_adjustment_summary(self, team_abbr: str) -> Dict:
        """Get summary of PFF adjustments applied"""
        try:
            team_name = self._get_team_full_name(team_abbr)
            team_grades = self.pff_system.team_grades.get(team_name, {})
            player_grades = self.pff_system.player_grades.get(team_name, {})
            
            return {
                'team_grades_available': bool(team_grades),
                'player_grades_available': bool(player_grades),
                'offensive_grade': team_grades.get('offense', {}).get('passing', 50) if team_grades else 50,
                'defensive_grade': team_grades.get('defense', {}).get('coverage', 50) if team_grades else 50,
                'key_players': self._get_key_players_summary(player_grades)
            }
            
        except Exception as e:
            logger.error(f"Error getting PFF adjustment summary: {e}")
            return {}
    
    def _get_key_players_summary(self, player_grades: Dict) -> Dict:
        """Get summary of key players and their grades"""
        try:
            key_players = {}
            
            for position, players in player_grades.items():
                if players:
                    # Get top 3 players by grade
                    sorted_players = sorted(players.items(), key=lambda x: x[1], reverse=True)
                    key_players[position] = sorted_players[:3]
            
            return key_players
            
        except Exception as e:
            logger.error(f"Error getting key players summary: {e}")
            return {}
    
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
        return team_mapping.get(team_abbr, team_abbr)
    
    def _get_default_epa_result(self) -> Dict:
        """Get default EPA result when calculation fails"""
        return {
            'final_score': 50.0,
            'weighted_epa': 0.0,
            'base_epa_by_season': {},
            'enhanced_epa_by_season': {},
            'situational_epa': {},
            'advanced_metrics': {},
            'pff_adjustments': {}
        }
