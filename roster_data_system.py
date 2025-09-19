#!/usr/bin/env python3
"""
Comprehensive Roster Data System
Fills the roster data gap using available weekly rosters and depth charts.
"""

import pandas as pd
import numpy as np
import nfl_data_py as nfl
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RosterDataSystem:
    """Comprehensive roster data system using available data sources"""
    
    def __init__(self):
        """Initialize roster data system"""
        self.weekly_rosters = None
        self.depth_charts = None
        self.current_week = None
        self.load_data()
        self.setup_roster_status_mapping()
    
    def load_data(self):
        """Load roster data"""
        logger.info("Loading roster data...")
        try:
            self.weekly_rosters = nfl.import_weekly_rosters([2025])
            self.depth_charts = nfl.import_depth_charts([2025])
            
            logger.info(f"✅ Loaded {len(self.weekly_rosters):,} weekly roster records")
            logger.info(f"✅ Loaded {len(self.depth_charts):,} depth chart records")
            
            # Get current week
            self.current_week = self.weekly_rosters['week'].max()
            logger.info(f"📅 Current week: {self.current_week}")
            
        except Exception as e:
            logger.error(f"Error loading roster data: {e}")
            self.weekly_rosters = None
            self.depth_charts = None
    
    def setup_roster_status_mapping(self):
        """Setup roster status mapping"""
        self.roster_status_map = {
            'ACT': 'Active',           # Active roster
            'INA': 'Inactive',         # Inactive (injured, etc.)
            'RES': 'Reserve',          # Reserve list
            'CUT': 'Cut',              # Cut from team
            'DEV': 'Practice Squad',   # Practice squad
            'RET': 'Retired',          # Retired
            'EXE': 'Exempt',           # Exempt list
        }
        
        self.status_description_map = {
            'A01': 'Active Roster',
            'P01': 'Practice Squad',
            'W03': 'Waived',
            'R01': 'Reserve/Injured',
            'P07': 'Practice Squad/Injured',
            'I01': 'Injured Reserve',
            'P06': 'Practice Squad/Injured',
            'R48': 'Reserve/COVID-19',
            'R04': 'Reserve/Suspended',
            'R02': 'Reserve/Injured',
            'R05': 'Reserve/Injured',
            'I02': 'Injured Reserve',
            'R40': 'Reserve/Injured',
            'P03': 'Practice Squad',
            'P02': 'Practice Squad',
            'R27': 'Reserve/Injured',
            'R36': 'Reserve/Injured',
            'E02': 'Exempt',
            'R06': 'Reserve/Injured',
            'W04': 'Waived',
            'F01': 'Free Agent',
        }
    
    def get_team_active_roster(self, team, week=None):
        """Get team's active roster for a specific week"""
        if self.weekly_rosters is None:
            return pd.DataFrame()
        
        if week is None:
            week = self.current_week
        
        # Get active roster for the team and week
        active_roster = self.weekly_rosters[
            (self.weekly_rosters['team'] == team) & 
            (self.weekly_rosters['week'] == week) & 
            (self.weekly_rosters['status'] == 'ACT')
        ].copy()
        
        logger.info(f"📋 {team} active roster (Week {week}): {len(active_roster)} players")
        return active_roster
    
    def get_team_inactive_players(self, team, week=None):
        """Get team's inactive players for a specific week"""
        if self.weekly_rosters is None:
            return pd.DataFrame()
        
        if week is None:
            week = self.current_week
        
        # Get inactive players
        inactive_players = self.weekly_rosters[
            (self.weekly_rosters['team'] == team) & 
            (self.weekly_rosters['week'] == week) & 
            (self.weekly_rosters['status'] == 'INA')
        ].copy()
        
        logger.info(f"🏥 {team} inactive players (Week {week}): {len(inactive_players)} players")
        return inactive_players
    
    def get_team_depth_chart(self, team, week=None):
        """Get team's depth chart"""
        if self.depth_charts is None:
            return pd.DataFrame()
        
        # Get depth chart for the team
        team_depth = self.depth_charts[self.depth_charts['team'] == team].copy()
        
        # Sort by position and rank
        team_depth = team_depth.sort_values(['pos_abb', 'pos_rank'])
        
        logger.info(f"📊 {team} depth chart: {len(team_depth)} players")
        return team_depth
    
    def get_position_depth(self, team, position, week=None):
        """Get depth chart for a specific position"""
        depth_chart = self.get_team_depth_chart(team, week)
        
        if depth_chart.empty:
            return pd.DataFrame()
        
        # Filter by position
        position_depth = depth_chart[depth_chart['pos_abb'] == position].copy()
        position_depth = position_depth.sort_values('pos_rank')
        
        logger.info(f"📋 {team} {position} depth: {len(position_depth)} players")
        return position_depth
    
    def get_starter_and_backup(self, team, position, week=None):
        """Get starter and backup for a specific position"""
        position_depth = self.get_position_depth(team, position, week)
        
        if position_depth.empty:
            return None, None
        
        # Get starter (rank 1)
        starter = position_depth[position_depth['pos_rank'] == 1]
        starter_name = starter['player_name'].iloc[0] if not starter.empty else None
        
        # Get backup (rank 2)
        backup = position_depth[position_depth['pos_rank'] == 2]
        backup_name = backup['player_name'].iloc[0] if not backup.empty else None
        
        logger.info(f"🏈 {team} {position}: Starter={starter_name}, Backup={backup_name}")
        return starter_name, backup_name
    
    def check_player_availability(self, team, player_name, week=None):
        """Check if a specific player is available"""
        if self.weekly_rosters is None:
            return None
        
        if week is None:
            week = self.current_week
        
        # Find player in weekly rosters
        player_data = self.weekly_rosters[
            (self.weekly_rosters['team'] == team) & 
            (self.weekly_rosters['player_name'] == player_name) & 
            (self.weekly_rosters['week'] == week)
        ]
        
        if player_data.empty:
            logger.warning(f"❌ Player {player_name} not found on {team} roster")
            return None
        
        status = player_data['status'].iloc[0]
        status_desc = player_data['status_description_abbr'].iloc[0]
        
        availability = {
            'player_name': player_name,
            'team': team,
            'week': week,
            'status': status,
            'status_description': self.status_description_map.get(status_desc, status_desc),
            'is_active': status == 'ACT',
            'is_inactive': status == 'INA',
            'is_available': status in ['ACT'],
            'position': player_data['position'].iloc[0] if 'position' in player_data.columns else None
        }
        
        logger.info(f"👤 {player_name} ({team}): {availability['status_description']} - Available: {availability['is_available']}")
        return availability
    
    def get_team_roster_summary(self, team, week=None):
        """Get comprehensive roster summary for a team"""
        if week is None:
            week = self.current_week
        
        logger.info(f"📊 Generating roster summary for {team} (Week {week})")
        
        # Get active roster
        active_roster = self.get_team_active_roster(team, week)
        
        # Get inactive players
        inactive_players = self.get_team_inactive_players(team, week)
        
        # Get depth chart
        depth_chart = self.get_team_depth_chart(team, week)
        
        # Create summary
        summary = {
            'team': team,
            'week': week,
            'active_players': len(active_roster),
            'inactive_players': len(inactive_players),
            'total_depth_chart': len(depth_chart),
            'active_roster': active_roster,
            'inactive_players': inactive_players,
            'depth_chart': depth_chart,
            'position_breakdown': self._get_position_breakdown(active_roster),
            'key_players': self._get_key_players(team, week)
        }
        
        return summary
    
    def _get_position_breakdown(self, active_roster):
        """Get position breakdown for active roster"""
        if active_roster.empty:
            return {}
        
        position_counts = active_roster['position'].value_counts().to_dict()
        return position_counts
    
    def _get_key_players(self, team, week=None):
        """Get key players (starters) for each position"""
        key_positions = ['QB', 'RB', 'WR', 'TE', 'K']
        key_players = {}
        
        for position in key_positions:
            starter, backup = self.get_starter_and_backup(team, position, week)
            key_players[position] = {
                'starter': starter,
                'backup': backup
            }
        
        return key_players
    
    def analyze_roster_changes(self, team, week1, week2):
        """Analyze roster changes between two weeks"""
        logger.info(f"🔄 Analyzing roster changes for {team}: Week {week1} → Week {week2}")
        
        # Get rosters for both weeks
        roster1 = self.get_team_active_roster(team, week1)
        roster2 = self.get_team_active_roster(team, week2)
        
        if roster1.empty or roster2.empty:
            logger.warning(f"❌ Insufficient data for {team} roster comparison")
            return None
        
        # Find changes
        players1 = set(roster1['player_name'])
        players2 = set(roster2['player_name'])
        
        added_players = players2 - players1
        removed_players = players1 - players2
        
        changes = {
            'team': team,
            'week1': week1,
            'week2': week2,
            'added_players': list(added_players),
            'removed_players': list(removed_players),
            'net_change': len(added_players) - len(removed_players),
            'total_players_week1': len(players1),
            'total_players_week2': len(players2)
        }
        
        logger.info(f"📈 {team} roster changes: +{len(added_players)}, -{len(removed_players)}")
        return changes
    
    def get_injury_impact_assessment(self, team, week=None):
        """Assess injury impact based on roster status"""
        if week is None:
            week = self.current_week
        
        logger.info(f"🏥 Assessing injury impact for {team} (Week {week})")
        
        # Get inactive players
        inactive_players = self.get_team_inactive_players(team, week)
        
        if inactive_players.empty:
            logger.info(f"✅ {team} has no inactive players")
            return {'team': team, 'week': week, 'inactive_count': 0, 'impact': 'None'}
        
        # Analyze impact by position
        position_impact = {}
        for _, player in inactive_players.iterrows():
            position = player['position']
            player_name = player['player_name']
            
            if position not in position_impact:
                position_impact[position] = []
            
            position_impact[position].append(player_name)
        
        # Calculate overall impact
        total_inactive = len(inactive_players)
        critical_positions = ['QB', 'RB', 'WR', 'TE']
        critical_injuries = sum(1 for pos in critical_positions if pos in position_impact)
        
        if critical_injuries > 0:
            impact_level = 'High'
        elif total_inactive > 5:
            impact_level = 'Medium'
        else:
            impact_level = 'Low'
        
        assessment = {
            'team': team,
            'week': week,
            'inactive_count': total_inactive,
            'critical_injuries': critical_injuries,
            'impact_level': impact_level,
            'position_breakdown': position_impact
        }
        
        logger.info(f"📊 {team} injury impact: {impact_level} ({total_inactive} inactive, {critical_injuries} critical)")
        return assessment

def main():
    """Main function to demonstrate roster data system"""
    logger.info("🏈 Roster Data System Starting...")
    
    # Create roster data system
    roster_system = RosterDataSystem()
    
    if roster_system.weekly_rosters is None:
        logger.error("Failed to load roster data. Exiting.")
        return
    
    # Test with MIA and BUF
    teams = ['MIA', 'BUF']
    
    for team in teams:
        print(f"\n📋 {team} ROSTER ANALYSIS")
        print("=" * 40)
        
        # Get roster summary
        summary = roster_system.get_team_roster_summary(team)
        
        print(f"Active Players: {summary['active_players']}")
        print(f"Inactive Players: {summary['inactive_players']}")
        print(f"Total Depth Chart: {summary['total_depth_chart']}")
        
        print(f"\nPosition Breakdown:")
        for position, count in summary['position_breakdown'].items():
            print(f"  {position}: {count}")
        
        print(f"\nKey Players:")
        for position, players in summary['key_players'].items():
            print(f"  {position}: {players['starter']} (Backup: {players['backup']})")
        
        # Check specific players
        print(f"\nPlayer Availability Check:")
        key_positions = ['QB', 'RB', 'WR']
        for position in key_positions:
            starter, backup = roster_system.get_starter_and_backup(team, position)
            if starter:
                availability = roster_system.check_player_availability(team, starter)
                if availability:
                    print(f"  {starter} ({position}): {availability['status_description']}")
        
        # Injury impact assessment
        injury_assessment = roster_system.get_injury_impact_assessment(team)
        print(f"\nInjury Impact: {injury_assessment['impact_level']}")
        print(f"Inactive Players: {injury_assessment['inactive_count']}")
        print(f"Critical Injuries: {injury_assessment['critical_injuries']}")
    
    logger.info("\n✅ Roster data system demonstration completed!")

if __name__ == "__main__":
    main()
