#!/usr/bin/env python3
"""
Comprehensive Historical Performance System
Tracks and analyzes historical performance trends, patterns, and consistency.
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

class HistoricalPerformanceSystem:
    """Comprehensive historical performance tracking and analysis system"""
    
    def __init__(self, seasons: List[int] = None):
        """Initialize historical performance system"""
        if seasons is None:
            seasons = [2022, 2023, 2024, 2025]
        
        self.seasons = seasons
        self.historical_data = {}
        self.performance_cache = {}
        self.load_historical_data()
    
    def load_historical_data(self):
        """Load historical data across multiple seasons"""
        logger.info(f"Loading historical data for seasons: {self.seasons}")
        
        try:
            # Load multi-season PBP data
            self.historical_data['pbp'] = nfl.import_pbp_data(self.seasons)
            logger.info(f"✅ Loaded {len(self.historical_data['pbp']):,} historical plays")
            
            # Load multi-season schedules
            self.historical_data['schedules'] = nfl.import_schedules(self.seasons)
            logger.info(f"✅ Loaded {len(self.historical_data['schedules']):,} historical games")
            
            # Load multi-season player stats (if available)
            try:
                self.historical_data['player_stats'] = nfl.import_player_stats(self.seasons)
                logger.info(f"✅ Loaded {len(self.historical_data['player_stats']):,} historical player stats")
            except AttributeError:
                logger.warning("Player stats not available, using PBP data for player analysis")
                self.historical_data['player_stats'] = pd.DataFrame()
            
            # Analyze historical data completeness
            self._analyze_historical_completeness()
            
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            self.historical_data = {}
    
    def _analyze_historical_completeness(self):
        """Analyze completeness of historical data"""
        if not self.historical_data:
            return
        
        logger.info("📊 Analyzing historical data completeness...")
        
        pbp_data = self.historical_data['pbp']
        
        # Analyze by season
        for season in self.seasons:
            season_data = pbp_data[pbp_data['season'] == season]
            logger.info(f"{season}: {len(season_data):,} plays")
        
        # Analyze team coverage
        teams = pbp_data['posteam'].nunique()
        logger.info(f"Teams covered: {teams}")
        
        # Analyze player coverage
        players = pbp_data['passer_player_name'].nunique()
        logger.info(f"Players covered: {players}")
    
    def get_player_historical_trends(self, player_name: str, team: str = None, 
                                   metric: str = 'epa', seasons: List[int] = None) -> Dict:
        """Get historical performance trends for a player"""
        if not self.historical_data:
            return {}
        
        if seasons is None:
            seasons = self.seasons
        
        logger.info(f"📊 Getting historical trends for {player_name}")
        
        # Filter data for player
        player_data = self.historical_data['pbp'][
            (self.historical_data['pbp']['passer_player_name'] == player_name) |
            (self.historical_data['pbp']['rusher_player_name'] == player_name) |
            (self.historical_data['pbp']['receiver_player_name'] == player_name)
        ].copy()
        
        if team:
            player_data = player_data[player_data['posteam'] == team]
        
        if player_data.empty:
            logger.warning(f"No historical data found for {player_name}")
            return {}
        
        # Calculate trends by season
        trends = {}
        
        for season in seasons:
            season_data = player_data[player_data['season'] == season]
            
            if season_data.empty:
                continue
            
            # Calculate season metrics
            season_metrics = {
                'season': season,
                'games_played': season_data['game_id'].nunique(),
                'total_plays': len(season_data),
                'total_epa': season_data['epa'].sum(),
                'avg_epa_per_play': season_data['epa'].mean(),
                'epa_per_game': season_data.groupby('game_id')['epa'].sum().mean(),
                'total_wpa': season_data['wpa'].sum(),
                'avg_wpa_per_play': season_data['wpa'].mean(),
                'wpa_per_game': season_data.groupby('game_id')['wpa'].sum().mean(),
                'success_rate': season_data['success'].mean(),
                'consistency_score': self._calculate_season_consistency(season_data),
                'clutch_factor': self._calculate_season_clutch_factor(season_data),
            }
            
            # Add QB-specific metrics if available
            if 'qb_epa' in season_data.columns:
                season_metrics['total_qb_epa'] = season_data['qb_epa'].sum()
                season_metrics['avg_qb_epa_per_play'] = season_data['qb_epa'].mean()
            
            # Fill NaN values
            for key, value in season_metrics.items():
                if isinstance(value, (int, float)) and pd.isna(value):
                    season_metrics[key] = 0
            
            trends[season] = season_metrics
        
        # Calculate trend analysis
        trend_analysis = self._analyze_performance_trends(trends, metric)
        
        return {
            'player_name': player_name,
            'team': team,
            'metric': metric,
            'seasons_analyzed': list(trends.keys()),
            'seasonal_performance': trends,
            'trend_analysis': trend_analysis
        }
    
    def get_team_historical_trends(self, team: str, metric: str = 'epa', 
                                 seasons: List[int] = None) -> Dict:
        """Get historical performance trends for a team"""
        if not self.historical_data:
            return {}
        
        if seasons is None:
            seasons = self.seasons
        
        logger.info(f"📊 Getting historical trends for {team}")
        
        # Filter data for team
        team_data = self.historical_data['pbp'][self.historical_data['pbp']['posteam'] == team].copy()
        
        if team_data.empty:
            logger.warning(f"No historical data found for {team}")
            return {}
        
        # Calculate trends by season
        trends = {}
        
        for season in seasons:
            season_data = team_data[team_data['season'] == season]
            
            if season_data.empty:
                continue
            
            # Calculate season metrics
            season_metrics = {
                'season': season,
                'games_played': season_data['game_id'].nunique(),
                'total_plays': len(season_data),
                'total_epa': season_data['epa'].sum(),
                'avg_epa_per_play': season_data['epa'].mean(),
                'epa_per_game': season_data.groupby('game_id')['epa'].sum().mean(),
                'total_wpa': season_data['wpa'].sum(),
                'avg_wpa_per_play': season_data['wpa'].mean(),
                'wpa_per_game': season_data.groupby('game_id')['wpa'].sum().mean(),
                'success_rate': season_data['success'].mean(),
                'consistency_score': self._calculate_season_consistency(season_data),
                'efficiency_metrics': self._calculate_season_efficiency(season_data),
            }
            
            # Fill NaN values
            for key, value in season_metrics.items():
                if isinstance(value, (int, float)) and pd.isna(value):
                    season_metrics[key] = 0
            
            trends[season] = season_metrics
        
        # Calculate trend analysis
        trend_analysis = self._analyze_performance_trends(trends, metric)
        
        return {
            'team': team,
            'metric': metric,
            'seasons_analyzed': list(trends.keys()),
            'seasonal_performance': trends,
            'trend_analysis': trend_analysis
        }
    
    def get_historical_matchup_analysis(self, team1: str, team2: str, 
                                      seasons: List[int] = None) -> Dict:
        """Get historical matchup analysis between two teams"""
        if not self.historical_data:
            return {}
        
        if seasons is None:
            seasons = self.seasons
        
        logger.info(f"📊 Getting historical matchup analysis: {team1} vs {team2}")
        
        # Get historical games between teams
        schedules = self.historical_data['schedules']
        historical_games = schedules[
            ((schedules['home_team'] == team1) & (schedules['away_team'] == team2)) |
            ((schedules['home_team'] == team2) & (schedules['away_team'] == team1))
        ].copy()
        
        if historical_games.empty:
            logger.warning(f"No historical games found between {team1} and {team2}")
            return {}
        
        # Analyze each historical game
        game_analyses = []
        
        for _, game in historical_games.iterrows():
            game_id = game['game_id']
            game_data = self.historical_data['pbp'][self.historical_data['pbp']['game_id'] == game_id]
            
            if game_data.empty:
                continue
            
            # Calculate game metrics
            team1_data = game_data[game_data['posteam'] == team1]
            team2_data = game_data[game_data['posteam'] == team2]
            
            game_analysis = {
                'game_id': game_id,
                'season': game['season'],
                'week': game['week'],
                'date': game['gameday'],
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'team1_epa': team1_data['epa'].sum(),
                'team2_epa': team2_data['epa'].sum(),
                'team1_wpa': team1_data['wpa'].sum(),
                'team2_wpa': team2_data['wpa'].sum(),
                'team1_success_rate': team1_data['success'].mean(),
                'team2_success_rate': team2_data['success'].mean(),
                'epa_differential': team1_data['epa'].sum() - team2_data['epa'].sum(),
                'wpa_differential': team1_data['wpa'].sum() - team2_data['wpa'].sum(),
                'winner': game['home_team'] if game['result'] > 0 else game['away_team'],
                'team1_won': 1 if (game['home_team'] == team1 and game['result'] > 0) or (game['away_team'] == team1 and game['result'] < 0) else 0
            }
            
            game_analyses.append(game_analysis)
        
        if not game_analyses:
            return {}
        
        # Calculate historical matchup summary
        matchup_summary = self._calculate_matchup_summary(game_analyses, team1, team2)
        
        return {
            'team1': team1,
            'team2': team2,
            'total_games': len(game_analyses),
            'seasons_analyzed': list(set([game['season'] for game in game_analyses])),
            'game_analyses': game_analyses,
            'matchup_summary': matchup_summary
        }
    
    def get_historical_situational_performance(self, team: str, situation: str, 
                                              seasons: List[int] = None) -> Dict:
        """Get historical performance in specific situations"""
        if not self.historical_data:
            return {}
        
        if seasons is None:
            seasons = self.seasons
        
        logger.info(f"📊 Getting historical situational performance for {team} in {situation}")
        
        # Filter data for team
        team_data = self.historical_data['pbp'][self.historical_data['pbp']['posteam'] == team].copy()
        
        if team_data.empty:
            logger.warning(f"No historical data found for {team}")
            return {}
        
        # Define situational filters
        situational_data = self._apply_situational_filter(team_data, situation)
        
        if situational_data.empty:
            logger.warning(f"No {situation} data found for {team}")
            return {}
        
        # Calculate situational performance by season
        situational_trends = {}
        
        for season in seasons:
            season_data = situational_data[situational_data['season'] == season]
            
            if season_data.empty:
                continue
            
            season_metrics = {
                'season': season,
                'games_played': season_data['game_id'].nunique(),
                'total_plays': len(season_data),
                'total_epa': season_data['epa'].sum(),
                'avg_epa_per_play': season_data['epa'].mean(),
                'total_wpa': season_data['wpa'].sum(),
                'avg_wpa_per_play': season_data['wpa'].mean(),
                'success_rate': season_data['success'].mean(),
                'consistency_score': self._calculate_season_consistency(season_data),
            }
            
            # Fill NaN values
            for key, value in season_metrics.items():
                if isinstance(value, (int, float)) and pd.isna(value):
                    season_metrics[key] = 0
            
            situational_trends[season] = season_metrics
        
        # Calculate trend analysis
        trend_analysis = self._analyze_performance_trends(situational_trends, 'epa')
        
        return {
            'team': team,
            'situation': situation,
            'seasons_analyzed': list(situational_trends.keys()),
            'situational_performance': situational_trends,
            'trend_analysis': trend_analysis
        }
    
    def get_historical_performance_consistency(self, team: str, seasons: List[int] = None) -> Dict:
        """Get historical performance consistency analysis"""
        if not self.historical_data:
            return {}
        
        if seasons is None:
            seasons = self.seasons
        
        logger.info(f"📊 Getting historical performance consistency for {team}")
        
        # Filter data for team
        team_data = self.historical_data['pbp'][self.historical_data['pbp']['posteam'] == team].copy()
        
        if team_data.empty:
            logger.warning(f"No historical data found for {team}")
            return {}
        
        # Calculate consistency metrics by season
        consistency_metrics = {}
        
        for season in seasons:
            season_data = team_data[team_data['season'] == season]
            
            if season_data.empty:
                continue
            
            # Calculate game-by-game performance
            game_performance = season_data.groupby('game_id').agg({
                'epa': ['sum', 'mean'],
                'wpa': ['sum', 'mean'],
                'success': 'mean'
            }).round(3)
            
            game_performance.columns = ['total_epa', 'avg_epa', 'total_wpa', 'avg_wpa', 'success_rate']
            
            # Calculate consistency metrics
            season_consistency = {
                'season': season,
                'games_played': len(game_performance),
                'epa_consistency': 1 - game_performance['total_epa'].std() / abs(game_performance['total_epa'].mean()) if game_performance['total_epa'].mean() != 0 else 0,
                'wpa_consistency': 1 - game_performance['total_wpa'].std() / abs(game_performance['total_wpa'].mean()) if game_performance['total_wpa'].mean() != 0 else 0,
                'success_rate_consistency': 1 - game_performance['success_rate'].std(),
                'epa_variance': game_performance['total_epa'].var(),
                'wpa_variance': game_performance['total_wpa'].var(),
                'success_rate_variance': game_performance['success_rate'].var(),
                'best_game_epa': game_performance['total_epa'].max(),
                'worst_game_epa': game_performance['total_epa'].min(),
                'best_game_wpa': game_performance['total_wpa'].max(),
                'worst_game_wpa': game_performance['total_wpa'].min(),
            }
            
            # Fill NaN values
            for key, value in season_consistency.items():
                if pd.isna(value):
                    season_consistency[key] = 0
            
            consistency_metrics[season] = season_consistency
        
        # Calculate overall consistency trend
        consistency_trend = self._analyze_consistency_trend(consistency_metrics)
        
        return {
            'team': team,
            'seasons_analyzed': list(consistency_metrics.keys()),
            'seasonal_consistency': consistency_metrics,
            'consistency_trend': consistency_trend
        }
    
    def get_historical_performance_momentum(self, team: str, seasons: List[int] = None) -> Dict:
        """Get historical performance momentum analysis"""
        if not self.historical_data:
            return {}
        
        if seasons is None:
            seasons = self.seasons
        
        logger.info(f"📊 Getting historical performance momentum for {team}")
        
        # Filter data for team
        team_data = self.historical_data['pbp'][self.historical_data['pbp']['posteam'] == team].copy()
        
        if team_data.empty:
            logger.warning(f"No historical data found for {team}")
            return {}
        
        # Calculate momentum by season
        momentum_metrics = {}
        
        for season in seasons:
            season_data = team_data[team_data['season'] == season].copy()
            
            if season_data.empty:
                continue
            
            # Sort by game and play
            season_data = season_data.sort_values(['game_id', 'play_id'])
            
            # Calculate rolling performance metrics
            season_data['rolling_epa'] = season_data['epa'].rolling(window=10, min_periods=1).sum()
            season_data['rolling_wpa'] = season_data['wpa'].rolling(window=10, min_periods=1).sum()
            season_data['rolling_success'] = season_data['success'].rolling(window=10, min_periods=1).mean()
            
            # Calculate momentum metrics
            season_momentum = {
                'season': season,
                'games_played': season_data['game_id'].nunique(),
                'total_plays': len(season_data),
                'momentum_score': self._calculate_momentum_score(season_data),
                'momentum_trend': self._analyze_momentum_trend(season_data),
                'hot_streaks': self._identify_hot_streaks(season_data),
                'cold_streaks': self._identify_cold_streaks(season_data),
                'momentum_consistency': self._calculate_momentum_consistency(season_data),
            }
            
            # Fill NaN values
            for key, value in season_momentum.items():
                if isinstance(value, (int, float)) and pd.isna(value):
                    season_momentum[key] = 0
                elif isinstance(value, list) and len(value) == 0:
                    season_momentum[key] = []
            
            momentum_metrics[season] = season_momentum
        
        # Calculate overall momentum trend
        momentum_trend = self._analyze_momentum_trend_across_seasons(momentum_metrics)
        
        return {
            'team': team,
            'seasons_analyzed': list(momentum_metrics.keys()),
            'seasonal_momentum': momentum_metrics,
            'momentum_trend': momentum_trend
        }
    
    def _calculate_season_consistency(self, season_data: pd.DataFrame) -> float:
        """Calculate consistency score for a season"""
        if season_data.empty:
            return 0
        
        # Calculate game-by-game performance
        game_performance = season_data.groupby('game_id')['epa'].sum()
        
        if len(game_performance) <= 1:
            return 1.0
        
        # Consistency is inverse of coefficient of variation
        mean_performance = game_performance.mean()
        std_performance = game_performance.std()
        
        if mean_performance == 0:
            return 1.0
        
        consistency = 1 - (std_performance / abs(mean_performance))
        return max(0, min(1, consistency))
    
    def _calculate_season_clutch_factor(self, season_data: pd.DataFrame) -> float:
        """Calculate clutch factor for a season"""
        if season_data.empty:
            return 0
        
        # Define high-leverage situations (high WPA plays)
        high_leverage = season_data[abs(season_data['wpa']) > 0.05]
        
        if len(high_leverage) == 0:
            return 0
        
        # Calculate average WPA in high-leverage situations
        clutch_wpa = high_leverage['wpa'].mean()
        return round(clutch_wpa, 4)
    
    def _calculate_season_efficiency(self, season_data: pd.DataFrame) -> Dict:
        """Calculate efficiency metrics for a season"""
        if season_data.empty:
            return {}
        
        efficiency = {}
        
        # Explosive play rate (EPA > 1.0)
        explosive_plays = season_data[season_data['epa'] > 1.0]
        efficiency['explosive_play_rate'] = len(explosive_plays) / len(season_data)
        
        # Negative play rate (EPA < -1.0)
        negative_plays = season_data[season_data['epa'] < -1.0]
        efficiency['negative_play_rate'] = len(negative_plays) / len(season_data)
        
        # Success rate
        efficiency['success_rate'] = season_data['success'].mean()
        
        return efficiency
    
    def _analyze_performance_trends(self, trends: Dict, metric: str) -> Dict:
        """Analyze performance trends over time"""
        if len(trends) < 2:
            return {'trend': 'Insufficient data', 'slope': 0, 'r_squared': 0}
        
        # Extract metric values and seasons
        seasons = sorted(trends.keys())
        values = [trends[season][f'total_{metric}'] for season in seasons]
        
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
    
    def _apply_situational_filter(self, data: pd.DataFrame, situation: str) -> pd.DataFrame:
        """Apply situational filter to data"""
        if situation == 'red_zone':
            return data[data['yardline_100'] <= 20]
        elif situation == 'third_down':
            return data[data['down'] == 3]
        elif situation == 'two_minute':
            return data[data['quarter_seconds_remaining'] <= 120]
        elif situation == 'goal_line':
            return data[data['goal_to_go'] == 1]
        elif situation == 'passing':
            return data[data['play_type'] == 'pass']
        elif situation == 'rushing':
            return data[data['play_type'] == 'run']
        else:
            return data
    
    def _calculate_matchup_summary(self, game_analyses: List[Dict], team1: str, team2: str) -> Dict:
        """Calculate historical matchup summary"""
        if not game_analyses:
            return {}
        
        # Calculate win/loss record
        team1_wins = sum([game['team1_won'] for game in game_analyses])
        team2_wins = len(game_analyses) - team1_wins
        
        # Calculate average performance differentials
        avg_epa_differential = np.mean([game['epa_differential'] for game in game_analyses])
        avg_wpa_differential = np.mean([game['wpa_differential'] for game in game_analyses])
        avg_success_differential = np.mean([game['team1_success_rate'] - game['team2_success_rate'] for game in game_analyses])
        
        return {
            'total_games': len(game_analyses),
            'team1_wins': team1_wins,
            'team2_wins': team2_wins,
            'team1_win_percentage': team1_wins / len(game_analyses),
            'avg_epa_differential': avg_epa_differential,
            'avg_wpa_differential': avg_wpa_differential,
            'avg_success_differential': avg_success_differential,
            'team1_advantage': 'EPA' if avg_epa_differential > 0 else 'WPA' if avg_wpa_differential > 0 else 'Success Rate' if avg_success_differential > 0 else 'None'
        }
    
    def _analyze_consistency_trend(self, consistency_metrics: Dict) -> Dict:
        """Analyze consistency trend across seasons"""
        if len(consistency_metrics) < 2:
            return {'trend': 'Insufficient data', 'slope': 0}
        
        seasons = sorted(consistency_metrics.keys())
        consistency_scores = [consistency_metrics[season]['epa_consistency'] for season in seasons]
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(seasons, consistency_scores)
        
        if abs(slope) < 0.01:
            trend_direction = 'Stable'
        elif slope > 0:
            trend_direction = 'Improving'
        else:
            trend_direction = 'Declining'
        
        return {
            'trend': trend_direction,
            'slope': slope,
            'r_squared': r_value ** 2,
            'correlation': r_value
        }
    
    def _calculate_momentum_score(self, season_data: pd.DataFrame) -> float:
        """Calculate overall momentum score for a season"""
        if season_data.empty:
            return 0
        
        # Calculate momentum as weighted average of recent performance
        weights = np.exp(np.linspace(-1, 0, len(season_data)))
        weighted_epa = np.average(season_data['epa'], weights=weights)
        weighted_wpa = np.average(season_data['wpa'], weights=weights)
        
        # Combine EPA and WPA for momentum score
        momentum_score = (weighted_epa * 0.7) + (weighted_wpa * 100 * 0.3)
        return round(momentum_score, 3)
    
    def _analyze_momentum_trend(self, season_data: pd.DataFrame) -> str:
        """Analyze momentum trend within a season"""
        if len(season_data) < 10:
            return 'Insufficient data'
        
        # Calculate rolling average
        rolling_epa = season_data['epa'].rolling(window=10, min_periods=1).mean()
        
        # Simple trend analysis
        first_half = rolling_epa.iloc[:len(rolling_epa)//2].mean()
        second_half = rolling_epa.iloc[len(rolling_epa)//2:].mean()
        
        if second_half > first_half * 1.1:
            return 'Positive momentum'
        elif second_half < first_half * 0.9:
            return 'Negative momentum'
        else:
            return 'Stable momentum'
    
    def _identify_hot_streaks(self, season_data: pd.DataFrame) -> List[Dict]:
        """Identify hot streaks in performance"""
        if len(season_data) < 5:
            return []
        
        # Define hot streak as 5+ consecutive plays with positive EPA
        hot_streaks = []
        current_streak = 0
        streak_start = 0
        
        for i, epa in enumerate(season_data['epa']):
            if epa > 0:
                if current_streak == 0:
                    streak_start = i
                current_streak += 1
            else:
                if current_streak >= 5:
                    hot_streaks.append({
                        'start_play': streak_start,
                        'length': current_streak,
                        'total_epa': season_data['epa'].iloc[streak_start:streak_start+current_streak].sum()
                    })
                current_streak = 0
        
        return hot_streaks
    
    def _identify_cold_streaks(self, season_data: pd.DataFrame) -> List[Dict]:
        """Identify cold streaks in performance"""
        if len(season_data) < 5:
            return []
        
        # Define cold streak as 5+ consecutive plays with negative EPA
        cold_streaks = []
        current_streak = 0
        streak_start = 0
        
        for i, epa in enumerate(season_data['epa']):
            if epa < 0:
                if current_streak == 0:
                    streak_start = i
                current_streak += 1
            else:
                if current_streak >= 5:
                    cold_streaks.append({
                        'start_play': streak_start,
                        'length': current_streak,
                        'total_epa': season_data['epa'].iloc[streak_start:streak_start+current_streak].sum()
                    })
                current_streak = 0
        
        return cold_streaks
    
    def _calculate_momentum_consistency(self, season_data: pd.DataFrame) -> float:
        """Calculate momentum consistency"""
        if len(season_data) < 10:
            return 0
        
        # Calculate rolling momentum
        rolling_epa = season_data['epa'].rolling(window=10, min_periods=1).mean()
        
        # Consistency is inverse of variance
        consistency = 1 - rolling_epa.var()
        return max(0, min(1, consistency))
    
    def _analyze_momentum_trend_across_seasons(self, momentum_metrics: Dict) -> Dict:
        """Analyze momentum trend across seasons"""
        if len(momentum_metrics) < 2:
            return {'trend': 'Insufficient data', 'slope': 0}
        
        seasons = sorted(momentum_metrics.keys())
        momentum_scores = [momentum_metrics[season]['momentum_score'] for season in seasons]
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(seasons, momentum_scores)
        
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
            'correlation': r_value
        }

def main():
    """Main function to demonstrate historical performance system"""
    logger.info("📊 Historical Performance System Starting...")
    
    # Create historical performance system
    historical_system = HistoricalPerformanceSystem()
    
    if not historical_system.historical_data:
        logger.error("Failed to load historical data. Exiting.")
        return
    
    # Test with key teams
    test_teams = ['BUF', 'MIA']
    
    for team in test_teams:
        print(f"\n📊 {team} - HISTORICAL PERFORMANCE ANALYSIS")
        print("=" * 60)
        
        # Get historical trends
        trends = historical_system.get_team_historical_trends(team)
        if trends:
            print(f"📈 HISTORICAL TRENDS:")
            print(f"  Seasons analyzed: {trends['seasons_analyzed']}")
            print(f"  Trend analysis: {trends['trend_analysis']['trend']}")
            print(f"  Trend slope: {trends['trend_analysis']['slope']:.3f}")
            print(f"  R-squared: {trends['trend_analysis']['r_squared']:.3f}")
            
            print(f"\n  Seasonal Performance:")
            for season, metrics in trends['seasonal_performance'].items():
                print(f"    {season}: EPA {metrics['total_epa']:.2f}, WPA {metrics['total_wpa']:.2f}, Success {metrics['success_rate']:.1%}")
        
        # Get historical consistency
        consistency = historical_system.get_historical_performance_consistency(team)
        if consistency:
            print(f"\n🎯 HISTORICAL CONSISTENCY:")
            print(f"  Seasons analyzed: {consistency['seasons_analyzed']}")
            print(f"  Consistency trend: {consistency['consistency_trend']['trend']}")
            
            print(f"\n  Seasonal Consistency:")
            for season, metrics in consistency['seasonal_consistency'].items():
                print(f"    {season}: EPA Consistency {metrics['epa_consistency']:.3f}, WPA Consistency {metrics['wpa_consistency']:.3f}")
        
        # Get historical momentum
        momentum = historical_system.get_historical_performance_momentum(team)
        if momentum:
            print(f"\n🚀 HISTORICAL MOMENTUM:")
            print(f"  Seasons analyzed: {momentum['seasons_analyzed']}")
            print(f"  Momentum trend: {momentum['momentum_trend']['trend']}")
            
            print(f"\n  Seasonal Momentum:")
            for season, metrics in momentum['seasonal_momentum'].items():
                print(f"    {season}: Momentum Score {metrics['momentum_score']:.3f}, Trend {metrics['momentum_trend']}")
    
    # Test historical matchup analysis
    print(f"\n🏈 HISTORICAL MATCHUP ANALYSIS")
    print("=" * 40)
    
    matchup = historical_system.get_historical_matchup_analysis('BUF', 'MIA')
    if matchup:
        print(f"📊 BUF vs MIA Historical Matchup:")
        print(f"  Total games: {matchup['total_games']}")
        print(f"  BUF wins: {matchup['matchup_summary']['team1_wins']}")
        print(f"  MIA wins: {matchup['matchup_summary']['team2_wins']}")
        print(f"  BUF win percentage: {matchup['matchup_summary']['team1_win_percentage']:.1%}")
        print(f"  Average EPA differential: {matchup['matchup_summary']['avg_epa_differential']:.2f}")
        print(f"  Average WPA differential: {matchup['matchup_summary']['avg_wpa_differential']:.3f}")
        print(f"  BUF advantage: {matchup['matchup_summary']['team1_advantage']}")
    
    # Test historical situational performance
    print(f"\n🎯 HISTORICAL SITUATIONAL PERFORMANCE")
    print("=" * 45)
    
    for team in test_teams:
        print(f"\n📊 {team} Situational Performance:")
        
        situations = ['red_zone', 'third_down', 'two_minute']
        for situation in situations:
            situational = historical_system.get_historical_situational_performance(team, situation)
            if situational:
                print(f"  {situation.title()}:")
                print(f"    Seasons: {situational['seasons_analyzed']}")
                print(f"    Trend: {situational['trend_analysis']['trend']}")
                
                # Show recent performance
                if situational['situational_performance']:
                    recent_season = max(situational['situational_performance'].keys())
                    recent_metrics = situational['situational_performance'][recent_season]
                    print(f"    {recent_season}: EPA {recent_metrics['total_epa']:.2f}, Success {recent_metrics['success_rate']:.1%}")
    
    logger.info("\n✅ Historical performance system demonstration completed!")

if __name__ == "__main__":
    main()
