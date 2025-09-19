#!/usr/bin/env python3
"""
Comprehensive Situational Statistics System
Tracks and analyzes situational performance patterns, efficiency ratings, and performance indexes.
"""

import pandas as pd
import numpy as np
import nfl_data_py as nfl
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SituationalStatisticsSystem:
    """Comprehensive situational statistics tracking and analysis system"""
    
    def __init__(self, seasons: List[int] = None):
        """Initialize situational statistics system"""
        if seasons is None:
            seasons = [datetime.now().year]
        
        self.seasons = seasons
        self.situational_data = {}
        self.situational_cache = {}
        self.load_situational_data()
    
    def load_situational_data(self):
        """Load situational data from PBP"""
        logger.info(f"Loading situational data for seasons: {self.seasons}")
        
        try:
            # Load PBP data
            self.situational_data['pbp'] = nfl.import_pbp_data(self.seasons)
            logger.info(f"✅ Loaded {len(self.situational_data['pbp']):,} plays for situational analysis")
            
            # Analyze situational data completeness
            self._analyze_situational_completeness()
            
        except Exception as e:
            logger.error(f"Error loading situational data: {e}")
            self.situational_data = {}
    
    def _analyze_situational_completeness(self):
        """Analyze completeness of situational data"""
        if not self.situational_data:
            return
        
        logger.info("📊 Analyzing situational data completeness...")
        
        pbp_data = self.situational_data['pbp']
        
        # Analyze situational coverage
        logger.info(f"Down data: {pbp_data['down'].notna().sum():,}/{len(pbp_data):,} plays")
        logger.info(f"Distance data: {pbp_data['ydstogo'].notna().sum():,}/{len(pbp_data):,} plays")
        logger.info(f"Field position data: {pbp_data['yardline_100'].notna().sum():,}/{len(pbp_data):,} plays")
        logger.info(f"Quarter data: {pbp_data['qtr'].notna().sum():,}/{len(pbp_data):,} plays")
        logger.info(f"Time data: {pbp_data['quarter_seconds_remaining'].notna().sum():,}/{len(pbp_data):,} plays")
    
    def get_team_situational_statistics(self, team: str, situation: str = None, 
                                       week: int = None) -> Dict:
        """Get comprehensive situational statistics for a team"""
        if not self.situational_data:
            return {}
        
        logger.info(f"📊 Getting situational statistics for {team}")
        
        # Filter data for team
        team_data = self.situational_data['pbp'][self.situational_data['pbp']['posteam'] == team].copy()
        
        if week:
            team_data = team_data[team_data['week'] == week]
        
        if team_data.empty:
            logger.warning(f"No data found for {team}")
            return {}
        
        # Calculate situational statistics
        situational_stats = {
            'team': team,
            'week': week,
            'total_plays': len(team_data),
            'games_played': team_data['game_id'].nunique(),
            
            # Down-specific statistics
            'down_statistics': self._calculate_down_statistics(team_data),
            
            # Distance-specific statistics
            'distance_statistics': self._calculate_distance_statistics(team_data),
            
            # Field position statistics
            'field_position_statistics': self._calculate_field_position_statistics(team_data),
            
            # Quarter-specific statistics
            'quarter_statistics': self._calculate_quarter_statistics(team_data),
            
            # Time-specific statistics
            'time_statistics': self._calculate_time_statistics(team_data),
            
            # Situational efficiency ratings
            'efficiency_ratings': self._calculate_situational_efficiency_ratings(team_data),
            
            # Situational performance indexes
            'performance_indexes': self._calculate_situational_performance_indexes(team_data),
            
            # Situational consistency metrics
            'consistency_metrics': self._calculate_situational_consistency_metrics(team_data),
        }
        
        # If specific situation requested, filter and return
        if situation:
            situational_stats['specific_situation'] = self._get_specific_situation_stats(team_data, situation)
        
        logger.info(f"📊 {team} situational statistics: {len(team_data):,} plays analyzed")
        return situational_stats
    
    def get_player_situational_statistics(self, player_name: str, team: str = None, 
                                        situation: str = None, week: int = None) -> Dict:
        """Get comprehensive situational statistics for a player"""
        if not self.situational_data:
            return {}
        
        logger.info(f"📊 Getting situational statistics for {player_name}")
        
        # Filter data for player
        player_data = self.situational_data['pbp'][
            (self.situational_data['pbp']['passer_player_name'] == player_name) |
            (self.situational_data['pbp']['rusher_player_name'] == player_name) |
            (self.situational_data['pbp']['receiver_player_name'] == player_name)
        ].copy()
        
        if team:
            player_data = player_data[player_data['posteam'] == team]
        if week:
            player_data = player_data[player_data['week'] == week]
        
        if player_data.empty:
            logger.warning(f"No data found for {player_name}")
            return {}
        
        # Calculate situational statistics
        situational_stats = {
            'player_name': player_name,
            'team': team,
            'week': week,
            'total_plays': len(player_data),
            'games_played': player_data['game_id'].nunique(),
            
            # Down-specific statistics
            'down_statistics': self._calculate_down_statistics(player_data),
            
            # Distance-specific statistics
            'distance_statistics': self._calculate_distance_statistics(player_data),
            
            # Field position statistics
            'field_position_statistics': self._calculate_field_position_statistics(player_data),
            
            # Quarter-specific statistics
            'quarter_statistics': self._calculate_quarter_statistics(player_data),
            
            # Time-specific statistics
            'time_statistics': self._calculate_time_statistics(player_data),
            
            # Situational efficiency ratings
            'efficiency_ratings': self._calculate_situational_efficiency_ratings(player_data),
            
            # Situational performance indexes
            'performance_indexes': self._calculate_situational_performance_indexes(player_data),
            
            # Situational consistency metrics
            'consistency_metrics': self._calculate_situational_consistency_metrics(player_data),
        }
        
        # If specific situation requested, filter and return
        if situation:
            situational_stats['specific_situation'] = self._get_specific_situation_stats(player_data, situation)
        
        logger.info(f"📊 {player_name} situational statistics: {len(player_data):,} plays analyzed")
        return situational_stats
    
    def get_situational_matchup_analysis(self, team1: str, team2: str, 
                                       situation: str = None) -> Dict:
        """Get situational matchup analysis between two teams"""
        if not self.situational_data:
            return {}
        
        logger.info(f"📊 Getting situational matchup analysis: {team1} vs {team2}")
        
        # Get data for both teams
        team1_data = self.situational_data['pbp'][self.situational_data['pbp']['posteam'] == team1].copy()
        team2_data = self.situational_data['pbp'][self.situational_data['pbp']['posteam'] == team2].copy()
        
        if team1_data.empty or team2_data.empty:
            logger.warning(f"Insufficient data for matchup analysis")
            return {}
        
        # Calculate situational matchup analysis
        matchup_analysis = {
            'team1': team1,
            'team2': team2,
            'situation': situation,
            
            # Team 1 situational statistics
            'team1_situational_stats': self.get_team_situational_statistics(team1, situation),
            
            # Team 2 situational statistics
            'team2_situational_stats': self.get_team_situational_statistics(team2, situation),
            
            # Situational advantages
            'situational_advantages': self._calculate_situational_advantages(team1_data, team2_data, situation),
            
            # Situational efficiency comparison
            'efficiency_comparison': self._calculate_situational_efficiency_comparison(team1_data, team2_data),
            
            # Situational performance comparison
            'performance_comparison': self._calculate_situational_performance_comparison(team1_data, team2_data),
        }
        
        logger.info(f"📊 {team1} vs {team2} situational matchup analysis completed")
        return matchup_analysis
    
    def get_situational_trend_analysis(self, team: str, situation: str, 
                                     seasons: List[int] = None) -> Dict:
        """Get situational trend analysis over time"""
        if not self.situational_data:
            return {}
        
        if seasons is None:
            seasons = self.seasons
        
        logger.info(f"📊 Getting situational trend analysis for {team} in {situation}")
        
        # Filter data for team
        team_data = self.situational_data['pbp'][self.situational_data['pbp']['posteam'] == team].copy()
        
        if team_data.empty:
            logger.warning(f"No data found for {team}")
            return {}
        
        # Calculate trend analysis by season
        trend_analysis = {}
        
        for season in seasons:
            season_data = team_data[team_data['season'] == season]
            
            if season_data.empty:
                continue
            
            # Apply situational filter
            situational_data = self._apply_situational_filter(season_data, situation)
            
            if situational_data.empty:
                continue
            
            # Calculate season situational metrics
            season_metrics = {
                'season': season,
                'plays': len(situational_data),
                'epa': situational_data['epa'].sum(),
                'avg_epa': situational_data['epa'].mean(),
                'wpa': situational_data['wpa'].sum(),
                'avg_wpa': situational_data['wpa'].mean(),
                'success_rate': situational_data['success'].mean(),
                'yards_gained': situational_data['yards_gained'].sum(),
                'avg_yards': situational_data['yards_gained'].mean(),
                'efficiency_rating': self._calculate_situational_efficiency_rating(situational_data),
                'performance_index': self._calculate_situational_performance_index(situational_data),
            }
            
            trend_analysis[season] = season_metrics
        
        # Calculate trend statistics
        trend_stats = self._calculate_trend_statistics(trend_analysis, situation)
        
        return {
            'team': team,
            'situation': situation,
            'seasons_analyzed': list(trend_analysis.keys()),
            'seasonal_metrics': trend_analysis,
            'trend_statistics': trend_stats
        }
    
    def get_situational_leaders(self, situation: str, metric: str = 'epa', 
                              position: str = None, limit: int = 10) -> List[Dict]:
        """Get leaders in specific situational metrics"""
        if not self.situational_data:
            return []
        
        logger.info(f"📊 Getting {situation} leaders by {metric}")
        
        # Filter by position if specified
        if position == 'QB':
            player_data = self.situational_data['pbp'][self.situational_data['pbp']['passer_player_name'].notna()].copy()
            player_col = 'passer_player_name'
        elif position == 'RB':
            player_data = self.situational_data['pbp'][self.situational_data['pbp']['rusher_player_name'].notna()].copy()
            player_col = 'rusher_player_name'
        elif position == 'WR':
            player_data = self.situational_data['pbp'][self.situational_data['pbp']['receiver_player_name'].notna()].copy()
            player_col = 'receiver_player_name'
        else:
            # All players
            player_data = self.situational_data['pbp'][
                (self.situational_data['pbp']['passer_player_name'].notna()) |
                (self.situational_data['pbp']['rusher_player_name'].notna()) |
                (self.situational_data['pbp']['receiver_player_name'].notna())
            ].copy()
            player_col = 'passer_player_name'  # Default to passer for now
        
        # Apply situational filter
        situational_data = self._apply_situational_filter(player_data, situation)
        
        if situational_data.empty:
            return []
        
        # Group by player and calculate metrics
        if metric == 'epa':
            leaders = situational_data.groupby(player_col).agg({
                'epa': ['sum', 'mean', 'count'],
                'posteam': 'first'
            }).round(3)
        elif metric == 'wpa':
            leaders = situational_data.groupby(player_col).agg({
                'wpa': ['sum', 'mean', 'count'],
                'posteam': 'first'
            }).round(3)
        elif metric == 'success_rate':
            leaders = situational_data.groupby(player_col).agg({
                'success': ['sum', 'mean', 'count'],
                'posteam': 'first'
            }).round(3)
        else:
            return []
        
        # Flatten column names
        leaders.columns = ['total', 'avg', 'plays', 'team']
        leaders = leaders[leaders['plays'] >= 5]  # Minimum 5 plays
        
        # Sort by total metric
        leaders = leaders.sort_values('total', ascending=False).head(limit)
        
        # Convert to list of dictionaries
        leaders_list = []
        for player, row in leaders.iterrows():
            leaders_list.append({
                'player': player,
                'team': row['team'],
                'total': row['total'],
                'average': row['avg'],
                'plays': row['plays']
            })
        
        return leaders_list
    
    def _calculate_down_statistics(self, data: pd.DataFrame) -> Dict:
        """Calculate down-specific statistics"""
        if data.empty:
            return {}
        
        down_stats = {}
        
        for down in [1, 2, 3, 4]:
            down_data = data[data['down'] == down]
            
            if len(down_data) == 0:
                continue
            
            down_stats[f'down_{int(down)}'] = {
                'plays': len(down_data),
                'epa': down_data['epa'].sum(),
                'avg_epa': down_data['epa'].mean(),
                'wpa': down_data['wpa'].sum(),
                'avg_wpa': down_data['wpa'].mean(),
                'success_rate': down_data['success'].mean(),
                'yards_gained': down_data['yards_gained'].sum(),
                'avg_yards': down_data['yards_gained'].mean(),
                'first_downs': down_data['first_down'].sum(),
                'first_down_rate': down_data['first_down'].mean(),
            }
        
        return down_stats
    
    def _calculate_distance_statistics(self, data: pd.DataFrame) -> Dict:
        """Calculate distance-specific statistics"""
        if data.empty:
            return {}
        
        distance_stats = {}
        
        # Define distance ranges
        distance_ranges = [
            (0, 3, 'short'),
            (4, 7, 'medium'),
            (8, 15, 'long'),
            (16, 99, 'very_long')
        ]
        
        for min_dist, max_dist, label in distance_ranges:
            distance_data = data[(data['ydstogo'] >= min_dist) & (data['ydstogo'] <= max_dist)]
            
            if len(distance_data) == 0:
                continue
            
            distance_stats[label] = {
                'plays': len(distance_data),
                'epa': distance_data['epa'].sum(),
                'avg_epa': distance_data['epa'].mean(),
                'wpa': distance_data['wpa'].sum(),
                'avg_wpa': distance_data['wpa'].mean(),
                'success_rate': distance_data['success'].mean(),
                'yards_gained': distance_data['yards_gained'].sum(),
                'avg_yards': distance_data['yards_gained'].mean(),
                'first_downs': distance_data['first_down'].sum(),
                'first_down_rate': distance_data['first_down'].mean(),
            }
        
        return distance_stats
    
    def _calculate_field_position_statistics(self, data: pd.DataFrame) -> Dict:
        """Calculate field position-specific statistics"""
        if data.empty:
            return {}
        
        fp_stats = {}
        
        # Define field position ranges
        fp_ranges = [
            (0, 20, 'red_zone'),
            (21, 50, 'opponent_territory'),
            (51, 80, 'own_territory'),
            (81, 100, 'own_red_zone')
        ]
        
        for min_yard, max_yard, label in fp_ranges:
            fp_data = data[(data['yardline_100'] >= min_yard) & (data['yardline_100'] <= max_yard)]
            
            if len(fp_data) == 0:
                continue
            
            fp_stats[label] = {
                'plays': len(fp_data),
                'epa': fp_data['epa'].sum(),
                'avg_epa': fp_data['epa'].mean(),
                'wpa': fp_data['wpa'].sum(),
                'avg_wpa': fp_data['wpa'].mean(),
                'success_rate': fp_data['success'].mean(),
                'yards_gained': fp_data['yards_gained'].sum(),
                'avg_yards': fp_data['yards_gained'].mean(),
                'touchdowns': fp_data['touchdown'].sum(),
                'touchdown_rate': fp_data['touchdown'].mean(),
            }
        
        return fp_stats
    
    def _calculate_quarter_statistics(self, data: pd.DataFrame) -> Dict:
        """Calculate quarter-specific statistics"""
        if data.empty:
            return {}
        
        quarter_stats = {}
        
        for quarter in [1, 2, 3, 4]:
            quarter_data = data[data['qtr'] == quarter]
            
            if len(quarter_data) == 0:
                continue
            
            quarter_stats[f'quarter_{quarter}'] = {
                'plays': len(quarter_data),
                'epa': quarter_data['epa'].sum(),
                'avg_epa': quarter_data['epa'].mean(),
                'wpa': quarter_data['wpa'].sum(),
                'avg_wpa': quarter_data['wpa'].mean(),
                'success_rate': quarter_data['success'].mean(),
                'yards_gained': quarter_data['yards_gained'].sum(),
                'avg_yards': quarter_data['yards_gained'].mean(),
            }
        
        return quarter_stats
    
    def _calculate_time_statistics(self, data: pd.DataFrame) -> Dict:
        """Calculate time-specific statistics"""
        if data.empty:
            return {}
        
        time_stats = {}
        
        # Define time ranges
        time_ranges = [
            (0, 300, 'early_quarter'),
            (301, 600, 'mid_quarter'),
            (601, 900, 'late_quarter'),
            (901, 1200, 'end_quarter')
        ]
        
        for min_time, max_time, label in time_ranges:
            time_data = data[(data['quarter_seconds_remaining'] >= min_time) & (data['quarter_seconds_remaining'] <= max_time)]
            
            if len(time_data) == 0:
                continue
            
            time_stats[label] = {
                'plays': len(time_data),
                'epa': time_data['epa'].sum(),
                'avg_epa': time_data['epa'].mean(),
                'wpa': time_data['wpa'].sum(),
                'avg_wpa': time_data['wpa'].mean(),
                'success_rate': time_data['success'].mean(),
                'yards_gained': time_data['yards_gained'].sum(),
                'avg_yards': time_data['yards_gained'].mean(),
            }
        
        return time_stats
    
    def _calculate_situational_efficiency_ratings(self, data: pd.DataFrame) -> Dict:
        """Calculate situational efficiency ratings"""
        if data.empty:
            return {}
        
        efficiency_ratings = {}
        
        # Red zone efficiency
        red_zone_data = data[data['yardline_100'] <= 20]
        if len(red_zone_data) > 0:
            efficiency_ratings['red_zone_efficiency'] = {
                'plays': len(red_zone_data),
                'epa_per_play': red_zone_data['epa'].mean(),
                'success_rate': red_zone_data['success'].mean(),
                'touchdown_rate': red_zone_data['touchdown'].mean(),
                'efficiency_score': (red_zone_data['epa'].mean() * 0.4) + (red_zone_data['success'].mean() * 0.6)
            }
        
        # Third down efficiency
        third_down_data = data[data['down'] == 3]
        if len(third_down_data) > 0:
            efficiency_ratings['third_down_efficiency'] = {
                'plays': len(third_down_data),
                'epa_per_play': third_down_data['epa'].mean(),
                'success_rate': third_down_data['success'].mean(),
                'conversion_rate': third_down_data['first_down'].mean(),
                'efficiency_score': (third_down_data['epa'].mean() * 0.3) + (third_down_data['success'].mean() * 0.7)
            }
        
        # Two-minute drill efficiency
        two_minute_data = data[data['quarter_seconds_remaining'] <= 120]
        if len(two_minute_data) > 0:
            efficiency_ratings['two_minute_efficiency'] = {
                'plays': len(two_minute_data),
                'epa_per_play': two_minute_data['epa'].mean(),
                'success_rate': two_minute_data['success'].mean(),
                'wpa_per_play': two_minute_data['wpa'].mean(),
                'efficiency_score': (two_minute_data['epa'].mean() * 0.5) + (two_minute_data['wpa'].mean() * 100 * 0.5)
            }
        
        # Goal-to-go efficiency
        goal_to_go_data = data[data['goal_to_go'] == 1]
        if len(goal_to_go_data) > 0:
            efficiency_ratings['goal_to_go_efficiency'] = {
                'plays': len(goal_to_go_data),
                'epa_per_play': goal_to_go_data['epa'].mean(),
                'success_rate': goal_to_go_data['success'].mean(),
                'touchdown_rate': goal_to_go_data['touchdown'].mean(),
                'efficiency_score': (goal_to_go_data['epa'].mean() * 0.3) + (goal_to_go_data['touchdown'].mean() * 0.7)
            }
        
        return efficiency_ratings
    
    def _calculate_situational_performance_indexes(self, data: pd.DataFrame) -> Dict:
        """Calculate situational performance indexes"""
        if data.empty:
            return {}
        
        performance_indexes = {}
        
        # Overall situational performance index
        performance_indexes['overall_situational_index'] = {
            'epa_index': data['epa'].mean() * 100,
            'wpa_index': data['wpa'].mean() * 1000,
            'success_index': data['success'].mean() * 100,
            'yards_index': data['yards_gained'].mean() * 10,
            'composite_index': (data['epa'].mean() * 100) + (data['wpa'].mean() * 1000) + (data['success'].mean() * 100) + (data['yards_gained'].mean() * 10)
        }
        
        # Situational performance by down
        for down in [1, 2, 3, 4]:
            down_data = data[data['down'] == down]
            if len(down_data) > 0:
                performance_indexes[f'down_{int(down)}_index'] = {
                    'epa_index': down_data['epa'].mean() * 100,
                    'success_index': down_data['success'].mean() * 100,
                    'composite_index': (down_data['epa'].mean() * 100) + (down_data['success'].mean() * 100)
                }
        
        # Situational performance by field position
        fp_ranges = [(0, 20, 'red_zone'), (21, 50, 'opponent_territory'), (51, 80, 'own_territory'), (81, 100, 'own_red_zone')]
        for min_yard, max_yard, label in fp_ranges:
            fp_data = data[(data['yardline_100'] >= min_yard) & (data['yardline_100'] <= max_yard)]
            if len(fp_data) > 0:
                performance_indexes[f'{label}_index'] = {
                    'epa_index': fp_data['epa'].mean() * 100,
                    'success_index': fp_data['success'].mean() * 100,
                    'composite_index': (fp_data['epa'].mean() * 100) + (fp_data['success'].mean() * 100)
                }
        
        return performance_indexes
    
    def _calculate_situational_consistency_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate situational consistency metrics"""
        if data.empty:
            return {}
        
        consistency_metrics = {}
        
        # Game-by-game consistency
        game_consistency = data.groupby('game_id').agg({
            'epa': ['sum', 'mean'],
            'wpa': ['sum', 'mean'],
            'success': 'mean'
        }).round(3)
        
        game_consistency.columns = ['total_epa', 'avg_epa', 'total_wpa', 'avg_wpa', 'success_rate']
        
        consistency_metrics['game_consistency'] = {
            'epa_consistency': 1 - (game_consistency['total_epa'].std() / abs(game_consistency['total_epa'].mean())) if game_consistency['total_epa'].mean() != 0 else 0,
            'wpa_consistency': 1 - (game_consistency['total_wpa'].std() / abs(game_consistency['total_wpa'].mean())) if game_consistency['total_wpa'].mean() != 0 else 0,
            'success_rate_consistency': 1 - game_consistency['success_rate'].std(),
            'epa_variance': game_consistency['total_epa'].var(),
            'wpa_variance': game_consistency['total_wpa'].var(),
            'success_rate_variance': game_consistency['success_rate'].var(),
        }
        
        # Situational consistency
        for down in [1, 2, 3, 4]:
            down_data = data[data['down'] == down]
            if len(down_data) > 0:
                consistency_metrics[f'down_{int(down)}_consistency'] = {
                    'epa_consistency': 1 - (down_data['epa'].std() / abs(down_data['epa'].mean())) if down_data['epa'].mean() != 0 else 0,
                    'success_consistency': 1 - down_data['success'].std(),
                }
        
        return consistency_metrics
    
    def _get_specific_situation_stats(self, data: pd.DataFrame, situation: str) -> Dict:
        """Get statistics for a specific situation"""
        situational_data = self._apply_situational_filter(data, situation)
        
        if situational_data.empty:
            return {}
        
        return {
            'situation': situation,
            'plays': len(situational_data),
            'epa': situational_data['epa'].sum(),
            'avg_epa': situational_data['epa'].mean(),
            'wpa': situational_data['wpa'].sum(),
            'avg_wpa': situational_data['wpa'].mean(),
            'success_rate': situational_data['success'].mean(),
            'yards_gained': situational_data['yards_gained'].sum(),
            'avg_yards': situational_data['yards_gained'].mean(),
            'efficiency_rating': self._calculate_situational_efficiency_rating(situational_data),
            'performance_index': self._calculate_situational_performance_index(situational_data),
        }
    
    def _apply_situational_filter(self, data: pd.DataFrame, situation: str) -> pd.DataFrame:
        """Apply situational filter to data"""
        if situation == 'red_zone':
            return data[data['yardline_100'] <= 20]
        elif situation == 'third_down':
            return data[data['down'] == 3]
        elif situation == 'two_minute':
            return data[data['quarter_seconds_remaining'] <= 120]
        elif situation == 'goal_to_go':
            return data[data['goal_to_go'] == 1]
        elif situation == 'passing':
            return data[data['play_type'] == 'pass']
        elif situation == 'rushing':
            return data[data['play_type'] == 'run']
        elif situation == 'first_down':
            return data[data['down'] == 1]
        elif situation == 'second_down':
            return data[data['down'] == 2]
        elif situation == 'fourth_down':
            return data[data['down'] == 4]
        else:
            return data
    
    def _calculate_situational_efficiency_rating(self, data: pd.DataFrame) -> float:
        """Calculate situational efficiency rating"""
        if data.empty:
            return 0
        
        # Weighted combination of EPA, success rate, and WPA
        epa_score = data['epa'].mean() * 100
        success_score = data['success'].mean() * 100
        wpa_score = data['wpa'].mean() * 1000
        
        efficiency_rating = (epa_score * 0.4) + (success_score * 0.4) + (wpa_score * 0.2)
        return round(efficiency_rating, 2)
    
    def _calculate_situational_performance_index(self, data: pd.DataFrame) -> float:
        """Calculate situational performance index"""
        if data.empty:
            return 0
        
        # Weighted combination of multiple metrics
        epa_index = data['epa'].mean() * 100
        success_index = data['success'].mean() * 100
        yards_index = data['yards_gained'].mean() * 10
        wpa_index = data['wpa'].mean() * 1000
        
        performance_index = (epa_index * 0.3) + (success_index * 0.3) + (yards_index * 0.2) + (wpa_index * 0.2)
        return round(performance_index, 2)
    
    def _calculate_situational_advantages(self, team1_data: pd.DataFrame, team2_data: pd.DataFrame, situation: str) -> Dict:
        """Calculate situational advantages between teams"""
        if team1_data.empty or team2_data.empty:
            return {}
        
        # Apply situational filter if specified
        if situation:
            team1_situational = self._apply_situational_filter(team1_data, situation)
            team2_situational = self._apply_situational_filter(team2_data, situation)
        else:
            team1_situational = team1_data
            team2_situational = team2_data
        
        if team1_situational.empty or team2_situational.empty:
            return {}
        
        advantages = {
            'team1_epa_advantage': team1_situational['epa'].mean() - team2_situational['epa'].mean(),
            'team1_wpa_advantage': team1_situational['wpa'].mean() - team2_situational['wpa'].mean(),
            'team1_success_advantage': team1_situational['success'].mean() - team2_situational['success'].mean(),
            'team1_yards_advantage': team1_situational['yards_gained'].mean() - team2_situational['yards_gained'].mean(),
            'team1_efficiency_advantage': self._calculate_situational_efficiency_rating(team1_situational) - self._calculate_situational_efficiency_rating(team2_situational),
            'team1_performance_advantage': self._calculate_situational_performance_index(team1_situational) - self._calculate_situational_performance_index(team2_situational),
        }
        
        return advantages
    
    def _calculate_situational_efficiency_comparison(self, team1_data: pd.DataFrame, team2_data: pd.DataFrame) -> Dict:
        """Calculate situational efficiency comparison"""
        if team1_data.empty or team2_data.empty:
            return {}
        
        comparison = {}
        
        # Compare efficiency in different situations
        situations = ['red_zone', 'third_down', 'two_minute', 'goal_to_go']
        
        for situation in situations:
            team1_situational = self._apply_situational_filter(team1_data, situation)
            team2_situational = self._apply_situational_filter(team2_data, situation)
            
            if not team1_situational.empty and not team2_situational.empty:
                comparison[f'{situation}_efficiency_comparison'] = {
                    'team1_efficiency': self._calculate_situational_efficiency_rating(team1_situational),
                    'team2_efficiency': self._calculate_situational_efficiency_rating(team2_situational),
                    'efficiency_differential': self._calculate_situational_efficiency_rating(team1_situational) - self._calculate_situational_efficiency_rating(team2_situational),
                    'team1_advantage': self._calculate_situational_efficiency_rating(team1_situational) > self._calculate_situational_efficiency_rating(team2_situational)
                }
        
        return comparison
    
    def _calculate_situational_performance_comparison(self, team1_data: pd.DataFrame, team2_data: pd.DataFrame) -> Dict:
        """Calculate situational performance comparison"""
        if team1_data.empty or team2_data.empty:
            return {}
        
        comparison = {}
        
        # Compare performance in different situations
        situations = ['red_zone', 'third_down', 'two_minute', 'goal_to_go']
        
        for situation in situations:
            team1_situational = self._apply_situational_filter(team1_data, situation)
            team2_situational = self._apply_situational_filter(team2_data, situation)
            
            if not team1_situational.empty and not team2_situational.empty:
                comparison[f'{situation}_performance_comparison'] = {
                    'team1_performance': self._calculate_situational_performance_index(team1_situational),
                    'team2_performance': self._calculate_situational_performance_index(team2_situational),
                    'performance_differential': self._calculate_situational_performance_index(team1_situational) - self._calculate_situational_performance_index(team2_situational),
                    'team1_advantage': self._calculate_situational_performance_index(team1_situational) > self._calculate_situational_performance_index(team2_situational)
                }
        
        return comparison
    
    def _calculate_trend_statistics(self, trend_analysis: Dict, situation: str) -> Dict:
        """Calculate trend statistics"""
        if len(trend_analysis) < 2:
            return {'trend': 'Insufficient data', 'slope': 0, 'r_squared': 0}
        
        # Extract metric values and seasons
        seasons = sorted(trend_analysis.keys())
        values = [trend_analysis[season]['epa'] for season in seasons]
        
        # Calculate trend
        slope, intercept, r_value, p_value, std_err = stats.linregress(seasons, values)
        
        # Determine trend direction
        if abs(slope) < 0.1:
            trend_direction = 'Stable'
        elif slope > 0:
            trend_direction = 'Improving'
        else:
            trend_direction = 'Declining'
        
        return {
            'trend': trend_direction,
            'slope': slope,
            'r_squared': r_value ** 2,
            'p_value': p_value,
            'std_error': std_err,
            'correlation': r_value
        }

def main():
    """Main function to demonstrate situational statistics system"""
    logger.info("📊 Situational Statistics System Starting...")
    
    # Create situational statistics system
    situational_system = SituationalStatisticsSystem()
    
    if not situational_system.situational_data:
        logger.error("Failed to load situational data. Exiting.")
        return
    
    # Test with key teams
    test_teams = ['BUF', 'MIA']
    
    for team in test_teams:
        print(f"\n📊 {team} - SITUATIONAL STATISTICS ANALYSIS")
        print("=" * 60)
        
        # Get comprehensive situational statistics
        situational_stats = situational_system.get_team_situational_statistics(team)
        
        if situational_stats:
            print(f"📈 DOWN-SPECIFIC STATISTICS:")
            for down, stats in situational_stats['down_statistics'].items():
                print(f"  {down.title()}: EPA {stats['epa']:.2f}, Success {stats['success_rate']:.1%}, Plays {stats['plays']}")
            
            print(f"\n📊 DISTANCE-SPECIFIC STATISTICS:")
            for distance, stats in situational_stats['distance_statistics'].items():
                print(f"  {distance.title()}: EPA {stats['epa']:.2f}, Success {stats['success_rate']:.1%}, Plays {stats['plays']}")
            
            print(f"\n🏟️ FIELD POSITION STATISTICS:")
            for fp, stats in situational_stats['field_position_statistics'].items():
                print(f"  {fp.replace('_', ' ').title()}: EPA {stats['epa']:.2f}, Success {stats['success_rate']:.1%}, Plays {stats['plays']}")
            
            print(f"\n⏰ QUARTER-SPECIFIC STATISTICS:")
            for quarter, stats in situational_stats['quarter_statistics'].items():
                print(f"  {quarter.replace('_', ' ').title()}: EPA {stats['epa']:.2f}, Success {stats['success_rate']:.1%}, Plays {stats['plays']}")
            
            print(f"\n🎯 SITUATIONAL EFFICIENCY RATINGS:")
            for efficiency, stats in situational_stats['efficiency_ratings'].items():
                print(f"  {efficiency.replace('_', ' ').title()}: {stats['efficiency_score']:.2f} (EPA {stats['epa_per_play']:.3f}, Success {stats['success_rate']:.1%})")
            
            print(f"\n📊 SITUATIONAL PERFORMANCE INDEXES:")
            for index, stats in situational_stats['performance_indexes'].items():
                if 'composite_index' in stats:
                    print(f"  {index.replace('_', ' ').title()}: {stats['composite_index']:.2f}")
    
    # Test situational matchup analysis
    print(f"\n🏈 SITUATIONAL MATCHUP ANALYSIS")
    print("=" * 40)
    
    matchup = situational_system.get_situational_matchup_analysis('BUF', 'MIA')
    if matchup:
        print(f"📊 BUF vs MIA Situational Matchup:")
        
        # Show situational advantages
        advantages = matchup['situational_advantages']
        print(f"  EPA Advantage: {advantages['team1_epa_advantage']:.3f}")
        print(f"  WPA Advantage: {advantages['team1_wpa_advantage']:.4f}")
        print(f"  Success Advantage: {advantages['team1_success_advantage']:.1%}")
        print(f"  Yards Advantage: {advantages['team1_yards_advantage']:.2f}")
        print(f"  Efficiency Advantage: {advantages['team1_efficiency_advantage']:.2f}")
        print(f"  Performance Advantage: {advantages['team1_performance_advantage']:.2f}")
        
        # Show efficiency comparison
        print(f"\n  Efficiency Comparison:")
        for comparison, stats in matchup['efficiency_comparison'].items():
            situation = comparison.replace('_efficiency_comparison', '')
            print(f"    {situation.replace('_', ' ').title()}: BUF {stats['team1_efficiency']:.2f} vs MIA {stats['team2_efficiency']:.2f}")
    
    # Test situational leaders
    print(f"\n🏆 SITUATIONAL LEADERS")
    print("=" * 30)
    
    situations = ['red_zone', 'third_down', 'two_minute']
    
    for situation in situations:
        print(f"\n📊 Top 5 {situation.replace('_', ' ').title()} Leaders:")
        leaders = situational_system.get_situational_leaders(situation, 'epa', 'QB', 5)
        for i, leader in enumerate(leaders, 1):
            print(f"  {i}. {leader['player']} ({leader['team']}): {leader['total']:.2f} EPA")
    
    # Test situational trend analysis
    print(f"\n📈 SITUATIONAL TREND ANALYSIS")
    print("=" * 40)
    
    for team in test_teams:
        print(f"\n📊 {team} Situational Trends:")
        
        for situation in ['red_zone', 'third_down']:
            trend = situational_system.get_situational_trend_analysis(team, situation)
            if trend:
                print(f"  {situation.replace('_', ' ').title()}:")
                print(f"    Trend: {trend['trend_statistics']['trend']}")
                print(f"    Slope: {trend['trend_statistics']['slope']:.3f}")
                print(f"    R-squared: {trend['trend_statistics']['r_squared']:.3f}")
    
    logger.info("\n✅ Situational statistics system demonstration completed!")

if __name__ == "__main__":
    main()
