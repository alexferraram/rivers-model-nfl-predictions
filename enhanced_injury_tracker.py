"""
Enhanced Injury Tracker with PFF Integration
Uses PFF grades to calculate dynamic injury penalties
"""

import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pff_data_system import PFFDataSystem

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedInjuryTracker:
    """
    Enhanced injury tracker that uses PFF grades for dynamic penalties
    """
    
    def __init__(self):
        self.pff_system = PFFDataSystem()
        self.injury_data = {}
        self.last_update = None
        self.update_frequency = 3600  # 1 hour
        
        # Team mapping for CBS Sports
        self.team_mapping = {
            'Buffalo Bills': 'BUF',
            'Miami Dolphins': 'MIA',
            'Philadelphia Eagles': 'PHI',
            'Los Angeles Rams': 'LA',
            'Arizona Cardinals': 'ARI',
            'Atlanta Falcons': 'ATL',
            'Carolina Panthers': 'CAR',
            'Chicago Bears': 'CHI',
            'Cincinnati Bengals': 'CIN',
            'Cleveland Browns': 'CLE',
            'Dallas Cowboys': 'DAL',
            'Denver Broncos': 'DEN',
            'Detroit Lions': 'DET',
            'Green Bay Packers': 'GB',
            'Houston Texans': 'HOU',
            'Indianapolis Colts': 'IND',
            'Jacksonville Jaguars': 'JAX',
            'Kansas City Chiefs': 'KC',
            'Las Vegas Raiders': 'LV',
            'Los Angeles Chargers': 'LAC',
            'Minnesota Vikings': 'MIN',
            'New England Patriots': 'NE',
            'New Orleans Saints': 'NO',
            'New York Giants': 'NYG',
            'New York Jets': 'NYJ',
            'Pittsburgh Steelers': 'PIT',
            'San Francisco 49ers': 'SF',
            'Seattle Seahawks': 'SEA',
            'Tampa Bay Buccaneers': 'TB',
            'Tennessee Titans': 'TEN',
            'Washington Commanders': 'WAS'
        }
    
    def scrape_cbs_injuries(self):
        """
        Scrape injury data from CBS Sports NFL injuries page
        """
        try:
            url = "https://www.cbssports.com/nfl/injuries/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse injury data from CBS Sports
            injury_data = {}
            
            # Find tables with injury data
            injury_tables = soup.find_all('table')
            
            for i, table in enumerate(injury_tables):
                team_name = self._extract_cbs_team_name(table, i)
                if team_name:
                    injuries = self._parse_cbs_injury_table(table)
                    if injuries:  # Only add if we found injuries
                        injury_data[team_name] = injuries
            
            self.injury_data = injury_data
            self.last_update = datetime.now()
            
            logger.info(f"Successfully scraped CBS injury data for {len(injury_data)} teams")
            return injury_data
            
        except Exception as e:
            logger.error(f"Error scraping CBS injuries: {e}")
            # Fallback to mock data if scraping fails
            return self._get_fallback_injury_data()
    
    def _extract_cbs_team_name(self, table, table_index=None):
        """Extract team name from CBS Sports injury table"""
        try:
            # Use table index approach (most reliable)
            if table_index is not None:
                team_name = self._get_team_by_index(table_index)
                if team_name:
                    return team_name
            
            # Fallback methods
            caption = table.find('caption')
            if caption:
                team_text = caption.get_text().strip()
                if team_text and len(team_text) > 3:
                    return team_text
            
            return None
                    
        except Exception as e:
            logger.debug(f"Error extracting CBS team name: {e}")
            return None
    
    def _get_team_by_index(self, index):
        """Get team name by table index (32 teams in order)"""
        teams = [
            'Arizona Cardinals', 'Atlanta Falcons', 'Baltimore Ravens', 'Buffalo Bills',
            'Carolina Panthers', 'Chicago Bears', 'Cincinnati Bengals', 'Cleveland Browns',
            'Dallas Cowboys', 'Denver Broncos', 'Detroit Lions', 'Green Bay Packers',
            'Houston Texans', 'Indianapolis Colts', 'Jacksonville Jaguars', 'Kansas City Chiefs',
            'Las Vegas Raiders', 'Los Angeles Chargers', 'Los Angeles Rams', 'Miami Dolphins',
            'Minnesota Vikings', 'New England Patriots', 'New Orleans Saints', 'New York Giants',
            'New York Jets', 'Philadelphia Eagles', 'Pittsburgh Steelers', 'San Francisco 49ers',
            'Seattle Seahawks', 'Tampa Bay Buccaneers', 'Tennessee Titans', 'Washington Commanders'
        ]
        
        if 0 <= index < len(teams):
            return teams[index]
        
        return None
    
    def _parse_cbs_injury_table(self, table):
        """Parse CBS Sports injury table"""
        injuries = []
        try:
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 4:  # CBS has: Player, Position, Updated, Injury, Injury Status
                    player_name = cells[0].get_text().strip()
                    position = cells[1].get_text().strip()
                    updated_date = cells[2].get_text().strip()
                    injury_type = cells[3].get_text().strip()
                    injury_status = cells[4].get_text().strip() if len(cells) > 4 else ""
                    
                    # Only include significant injuries (OUT status only for dynamic penalties)
                    if injury_status and any(status in injury_status.upper() for status in ['OUT', 'DOUBTFUL', 'QUESTIONABLE', 'IR', 'INJURED RESERVE']):
                        injuries.append({
                            'player': player_name,
                            'position': position,
                            'status': injury_status,
                            'injury_type': injury_type,
                            'updated_date': updated_date,
                            'timestamp': datetime.now()
                        })
        except Exception as e:
            logger.error(f"Error parsing CBS injury table: {e}")
        
        return injuries
    
    def _get_fallback_injury_data(self):
        """Fallback injury data if CBS scraping fails"""
        mock_injury_data = {
            'Buffalo Bills': [
                {'player': 'Josh Allen', 'position': 'QB', 'status': 'Questionable', 'return_date': 'Sep 22', 'comment': 'Shoulder injury'},
                {'player': 'Stefon Diggs', 'position': 'WR', 'status': 'Probable', 'return_date': 'Sep 22', 'comment': 'Minor ankle'}
            ],
            'Miami Dolphins': [
                {'player': 'Tua Tagovailoa', 'position': 'QB', 'status': 'Probable', 'return_date': 'Sep 22', 'comment': 'Concussion protocol'},
                {'player': 'Tyreek Hill', 'position': 'WR', 'status': 'Questionable', 'return_date': 'Sep 22', 'comment': 'Hamstring'}
            ]
        }
        
        self.injury_data = mock_injury_data
        self.last_update = datetime.now()
        
        logger.info(f"Using fallback injury data for {len(mock_injury_data)} teams")
        return mock_injury_data
    
    def get_enhanced_injury_impact(self, team_abbr: str, position_type: str = None) -> float:
        """
        Get enhanced injury impact using PFF grades
        Only counts 'OUT' and 'DOUBTFUL' status as injured
        QUESTIONABLE players are counted as healthy (active)
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
                # Use PFF-based dynamic penalty with starter/backup analysis
                impact = self._calculate_dynamic_pff_injury_penalty(
                    player, position, team_abbr, status
                )
                total_impact += impact
                logger.info(f"{team_abbr} {player} ({position}) - {status}: {impact:.1f} points")
            
            # QUESTIONABLE players are counted as healthy (no penalty)
            elif status in ['QUESTIONABLE']:
                logger.info(f"{team_abbr} {player} ({position}) - {status}: 0 points (counted as healthy)")
            
            elif status in ['IR', 'INJURED RESERVE']:
                # IR players get full traditional penalty
                traditional_penalty = self._get_traditional_penalty(position)
                total_impact += traditional_penalty
                logger.info(f"{team_abbr} {player} ({position}) - {status}: {traditional_penalty:.1f} points (IR)")
        
        return total_impact
    
    def _get_traditional_penalty(self, position: str) -> float:
        """Traditional injury penalties for non-OUT statuses"""
        traditional_penalties = {
            'QB': -20.0,
            'RB': -12.0,
            'WR': -12.0,
            'TE': -10.0,
            'OT': -8.0,
            'OG': -7.0,
            'C': -7.0,
            'DE': -7.0,
            'DT': -7.0,
            'LB': -7.0,
            'CB': -7.0,
            'S': -7.0,
            'K': -3.0,
            'P': -2.0,
            'LS': -1.0
        }
        return traditional_penalties.get(position, -5.0)
    
    def _calculate_dynamic_pff_injury_penalty(self, player_name: str, position: str, 
                                            team_abbr: str, injury_status: str) -> float:
        """
        Calculate dynamic injury penalty based on PFF grades of starter and backup
        """
        try:
            team_name = self._get_team_full_name(team_abbr)
            
            # Get starter's PFF grade
            starter_grade = self._get_player_pff_grade(team_name, player_name, position)
            
            # Get backup's PFF grade
            backup_grade = self._get_backup_pff_grade(team_name, position)
            
            # Calculate penalty based on grade difference
            grade_difference = starter_grade - backup_grade
            
            # Base penalty by position
            base_penalty = self._get_base_penalty(position)
            
            # Dynamic penalty calculation
            if grade_difference > 20:  # Elite starter, poor backup
                dynamic_penalty = base_penalty * 1.5
            elif grade_difference > 10:  # Good starter, average backup
                dynamic_penalty = base_penalty * 1.2
            elif grade_difference > 0:  # Starter better than backup
                dynamic_penalty = base_penalty * 1.0
            elif grade_difference > -10:  # Similar quality
                dynamic_penalty = base_penalty * 0.8
            else:  # Backup might be better
                dynamic_penalty = base_penalty * 0.5
            
            # Apply injury status multiplier
            if injury_status == 'OUT':
                status_multiplier = 1.0
            elif injury_status == 'DOUBTFUL':
                status_multiplier = 0.7  # Doubtful players might play
            
            final_penalty = dynamic_penalty * status_multiplier
            
            logger.info(f"{team_abbr} {player_name} ({position}) - Starter: {starter_grade:.1f}, Backup: {backup_grade:.1f}, Penalty: {final_penalty:.1f}")
            
            return final_penalty
            
        except Exception as e:
            logger.error(f"Error calculating dynamic PFF injury penalty: {e}")
            return self._get_traditional_penalty(position)
    
    def _get_player_pff_grade(self, team_name: str, player_name: str, position: str) -> float:
        """Get PFF grade for a specific player"""
        try:
            # Get team player grades from PFF system
            team_players = self.pff_system.player_grades.get(team_name, {})
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
            team_players = self.pff_system.player_grades.get(team_name, {})
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
    
    def _get_base_penalty(self, position: str) -> float:
        """Base penalty by position"""
        base_penalties = {
            'QB': -30.0,    # Highest impact
            'RB': -15.0,
            'WR': -15.0,
            'TE': -12.0,
            'OT': -10.0,
            'OG': -8.0,
            'C': -8.0,
            'DE': -10.0,
            'DT': -8.0,
            'LB': -8.0,
            'CB': -10.0,
            'S': -8.0,
            'K': -4.0,
            'P': -3.0,
            'LS': -2.0
        }
        return base_penalties.get(position, -6.0)
    
    def _get_team_full_name(self, team_abbr: str) -> str:
        """Convert team abbreviation to full name"""
        team_mapping = {
            'BUF': 'Buffalo Bills',
            'MIA': 'Miami Dolphins',
            'PHI': 'Philadelphia Eagles',
            'LA': 'Los Angeles Rams',
            'ARI': 'Arizona Cardinals',
            'ATL': 'Atlanta Falcons',
            'CAR': 'Carolina Panthers',
            'CHI': 'Chicago Bears',
            'CIN': 'Cincinnati Bengals',
            'CLE': 'Cleveland Browns',
            'DAL': 'Dallas Cowboys',
            'DEN': 'Denver Broncos',
            'DET': 'Detroit Lions',
            'GB': 'Green Bay Packers',
            'HOU': 'Houston Texans',
            'IND': 'Indianapolis Colts',
            'JAX': 'Jacksonville Jaguars',
            'KC': 'Kansas City Chiefs',
            'LV': 'Las Vegas Raiders',
            'LAC': 'Los Angeles Chargers',
            'MIN': 'Minnesota Vikings',
            'NE': 'New England Patriots',
            'NO': 'New Orleans Saints',
            'NYG': 'New York Giants',
            'NYJ': 'New York Jets',
            'PIT': 'Pittsburgh Steelers',
            'SF': 'San Francisco 49ers',
            'SEA': 'Seattle Seahawks',
            'TB': 'Tampa Bay Buccaneers',
            'TEN': 'Tennessee Titans',
            'WAS': 'Washington Commanders'
        }
        return team_mapping.get(team_abbr, team_abbr)
    
    def get_injury_summary(self, team_abbr: str) -> Dict:
        """Get detailed injury summary for a team"""
        team_name = self._get_team_full_name(team_abbr)
        if team_name not in self.injury_data:
            return {'total_impact': 0, 'injuries': []}
        
        injuries = self.injury_data[team_name]
        total_impact = self.get_enhanced_injury_impact(team_abbr)
        
        return {
            'total_impact': total_impact,
            'injuries': injuries,
            'out_count': len([i for i in injuries if 'OUT' in i['status'].upper()]),
            'questionable_count': len([i for i in injuries if 'QUESTIONABLE' in i['status'].upper()]),
            'ir_count': len([i for i in injuries if 'IR' in i['status'].upper()])
        }
    
    def update_injury_data(self):
        """Update injury data if needed"""
        if (self.last_update is None or 
            datetime.now() - self.last_update > timedelta(seconds=self.update_frequency)):
            self.scrape_cbs_injuries()

if __name__ == "__main__":
    # Test the enhanced injury tracker
    tracker = EnhancedInjuryTracker()
    
    print("🔍 Testing Enhanced Injury Tracker with PFF Integration")
    print("=" * 60)
    
    # Test injury data scraping
    injury_data = tracker.scrape_cbs_injuries()
    print(f"Scraped injury data for {len(injury_data)} teams")
    
    # Test enhanced injury impact
    test_teams = ['BUF', 'MIA', 'PHI', 'LA']
    
    print("\n🏥 Testing Enhanced Injury Impact:")
    for team in test_teams:
        impact = tracker.get_enhanced_injury_impact(team)
        summary = tracker.get_injury_summary(team)
        print(f"   {team}: {impact:.1f} points")
        print(f"     OUT: {summary['out_count']}, Questionable: {summary['questionable_count']}, IR: {summary['ir_count']}")
    
    print("\n✅ Enhanced Injury Tracker Test Complete")
