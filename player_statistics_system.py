#!/usr/bin/env python3
"""
Comprehensive Player Statistics System
Extracts and aggregates individual player statistics from play-by-play data.
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

class PlayerStatisticsSystem:
    """Comprehensive player statistics system using PBP data"""
    
    def __init__(self, seasons: List[int] = None):
        """Initialize player statistics system"""
        if seasons is None:
            seasons = [datetime.now().year]
        
        self.seasons = seasons
        self.pbp_data = None
        self.player_stats_cache = {}
        self.load_data()
    
    def load_data(self):
        """Load play-by-play data"""
        logger.info(f"Loading PBP data for seasons: {self.seasons}")
        try:
            self.pbp_data = nfl.import_pbp_data(self.seasons)
            logger.info(f"✅ Loaded {len(self.pbp_data):,} plays")
            
            # Analyze data completeness
            self._analyze_data_completeness()
            
        except Exception as e:
            logger.error(f"Error loading PBP data: {e}")
            self.pbp_data = None
    
    def _analyze_data_completeness(self):
        """Analyze completeness of player data in PBP"""
        if self.pbp_data is None:
            return
        
        logger.info("📊 Analyzing player data completeness...")
        
        # Passing data
        passing_plays = self.pbp_data[self.pbp_data['play_type'] == 'pass']
        passer_complete = passing_plays['passer_player_name'].notna().sum()
        receiver_complete = passing_plays['receiver_player_name'].notna().sum()
        
        logger.info(f"Passing: {passer_complete:,}/{len(passing_plays):,} passer names ({passer_complete/len(passing_plays)*100:.1f}%)")
        logger.info(f"Receiving: {receiver_complete:,}/{len(passing_plays):,} receiver names ({receiver_complete/len(passing_plays)*100:.1f}%)")
        
        # Rushing data
        rushing_plays = self.pbp_data[self.pbp_data['play_type'] == 'run']
        rusher_complete = rushing_plays['rusher_player_name'].notna().sum()
        logger.info(f"Rushing: {rusher_complete:,}/{len(rushing_plays):,} rusher names ({rusher_complete/len(rushing_plays)*100:.1f}%)")
        
        # Defensive data
        tackle_plays = self.pbp_data[self.pbp_data['solo_tackle_1_player_name'].notna()]
        sack_plays = self.pbp_data[self.pbp_data['sack_player_name'].notna()]
        int_plays = self.pbp_data[self.pbp_data['interception_player_name'].notna()]
        
        logger.info(f"Defense: {len(tackle_plays):,} tackles, {len(sack_plays):,} sacks, {len(int_plays):,} interceptions")
    
    def get_player_passing_stats(self, player_name: str, team: str = None, week: int = None) -> Dict:
        """Get comprehensive passing statistics for a player"""
        if self.pbp_data is None:
            return {}
        
        # Filter data
        player_data = self.pbp_data[self.pbp_data['passer_player_name'] == player_name].copy()
        
        if team:
            player_data = player_data[player_data['posteam'] == team]
        if week:
            player_data = player_data[player_data['week'] == week]
        
        if player_data.empty:
            logger.warning(f"No passing data found for {player_name}")
            return {}
        
        # Calculate statistics
        stats = {
            'player_name': player_name,
            'team': team or player_data['posteam'].iloc[0] if not player_data.empty else None,
            'week': week,
            'games_played': player_data['game_id'].nunique(),
            'pass_attempts': len(player_data),
            'pass_completions': player_data['complete_pass'].sum(),
            'pass_yards': player_data['passing_yards'].sum(),
            'pass_touchdowns': player_data['pass_touchdown'].sum(),
            'interceptions': player_data['interception'].sum(),
            'sacks': player_data['sack'].sum(),
            'sack_yards': 0,  # Not available in current data
            'completion_rate': player_data['complete_pass'].mean(),
            'yards_per_attempt': player_data['passing_yards'].mean(),
            'yards_per_completion': player_data[player_data['complete_pass'] == 1]['passing_yards'].mean(),
            'touchdown_rate': player_data['pass_touchdown'].mean(),
            'interception_rate': player_data['interception'].mean(),
            'sack_rate': player_data['sack'].mean(),
            'passer_rating': self._calculate_passer_rating(player_data),
            'first_downs': player_data['first_down'].sum(),
            'air_yards': player_data['air_yards'].sum(),
            'yards_after_catch': player_data['yards_after_catch'].sum(),
        }
        
        # Fill NaN values
        for key, value in stats.items():
            if pd.isna(value):
                stats[key] = 0
        
        logger.info(f"📊 {player_name} passing stats: {stats['pass_completions']}/{stats['pass_attempts']} completions, {stats['pass_yards']} yards, {stats['pass_touchdowns']} TDs")
        return stats
    
    def get_player_rushing_stats(self, player_name: str, team: str = None, week: int = None) -> Dict:
        """Get comprehensive rushing statistics for a player"""
        if self.pbp_data is None:
            return {}
        
        # Filter data
        player_data = self.pbp_data[self.pbp_data['rusher_player_name'] == player_name].copy()
        
        if team:
            player_data = player_data[player_data['posteam'] == team]
        if week:
            player_data = player_data[player_data['week'] == week]
        
        if player_data.empty:
            logger.warning(f"No rushing data found for {player_name}")
            return {}
        
        # Calculate statistics
        stats = {
            'player_name': player_name,
            'team': team or player_data['posteam'].iloc[0] if not player_data.empty else None,
            'week': week,
            'games_played': player_data['game_id'].nunique(),
            'rush_attempts': len(player_data),
            'rush_yards': player_data['rushing_yards'].sum(),
            'rush_touchdowns': player_data['rush_touchdown'].sum(),
            'yards_per_attempt': player_data['rushing_yards'].mean(),
            'touchdown_rate': player_data['rush_touchdown'].mean(),
            'first_downs': player_data['first_down'].sum(),
            'fumbles': player_data['fumble_lost'].sum(),
            'fumble_rate': player_data['fumble_lost'].mean(),
            'longest_rush': player_data['rushing_yards'].max(),
            'runs_10_plus': len(player_data[player_data['rushing_yards'] >= 10]),
            'runs_20_plus': len(player_data[player_data['rushing_yards'] >= 20]),
            'success_rate': self._calculate_success_rate(player_data, 'rushing'),
        }
        
        # Fill NaN values
        for key, value in stats.items():
            if pd.isna(value):
                stats[key] = 0
        
        logger.info(f"🏃 {player_name} rushing stats: {stats['rush_attempts']} attempts, {stats['rush_yards']} yards, {stats['rush_touchdowns']} TDs")
        return stats
    
    def get_player_receiving_stats(self, player_name: str, team: str = None, week: int = None) -> Dict:
        """Get comprehensive receiving statistics for a player"""
        if self.pbp_data is None:
            return {}
        
        # Filter data
        player_data = self.pbp_data[self.pbp_data['receiver_player_name'] == player_name].copy()
        
        if team:
            player_data = player_data[player_data['posteam'] == team]
        if week:
            player_data = player_data[player_data['week'] == week]
        
        if player_data.empty:
            logger.warning(f"No receiving data found for {player_name}")
            return {}
        
        # Calculate statistics
        stats = {
            'player_name': player_name,
            'team': team or player_data['posteam'].iloc[0] if not player_data.empty else None,
            'week': week,
            'games_played': player_data['game_id'].nunique(),
            'targets': len(player_data),
            'receptions': player_data['complete_pass'].sum(),
            'receiving_yards': player_data['receiving_yards'].sum(),
            'receiving_touchdowns': player_data['pass_touchdown'].sum(),
            'catch_rate': player_data['complete_pass'].mean(),
            'yards_per_target': player_data['receiving_yards'].mean(),
            'yards_per_reception': player_data[player_data['complete_pass'] == 1]['receiving_yards'].mean(),
            'touchdown_rate': player_data['pass_touchdown'].mean(),
            'first_downs': player_data['first_down'].sum(),
            'air_yards': player_data['air_yards'].sum(),
            'yards_after_catch': player_data['yards_after_catch'].sum(),
            'longest_reception': player_data['receiving_yards'].max(),
            'receptions_20_plus': len(player_data[player_data['receiving_yards'] >= 20]),
            'receptions_40_plus': len(player_data[player_data['receiving_yards'] >= 40]),
            'success_rate': self._calculate_success_rate(player_data, 'receiving'),
        }
        
        # Fill NaN values
        for key, value in stats.items():
            if pd.isna(value):
                stats[key] = 0
        
        logger.info(f"🎯 {player_name} receiving stats: {stats['receptions']}/{stats['targets']} receptions, {stats['receiving_yards']} yards, {stats['receiving_touchdowns']} TDs")
        return stats
    
    def get_player_defensive_stats(self, player_name: str, team: str = None, week: int = None) -> Dict:
        """Get comprehensive defensive statistics for a player"""
        if self.pbp_data is None:
            return {}
        
        # Filter data for defensive plays
        defensive_data = self.pbp_data[
            (self.pbp_data['solo_tackle_1_player_name'] == player_name) |
            (self.pbp_data['solo_tackle_2_player_name'] == player_name) |
            (self.pbp_data['assist_tackle_1_player_name'] == player_name) |
            (self.pbp_data['assist_tackle_2_player_name'] == player_name) |
            (self.pbp_data['sack_player_name'] == player_name) |
            (self.pbp_data['interception_player_name'] == player_name) |
            (self.pbp_data['fumble_recovery_1_player_name'] == player_name) |
            (self.pbp_data['fumble_recovery_2_player_name'] == player_name) |
            (self.pbp_data['pass_defense_1_player_name'] == player_name) |
            (self.pbp_data['pass_defense_2_player_name'] == player_name)
        ].copy()
        
        if team:
            defensive_data = defensive_data[defensive_data['defteam'] == team]
        if week:
            defensive_data = defensive_data[defensive_data['week'] == week]
        
        if defensive_data.empty:
            logger.warning(f"No defensive data found for {player_name}")
            return {}
        
        # Calculate statistics
        stats = {
            'player_name': player_name,
            'team': team or defensive_data['defteam'].iloc[0] if not defensive_data.empty else None,
            'week': week,
            'games_played': defensive_data['game_id'].nunique(),
            'solo_tackles': len(defensive_data[defensive_data['solo_tackle_1_player_name'] == player_name]) + 
                           len(defensive_data[defensive_data['solo_tackle_2_player_name'] == player_name]),
            'assist_tackles': len(defensive_data[defensive_data['assist_tackle_1_player_name'] == player_name]) + 
                             len(defensive_data[defensive_data['assist_tackle_2_player_name'] == player_name]),
            'total_tackles': 0,  # Will be calculated
            'sacks': len(defensive_data[defensive_data['sack_player_name'] == player_name]),
            'interceptions': len(defensive_data[defensive_data['interception_player_name'] == player_name]),
            'fumble_recoveries': len(defensive_data[defensive_data['fumble_recovery_1_player_name'] == player_name]) + 
                                len(defensive_data[defensive_data['fumble_recovery_2_player_name'] == player_name]),
            'pass_defenses': len(defensive_data[defensive_data['pass_defense_1_player_name'] == player_name]) + 
                            len(defensive_data[defensive_data['pass_defense_2_player_name'] == player_name]),
            'tackles_for_loss': len(defensive_data[defensive_data['tackle_for_loss_1_player_name'] == player_name]) + 
                               len(defensive_data[defensive_data['tackle_for_loss_2_player_name'] == player_name]),
            'qb_hits': len(defensive_data[defensive_data['qb_hit_1_player_name'] == player_name]) + 
                      len(defensive_data[defensive_data['qb_hit_2_player_name'] == player_name]),
        }
        
        # Calculate total tackles
        stats['total_tackles'] = stats['solo_tackles'] + stats['assist_tackles']
        
        # Fill NaN values
        for key, value in stats.items():
            if pd.isna(value):
                stats[key] = 0
        
        logger.info(f"🛡️ {player_name} defensive stats: {stats['total_tackles']} tackles, {stats['sacks']} sacks, {stats['interceptions']} INTs")
        return stats
    
    def get_player_comprehensive_stats(self, player_name: str, team: str = None, week: int = None) -> Dict:
        """Get comprehensive statistics for a player (all categories)"""
        logger.info(f"📊 Getting comprehensive stats for {player_name}")
        
        comprehensive_stats = {
            'player_name': player_name,
            'team': team,
            'week': week,
            'passing': self.get_player_passing_stats(player_name, team, week),
            'rushing': self.get_player_rushing_stats(player_name, team, week),
            'receiving': self.get_player_receiving_stats(player_name, team, week),
            'defensive': self.get_player_defensive_stats(player_name, team, week),
        }
        
        # Calculate totals
        comprehensive_stats['total_touchdowns'] = (
            comprehensive_stats['passing'].get('pass_touchdowns', 0) +
            comprehensive_stats['rushing'].get('rush_touchdowns', 0) +
            comprehensive_stats['receiving'].get('receiving_touchdowns', 0)
        )
        
        comprehensive_stats['total_yards'] = (
            comprehensive_stats['passing'].get('pass_yards', 0) +
            comprehensive_stats['rushing'].get('rush_yards', 0) +
            comprehensive_stats['receiving'].get('receiving_yards', 0)
        )
        
        return comprehensive_stats
    
    def get_team_player_stats(self, team: str, week: int = None) -> Dict:
        """Get statistics for all players on a team"""
        logger.info(f"📊 Getting team player stats for {team}")
        
        if self.pbp_data is None:
            return {}
        
        # Get all unique players for the team
        team_data = self.pbp_data[self.pbp_data['posteam'] == team]
        if week:
            team_data = team_data[team_data['week'] == week]
        
        # Get unique players from different positions
        players = set()
        
        # Offensive players
        players.update(team_data['passer_player_name'].dropna().unique())
        players.update(team_data['rusher_player_name'].dropna().unique())
        players.update(team_data['receiver_player_name'].dropna().unique())
        
        # Defensive players
        players.update(team_data['solo_tackle_1_player_name'].dropna().unique())
        players.update(team_data['sack_player_name'].dropna().unique())
        players.update(team_data['interception_player_name'].dropna().unique())
        
        # Special teams
        players.update(team_data['kicker_player_name'].dropna().unique())
        players.update(team_data['punter_player_name'].dropna().unique())
        
        # Remove None values
        players = [p for p in players if p is not None]
        
        logger.info(f"Found {len(players)} players for {team}")
        
        # Get stats for each player
        team_stats = {}
        for player in players:
            team_stats[player] = self.get_player_comprehensive_stats(player, team, week)
        
        return team_stats
    
    def get_position_leaders(self, position: str, stat: str, limit: int = 10) -> List[Dict]:
        """Get position leaders for a specific statistic"""
        logger.info(f"📊 Getting {position} leaders in {stat}")
        
        if self.pbp_data is None:
            return []
        
        # This would need to be implemented based on the specific position and stat
        # For now, return empty list
        return []
    
    def _calculate_passer_rating(self, passing_data: pd.DataFrame) -> float:
        """Calculate passer rating"""
        if passing_data.empty:
            return 0
        
        completions = passing_data['complete_pass'].sum()
        attempts = len(passing_data)
        yards = passing_data['passing_yards'].sum()
        touchdowns = passing_data['pass_touchdown'].sum()
        interceptions = passing_data['interception'].sum()
        
        if attempts == 0:
            return 0
        
        # NFL Passer Rating formula
        completion_percentage = (completions / attempts) * 100
        yards_per_attempt = yards / attempts
        touchdown_percentage = (touchdowns / attempts) * 100
        interception_percentage = (interceptions / attempts) * 100
        
        # Calculate components
        a = max(0, min(2.375, (completion_percentage - 30) / 5))
        b = max(0, min(2.375, (yards_per_attempt - 3) / 4))
        c = max(0, min(2.375, touchdown_percentage / 4))
        d = max(0, min(2.375, (9.5 - interception_percentage) / 4))
        
        passer_rating = ((a + b + c + d) / 6) * 100
        return round(passer_rating, 1)
    
    def _calculate_success_rate(self, data: pd.DataFrame, play_type: str) -> float:
        """Calculate success rate for plays"""
        if data.empty:
            return 0
        
        if play_type == 'rushing':
            # Success: 40% of yards needed on 1st down, 60% on 2nd down, 100% on 3rd/4th down
            success_plays = 0
            for _, play in data.iterrows():
                down = play.get('down', 1)
                yards_gained = play.get('rushing_yards', 0)
                yards_to_go = play.get('ydstogo', 10)
                
                if down == 1 and yards_gained >= yards_to_go * 0.4:
                    success_plays += 1
                elif down == 2 and yards_gained >= yards_to_go * 0.6:
                    success_plays += 1
                elif down >= 3 and yards_gained >= yards_to_go:
                    success_plays += 1
            
            return success_plays / len(data)
        
        elif play_type == 'receiving':
            # Success: 50% of yards needed on 1st down, 70% on 2nd down, 100% on 3rd/4th down
            success_plays = 0
            for _, play in data.iterrows():
                down = play.get('down', 1)
                yards_gained = play.get('receiving_yards', 0)
                yards_to_go = play.get('ydstogo', 10)
                
                if down == 1 and yards_gained >= yards_to_go * 0.5:
                    success_plays += 1
                elif down == 2 and yards_gained >= yards_to_go * 0.7:
                    success_plays += 1
                elif down >= 3 and yards_gained >= yards_to_go:
                    success_plays += 1
            
            return success_plays / len(data)
        
        return 0

def main():
    """Main function to demonstrate player statistics system"""
    logger.info("🏈 Player Statistics System Starting...")
    
    # Create player statistics system
    player_system = PlayerStatisticsSystem()
    
    if player_system.pbp_data is None:
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
        print(f"\n👤 {player_name} ({team}) - COMPREHENSIVE STATISTICS")
        print("=" * 60)
        
        # Get comprehensive stats
        stats = player_system.get_player_comprehensive_stats(player_name, team)
        
        # Display passing stats
        passing = stats['passing']
        if passing:
            print(f"📊 PASSING:")
            print(f"  Completions/Attempts: {passing['pass_completions']}/{passing['pass_attempts']}")
            print(f"  Yards: {passing['pass_yards']}")
            print(f"  Touchdowns: {passing['pass_touchdowns']}")
            print(f"  Interceptions: {passing['interceptions']}")
            print(f"  Completion Rate: {passing['completion_rate']:.1%}")
            print(f"  Passer Rating: {passing['passer_rating']}")
        
        # Display rushing stats
        rushing = stats['rushing']
        if rushing:
            print(f"🏃 RUSHING:")
            print(f"  Attempts: {rushing['rush_attempts']}")
            print(f"  Yards: {rushing['rush_yards']}")
            print(f"  Touchdowns: {rushing['rush_touchdowns']}")
            print(f"  Yards/Attempt: {rushing['yards_per_attempt']:.1f}")
        
        # Display receiving stats
        receiving = stats['receiving']
        if receiving:
            print(f"🎯 RECEIVING:")
            print(f"  Targets: {receiving['targets']}")
            print(f"  Receptions: {receiving['receptions']}")
            print(f"  Yards: {receiving['receiving_yards']}")
            print(f"  Touchdowns: {receiving['receiving_touchdowns']}")
            print(f"  Catch Rate: {receiving['catch_rate']:.1%}")
        
        # Display defensive stats
        defensive = stats['defensive']
        if defensive:
            print(f"🛡️ DEFENSIVE:")
            print(f"  Total Tackles: {defensive['total_tackles']}")
            print(f"  Sacks: {defensive['sacks']}")
            print(f"  Interceptions: {defensive['interceptions']}")
            print(f"  Fumble Recoveries: {defensive['fumble_recoveries']}")
        
        # Display totals
        print(f"📈 TOTALS:")
        print(f"  Total Touchdowns: {stats['total_touchdowns']}")
        print(f"  Total Yards: {stats['total_yards']}")
    
    # Test team stats
    print(f"\n🏈 TEAM PLAYER STATISTICS - BUFFALO BILLS")
    print("=" * 50)
    
    team_stats = player_system.get_team_player_stats('BUF')
    
    # Show top players by total yards
    player_totals = []
    for player, stats in team_stats.items():
        total_yards = stats['total_yards']
        if total_yards > 0:
            player_totals.append((player, total_yards))
    
    player_totals.sort(key=lambda x: x[1], reverse=True)
    
    print("Top 5 players by total yards:")
    for i, (player, yards) in enumerate(player_totals[:5]):
        print(f"  {i+1}. {player}: {yards} yards")
    
    logger.info("\n✅ Player statistics system demonstration completed!")

if __name__ == "__main__":
    main()
