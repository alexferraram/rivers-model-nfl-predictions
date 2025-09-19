"""
Advanced NFL Data Preprocessing Module

This module handles advanced feature engineering including:
- Situational statistics (3rd down, redzone, etc.)
- Player-level statistics and injury tracking
- Matchup analysis (offense vs defense)
- Team tendencies and advanced metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class AdvancedNFLPreprocessor:
    """Advanced preprocessing for NFL data with comprehensive feature engineering."""
    
    def __init__(self):
        self.feature_columns = []
        self.target_column = None
        self.player_positions = ['QB', 'RB', 'WR', 'TE', 'OL', 'DL', 'LB', 'DB', 'K', 'P']
    
    def extract_situational_stats(self, pbp_data: pd.DataFrame) -> pd.DataFrame:
        """Extract situational statistics from play-by-play data."""
        logger.info("Extracting situational statistics...")
        
        if pbp_data.empty:
            return pd.DataFrame()
        
        situational_stats = []
        
        for (season, week, team), group in pbp_data.groupby(['season', 'week', 'posteam']):
            if pd.isna(team):
                continue
            
            # Third down statistics
            third_down_plays = group[group['down'] == 3]
            third_down_conversions = len(third_down_plays[third_down_plays['first_down'] == 1])
            third_down_attempts = len(third_down_plays)
            
            # Red zone statistics
            redzone_plays = group[group['yardline_100'] <= 20]
            redzone_touchdowns = len(redzone_plays[redzone_plays['touchdown'] == 1])
            redzone_attempts = len(redzone_plays)
            
            # Goal line statistics (inside 5 yards)
            goal_line_plays = group[group['yardline_100'] <= 5]
            goal_line_touchdowns = len(goal_line_plays[goal_line_plays['touchdown'] == 1])
            goal_line_attempts = len(goal_line_plays)
            
            # Two-minute drill statistics
            two_min_plays = group[group['game_seconds_remaining'] <= 120]
            two_min_touchdowns = len(two_min_plays[two_min_plays['touchdown'] == 1])
            two_min_attempts = len(two_min_plays)
            
            # Down and distance tendencies
            short_yardage = group[(group['ydstogo'] <= 3) & (group['down'] <= 2)]
            long_yardage = group[(group['ydstogo'] >= 7) & (group['down'] <= 2)]
            
            stats = {
                'season': season,
                'week': week,
                'team': team,
                'games_played': 1,
                
                # Third down stats
                'third_down_conversions': third_down_conversions,
                'third_down_attempts': third_down_attempts,
                'third_down_rate': third_down_conversions / max(third_down_attempts, 1),
                
                # Red zone stats
                'redzone_touchdowns': redzone_touchdowns,
                'redzone_attempts': redzone_attempts,
                'redzone_td_rate': redzone_touchdowns / max(redzone_attempts, 1),
                
                # Goal line stats
                'goal_line_touchdowns': goal_line_touchdowns,
                'goal_line_attempts': goal_line_attempts,
                'goal_line_td_rate': goal_line_touchdowns / max(goal_line_attempts, 1),
                
                # Two-minute drill
                'two_min_touchdowns': two_min_touchdowns,
                'two_min_attempts': two_min_attempts,
                'two_min_td_rate': two_min_touchdowns / max(two_min_attempts, 1),
                
                # Situational tendencies
                'short_yardage_plays': len(short_yardage),
                'long_yardage_plays': len(long_yardage),
                'short_yardage_success': len(short_yardage[short_yardage['first_down'] == 1]) / max(len(short_yardage), 1),
                'long_yardage_success': len(long_yardage[long_yardage['first_down'] == 1]) / max(len(long_yardage), 1),
            }
            
            situational_stats.append(stats)
        
        situational_df = pd.DataFrame(situational_stats)
        
        # Aggregate by team and season
        season_situational = situational_df.groupby(['season', 'team']).agg({
            'games_played': 'sum',
            'third_down_conversions': 'sum',
            'third_down_attempts': 'sum',
            'third_down_rate': 'mean',
            'redzone_touchdowns': 'sum',
            'redzone_attempts': 'sum',
            'redzone_td_rate': 'mean',
            'goal_line_touchdowns': 'sum',
            'goal_line_attempts': 'sum',
            'goal_line_td_rate': 'mean',
            'two_min_touchdowns': 'sum',
            'two_min_attempts': 'sum',
            'two_min_td_rate': 'mean',
            'short_yardage_plays': 'sum',
            'long_yardage_plays': 'sum',
            'short_yardage_success': 'mean',
            'long_yardage_success': 'mean'
        }).reset_index()
        
        logger.info(f"Extracted situational statistics for {len(season_situational)} team-seasons")
        return season_situational
    
    def extract_player_stats(self, player_stats: pd.DataFrame, rosters: pd.DataFrame) -> pd.DataFrame:
        """Extract and aggregate player statistics by position and team."""
        logger.info("Extracting player statistics...")
        
        if player_stats.empty or rosters.empty:
            return pd.DataFrame()
        
        # Merge player stats with roster data to get positions
        player_data = player_stats.merge(
            rosters[['player_id', 'position', 'team']], 
            on='player_id', 
            how='left'
        )
        
        # Filter for relevant positions
        skill_positions = ['QB', 'RB', 'WR', 'TE']
        defensive_positions = ['DL', 'LB', 'DB']
        
        team_player_stats = []
        
        for (season, team), group in player_data.groupby(['season', 'team']):
            if pd.isna(team):
                continue
            
            stats = {
                'season': season,
                'team': team,
                'games_played': group['games'].sum() if 'games' in group.columns else 0,
            }
            
            # Offensive skill position stats
            skill_players = group[group['position'].isin(skill_positions)]
            if not skill_players.empty:
                stats.update({
                    'skill_player_games': skill_players['games'].sum() if 'games' in skill_players.columns else 0,
                    'total_passing_yards': skill_players['passing_yards'].sum() if 'passing_yards' in skill_players.columns else 0,
                    'total_rushing_yards': skill_players['rushing_yards'].sum() if 'rushing_yards' in skill_players.columns else 0,
                    'total_receiving_yards': skill_players['receiving_yards'].sum() if 'receiving_yards' in skill_players.columns else 0,
                    'total_touchdowns': skill_players['passing_tds'].sum() + skill_players['rushing_tds'].sum() + skill_players['receiving_tds'].sum() if all(col in skill_players.columns for col in ['passing_tds', 'rushing_tds', 'receiving_tds']) else 0,
                })
            
            # Defensive stats
            defensive_players = group[group['position'].isin(defensive_positions)]
            if not defensive_players.empty:
                stats.update({
                    'defensive_player_games': defensive_players['games'].sum() if 'games' in defensive_players.columns else 0,
                    'total_tackles': defensive_players['tackles'].sum() if 'tackles' in defensive_players.columns else 0,
                    'total_sacks': defensive_players['sacks'].sum() if 'sacks' in defensive_players.columns else 0,
                    'total_interceptions': defensive_players['interceptions'].sum() if 'interceptions' in defensive_players.columns else 0,
                    'total_passes_defended': defensive_players['passes_defended'].sum() if 'passes_defended' in defensive_players.columns else 0,
                })
            
            # Calculate per-game averages
            if stats['games_played'] > 0:
                stats.update({
                    'passing_yards_per_game': stats.get('total_passing_yards', 0) / stats['games_played'],
                    'rushing_yards_per_game': stats.get('total_rushing_yards', 0) / stats['games_played'],
                    'receiving_yards_per_game': stats.get('total_receiving_yards', 0) / stats['games_played'],
                    'touchdowns_per_game': stats.get('total_touchdowns', 0) / stats['games_played'],
                    'tackles_per_game': stats.get('total_tackles', 0) / stats['games_played'],
                    'sacks_per_game': stats.get('total_sacks', 0) / stats['games_played'],
                })
            else:
                stats.update({
                    'passing_yards_per_game': 0, 'rushing_yards_per_game': 0,
                    'receiving_yards_per_game': 0, 'touchdowns_per_game': 0,
                    'tackles_per_game': 0, 'sacks_per_game': 0
                })
            
            team_player_stats.append(stats)
        
        team_stats_df = pd.DataFrame(team_player_stats)
        logger.info(f"Extracted player statistics for {len(team_stats_df)} team-seasons")
        return team_stats_df
    
    def extract_injury_impact(self, injuries: pd.DataFrame, depth_charts: pd.DataFrame) -> pd.DataFrame:
        """Extract injury impact on team performance."""
        logger.info("Extracting injury impact data...")
        
        if injuries.empty or depth_charts.empty:
            return pd.DataFrame()
        
        injury_impact = []
        
        for (season, team), injury_group in injuries.groupby(['season', 'team']):
            if pd.isna(team):
                continue
            
            # Get depth chart for the team
            team_depth = depth_charts[(depth_charts['season'] == season) & (depth_charts['team'] == team)]
            
            stats = {
                'season': season,
                'team': team,
                'total_injuries': len(injury_group),
                'key_player_injuries': 0,
                'injury_games_lost': 0,
            }
            
            # Count key position injuries
            key_positions = ['QB', 'RB', 'WR', 'TE', 'OL', 'DL', 'LB', 'DB']
            for pos in key_positions:
                pos_injuries = injury_group[injury_group['position'] == pos]
                if not pos_injuries.empty:
                    # Check if injured players are starters
                    starters = team_depth[team_depth['position'] == pos]
                    for _, injury in pos_injuries.iterrows():
                        if not starters.empty and injury['player_id'] in starters['player_id'].values:
                            stats['key_player_injuries'] += 1
                            stats['injury_games_lost'] += injury.get('games_missed', 0)
            
            # Calculate injury impact metrics
            stats['injury_rate'] = stats['total_injuries'] / max(len(team_depth), 1)
            stats['key_injury_rate'] = stats['key_player_injuries'] / max(len(team_depth[team_depth['position'].isin(key_positions)]), 1)
            
            injury_impact.append(stats)
        
        injury_df = pd.DataFrame(injury_impact)
        logger.info(f"Extracted injury impact for {len(injury_df)} team-seasons")
        return injury_df
    
    def create_matchup_features(self, offense_stats: pd.DataFrame, defense_stats: pd.DataFrame) -> pd.DataFrame:
        """Create matchup features comparing offense vs defense rankings."""
        logger.info("Creating matchup features...")
        
        if offense_stats.empty or defense_stats.empty:
            return pd.DataFrame()
        
        # Calculate team rankings for various metrics
        ranking_cols = [
            'yards_per_play', 'first_down_rate', 'turnover_rate',
            'third_down_rate', 'redzone_td_rate', 'passing_yards_per_game',
            'rushing_yards_per_game', 'touchdowns_per_game'
        ]
        
        offense_rankings = offense_stats.copy()
        defense_rankings = defense_stats.copy()
        
        for col in ranking_cols:
            if col in offense_rankings.columns:
                offense_rankings[f'{col}_rank'] = offense_rankings.groupby('season')[col].rank(ascending=False)
            if col in defense_rankings.columns:
                defense_rankings[f'{col}_rank'] = defense_rankings.groupby('season')[col].rank(ascending=True)  # Lower is better for defense
        
        # Merge offense and defense rankings
        matchup_features = offense_rankings.merge(
            defense_rankings,
            on=['season', 'team'],
            suffixes=('_off', '_def')
        )
        
        # Create matchup advantage features
        matchup_cols = []
        for col in ranking_cols:
            off_col = f'{col}_rank_off'
            def_col = f'{col}_rank_def'
            if off_col in matchup_features.columns and def_col in matchup_features.columns:
                matchup_features[f'{col}_matchup_adv'] = matchup_features[def_col] - matchup_features[off_col]
                matchup_cols.append(f'{col}_matchup_adv')
        
        logger.info(f"Created matchup features for {len(matchup_features)} team-seasons")
        return matchup_features[matchup_cols + ['season', 'team']]
    
    def extract_team_tendencies(self, pbp_data: pd.DataFrame) -> pd.DataFrame:
        """Extract team tendencies and play-calling patterns."""
        logger.info("Extracting team tendencies...")
        
        if pbp_data.empty:
            return pd.DataFrame()
        
        tendencies = []
        
        for (season, team), group in pbp_data.groupby(['season', 'week', 'posteam']):
            if pd.isna(team):
                continue
            
            # Play type tendencies
            total_plays = len(group)
            pass_plays = len(group[group['play_type'] == 'pass'])
            run_plays = len(group[group['play_type'] == 'run'])
            
            # Down and distance tendencies
            first_down_passes = len(group[(group['down'] == 1) & (group['play_type'] == 'pass')])
            first_down_runs = len(group[(group['down'] == 1) & (group['play_type'] == 'run')])
            
            # Formation tendencies
            shotgun_plays = len(group[group['shotgun'] == 1])
            no_huddle = len(group[group['no_huddle'] == 1])
            
            # Situational tendencies
            redzone_passes = len(group[(group['yardline_100'] <= 20) & (group['play_type'] == 'pass')])
            redzone_runs = len(group[(group['yardline_100'] <= 20) & (group['play_type'] == 'run')])
            
            stats = {
                'season': season,
                'week': week,
                'team': team,
                'games_played': 1,
                
                # Basic tendencies
                'pass_rate': pass_plays / max(total_plays, 1),
                'run_rate': run_plays / max(total_plays, 1),
                'shotgun_rate': shotgun_plays / max(total_plays, 1),
                'no_huddle_rate': no_huddle / max(total_plays, 1),
                
                # First down tendencies
                'first_down_pass_rate': first_down_passes / max(first_down_passes + first_down_runs, 1),
                
                # Red zone tendencies
                'redzone_pass_rate': redzone_passes / max(redzone_passes + redzone_runs, 1),
            }
            
            tendencies.append(stats)
        
        tendencies_df = pd.DataFrame(tendencies)
        
        # Aggregate by team and season
        season_tendencies = tendencies_df.groupby(['season', 'team']).agg({
            'games_played': 'sum',
            'pass_rate': 'mean',
            'run_rate': 'mean',
            'shotgun_rate': 'mean',
            'no_huddle_rate': 'mean',
            'first_down_pass_rate': 'mean',
            'redzone_pass_rate': 'mean'
        }).reset_index()
        
        logger.info(f"Extracted tendencies for {len(season_tendencies)} team-seasons")
        return season_tendencies
    
    def create_comprehensive_features(self, schedules: pd.DataFrame, pbp_data: pd.DataFrame, 
                                    player_stats: pd.DataFrame, rosters: pd.DataFrame,
                                    injuries: pd.DataFrame, depth_charts: pd.DataFrame) -> pd.DataFrame:
        """Create comprehensive game features combining all data sources."""
        logger.info("Creating comprehensive game features...")
        
        # Clean schedule data
        clean_schedules = self.clean_schedule_data(schedules)
        
        # Extract all feature sets
        situational_stats = self.extract_situational_stats(pbp_data)
        player_stats_agg = self.extract_player_stats(player_stats, rosters)
        injury_impact = self.extract_injury_impact(injuries, depth_charts)
        tendencies = self.extract_team_tendencies(pbp_data)
        
        # Create offense and defense stats
        offense_stats = self.extract_team_stats_from_pbp(pbp_data, side='offense')
        defense_stats = self.extract_team_stats_from_pbp(pbp_data, side='defense')
        
        # Create matchup features
        matchup_features = self.create_matchup_features(offense_stats, defense_stats)
        
        # Combine all features
        game_features = []
        
        for _, game in clean_schedules.iterrows():
            season = game['season']
            home_team = game['home_team']
            away_team = game['away_team']
            
            # Get all feature sets for both teams
            home_features = self._get_team_features(season, home_team, {
                'situational': situational_stats,
                'player': player_stats_agg,
                'injury': injury_impact,
                'tendencies': tendencies,
                'offense': offense_stats,
                'defense': defense_stats,
                'matchup': matchup_features
            })
            
            away_features = self._get_team_features(season, away_team, {
                'situational': situational_stats,
                'player': player_stats_agg,
                'injury': injury_impact,
                'tendencies': tendencies,
                'offense': offense_stats,
                'defense': defense_stats,
                'matchup': matchup_features
            })
            
            if home_features is None or away_features is None:
                continue
            
            # Create comprehensive feature row
            features = {
                'season': season,
                'week': game['week'],
                'home_team': home_team,
                'away_team': away_team,
                'home_score': game['home_score'],
                'away_score': game['away_score'],
                'home_win': game['home_win'],
            }
            
            # Add home team features
            for key, value in home_features.items():
                features[f'home_{key}'] = value
            
            # Add away team features
            for key, value in away_features.items():
                features[f'away_{key}'] = value
            
            # Add matchup differential features
            for key in home_features.keys():
                if key in away_features:
                    features[f'{key}_diff'] = home_features[key] - away_features[key]
            
            game_features.append(features)
        
        features_df = pd.DataFrame(game_features)
        logger.info(f"Created comprehensive features for {len(features_df)} games")
        
        return features_df
    
    def _get_team_features(self, season: int, team: str, feature_sets: Dict) -> Optional[Dict]:
        """Get all features for a specific team and season."""
        team_features = {}
        
        for feature_type, df in feature_sets.items():
            if df.empty:
                continue
            
            team_data = df[(df['season'] == season) & (df['team'] == team)]
            if team_data.empty:
                continue
            
            team_data = team_data.iloc[0]
            
            # Add all numeric columns as features
            for col in team_data.index:
                if col not in ['season', 'team'] and pd.api.types.is_numeric_dtype(team_data[col]):
                    team_features[f'{feature_type}_{col}'] = team_data[col]
        
        return team_features if team_features else None
    
    def clean_schedule_data(self, schedules: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare schedule data."""
        logger.info("Cleaning schedule data...")
        
        df = schedules.copy()
        
        # Convert date columns
        if 'gameday' in df.columns:
            df['gameday'] = pd.to_datetime(df['gameday'])
        
        # Filter out games without results
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
    
    def extract_team_stats_from_pbp(self, pbp_data: pd.DataFrame, side: str = 'offense') -> pd.DataFrame:
        """Extract team-level statistics from play-by-play data."""
        logger.info(f"Extracting {side} team statistics...")
        
        if pbp_data.empty:
            return pd.DataFrame()
        
        team_stats = []
        
        if side == 'offense':
            group_cols = ['season', 'week', 'posteam']
            team_col = 'posteam'
        else:  # defense
            group_cols = ['season', 'week', 'defteam']
            team_col = 'defteam'
        
        for group_key, group in pbp_data.groupby(group_cols):
            season, week, team = group_key
            if pd.isna(team):
                continue
            
            stats = {
                'season': season,
                'week': week,
                'team': team,
                'games_played': 1,
                'total_plays': len(group),
                'total_yards': group['yards_gained'].sum(),
                'first_downs': len(group[group['first_down'] == 1]),
                'touchdowns': len(group[group['touchdown'] == 1]),
                'turnovers': len(group[group['interception'] == 1]) + len(group[group['fumble_lost'] == 1]),
            }
            
            # Calculate rates
            if stats['total_plays'] > 0:
                stats['yards_per_play'] = stats['total_yards'] / stats['total_plays']
                stats['first_down_rate'] = stats['first_downs'] / stats['total_plays']
                stats['turnover_rate'] = stats['turnovers'] / stats['total_plays']
            else:
                stats.update({'yards_per_play': 0, 'first_down_rate': 0, 'turnover_rate': 0})
            
            team_stats.append(stats)
        
        team_stats_df = pd.DataFrame(team_stats)
        
        # Aggregate by team and season
        season_stats = team_stats_df.groupby(['season', 'team']).agg({
            'games_played': 'sum',
            'total_plays': 'sum',
            'total_yards': 'sum',
            'first_downs': 'sum',
            'touchdowns': 'sum',
            'turnovers': 'sum',
            'yards_per_play': 'mean',
            'first_down_rate': 'mean',
            'turnover_rate': 'mean'
        }).reset_index()
        
        logger.info(f"Extracted {side} statistics for {len(season_stats)} team-seasons")
        return season_stats
    
    def prepare_ml_data(self, game_features: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare data for machine learning."""
        logger.info("Preparing data for machine learning...")
        
        # Select feature columns
        exclude_cols = ['season', 'week', 'home_team', 'away_team', 'home_score', 'away_score', 'home_win']
        feature_cols = [col for col in game_features.columns if col not in exclude_cols]
        
        X = game_features[feature_cols].copy()
        y = game_features['home_win'].copy()
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        # Store feature columns
        self.feature_columns = feature_cols
        self.target_column = 'home_win'
        
        logger.info(f"Prepared ML data: {X.shape[0]} samples, {X.shape[1]} features")
        return X, y






