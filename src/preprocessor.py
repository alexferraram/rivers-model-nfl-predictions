"""
NFL Data Preprocessing Module

This module handles cleaning and preprocessing of NFL data for machine learning.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class NFLPreprocessor:
    """Preprocesses NFL data for machine learning."""
    
    def __init__(self):
        self.feature_columns = []
        self.target_column = None
    
    def clean_schedule_data(self, schedules: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare schedule data."""
        logger.info("Cleaning schedule data...")
        
        # Create a copy to avoid modifying original
        df = schedules.copy()
        
        # Convert date columns
        if 'gameday' in df.columns:
            df['gameday'] = pd.to_datetime(df['gameday'])
        
        # Filter out games without results (future games)
        df = df.dropna(subset=['home_score', 'away_score'])
        
        # Create game outcome features
        df['home_win'] = (df['home_score'] > df['away_score']).astype(int)
        df['away_win'] = (df['away_score'] > df['home_score']).astype(int)
        df['tie'] = (df['home_score'] == df['away_score']).astype(int)
        
        # Calculate point differential
        df['home_point_diff'] = df['home_score'] - df['away_score']
        df['away_point_diff'] = df['away_score'] - df['home_score']
        
        logger.info(f"Cleaned schedule data: {len(df)} games")
        return df
    
    def extract_team_stats_from_pbp(self, pbp_data: pd.DataFrame) -> pd.DataFrame:
        """Extract team-level statistics from play-by-play data."""
        logger.info("Extracting team statistics from play-by-play data...")
        
        if pbp_data.empty:
            logger.warning("No play-by-play data available")
            return pd.DataFrame()
        
        # Group by team and game
        team_stats = []
        
        for (season, week, team), group in pbp_data.groupby(['season', 'week', 'posteam']):
            if pd.isna(team):  # Skip plays without team info
                continue
                
            stats = {
                'season': season,
                'week': week,
                'team': team,
                'games_played': 1,
                'total_plays': len(group),
                'pass_attempts': len(group[group['play_type'] == 'pass']),
                'rush_attempts': len(group[group['play_type'] == 'run']),
                'total_yards': group['yards_gained'].sum(),
                'pass_yards': group[group['play_type'] == 'pass']['yards_gained'].sum(),
                'rush_yards': group[group['play_type'] == 'run']['yards_gained'].sum(),
                'first_downs': len(group[group['first_down'] == 1]),
                'turnovers': len(group[group['interception'] == 1]) + len(group[group['fumble_lost'] == 1]),
                'sacks': len(group[group['sack'] == 1]),
                'touchdowns': len(group[group['touchdown'] == 1]),
                'field_goals_made': len(group[group['field_goal_result'] == 'made']),
                'field_goals_attempted': len(group[group['play_type'] == 'field_goal']),
            }
            
            # Calculate rates and averages
            if stats['total_plays'] > 0:
                stats['pass_rate'] = stats['pass_attempts'] / stats['total_plays']
                stats['rush_rate'] = stats['rush_attempts'] / stats['total_plays']
                stats['yards_per_play'] = stats['total_yards'] / stats['total_plays']
                stats['first_down_rate'] = stats['first_downs'] / stats['total_plays']
                stats['turnover_rate'] = stats['turnovers'] / stats['total_plays']
            else:
                stats.update({
                    'pass_rate': 0, 'rush_rate': 0, 'yards_per_play': 0,
                    'first_down_rate': 0, 'turnover_rate': 0
                })
            
            # Handle field goal percentage
            if stats['field_goals_attempted'] > 0:
                stats['fg_percentage'] = stats['field_goals_made'] / stats['field_goals_attempted']
            else:
                stats['fg_percentage'] = 0
            
            team_stats.append(stats)
        
        team_stats_df = pd.DataFrame(team_stats)
        
        # Aggregate by team and season for season-long stats
        season_stats = team_stats_df.groupby(['season', 'team']).agg({
            'games_played': 'sum',
            'total_plays': 'sum',
            'pass_attempts': 'sum',
            'rush_attempts': 'sum',
            'total_yards': 'sum',
            'pass_yards': 'sum',
            'rush_yards': 'sum',
            'first_downs': 'sum',
            'turnovers': 'sum',
            'sacks': 'sum',
            'touchdowns': 'sum',
            'field_goals_made': 'sum',
            'field_goals_attempted': 'sum',
            'pass_rate': 'mean',
            'rush_rate': 'mean',
            'yards_per_play': 'mean',
            'first_down_rate': 'mean',
            'turnover_rate': 'mean',
            'fg_percentage': 'mean'
        }).reset_index()
        
        logger.info(f"Extracted team statistics for {len(season_stats)} team-seasons")
        return season_stats
    
    def create_game_features(self, schedules: pd.DataFrame, team_stats: pd.DataFrame) -> pd.DataFrame:
        """Create features for each game by combining schedule and team statistics."""
        logger.info("Creating game features...")
        
        if schedules.empty or team_stats.empty:
            logger.warning("Missing required data for feature creation")
            return pd.DataFrame()
        
        game_features = []
        
        for _, game in schedules.iterrows():
            season = game['season']
            home_team = game['home_team']
            away_team = game['away_team']
            
            # Get team stats for the season
            home_stats = team_stats[(team_stats['season'] == season) & 
                                  (team_stats['team'] == home_team)]
            away_stats = team_stats[(team_stats['season'] == season) & 
                                  (team_stats['team'] == away_team)]
            
            if home_stats.empty or away_stats.empty:
                continue  # Skip games where we don't have team stats
            
            home_stats = home_stats.iloc[0]
            away_stats = away_stats.iloc[0]
            
            # Create feature row
            features = {
                'season': season,
                'week': game['week'],
                'home_team': home_team,
                'away_team': away_team,
                'home_score': game['home_score'],
                'away_score': game['away_score'],
                'home_win': game['home_win'],
                
                # Home team features
                'home_games_played': home_stats['games_played'],
                'home_total_plays': home_stats['total_plays'],
                'home_pass_rate': home_stats['pass_rate'],
                'home_rush_rate': home_stats['rush_rate'],
                'home_yards_per_play': home_stats['yards_per_play'],
                'home_first_down_rate': home_stats['first_down_rate'],
                'home_turnover_rate': home_stats['turnover_rate'],
                'home_fg_percentage': home_stats['fg_percentage'],
                'home_touchdowns': home_stats['touchdowns'],
                
                # Away team features
                'away_games_played': away_stats['games_played'],
                'away_total_plays': away_stats['total_plays'],
                'away_pass_rate': away_stats['pass_rate'],
                'away_rush_rate': away_stats['rush_rate'],
                'away_yards_per_play': away_stats['yards_per_play'],
                'away_first_down_rate': away_stats['first_down_rate'],
                'away_turnover_rate': away_stats['turnover_rate'],
                'away_fg_percentage': away_stats['fg_percentage'],
                'away_touchdowns': away_stats['touchdowns'],
            }
            
            # Calculate differential features
            features.update({
                'yards_per_play_diff': home_stats['yards_per_play'] - away_stats['yards_per_play'],
                'first_down_rate_diff': home_stats['first_down_rate'] - away_stats['first_down_rate'],
                'turnover_rate_diff': home_stats['turnover_rate'] - away_stats['turnover_rate'],
                'fg_percentage_diff': home_stats['fg_percentage'] - away_stats['fg_percentage'],
                'touchdown_diff': home_stats['touchdowns'] - away_stats['touchdowns'],
            })
            
            game_features.append(features)
        
        features_df = pd.DataFrame(game_features)
        logger.info(f"Created features for {len(features_df)} games")
        
        return features_df
    
    def prepare_ml_data(self, game_features: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare data for machine learning."""
        logger.info("Preparing data for machine learning...")
        
        # Select feature columns (exclude identifiers and target)
        exclude_cols = ['season', 'week', 'home_team', 'away_team', 'home_score', 'away_score', 'home_win']
        feature_cols = [col for col in game_features.columns if col not in exclude_cols]
        
        X = game_features[feature_cols].copy()
        y = game_features['home_win'].copy()
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        # Store feature columns for later use
        self.feature_columns = feature_cols
        self.target_column = 'home_win'
        
        logger.info(f"Prepared ML data: {X.shape[0]} samples, {X.shape[1]} features")
        return X, y
    
    def get_feature_importance_data(self) -> Dict[str, List[str]]:
        """Get feature information for analysis."""
        return {
            'feature_columns': self.feature_columns,
            'target_column': self.target_column
        }






