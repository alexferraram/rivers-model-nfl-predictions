"""
Fantasy Football Enhanced Preprocessing Module

This module handles advanced feature engineering incorporating:
- Fantasy football data and player valuations
- Expected vs actual performance metrics
- Opportunity-based statistics
- Efficiency metrics and advanced analytics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class FantasyEnhancedPreprocessor:
    """Enhanced preprocessing incorporating fantasy football and efficiency metrics."""
    
    def __init__(self):
        self.feature_columns = []
        self.target_column = None
        self.fantasy_positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DST']
    
    def extract_fantasy_team_strength(self, fantasy_data: pd.DataFrame, rosters: pd.DataFrame) -> pd.DataFrame:
        """Extract team-level fantasy football strength metrics."""
        logger.info("Extracting fantasy team strength metrics...")
        
        if fantasy_data.empty or rosters.empty:
            return pd.DataFrame()
        
        # Merge fantasy data with roster data to get team and position
        fantasy_with_teams = fantasy_data.merge(
            rosters[['player_id', 'position', 'team']], 
            on='player_id', 
            how='left'
        )
        
        team_fantasy_stats = []
        
        for (season, team), group in fantasy_with_teams.groupby(['season', 'team']):
            if pd.isna(team):
                continue
            
            stats = {
                'season': season,
                'team': team,
                'games_played': group['games'].sum() if 'games' in group.columns else 0,
            }
            
            # Position-specific fantasy metrics
            for pos in self.fantasy_positions:
                pos_players = group[group['position'] == pos]
                if not pos_players.empty:
                    # Fantasy points
                    if 'fantasy_points' in pos_players.columns:
                        stats[f'{pos.lower()}_fantasy_points'] = pos_players['fantasy_points'].sum()
                        stats[f'{pos.lower()}_fantasy_points_per_game'] = pos_players['fantasy_points'].sum() / max(stats['games_played'], 1)
                    
                    # Expected fantasy points
                    if 'expected_fantasy_points' in pos_players.columns:
                        stats[f'{pos.lower()}_expected_fantasy_points'] = pos_players['expected_fantasy_points'].sum()
                        stats[f'{pos.lower()}_fantasy_efficiency'] = (
                            pos_players['fantasy_points'].sum() / 
                            max(pos_players['expected_fantasy_points'].sum(), 1)
                        )
                    
                    # Opportunity metrics
                    if 'targets' in pos_players.columns:
                        stats[f'{pos.lower()}_targets'] = pos_players['targets'].sum()
                    if 'carries' in pos_players.columns:
                        stats[f'{pos.lower()}_carries'] = pos_players['carries'].sum()
                    if 'snap_share' in pos_players.columns:
                        stats[f'{pos.lower()}_snap_share'] = pos_players['snap_share'].mean()
            
            # Overall team fantasy metrics
            if 'fantasy_points' in group.columns:
                stats['total_fantasy_points'] = group['fantasy_points'].sum()
                stats['fantasy_points_per_game'] = stats['total_fantasy_points'] / max(stats['games_played'], 1)
            
            if 'expected_fantasy_points' in group.columns:
                stats['total_expected_fantasy_points'] = group['expected_fantasy_points'].sum()
                stats['team_fantasy_efficiency'] = (
                    stats['total_fantasy_points'] / 
                    max(stats['total_expected_fantasy_points'], 1)
                )
            
            # Fantasy consistency metrics
            if 'fantasy_points' in group.columns:
                player_fantasy_points = group.groupby('player_id')['fantasy_points'].sum()
                stats['fantasy_consistency'] = 1 - (player_fantasy_points.std() / max(player_fantasy_points.mean(), 1))
            
            team_fantasy_stats.append(stats)
        
        fantasy_stats_df = pd.DataFrame(team_fantasy_stats)
        logger.info(f"Extracted fantasy team strength for {len(fantasy_stats_df)} team-seasons")
        return fantasy_stats_df
    
    def extract_opportunity_metrics(self, opportunity_data: pd.DataFrame, rosters: pd.DataFrame) -> pd.DataFrame:
        """Extract opportunity-based performance metrics."""
        logger.info("Extracting opportunity-based metrics...")
        
        if opportunity_data.empty or rosters.empty:
            return pd.DataFrame()
        
        # Merge opportunity data with roster data
        opportunity_with_teams = opportunity_data.merge(
            rosters[['player_id', 'position', 'team']], 
            on='player_id', 
            how='left'
        )
        
        team_opportunity_stats = []
        
        for (season, team), group in opportunity_with_teams.groupby(['season', 'team']):
            if pd.isna(team):
                continue
            
            stats = {
                'season': season,
                'team': team,
                'games_played': group['games'].sum() if 'games' in group.columns else 0,
            }
            
            # Expected vs actual performance
            if 'expected_yards' in group.columns and 'actual_yards' in group.columns:
                stats['total_expected_yards'] = group['expected_yards'].sum()
                stats['total_actual_yards'] = group['actual_yards'].sum()
                stats['yards_over_expected'] = stats['total_actual_yards'] - stats['total_expected_yards']
                stats['yards_efficiency'] = stats['total_actual_yards'] / max(stats['total_expected_yards'], 1)
            
            # Opportunity share metrics
            if 'target_share' in group.columns:
                stats['avg_target_share'] = group['target_share'].mean()
                stats['max_target_share'] = group['target_share'].max()
            
            if 'air_yards_share' in group.columns:
                stats['avg_air_yards_share'] = group['air_yards_share'].mean()
                stats['max_air_yards_share'] = group['air_yards_share'].max()
            
            if 'carry_share' in group.columns:
                stats['avg_carry_share'] = group['carry_share'].mean()
                stats['max_carry_share'] = group['carry_share'].max()
            
            # Red zone opportunities
            if 'red_zone_targets' in group.columns:
                stats['red_zone_targets'] = group['red_zone_targets'].sum()
            if 'red_zone_carries' in group.columns:
                stats['red_zone_carries'] = group['red_zone_carries'].sum()
            
            # High-value touches
            if 'high_value_touches' in group.columns:
                stats['high_value_touches'] = group['high_value_touches'].sum()
                stats['high_value_touch_rate'] = stats['high_value_touches'] / max(group['targets'].sum() + group['carries'].sum(), 1)
            
            team_opportunity_stats.append(stats)
        
        opportunity_stats_df = pd.DataFrame(team_opportunity_stats)
        logger.info(f"Extracted opportunity metrics for {len(opportunity_stats_df)} team-seasons")
        return opportunity_stats_df
    
    def extract_efficiency_metrics(self, efficiency_data: pd.DataFrame, rosters: pd.DataFrame) -> pd.DataFrame:
        """Extract advanced efficiency and analytics metrics."""
        logger.info("Extracting efficiency and analytics metrics...")
        
        if efficiency_data.empty or rosters.empty:
            return pd.DataFrame()
        
        # Merge efficiency data with roster data
        efficiency_with_teams = efficiency_data.merge(
            rosters[['player_id', 'position', 'team']], 
            on='player_id', 
            how='left'
        )
        
        team_efficiency_stats = []
        
        for (season, team), group in efficiency_with_teams.groupby(['season', 'team']):
            if pd.isna(team):
                continue
            
            stats = {
                'season': season,
                'team': team,
                'games_played': group['games'].sum() if 'games' in group.columns else 0,
            }
            
            # Advanced efficiency metrics
            if 'yards_per_target' in group.columns:
                stats['avg_yards_per_target'] = group['yards_per_target'].mean()
                stats['weighted_yards_per_target'] = (
                    group['yards_per_target'] * group['targets']
                ).sum() / max(group['targets'].sum(), 1)
            
            if 'yards_per_carry' in group.columns:
                stats['avg_yards_per_carry'] = group['yards_per_carry'].mean()
                stats['weighted_yards_per_carry'] = (
                    group['yards_per_carry'] * group['carries']
                ).sum() / max(group['carries'].sum(), 1)
            
            # Success rate metrics
            if 'success_rate' in group.columns:
                stats['avg_success_rate'] = group['success_rate'].mean()
                stats['weighted_success_rate'] = (
                    group['success_rate'] * (group['targets'].fillna(0) + group['carries'].fillna(0))
                ).sum() / max((group['targets'].fillna(0) + group['carries'].fillna(0)).sum(), 1)
            
            # Explosive play metrics
            if 'explosive_plays' in group.columns:
                stats['explosive_plays'] = group['explosive_plays'].sum()
                stats['explosive_play_rate'] = stats['explosive_plays'] / max(group['targets'].sum() + group['carries'].sum(), 1)
            
            # Route running efficiency
            if 'route_efficiency' in group.columns:
                stats['avg_route_efficiency'] = group['route_efficiency'].mean()
            
            # Pass blocking efficiency
            if 'pass_block_efficiency' in group.columns:
                stats['avg_pass_block_efficiency'] = group['pass_block_efficiency'].mean()
            
            # Run blocking efficiency
            if 'run_block_efficiency' in group.columns:
                stats['avg_run_block_efficiency'] = group['run_block_efficiency'].mean()
            
            # Defensive efficiency metrics
            defensive_players = group[group['position'].isin(['DL', 'LB', 'DB'])]
            if not defensive_players.empty:
                if 'tackle_efficiency' in defensive_players.columns:
                    stats['avg_tackle_efficiency'] = defensive_players['tackle_efficiency'].mean()
                if 'pass_rush_efficiency' in defensive_players.columns:
                    stats['avg_pass_rush_efficiency'] = defensive_players['pass_rush_efficiency'].mean()
                if 'coverage_efficiency' in defensive_players.columns:
                    stats['avg_coverage_efficiency'] = defensive_players['coverage_efficiency'].mean()
            
            team_efficiency_stats.append(stats)
        
        efficiency_stats_df = pd.DataFrame(team_efficiency_stats)
        logger.info(f"Extracted efficiency metrics for {len(efficiency_stats_df)} team-seasons")
        return efficiency_stats_df
    
    def create_fantasy_matchup_features(self, home_fantasy: pd.DataFrame, away_fantasy: pd.DataFrame) -> pd.DataFrame:
        """Create fantasy-based matchup features."""
        logger.info("Creating fantasy-based matchup features...")
        
        if home_fantasy.empty or away_fantasy.empty:
            return pd.DataFrame()
        
        # Calculate fantasy rankings
        fantasy_ranking_cols = [
            'total_fantasy_points', 'fantasy_points_per_game', 'team_fantasy_efficiency',
            'qb_fantasy_points_per_game', 'rb_fantasy_points_per_game', 
            'wr_fantasy_points_per_game', 'te_fantasy_points_per_game'
        ]
        
        home_rankings = home_fantasy.copy()
        away_rankings = away_fantasy.copy()
        
        for col in fantasy_ranking_cols:
            if col in home_rankings.columns:
                home_rankings[f'{col}_rank'] = home_rankings.groupby('season')[col].rank(ascending=False)
            if col in away_rankings.columns:
                away_rankings[f'{col}_rank'] = away_rankings.groupby('season')[col].rank(ascending=False)
        
        # Merge rankings
        matchup_features = home_rankings.merge(
            away_rankings,
            on=['season', 'team'],
            suffixes=('_home', '_away')
        )
        
        # Create matchup advantage features
        matchup_cols = []
        for col in fantasy_ranking_cols:
            home_col = f'{col}_rank_home'
            away_col = f'{col}_rank_away'
            if home_col in matchup_features.columns and away_col in matchup_features.columns:
                matchup_features[f'{col}_matchup_adv'] = matchup_features[away_col] - matchup_features[home_col]
                matchup_cols.append(f'{col}_matchup_adv')
        
        logger.info(f"Created fantasy matchup features for {len(matchup_features)} team-seasons")
        return matchup_features[matchup_cols + ['season', 'team']]
    
    def create_comprehensive_fantasy_features(self, schedules: pd.DataFrame, pbp_data: pd.DataFrame,
                                            player_stats: pd.DataFrame, rosters: pd.DataFrame,
                                            injuries: pd.DataFrame, depth_charts: pd.DataFrame,
                                            fantasy_data: pd.DataFrame, opportunity_data: pd.DataFrame,
                                            efficiency_data: pd.DataFrame) -> pd.DataFrame:
        """Create comprehensive game features incorporating fantasy and efficiency data."""
        logger.info("Creating comprehensive fantasy-enhanced game features...")
        
        # Import the advanced preprocessor for base features
        from advanced_preprocessor import AdvancedNFLPreprocessor
        base_preprocessor = AdvancedNFLPreprocessor()
        
        # Clean schedule data
        clean_schedules = base_preprocessor.clean_schedule_data(schedules)
        
        # Extract base features
        situational_stats = base_preprocessor.extract_situational_stats(pbp_data)
        player_stats_agg = base_preprocessor.extract_player_stats(player_stats, rosters)
        injury_impact = base_preprocessor.extract_injury_impact(injuries, depth_charts)
        tendencies = base_preprocessor.extract_team_tendencies(pbp_data)
        offense_stats = base_preprocessor.extract_team_stats_from_pbp(pbp_data, side='offense')
        defense_stats = base_preprocessor.extract_team_stats_from_pbp(pbp_data, side='defense')
        
        # Extract fantasy and efficiency features
        fantasy_team_strength = self.extract_fantasy_team_strength(fantasy_data, rosters)
        opportunity_metrics = self.extract_opportunity_metrics(opportunity_data, rosters)
        efficiency_metrics = self.extract_efficiency_metrics(efficiency_data, rosters)
        
        # Create matchup features
        base_matchup_features = base_preprocessor.create_matchup_features(offense_stats, defense_stats)
        fantasy_matchup_features = self.create_fantasy_matchup_features(fantasy_team_strength, fantasy_team_strength)
        
        # Combine all features
        game_features = []
        
        for _, game in clean_schedules.iterrows():
            season = game['season']
            home_team = game['home_team']
            away_team = game['away_team']
            
            # Get all feature sets for both teams
            home_features = self._get_comprehensive_team_features(season, home_team, {
                'situational': situational_stats,
                'player': player_stats_agg,
                'injury': injury_impact,
                'tendencies': tendencies,
                'offense': offense_stats,
                'defense': defense_stats,
                'matchup': base_matchup_features,
                'fantasy': fantasy_team_strength,
                'opportunity': opportunity_metrics,
                'efficiency': efficiency_metrics,
                'fantasy_matchup': fantasy_matchup_features
            })
            
            away_features = self._get_comprehensive_team_features(season, away_team, {
                'situational': situational_stats,
                'player': player_stats_agg,
                'injury': injury_impact,
                'tendencies': tendencies,
                'offense': offense_stats,
                'defense': defense_stats,
                'matchup': base_matchup_features,
                'fantasy': fantasy_team_strength,
                'opportunity': opportunity_metrics,
                'efficiency': efficiency_metrics,
                'fantasy_matchup': fantasy_matchup_features
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
            
            # Add differential features
            for key in home_features.keys():
                if key in away_features:
                    features[f'{key}_diff'] = home_features[key] - away_features[key]
            
            game_features.append(features)
        
        features_df = pd.DataFrame(game_features)
        logger.info(f"Created comprehensive fantasy-enhanced features for {len(features_df)} games")
        
        return features_df
    
    def _get_comprehensive_team_features(self, season: int, team: str, feature_sets: Dict) -> Optional[Dict]:
        """Get all features for a specific team and season including fantasy data."""
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
    
    def prepare_ml_data(self, game_features: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare data for machine learning."""
        logger.info("Preparing fantasy-enhanced data for machine learning...")
        
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
        
        logger.info(f"Prepared fantasy-enhanced ML data: {X.shape[0]} samples, {X.shape[1]} features")
        return X, y






