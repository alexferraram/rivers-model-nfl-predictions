"""
Dynamic Injury System - Direct Impact on Win Probability
Completely reworked injury penalty system based on PFF grades and position importance
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

class DynamicInjurySystem:
    """
    Dynamic injury system that directly impacts win probability
    """
    
    def __init__(self, pff_data_system: PFFDataSystem):
        self.pff_data_system = pff_data_system
        self.injury_data = {}
        self.last_update = None
        
        # Season start date (for determining long-term injuries)
        self.season_start = datetime(2025, 9, 5)  # Approximate NFL season start
        
        # Position impact multipliers (direct win probability impact)
        self.position_impact_multipliers = {
            'QB': 1.0,      # Highest impact - direct win probability
            'C': 0.15,      # Center - moderate impact
            'OT': 0.12,     # Tackles - moderate impact
            'OG': 0.08,     # Guards - lower impact
            'TE': 0.06,     # Tight ends - skill position impact
            'WR': 0.05,     # Receivers - skill position impact
            'RB': 0.05,     # Running backs - skill position impact
            'DE': 0.04,     # Defensive ends - defensive impact
            'DT': 0.03,     # Defensive tackles - defensive impact
            'LB': 0.03,     # Linebackers - defensive impact
            'CB': 0.03,     # Cornerbacks - defensive impact
            'S': 0.03,      # Safeties - defensive impact
            'K': 0.01,      # Kickers - minimal impact
            'P': 0.01,      # Punters - minimal impact
            'LS': 0.01       # Long snappers - minimal impact
        }
        
        # PFF grade thresholds for player quality
        self.pff_thresholds = {
            'elite': 85.0,      # Elite players
            'above_average': 75.0,  # Above average players
            'average': 65.0,    # Average players
            'below_average': 55.0,  # Below average players
            'poor': 45.0        # Poor players
        }
        
        # Injury status multipliers
        self.injury_status_multipliers = {
            'OUT': 1.0,        # Definite absence
            'DOUBTFUL': 0.8,   # Likely to miss
            'QUESTIONABLE': 0.0,  # Counted as healthy
            'IR': 1.0,         # Season ending
            'PUP': 0.9,        # Physically Unable to Perform
            'NFI': 0.9         # Non-Football Injury
        }
    
    def calculate_dynamic_injury_impact(self, team_abbr: str) -> Dict:
        """
        Calculate dynamic injury impact that directly affects win probability
        Returns: {'total_impact': float, 'position_impacts': dict, 'injuries': list}
        """
        if not self.injury_data:
            self.scrape_nfl_injuries()
        
        team_city = self._get_team_city_name(team_abbr)
        if team_city not in self.injury_data:
            return {'total_impact': 0.0, 'position_impacts': {}, 'injuries': []}
        
        injuries = self.injury_data[team_city]
        total_impact = 0.0
        position_impacts = {}
        significant_injuries = []
        
        for injury in injuries:
            player = injury['player']
            position = injury['position']
            status = injury['status'].upper()
            
            # Only count OUT players as injured
            if status == 'OUT':
                # Check if injury is long-term (more than 2 months)
                if self._is_long_term_injury(injury):
                    logger.info(f"{team_abbr} {player} ({position}) - {status}: SKIPPED (long-term injury)")
                    continue
                
                # Check if injury is from beginning of season
                if self._is_season_starting_injury(injury):
                    logger.info(f"{team_abbr} {player} ({position}) - {status}: SKIPPED (season-starting injury)")
                    continue
                
                # Calculate dynamic impact
                impact = self._calculate_position_impact(player, position, team_abbr, status)
                
                if impact > 0:
                    total_impact += impact
                    position_impacts[position] = position_impacts.get(position, 0) + impact
                    significant_injuries.append({
                        'player': player,
                        'position': position,
                        'status': status,
                        'impact': impact
                    })
                    
                    logger.info(f"{team_abbr} {player} ({position}) - {status}: {impact:.2f}% win probability impact")
            
            # QUESTIONABLE players are counted as healthy
            elif status in ['QUESTIONABLE']:
                logger.info(f"{team_abbr} {player} ({position}) - {status}: 0% impact (counted as healthy)")
        
        return {
            'total_impact': total_impact,
            'position_impacts': position_impacts,
            'injuries': significant_injuries
        }
    
    def _calculate_position_impact(self, player_name: str, position: str, 
                                 team_abbr: str, injury_status: str) -> float:
        """
        Calculate position-specific impact on win probability
        """
        try:
            team_name = self._get_team_full_name(team_abbr)
            
            # Get player's PFF grade
            player_grade = self._get_player_pff_grade(team_name, player_name, position)
            
            # Get backup's PFF grade
            backup_grade = self._get_backup_pff_grade(team_name, position)
            
            # Get position impact multiplier
            position_multiplier = self.position_impact_multipliers.get(position, 0.05)
            
            # Get injury status multiplier
            status_multiplier = self.injury_status_multipliers.get(injury_status, 1.0)
            
            # Calculate impact based on position
            if position == 'QB':
                impact = self._calculate_qb_impact(player_grade, backup_grade, status_multiplier)
            elif position in ['WR', 'RB', 'TE']:
                impact = self._calculate_skill_position_impact(player_grade, backup_grade, position, status_multiplier)
            elif position in ['OT', 'OG', 'C']:
                impact = self._calculate_offensive_line_impact(player_grade, backup_grade, position, status_multiplier)
            elif position in ['DE', 'DT', 'LB', 'CB', 'S']:
                impact = self._calculate_defensive_impact(player_grade, backup_grade, position, status_multiplier)
            else:
                impact = self._calculate_special_teams_impact(player_grade, backup_grade, position, status_multiplier)
            
            return impact
            
        except Exception as e:
            logger.error(f"Error calculating position impact: {e}")
            return 0.0
    
    def _calculate_qb_impact(self, player_grade: float, backup_grade: float, status_multiplier: float) -> float:
        """
        Calculate QB impact on win probability (8-20% for elite QBs)
        """
        # Base QB impact based on player quality
        if player_grade >= self.pff_thresholds['elite']:
            base_impact = 20.0  # Elite QB out = 20% win probability drop
        elif player_grade >= self.pff_thresholds['above_average']:
            base_impact = 15.0  # Above average QB out = 15% win probability drop
        elif player_grade >= self.pff_thresholds['average']:
            base_impact = 10.0  # Average QB out = 10% win probability drop
        else:
            base_impact = 8.0   # Below average QB out = 8% win probability drop
        
        # Adjust for backup quality
        if backup_grade >= self.pff_thresholds['above_average']:
            backup_adjustment = 0.3  # Good backup reduces impact by 70%
        elif backup_grade >= self.pff_thresholds['average']:
            backup_adjustment = 0.5  # Average backup reduces impact by 50%
        else:
            backup_adjustment = 0.7  # Poor backup reduces impact by 30%
        
        # If no PFF data for backup (rookie first start), give half penalty
        if backup_grade == 65.0:  # Default backup grade
            backup_adjustment = 0.5
        
        final_impact = base_impact * backup_adjustment * status_multiplier
        
        logger.info(f"QB Impact: Player {player_grade:.1f}, Backup {backup_grade:.1f}, "
                   f"Base {base_impact:.1f}%, Backup Adj {backup_adjustment:.1f}, Final {final_impact:.1f}%")
        
        return final_impact
    
    def _calculate_skill_position_impact(self, player_grade: float, backup_grade: float, 
                                       position: str, status_multiplier: float) -> float:
        """
        Calculate skill position impact (1-5% for elite players)
        """
        # Base impact based on player quality
        if player_grade >= self.pff_thresholds['elite']:
            base_impact = 5.0   # Elite skill player out = 5% win probability drop
        elif player_grade >= self.pff_thresholds['above_average']:
            base_impact = 3.0   # Above average skill player out = 3% win probability drop
        elif player_grade >= self.pff_thresholds['average']:
            base_impact = 2.0   # Average skill player out = 2% win probability drop
        else:
            base_impact = 1.0   # Below average skill player out = 1% win probability drop
        
        # Adjust for backup quality
        if backup_grade >= self.pff_thresholds['above_average']:
            backup_adjustment = 0.4  # Good backup reduces impact by 60%
        elif backup_grade >= self.pff_thresholds['average']:
            backup_adjustment = 0.6  # Average backup reduces impact by 40%
        else:
            backup_adjustment = 0.8  # Poor backup reduces impact by 20%
        
        final_impact = base_impact * backup_adjustment * status_multiplier
        
        logger.info(f"{position} Impact: Player {player_grade:.1f}, Backup {backup_grade:.1f}, "
                   f"Base {base_impact:.1f}%, Backup Adj {backup_adjustment:.1f}, Final {final_impact:.1f}%")
        
        return final_impact
    
    def _calculate_offensive_line_impact(self, player_grade: float, backup_grade: float, 
                                       position: str, status_multiplier: float) -> float:
        """
        Calculate offensive line impact (0.5-2% for single injury)
        """
        # Position importance within offensive line
        position_importance = {
            'OT': 1.0,  # Tackles most important
            'C': 0.8,   # Center important
            'OG': 0.6   # Guards less important
        }
        
        pos_importance = position_importance.get(position, 0.6)
        
        # Base impact based on player quality
        if player_grade >= self.pff_thresholds['elite']:
            base_impact = 2.0 * pos_importance
        elif player_grade >= self.pff_thresholds['above_average']:
            base_impact = 1.5 * pos_importance
        elif player_grade >= self.pff_thresholds['average']:
            base_impact = 1.0 * pos_importance
        else:
            base_impact = 0.5 * pos_importance
        
        # Adjust for backup quality
        if backup_grade >= self.pff_thresholds['above_average']:
            backup_adjustment = 0.5
        elif backup_grade >= self.pff_thresholds['average']:
            backup_adjustment = 0.7
        else:
            backup_adjustment = 0.9
        
        final_impact = base_impact * backup_adjustment * status_multiplier
        
        logger.info(f"{position} Impact: Player {player_grade:.1f}, Backup {backup_grade:.1f}, "
                   f"Base {base_impact:.1f}%, Backup Adj {backup_adjustment:.1f}, Final {final_impact:.1f}%")
        
        return final_impact
    
    def _calculate_defensive_impact(self, player_grade: float, backup_grade: float, 
                                   position: str, status_multiplier: float) -> float:
        """
        Calculate defensive impact (minimal unless elite player)
        """
        # Base impact based on player quality
        if player_grade >= self.pff_thresholds['elite']:
            base_impact = 2.0   # Elite defender out = 2% win probability drop
        elif player_grade >= self.pff_thresholds['above_average']:
            base_impact = 1.0   # Above average defender out = 1% win probability drop
        else:
            base_impact = 0.5   # Average/below average defender out = 0.5% win probability drop
        
        # Adjust for backup quality
        if backup_grade >= self.pff_thresholds['above_average']:
            backup_adjustment = 0.3
        elif backup_grade >= self.pff_thresholds['average']:
            backup_adjustment = 0.5
        else:
            backup_adjustment = 0.7
        
        final_impact = base_impact * backup_adjustment * status_multiplier
        
        logger.info(f"{position} Impact: Player {player_grade:.1f}, Backup {backup_grade:.1f}, "
                   f"Base {base_impact:.1f}%, Backup Adj {backup_adjustment:.1f}, Final {final_impact:.1f}%")
        
        return final_impact
    
    def _calculate_special_teams_impact(self, player_grade: float, backup_grade: float, 
                                     position: str, status_multiplier: float) -> float:
        """
        Calculate special teams impact (minimal)
        """
        # Special teams have minimal impact
        base_impact = 0.5
        backup_adjustment = 0.8
        final_impact = base_impact * backup_adjustment * status_multiplier
        
        logger.info(f"{position} Impact: Player {player_grade:.1f}, Backup {backup_grade:.1f}, "
                   f"Base {base_impact:.1f}%, Backup Adj {backup_adjustment:.1f}, Final {final_impact:.1f}%")
        
        return final_impact
    
    def _is_long_term_injury(self, injury: Dict) -> bool:
        """
        Check if injury is long-term (more than 2 months)
        """
        try:
            return_date = injury.get('return_date', '')
            if not return_date:
                return False
            
            # Parse return date (assuming format like "Dec 15" or "2025-12-15")
            # For now, assume any injury with return date is not long-term
            # In real implementation, would parse dates and check if > 2 months
            return False
            
        except Exception:
            return False
    
    def _is_season_starting_injury(self, injury: Dict) -> bool:
        """
        Check if injury is from beginning of season (team already adjusted)
        """
        try:
            # Check if injury occurred before or at season start
            # For now, assume no season-starting injuries
            # In real implementation, would check injury date vs season start
            return False
            
        except Exception:
            return False
    
    def _get_player_pff_grade(self, team_name: str, player_name: str, position: str) -> float:
        """Get PFF grade for a specific player"""
        try:
            team_players = self.pff_data_system.player_grades.get(team_name, {})
            position_players = team_players.get(position, {})
            
            # Find player by name
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
            team_players = self.pff_data_system.player_grades.get(team_name, {})
            position_players = team_players.get(position, {})
            
            if len(position_players) >= 2:
                sorted_players = sorted(position_players.items(), key=lambda x: x[1], reverse=True)
                return sorted_players[1][1]  # Second best player
            elif len(position_players) == 1:
                return list(position_players.values())[0] - 15.0
            else:
                # Default backup grades
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
    
    def scrape_nfl_injuries(self) -> Dict:
        """Scrape injury data from NFL.com"""
        try:
            logger.info("Scraping NFL.com injury data...")
            
            # Import the NFL scraper
            from simple_nfl_scraper import SimpleNFLInjuryScraper
            
            scraper = SimpleNFLInjuryScraper()
            real_injury_data = scraper.scrape_all_injuries()
            
            if real_injury_data and len(real_injury_data) == 32:
                self.injury_data = real_injury_data
                self.last_update = datetime.now()
                
                logger.info(f"Successfully scraped NFL.com injury data for all 32 teams")
                return real_injury_data
            else:
                logger.warning("No real injury data found, using mock data")
                # Fallback to mock data
                mock_injury_data = {
                    'Buffalo': [
                        {'player': 'Josh Allen', 'position': 'QB', 'status': 'OUT', 'return_date': 'Oct 15', 'comment': 'Shoulder injury'},
                        {'player': 'Stefon Diggs', 'position': 'WR', 'status': 'DOUBTFUL', 'return_date': 'Sep 22', 'comment': 'Hamstring'}
                    ],
                    'Miami': [
                        {'player': 'Tua Tagovailoa', 'position': 'QB', 'status': 'QUESTIONABLE', 'return_date': 'Sep 22', 'comment': 'Healthy'},
                        {'player': 'Tyreek Hill', 'position': 'WR', 'status': 'OUT', 'return_date': 'Sep 22', 'comment': 'Ankle injury'}
                    ]
                }
                
                self.injury_data = mock_injury_data
                self.last_update = datetime.now()
                
                logger.info(f"Using mock injury data for {len(mock_injury_data)} teams")
                return mock_injury_data
            
        except Exception as e:
            logger.error(f"Error scraping NFL.com injury data: {e}")
            return {}
    
    def _get_team_city_name(self, team_abbr: str) -> str:
        """Convert team abbreviation to city name (as used by NFL.com)"""
        team_mapping = {
            'BUF': 'Buffalo', 'MIA': 'Miami', 'PHI': 'Philadelphia',
            'DAL': 'Dallas', 'NYG': 'New York Giants', 'WAS': 'Washington',
            'CHI': 'Chicago', 'DET': 'Detroit', 'GB': 'Green Bay',
            'MIN': 'Minnesota', 'ATL': 'Atlanta', 'CAR': 'Carolina',
            'NO': 'New Orleans', 'TB': 'Tampa Bay', 'ARI': 'Arizona',
            'LAR': 'Los Angeles Rams', 'SF': 'San Francisco', 'SEA': 'Seattle',
            'BAL': 'Baltimore', 'CIN': 'Cincinnati', 'CLE': 'Cleveland',
            'PIT': 'Pittsburgh', 'HOU': 'Houston', 'IND': 'Indianapolis',
            'JAX': 'Jacksonville', 'TEN': 'Tennessee', 'DEN': 'Denver',
            'KC': 'Kansas City', 'LV': 'Las Vegas', 'LAC': 'Los Angeles Chargers',
            'NE': 'New England', 'NYJ': 'New York Jets'
        }
        return team_mapping.get(team_abbr, team_abbr)
    
    def _get_team_full_name(self, team_abbr: str) -> str:
        """Convert team abbreviation to full team name (as used by PFF)"""
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
    
    def update_injury_data(self):
        """Update injury data"""
        self.scrape_cbs_injuries()
    
    def get_injury_summary(self, team_abbr: str) -> Dict:
        """Get injury summary for a team"""
        impact_data = self.calculate_dynamic_injury_impact(team_abbr)
        
        return {
            'total_impact': impact_data['total_impact'],
            'position_impacts': impact_data['position_impacts'],
            'injuries': impact_data['injuries'],
            'last_update': self.last_update
        }

if __name__ == "__main__":
    # Test the dynamic injury system
    from pff_data_system import PFFDataSystem
    
    pff_system = PFFDataSystem()
    injury_system = DynamicInjurySystem(pff_system)
    
    print("🔍 Testing Dynamic Injury System")
    print("=" * 50)
    
    # Test injury impact calculation
    test_teams = ['BUF', 'MIA', 'KC', 'SF']
    
    for team in test_teams:
        summary = injury_system.get_injury_summary(team)
        
        print(f"\n{team}:")
        print(f"  Total Win Probability Impact: {summary['total_impact']:.2f}%")
        print(f"  Position Impacts: {summary['position_impacts']}")
        print(f"  Significant Injuries: {len(summary['injuries'])}")
        
        for injury in summary['injuries']:
            print(f"    {injury['player']} ({injury['position']}) - {injury['status']}: {injury['impact']:.2f}%")
    
    print("\n✅ Dynamic Injury System Test Complete")
