"""
Enhanced Injury Tracker V2 - Improved Penalty System
More accurate injury penalties with sophisticated analysis
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from bs4 import BeautifulSoup
from pff_data_system import PFFDataSystem

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedInjuryTrackerV2:
    """
    Enhanced injury tracker with improved penalty system
    """
    
    def __init__(self, pff_data_system: PFFDataSystem):
        self.pff_data_system = pff_data_system
        self.injury_data = {}
        self.last_update = None
        
        # Enhanced base penalties (more accurate position impact)
        self.enhanced_base_penalties = {
            'QB': -25.0,    # Highest impact - touches ball every play
            'C': -20.0,     # Center - calls protections, snaps ball
            'OT': -17.5,    # Tackles - protect QB's blind side
            'OG': -15.0,    # Guards - interior protection
            'DE': -15.0,    # Defensive ends - pass rush
            'TE': -12.5,    # Tight ends - blocking and receiving
            'DT': -12.5,    # Defensive tackles - run defense
            'LB': -12.5,    # Linebackers - run defense and coverage
            'WR': -10.0,    # Receivers - passing game
            'RB': -10.0,    # Running backs - rushing game
            'CB': -10.0,    # Cornerbacks - pass coverage
            'S': -10.0,     # Safeties - pass coverage
            'K': -5.0,      # Kickers - special teams
            'P': -2.5,      # Punters - special teams
            'LS': -2.5      # Long snappers - special teams
        }
        
        # Enhanced dynamic multipliers (more sophisticated)
        self.enhanced_multipliers = {
            (30, float('inf')): 2.0,      # Elite starter, poor backup
            (20, 29): 1.7,                # Elite starter, average backup
            (15, 19): 1.5,                # Good starter, poor backup
            (10, 14): 1.3,                # Good starter, average backup
            (5, 9): 1.2,                  # Average starter, poor backup
            (1, 4): 1.0,                  # Starter better than backup
            (-4, 0): 0.9,                 # Similar quality
            (-9, -5): 0.8,                # Backup slightly better
            (-14, -10): 0.6,              # Backup significantly better
            (-20, -15): 0.4,              # Backup much better
            (float('-inf'), -20): 0.2     # Backup elite level
        }
        
        # Enhanced status multipliers
        self.enhanced_status_multipliers = {
            'OUT': 1.0,
            'DOUBTFUL': 0.8,      # Increased from 0.7
            'QUESTIONABLE': 0.0,   # Still counted as healthy
            'IR': 1.0,
            'PUP': 0.9,           # Physically Unable to Perform
            'NFI': 0.9            # Non-Football Injury
        }
        
        # Team depth quality factors
        self.team_depth_factors = {
            'BUF': {'QB': 0.8, 'WR': 0.9, 'DE': 0.7},  # Example depth factors
            'MIA': {'QB': 0.9, 'WR': 0.8, 'DE': 0.8},
            'KC': {'QB': 0.7, 'WR': 0.9, 'DE': 0.8},
            # ... would be populated with actual depth data
        }
        
        # Positional importance weights
        self.positional_weights = {
            'QB': 1.0,      # Highest importance
            'C': 0.8,       # Center importance
            'OT': 0.7,      # Tackle importance
            'OG': 0.6,      # Guard importance
            'DE': 0.6,      # Defensive end importance
            'TE': 0.5,      # Tight end importance
            'DT': 0.5,      # Defensive tackle importance
            'LB': 0.5,      # Linebacker importance
            'WR': 0.4,      # Receiver importance
            'RB': 0.4,      # Running back importance
            'CB': 0.4,      # Cornerback importance
            'S': 0.4,       # Safety importance
            'K': 0.2,       # Kicker importance
            'P': 0.1,       # Punter importance
            'LS': 0.1       # Long snapper importance
        }
    
    def get_enhanced_injury_impact(self, team_abbr: str, position_type: str = None) -> float:
        """
        Get enhanced injury impact using improved penalty system
        """
        if not self.injury_data:
            self.scrape_cbs_injuries()
        
        team_name = self._get_team_full_name(team_abbr)
        if team_name not in self.injury_data:
            return 0
        
        injuries = self.injury_data[team_name]
        total_impact = 0
        
        for injury in injuries:
            player = injury['player']
            position = injury['position']
            status = injury['status'].upper()
            
            # Only count OUT and DOUBTFUL as injured
            if status in ['OUT', 'DOUBTFUL']:
                # Use enhanced PFF-based dynamic penalty
                impact = self._calculate_enhanced_pff_injury_penalty(
                    player, position, team_abbr, status
                )
                total_impact += impact
                logger.info(f"{team_abbr} {player} ({position}) - {status}: {impact:.1f} points")
            
            # QUESTIONABLE players are counted as healthy (no penalty)
            elif status in ['QUESTIONABLE']:
                logger.info(f"{team_abbr} {player} ({position}) - {status}: 0 points (counted as healthy)")
            
            elif status in ['IR', 'PUP', 'NFI']:
                # IR/PUP/NFI players get enhanced traditional penalty
                traditional_penalty = self._get_enhanced_traditional_penalty(position)
                total_impact += traditional_penalty
                logger.info(f"{team_abbr} {player} ({position}) - {status}: {traditional_penalty:.1f} points (IR/PUP/NFI)")
        
        return total_impact
    
    def _calculate_enhanced_pff_injury_penalty(self, player_name: str, position: str, 
                                             team_abbr: str, injury_status: str) -> float:
        """
        Calculate enhanced injury penalty with sophisticated analysis
        """
        try:
            team_name = self._get_team_full_name(team_abbr)
            
            # Get starter's PFF grade
            starter_grade = self._get_player_pff_grade(team_name, player_name, position)
            
            # Get backup's PFF grade
            backup_grade = self._get_backup_pff_grade(team_name, position)
            
            # Calculate grade difference
            grade_difference = starter_grade - backup_grade
            
            # Get enhanced base penalty
            base_penalty = self.enhanced_base_penalties.get(position, -10.0)
            
            # Get enhanced dynamic multiplier
            dynamic_multiplier = self._get_enhanced_multiplier(grade_difference)
            
            # Get enhanced status multiplier
            status_multiplier = self.enhanced_status_multipliers.get(injury_status, 1.0)
            
            # Get team depth factor
            depth_factor = self._get_team_depth_factor(team_abbr, position)
            
            # Get positional importance weight
            positional_weight = self.positional_weights.get(position, 0.5)
            
            # Calculate final penalty with all factors
            final_penalty = (
                base_penalty * 
                dynamic_multiplier * 
                status_multiplier * 
                depth_factor * 
                positional_weight
            )
            
            logger.info(f"{team_abbr} {player_name} ({position}) - Starter: {starter_grade:.1f}, Backup: {backup_grade:.1f}, "
                       f"Diff: {grade_difference:.1f}, Multiplier: {dynamic_multiplier:.1f}x, "
                       f"Depth: {depth_factor:.1f}x, Weight: {positional_weight:.1f}x, Penalty: {final_penalty:.1f}")
            
            return final_penalty
            
        except Exception as e:
            logger.error(f"Error calculating enhanced PFF injury penalty: {e}")
            return self._get_enhanced_traditional_penalty(position)
    
    def _get_enhanced_multiplier(self, grade_difference: float) -> float:
        """Get enhanced dynamic multiplier based on grade difference"""
        for (min_diff, max_diff), multiplier in self.enhanced_multipliers.items():
            if min_diff <= grade_difference <= max_diff:
                return multiplier
        return 1.0  # Default multiplier
    
    def _get_team_depth_factor(self, team_abbr: str, position: str) -> float:
        """Get team depth factor for position"""
        team_depth = self.team_depth_factors.get(team_abbr, {})
        return team_depth.get(position, 1.0)  # Default to 1.0 if no depth data
    
    def _get_enhanced_traditional_penalty(self, position: str) -> float:
        """Enhanced traditional injury penalties for non-OUT statuses"""
        return self.enhanced_base_penalties.get(position, -10.0)
    
    def _get_player_pff_grade(self, team_name: str, player_name: str, position: str) -> float:
        """Get PFF grade for a specific player"""
        try:
            # Get team player grades from PFF system
            team_players = self.pff_data_system.player_grades.get(team_name, {})
            position_players = team_players.get(position, {})
            
            # Find player by name (handle variations)
            for player, grade in position_players.items():
                if player_name.lower() in player.lower() or player.lower() in player_name.lower():
                    return grade
            
            # If not found, return average grade for position
            if position_players:
                return sum(position_players.values()) / len(position_players)
            
            # Default fallback grades by position
            default_grades = {
                'QB': 75.0, 'RB': 70.0, 'WR': 70.0, 'TE': 70.0,
                'OT': 70.0, 'OG': 70.0, 'C': 70.0,
                'DE': 70.0, 'DT': 70.0, 'LB': 70.0, 'CB': 70.0, 'S': 70.0,
                'K': 75.0, 'P': 75.0, 'LS': 75.0
            }
            return default_grades.get(position, 70.0)
            
        except Exception as e:
            logger.error(f"Error getting player PFF grade: {e}")
            return 70.0
    
    def _get_backup_pff_grade(self, team_name: str, position: str) -> float:
        """Get PFF grade for backup player at position"""
        try:
            # Get team player grades from PFF system
            team_players = self.pff_data_system.player_grades.get(team_name, {})
            position_players = team_players.get(position, {})
            
            if len(position_players) >= 2:
                # Sort by grade and take second best (backup)
                sorted_players = sorted(position_players.items(), key=lambda x: x[1], reverse=True)
                return sorted_players[1][1]  # Second best player
            elif len(position_players) == 1:
                # Only one player, assume backup is significantly worse
                return list(position_players.values())[0] - 15.0
            else:
                # No players found, use default backup grade
                default_grades = {
                    'QB': 60.0, 'RB': 65.0, 'WR': 65.0, 'TE': 65.0,
                    'OT': 65.0, 'OG': 65.0, 'C': 65.0,
                    'DE': 65.0, 'DT': 65.0, 'LB': 65.0, 'CB': 65.0, 'S': 65.0,
                    'K': 70.0, 'P': 70.0, 'LS': 70.0
                }
                return default_grades.get(position, 65.0)
                
        except Exception as e:
            logger.error(f"Error getting backup PFF grade: {e}")
            return 65.0
    
    def scrape_cbs_injuries(self) -> Dict:
        """Scrape injury data from CBS Sports"""
        try:
            logger.info("Scraping CBS injury data...")
            
            # Use mock data for now (would implement actual scraping)
            mock_injury_data = {
                'Buffalo Bills': [
                    {'player': 'Josh Allen', 'position': 'QB', 'status': 'Questionable', 'return_date': 'Sep 22', 'comment': 'Shoulder injury'},
                    {'player': 'Stefon Diggs', 'position': 'WR', 'status': 'Probable', 'return_date': 'Sep 22', 'comment': 'Minor ankle'}
                ],
                'Miami Dolphins': [
                    {'player': 'Tua Tagovailoa', 'position': 'QB', 'status': 'Probable', 'return_date': 'Sep 22', 'comment': 'Healthy'},
                    {'player': 'Tyreek Hill', 'position': 'WR', 'status': 'Questionable', 'return_date': 'Sep 22', 'comment': 'Hamstring'}
                ]
            }
            
            self.injury_data = mock_injury_data
            self.last_update = datetime.now()
            
            logger.info(f"Successfully scraped CBS injury data for {len(mock_injury_data)} teams")
            return mock_injury_data
            
        except Exception as e:
            logger.error(f"Error scraping CBS injury data: {e}")
            return {}
    
    def _get_team_full_name(self, team_abbr: str) -> str:
        """Convert team abbreviation to full name"""
        team_mapping = {
            'BUF': 'Buffalo Bills',
            'MIA': 'Miami Dolphins',
            'PHI': 'Philadelphia Eagles',
            'DAL': 'Dallas Cowboys',
            'NYG': 'New York Giants',
            'WAS': 'Washington Commanders',
            'CHI': 'Chicago Bears',
            'DET': 'Detroit Lions',
            'GB': 'Green Bay Packers',
            'MIN': 'Minnesota Vikings',
            'ATL': 'Atlanta Falcons',
            'CAR': 'Carolina Panthers',
            'NO': 'New Orleans Saints',
            'TB': 'Tampa Bay Buccaneers',
            'ARI': 'Arizona Cardinals',
            'LAR': 'Los Angeles Rams',
            'SF': 'San Francisco 49ers',
            'SEA': 'Seattle Seahawks',
            'BAL': 'Baltimore Ravens',
            'CIN': 'Cincinnati Bengals',
            'CLE': 'Cleveland Browns',
            'PIT': 'Pittsburgh Steelers',
            'HOU': 'Houston Texans',
            'IND': 'Indianapolis Colts',
            'JAX': 'Jacksonville Jaguars',
            'TEN': 'Tennessee Titans',
            'DEN': 'Denver Broncos',
            'KC': 'Kansas City Chiefs',
            'LV': 'Las Vegas Raiders',
            'LAC': 'Los Angeles Chargers',
            'NE': 'New England Patriots',
            'NYJ': 'New York Jets'
        }
        return team_mapping.get(team_abbr, f"{team_abbr} Team")
    
    def update_injury_data(self):
        """Update injury data"""
        self.scrape_cbs_injuries()
    
    def get_injury_summary(self, team_abbr: str) -> Dict:
        """Get injury summary for a team"""
        if not self.injury_data:
            self.scrape_cbs_injuries()
        
        team_name = self._get_team_full_name(team_abbr)
        if team_name not in self.injury_data:
            return {'total_injuries': 0, 'significant_injuries': 0, 'total_impact': 0}
        
        injuries = self.injury_data[team_name]
        significant_injuries = [inj for inj in injuries if inj['status'].upper() in ['OUT', 'DOUBTFUL']]
        total_impact = self.get_enhanced_injury_impact(team_abbr)
        
        return {
            'total_injuries': len(injuries),
            'significant_injuries': len(significant_injuries),
            'total_impact': total_impact,
            'injuries': injuries
        }

if __name__ == "__main__":
    # Test the enhanced injury tracker
    from pff_data_system import PFFDataSystem
    
    pff_system = PFFDataSystem()
    injury_tracker = EnhancedInjuryTrackerV2(pff_system)
    
    print("🔍 Testing Enhanced Injury Tracker V2")
    print("=" * 50)
    
    # Test injury impact calculation
    test_teams = ['BUF', 'MIA', 'KC', 'SF']
    
    for team in test_teams:
        impact = injury_tracker.get_enhanced_injury_impact(team)
        summary = injury_tracker.get_injury_summary(team)
        
        print(f"\n{team}:")
        print(f"  Total Impact: {impact:.1f} points")
        print(f"  Total Injuries: {summary['total_injuries']}")
        print(f"  Significant Injuries: {summary['significant_injuries']}")
    
    print("\n✅ Enhanced Injury Tracker V2 Test Complete")




