#!/usr/bin/env python3
"""
Comprehensive Advanced Analytics System
Extracts and processes advanced analytics from play-by-play data.
"""

import pandas as pd
import numpy as np
import nfl_data_py as nfl
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedAnalyticsSystem:
    """Comprehensive advanced analytics system using PBP data"""
    
    def __init__(self, seasons: List[int] = None):
        """Initialize advanced analytics system"""
        if seasons is None:
            seasons = [datetime.now().year]
        
        self.seasons = seasons
        self.pbp_data = None
        self.analytics_cache = {}
        self.load_data()
    
    def load_data(self):
        """Load play-by-play data"""
        logger.info(f"Loading PBP data for seasons: {self.seasons}")
        try:
            self.pbp_data = nfl.import_pbp_data(self.seasons)
            logger.info(f"✅ Loaded {len(self.pbp_data):,} plays")
            
            # Analyze advanced analytics completeness
            self._analyze_analytics_completeness()
            
        except Exception as e:
            logger.error(f"Error loading PBP data: {e}")
            self.pbp_data = None
    
    def _analyze_analytics_completeness(self):
        """Analyze completeness of advanced analytics data in PBP"""
        if self.pbp_data is None:
            return
        
        logger.info("📊 Analyzing advanced analytics completeness...")
        
        # EPA data analysis
        epa_data = self.pbp_data['epa'].notna().sum()
        logger.info(f"EPA data: {epa_data:,}/{len(self.pbp_data):,} plays ({epa_data/len(self.pbp_data)*100:.1f}%)")
        
        # WPA data analysis
        wpa_data = self.pbp_data['wpa'].notna().sum()
        logger.info(f"WPA data: {wpa_data:,}/{len(self.pbp_data):,} plays ({wpa_data/len(self.pbp_data)*100:.1f}%)")
        
        # Success rate data analysis
        success_data = self.pbp_data['success'].notna().sum()
        logger.info(f"Success rate data: {success_data:,}/{len(self.pbp_data):,} plays ({success_data/len(self.pbp_data)*100:.1f}%)")
        
        # QB EPA data analysis
        qb_epa_data = self.pbp_data['qb_epa'].notna().sum()
        logger.info(f"QB EPA data: {qb_epa_data:,}/{len(self.pbp_data):,} plays ({qb_epa_data/len(self.pbp_data)*100:.1f}%)")
    
    def get_player_epa_stats(self, player_name: str, team: str = None, week: int = None) -> Dict:
        """Get comprehensive EPA statistics for a player"""
        if self.pbp_data is None:
            return {}
        
        # Filter data for player
        player_data = self.pbp_data[
            (self.pbp_data['passer_player_name'] == player_name) |
            (self.pbp_data['rusher_player_name'] == player_name) |
            (self.pbp_data['receiver_player_name'] == player_name)
        ].copy()
        
        if team:
            player_data = player_data[player_data['posteam'] == team]
        if week:
            player_data = player_data[player_data['week'] == week]
        
        if player_data.empty:
            logger.warning(f"No EPA data found for {player_name}")
            return {}
        
        # Calculate EPA statistics
        epa_stats = {
            'player_name': player_name,
            'team': team or player_data['posteam'].iloc[0] if not player_data.empty else None,
            'week': week,
            'games_played': player_data['game_id'].nunique(),
            'total_plays': len(player_data),
            'total_epa': player_data['epa'].sum(),
            'avg_epa_per_play': player_data['epa'].mean(),
            'epa_per_game': player_data.groupby('game_id')['epa'].sum().mean(),
            'positive_epa_plays': len(player_data[player_data['epa'] > 0]),
            'negative_epa_plays': len(player_data[player_data['epa'] < 0]),
            'epa_efficiency': len(player_data[player_data['epa'] > 0]) / len(player_data),
            'max_single_play_epa': player_data['epa'].max(),
            'min_single_play_epa': player_data['epa'].min(),
            'epa_std': player_data['epa'].std(),
            'qb_epa': player_data['qb_epa'].sum() if 'qb_epa' in player_data.columns else 0,
            'air_epa': player_data['air_epa'].sum() if 'air_epa' in player_data.columns else 0,
            'yac_epa': player_data['yac_epa'].sum() if 'yac_epa' in player_data.columns else 0,
        }
        
        # Fill NaN values
        for key, value in epa_stats.items():
            if pd.isna(value):
                epa_stats[key] = 0
        
        logger.info(f"📊 {player_name} EPA stats: {epa_stats['total_epa']:.2f} total EPA, {epa_stats['avg_epa_per_play']:.3f} avg EPA/play")
        return epa_stats
    
    def get_player_wpa_stats(self, player_name: str, team: str = None, week: int = None) -> Dict:
        """Get comprehensive WPA statistics for a player"""
        if self.pbp_data is None:
            return {}
        
        # Filter data for player
        player_data = self.pbp_data[
            (self.pbp_data['passer_player_name'] == player_name) |
            (self.pbp_data['rusher_player_name'] == player_name) |
            (self.pbp_data['receiver_player_name'] == player_name)
        ].copy()
        
        if team:
            player_data = player_data[player_data['posteam'] == team]
        if week:
            player_data = player_data[player_data['week'] == week]
        
        if player_data.empty:
            logger.warning(f"No WPA data found for {player_name}")
            return {}
        
        # Calculate WPA statistics
        wpa_stats = {
            'player_name': player_name,
            'team': team or player_data['posteam'].iloc[0] if not player_data.empty else None,
            'week': week,
            'games_played': player_data['game_id'].nunique(),
            'total_plays': len(player_data),
            'total_wpa': player_data['wpa'].sum(),
            'avg_wpa_per_play': player_data['wpa'].mean(),
            'wpa_per_game': player_data.groupby('game_id')['wpa'].sum().mean(),
            'positive_wpa_plays': len(player_data[player_data['wpa'] > 0]),
            'negative_wpa_plays': len(player_data[player_data['wpa'] < 0]),
            'wpa_efficiency': len(player_data[player_data['wpa'] > 0]) / len(player_data),
            'max_single_play_wpa': player_data['wpa'].max(),
            'min_single_play_wpa': player_data['wpa'].min(),
            'wpa_std': player_data['wpa'].std(),
            'clutch_factor': self._calculate_clutch_factor(player_data),
        }
        
        # Fill NaN values
        for key, value in wpa_stats.items():
            if pd.isna(value):
                wpa_stats[key] = 0
        
        logger.info(f"📊 {player_name} WPA stats: {wpa_stats['total_wpa']:.3f} total WPA, {wpa_stats['avg_wpa_per_play']:.4f} avg WPA/play")
        return wpa_stats
    
    def get_player_success_rate(self, player_name: str, team: str = None, week: int = None) -> Dict:
        """Get comprehensive success rate statistics for a player"""
        if self.pbp_data is None:
            return {}
        
        # Filter data for player
        player_data = self.pbp_data[
            (self.pbp_data['passer_player_name'] == player_name) |
            (self.pbp_data['rusher_player_name'] == player_name) |
            (self.pbp_data['receiver_player_name'] == player_name)
        ].copy()
        
        if team:
            player_data = player_data[player_data['posteam'] == team]
        if week:
            player_data = player_data[player_data['week'] == week]
        
        if player_data.empty:
            logger.warning(f"No success rate data found for {player_name}")
            return {}
        
        # Calculate success rate statistics
        success_stats = {
            'player_name': player_name,
            'team': team or player_data['posteam'].iloc[0] if not player_data.empty else None,
            'week': week,
            'games_played': player_data['game_id'].nunique(),
            'total_plays': len(player_data),
            'successful_plays': player_data['success'].sum(),
            'success_rate': player_data['success'].mean(),
            'success_rate_per_game': player_data.groupby('game_id')['success'].mean().mean(),
            'consistency_score': self._calculate_consistency_score(player_data),
            'situational_success': self._calculate_situational_success(player_data),
        }
        
        # Fill NaN values
        for key, value in success_stats.items():
            if pd.isna(value):
                success_stats[key] = 0
        
        logger.info(f"📊 {player_name} success rate: {success_stats['success_rate']:.1%} ({success_stats['successful_plays']}/{success_stats['total_plays']})")
        return success_stats
    
    def get_team_advanced_analytics(self, team: str, week: int = None) -> Dict:
        """Get comprehensive advanced analytics for a team"""
        logger.info(f"📊 Getting advanced analytics for {team}")
        
        if self.pbp_data is None:
            return {}
        
        # Filter data for team
        team_data = self.pbp_data[self.pbp_data['posteam'] == team].copy()
        
        if week:
            team_data = team_data[team_data['week'] == week]
        
        if team_data.empty:
            logger.warning(f"No data found for {team}")
            return {}
        
        # Calculate team advanced analytics
        team_analytics = {
            'team': team,
            'week': week,
            'games_played': team_data['game_id'].nunique(),
            'total_plays': len(team_data),
            
            # EPA Analytics
            'total_epa': team_data['epa'].sum(),
            'avg_epa_per_play': team_data['epa'].mean(),
            'epa_per_game': team_data.groupby('game_id')['epa'].sum().mean(),
            'epa_efficiency': len(team_data[team_data['epa'] > 0]) / len(team_data),
            
            # WPA Analytics
            'total_wpa': team_data['wpa'].sum(),
            'avg_wpa_per_play': team_data['wpa'].mean(),
            'wpa_per_game': team_data.groupby('game_id')['wpa'].sum().mean(),
            'wpa_efficiency': len(team_data[team_data['wpa'] > 0]) / len(team_data),
            
            # Success Rate Analytics
            'total_successful_plays': team_data['success'].sum(),
            'success_rate': team_data['success'].mean(),
            'success_rate_per_game': team_data.groupby('game_id')['success'].mean().mean(),
            
            # Situational Analytics
            'situational_analytics': self._calculate_team_situational_analytics(team_data),
            
            # Efficiency Metrics
            'efficiency_metrics': self._calculate_team_efficiency_metrics(team_data),
        }
        
        # Fill NaN values
        for key, value in team_analytics.items():
            if pd.isna(value):
                team_analytics[key] = 0
        
        logger.info(f"📊 {team} advanced analytics: {team_analytics['total_epa']:.2f} EPA, {team_analytics['success_rate']:.1%} success rate")
        return team_analytics
    
    def get_game_advanced_analytics(self, game_id: str) -> Dict:
        """Get comprehensive advanced analytics for a specific game"""
        if self.pbp_data is None:
            return {}
        
        # Get game data
        game_data = self.pbp_data[self.pbp_data['game_id'] == game_id]
        
        if game_data.empty:
            logger.warning(f"No data found for game {game_id}")
            return {}
        
        # Get home and away teams
        home_team = game_data['home_team'].iloc[0]
        away_team = game_data['away_team'].iloc[0]
        
        # Calculate game advanced analytics
        game_analytics = {
            'game_id': game_id,
            'home_team': home_team,
            'away_team': away_team,
            
            # Overall Game Analytics
            'total_plays': len(game_data),
            'total_epa': game_data['epa'].sum(),
            'total_wpa': game_data['wpa'].sum(),
            'avg_success_rate': game_data['success'].mean(),
            
            # Home Team Analytics
            'home_epa': game_data[game_data['posteam'] == home_team]['epa'].sum(),
            'home_wpa': game_data[game_data['posteam'] == home_team]['wpa'].sum(),
            'home_success_rate': game_data[game_data['posteam'] == home_team]['success'].mean(),
            
            # Away Team Analytics
            'away_epa': game_data[game_data['posteam'] == away_team]['epa'].sum(),
            'away_wpa': game_data[game_data['posteam'] == away_team]['wpa'].sum(),
            'away_success_rate': game_data[game_data['posteam'] == away_team]['success'].mean(),
            
            # Game Flow Analytics
            'game_flow': self._analyze_game_flow(game_data),
            
            # Momentum Analytics
            'momentum_shifts': self._analyze_momentum_shifts(game_data),
        }
        
        # Calculate EPA and WPA differentials
        game_analytics['epa_differential'] = game_analytics['home_epa'] - game_analytics['away_epa']
        game_analytics['wpa_differential'] = game_analytics['home_wpa'] - game_analytics['away_wpa']
        
        logger.info(f"📊 {game_id}: Home EPA {game_analytics['home_epa']:.2f}, Away EPA {game_analytics['away_epa']:.2f}")
        return game_analytics
    
    def get_advanced_analytics_leaders(self, metric: str, position: str = None, limit: int = 10) -> List[Dict]:
        """Get leaders in advanced analytics metrics"""
        if self.pbp_data is None:
            return []
        
        logger.info(f"📊 Getting {metric} leaders")
        
        # Filter by position if specified
        if position == 'QB':
            player_data = self.pbp_data[self.pbp_data['passer_player_name'].notna()].copy()
            player_col = 'passer_player_name'
        elif position == 'RB':
            player_data = self.pbp_data[self.pbp_data['rusher_player_name'].notna()].copy()
            player_col = 'rusher_player_name'
        elif position == 'WR':
            player_data = self.pbp_data[self.pbp_data['receiver_player_name'].notna()].copy()
            player_col = 'receiver_player_name'
        else:
            # All players
            player_data = self.pbp_data[
                (self.pbp_data['passer_player_name'].notna()) |
                (self.pbp_data['rusher_player_name'].notna()) |
                (self.pbp_data['receiver_player_name'].notna())
            ].copy()
            player_col = 'passer_player_name'  # Default to passer for now
        
        # Group by player and calculate metrics
        if metric == 'epa':
            leaders = player_data.groupby(player_col).agg({
                'epa': ['sum', 'mean', 'count'],
                'posteam': 'first'
            }).round(3)
        elif metric == 'wpa':
            leaders = player_data.groupby(player_col).agg({
                'wpa': ['sum', 'mean', 'count'],
                'posteam': 'first'
            }).round(3)
        elif metric == 'success_rate':
            leaders = player_data.groupby(player_col).agg({
                'success': ['sum', 'mean', 'count'],
                'posteam': 'first'
            }).round(3)
        else:
            return []
        
        # Flatten column names
        leaders.columns = ['total', 'avg', 'plays', 'team']
        leaders = leaders[leaders['plays'] >= 10]  # Minimum 10 plays
        
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
    
    def _calculate_clutch_factor(self, player_data: pd.DataFrame) -> float:
        """Calculate clutch factor based on WPA in high-leverage situations"""
        if player_data.empty:
            return 0
        
        # Define high-leverage situations (high WPA plays)
        high_leverage = player_data[abs(player_data['wpa']) > 0.05]
        
        if len(high_leverage) == 0:
            return 0
        
        # Calculate average WPA in high-leverage situations
        clutch_wpa = high_leverage['wpa'].mean()
        return round(clutch_wpa, 4)
    
    def _calculate_consistency_score(self, player_data: pd.DataFrame) -> float:
        """Calculate consistency score based on success rate variance"""
        if player_data.empty:
            return 0
        
        # Calculate success rate by game
        game_success = player_data.groupby('game_id')['success'].mean()
        
        if len(game_success) <= 1:
            return 1.0
        
        # Consistency is inverse of variance
        consistency = 1 - game_success.std()
        return max(0, min(1, consistency))
    
    def _calculate_situational_success(self, player_data: pd.DataFrame) -> Dict:
        """Calculate success rate in different situations"""
        if player_data.empty:
            return {}
        
        situational = {}
        
        # Down-specific success rates
        for down in [1, 2, 3, 4]:
            down_data = player_data[player_data['down'] == down]
            if len(down_data) > 0:
                situational[f'down_{down}_success_rate'] = down_data['success'].mean()
        
        # Distance-specific success rates
        short_distance = player_data[player_data['ydstogo'] <= 3]
        medium_distance = player_data[(player_data['ydstogo'] > 3) & (player_data['ydstogo'] <= 7)]
        long_distance = player_data[player_data['ydstogo'] > 7]
        
        if len(short_distance) > 0:
            situational['short_distance_success_rate'] = short_distance['success'].mean()
        if len(medium_distance) > 0:
            situational['medium_distance_success_rate'] = medium_distance['success'].mean()
        if len(long_distance) > 0:
            situational['long_distance_success_rate'] = long_distance['success'].mean()
        
        return situational
    
    def _calculate_team_situational_analytics(self, team_data: pd.DataFrame) -> Dict:
        """Calculate team situational analytics"""
        if team_data.empty:
            return {}
        
        situational = {}
        
        # Red zone analytics
        red_zone = team_data[team_data['yardline_100'] <= 20]
        if len(red_zone) > 0:
            situational['red_zone_epa'] = red_zone['epa'].sum()
            situational['red_zone_success_rate'] = red_zone['success'].mean()
        
        # Third down analytics
        third_down = team_data[team_data['down'] == 3]
        if len(third_down) > 0:
            situational['third_down_epa'] = third_down['epa'].sum()
            situational['third_down_success_rate'] = third_down['success'].mean()
        
        # Two-minute drill analytics (using quarter_seconds_remaining <= 120)
        two_minute = team_data[team_data['quarter_seconds_remaining'] <= 120]
        if len(two_minute) > 0:
            situational['two_minute_epa'] = two_minute['epa'].sum()
            situational['two_minute_success_rate'] = two_minute['success'].mean()
        
        return situational
    
    def _calculate_team_efficiency_metrics(self, team_data: pd.DataFrame) -> Dict:
        """Calculate team efficiency metrics"""
        if team_data.empty:
            return {}
        
        efficiency = {}
        
        # EPA per play by play type
        pass_plays = team_data[team_data['play_type'] == 'pass']
        run_plays = team_data[team_data['play_type'] == 'run']
        
        if len(pass_plays) > 0:
            efficiency['pass_epa_per_play'] = pass_plays['epa'].mean()
            efficiency['pass_success_rate'] = pass_plays['success'].mean()
        
        if len(run_plays) > 0:
            efficiency['run_epa_per_play'] = run_plays['epa'].mean()
            efficiency['run_success_rate'] = run_plays['success'].mean()
        
        # Explosive play rate (EPA > 1.0)
        explosive_plays = team_data[team_data['epa'] > 1.0]
        efficiency['explosive_play_rate'] = len(explosive_plays) / len(team_data)
        
        # Negative play rate (EPA < -1.0)
        negative_plays = team_data[team_data['epa'] < -1.0]
        efficiency['negative_play_rate'] = len(negative_plays) / len(team_data)
        
        return efficiency
    
    def _analyze_game_flow(self, game_data: pd.DataFrame) -> Dict:
        """Analyze game flow and momentum"""
        if game_data.empty:
            return {}
        
        # Calculate EPA by quarter
        game_data['quarter'] = game_data['qtr']
        quarter_epa = game_data.groupby('quarter')['epa'].sum()
        
        # Calculate WPA by quarter
        quarter_wpa = game_data.groupby('quarter')['wpa'].sum()
        
        return {
            'quarter_epa': quarter_epa.to_dict(),
            'quarter_wpa': quarter_wpa.to_dict(),
            'momentum_trend': self._calculate_momentum_trend(quarter_epa)
        }
    
    def _analyze_momentum_shifts(self, game_data: pd.DataFrame) -> List[Dict]:
        """Analyze momentum shifts in the game"""
        if game_data.empty:
            return []
        
        # Find plays with significant WPA changes
        momentum_shifts = game_data[abs(game_data['wpa']) > 0.1].copy()
        
        shifts = []
        for _, play in momentum_shifts.iterrows():
            shifts.append({
                'play_id': play.get('play_id', ''),
                'quarter': play.get('qtr', ''),
                'time': play.get('time', ''),
                'wpa_change': play['wpa'],
                'description': play.get('desc', '')
            })
        
        return shifts
    
    def _calculate_momentum_trend(self, quarter_epa: pd.Series) -> str:
        """Calculate momentum trend based on quarter EPA"""
        if len(quarter_epa) < 2:
            return 'Insufficient data'
        
        # Simple trend analysis
        if quarter_epa.iloc[-1] > quarter_epa.iloc[0]:
            return 'Positive momentum'
        elif quarter_epa.iloc[-1] < quarter_epa.iloc[0]:
            return 'Negative momentum'
        else:
            return 'Stable momentum'

def main():
    """Main function to demonstrate advanced analytics system"""
    logger.info("📊 Advanced Analytics System Starting...")
    
    # Create advanced analytics system
    analytics_system = AdvancedAnalyticsSystem()
    
    if analytics_system.pbp_data is None:
        logger.error("Failed to load PBP data. Exiting.")
        return
    
    # Test with key players
    test_players = [
        ('J.Allen', 'BUF'),
        ('T.Tagovailoa', 'MIA'),
        ('K.Murray', 'ARI'),
        ('S.Rattler', 'NO'),
    ]
    
    for player_name, team in test_players:
        print(f"\n📊 {player_name} ({team}) - ADVANCED ANALYTICS")
        print("=" * 60)
        
        # Get EPA stats
        epa_stats = analytics_system.get_player_epa_stats(player_name, team)
        if epa_stats:
            print(f"📈 EPA STATISTICS:")
            print(f"  Total EPA: {epa_stats['total_epa']:.2f}")
            print(f"  Average EPA/Play: {epa_stats['avg_epa_per_play']:.3f}")
            print(f"  EPA Efficiency: {epa_stats['epa_efficiency']:.1%}")
            print(f"  QB EPA: {epa_stats['qb_epa']:.2f}")
            print(f"  Air EPA: {epa_stats['air_epa']:.2f}")
            print(f"  YAC EPA: {epa_stats['yac_epa']:.2f}")
        
        # Get WPA stats
        wpa_stats = analytics_system.get_player_wpa_stats(player_name, team)
        if wpa_stats:
            print(f"📊 WPA STATISTICS:")
            print(f"  Total WPA: {wpa_stats['total_wpa']:.3f}")
            print(f"  Average WPA/Play: {wpa_stats['avg_wpa_per_play']:.4f}")
            print(f"  WPA Efficiency: {wpa_stats['wpa_efficiency']:.1%}")
            print(f"  Clutch Factor: {wpa_stats['clutch_factor']:.4f}")
        
        # Get success rate stats
        success_stats = analytics_system.get_player_success_rate(player_name, team)
        if success_stats:
            print(f"🎯 SUCCESS RATE:")
            print(f"  Success Rate: {success_stats['success_rate']:.1%}")
            print(f"  Successful Plays: {success_stats['successful_plays']}/{success_stats['total_plays']}")
            print(f"  Consistency Score: {success_stats['consistency_score']:.3f}")
    
    # Test team analytics
    print(f"\n🏈 TEAM ADVANCED ANALYTICS")
    print("=" * 40)
    
    test_teams = ['BUF', 'MIA']
    
    for team in test_teams:
        print(f"\n📊 {team} Advanced Analytics:")
        print("-" * 30)
        
        team_analytics = analytics_system.get_team_advanced_analytics(team)
        
        print(f"Total EPA: {team_analytics['total_epa']:.2f}")
        print(f"Average EPA/Play: {team_analytics['avg_epa_per_play']:.3f}")
        print(f"EPA Efficiency: {team_analytics['epa_efficiency']:.1%}")
        print(f"Total WPA: {team_analytics['total_wpa']:.3f}")
        print(f"Success Rate: {team_analytics['success_rate']:.1%}")
    
    # Test leaders
    print(f"\n🏆 ADVANCED ANALYTICS LEADERS")
    print("=" * 40)
    
    # EPA leaders
    epa_leaders = analytics_system.get_advanced_analytics_leaders('epa', 'QB', 5)
    print(f"\nTop 5 QBs by Total EPA:")
    for i, leader in enumerate(epa_leaders, 1):
        print(f"  {i}. {leader['player']} ({leader['team']}): {leader['total']:.2f} EPA")
    
    # Success rate leaders
    success_leaders = analytics_system.get_advanced_analytics_leaders('success_rate', 'QB', 5)
    print(f"\nTop 5 QBs by Success Rate:")
    for i, leader in enumerate(success_leaders, 1):
        print(f"  {i}. {leader['player']} ({leader['team']}): {leader['average']:.1%} success rate")
    
    logger.info("\n✅ Advanced analytics system demonstration completed!")

if __name__ == "__main__":
    main()
