"""
Comprehensive NFL.com Injury Scraper
Scrapes all available injury data from NFL.com and creates entries for all 32 teams
"""

import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Optional
import re
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveNFLInjuryScraper:
    """
    Comprehensive scraper for NFL.com injury data
    """
    
    def __init__(self):
        self.base_url = "https://www.nfl.com/injuries/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # All 32 NFL teams
        self.all_teams = {
            'Buffalo': 'BUF',
            'Miami': 'MIA', 
            'New England': 'NE',
            'New York Jets': 'NYJ',
            'Baltimore': 'BAL',
            'Cincinnati': 'CIN',
            'Cleveland': 'CLE',
            'Pittsburgh': 'PIT',
            'Houston': 'HOU',
            'Indianapolis': 'IND',
            'Jacksonville': 'JAX',
            'Tennessee': 'TEN',
            'Denver': 'DEN',
            'Kansas City': 'KC',
            'Las Vegas': 'LV',
            'Los Angeles Chargers': 'LAC',
            'Dallas': 'DAL',
            'New York Giants': 'NYG',
            'Philadelphia': 'PHI',
            'Washington': 'WAS',
            'Chicago': 'CHI',
            'Detroit': 'DET',
            'Green Bay': 'GB',
            'Minnesota': 'MIN',
            'Atlanta': 'ATL',
            'Carolina': 'CAR',
            'New Orleans': 'NO',
            'Tampa Bay': 'TB',
            'Arizona': 'ARI',
            'Los Angeles Rams': 'LAR',
            'San Francisco': 'SF',
            'Seattle': 'SEA'
        }
    
    def scrape_all_injuries(self) -> Dict:
        """
        Scrape injury data for all NFL teams
        """
        logger.info("🔍 Scraping NFL.com injury data...")
        
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Initialize with empty injury lists for all 32 teams
            injury_data = {team: [] for team in self.all_teams.keys()}
            
            # Find all tables
            all_tables = soup.find_all('table')
            logger.info(f"Found {len(all_tables)} tables")
            
            # Process each table - each table contains ONE team's injuries
            # The team is determined by the order in the section context
            processed_teams = set()
            table_index = 0
            
            for table in all_tables:
                # Extract team name based on table position in section
                team_name = self._extract_team_name_by_position(table, table_index)
                
                if team_name and team_name not in processed_teams:
                    injuries = self._extract_team_injuries(table, team_name)
                    injury_data[team_name] = injuries
                    processed_teams.add(team_name)
                    logger.info(f"✅ Found {len(injuries)} injuries for {team_name}")
                    table_index += 1
            
            # Log summary
            teams_with_injuries = sum(1 for injuries in injury_data.values() if injuries)
            logger.info(f"✅ Successfully processed {teams_with_injuries} teams with injury data")
            logger.info(f"✅ All 32 NFL teams have injury data (some may be empty)")
            
            return injury_data
            
        except Exception as e:
            logger.error(f"❌ Error scraping NFL injury data: {e}")
            return {}
    
    def _extract_both_teams_from_table(self, table) -> List[str]:
        """Extract BOTH team names from table context (each table has both teams playing)"""
        try:
            # Get all text from table and its context
            all_text = ""
            
            # Add table text
            all_text += " " + table.get_text(strip=True)
            
            # Add parent elements text
            parent = table.parent
            if parent:
                all_text += " " + parent.get_text(strip=True)
                
                # Add grandparent text
                grandparent = parent.parent
                if grandparent:
                    all_text += " " + grandparent.get_text(strip=True)
            
            found_teams = []
            
            # Check for team abbreviations first (most reliable)
            for city_name, abbr in self.all_teams.items():
                if abbr in all_text and city_name not in found_teams:
                    found_teams.append(city_name)
            
            # Check for team names
            team_names = {
                'Bills': 'Buffalo',
                'Dolphins': 'Miami',
                'Patriots': 'New England',
                'Jets': 'New York Jets',
                'Ravens': 'Baltimore',
                'Bengals': 'Cincinnati',
                'Browns': 'Cleveland',
                'Steelers': 'Pittsburgh',
                'Texans': 'Houston',
                'Colts': 'Indianapolis',
                'Jaguars': 'Jacksonville',
                'Titans': 'Tennessee',
                'Broncos': 'Denver',
                'Chiefs': 'Kansas City',
                'Raiders': 'Las Vegas',
                'Chargers': 'Los Angeles Chargers',
                'Cowboys': 'Dallas',
                'Giants': 'New York Giants',
                'Eagles': 'Philadelphia',
                'Commanders': 'Washington',
                'Bears': 'Chicago',
                'Lions': 'Detroit',
                'Packers': 'Green Bay',
                'Vikings': 'Minnesota',
                'Falcons': 'Atlanta',
                'Panthers': 'Carolina',
                'Saints': 'New Orleans',
                'Buccaneers': 'Tampa Bay',
                'Cardinals': 'Arizona',
                'Rams': 'Los Angeles Rams',
                '49ers': 'San Francisco',
                'Seahawks': 'Seattle'
            }
            
            for team_name, city_name in team_names.items():
                if team_name in all_text and city_name not in found_teams:
                    found_teams.append(city_name)
            
            return found_teams
            
        except Exception as e:
            logger.error(f"Error extracting team names from table: {e}")
            return []
    
    def _extract_team_name_by_position(self, table, table_index: int) -> Optional[str]:
        """Extract team name based on table position in section"""
        try:
            # Get section context
            parent = table.parent
            if not parent:
                return None
            
            grandparent = parent.parent
            if not grandparent:
                return None
            
            # Get text from the section
            section_text = grandparent.get_text(strip=True)
            
            # Extract team names in order from section text
            # Format: "MIADolphins(0-2)BUFBills(2-0)" or similar
            teams_in_order = []
            
            # Check for team abbreviations first (most reliable)
            # Extract teams in the order they appear in the section text
            for city_name, abbr in self.all_teams.items():
                if abbr in section_text:
                    # Find the position of this abbreviation in the text
                    pos = section_text.find(abbr)
                    teams_in_order.append((pos, city_name))
            
            # Sort by position and extract city names
            teams_in_order.sort(key=lambda x: x[0])
            teams_in_order = [city_name for pos, city_name in teams_in_order]
            
            # If no abbreviations found, check for team names
            if not teams_in_order:
                team_names = {
                    'Bills': 'Buffalo', 'Dolphins': 'Miami', 'Patriots': 'New England',
                    'Jets': 'New York Jets', 'Ravens': 'Baltimore', 'Bengals': 'Cincinnati',
                    'Browns': 'Cleveland', 'Steelers': 'Pittsburgh', 'Texans': 'Houston',
                    'Colts': 'Indianapolis', 'Jaguars': 'Jacksonville', 'Titans': 'Tennessee',
                    'Broncos': 'Denver', 'Chiefs': 'Kansas City', 'Raiders': 'Las Vegas',
                    'Chargers': 'Los Angeles Chargers', 'Cowboys': 'Dallas', 'Giants': 'New York Giants',
                    'Eagles': 'Philadelphia', 'Commanders': 'Washington', 'Bears': 'Chicago',
                    'Lions': 'Detroit', 'Packers': 'Green Bay', 'Vikings': 'Minnesota',
                    'Falcons': 'Atlanta', 'Panthers': 'Carolina', 'Saints': 'New Orleans',
                    'Buccaneers': 'Tampa Bay', 'Cardinals': 'Arizona', 'Rams': 'Los Angeles Rams',
                    '49ers': 'San Francisco', 'Seahawks': 'Seattle'
                }
                
                for team_name, city_name in team_names.items():
                    if team_name in section_text:
                        teams_in_order.append(city_name)
            
            # Return team at the specified index
            if table_index < len(teams_in_order):
                return teams_in_order[table_index]
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting team name by position: {e}")
            return None
    
    def _extract_team_name_from_table(self, table) -> Optional[str]:
        """Extract team name from table context (legacy method)"""
        teams = self._extract_both_teams_from_table(table)
        return teams[0] if teams else None
    
    def _extract_team_injuries_from_mixed_table(self, table, team_name: str) -> List[Dict]:
        """Extract injuries for a specific team from a table that contains both teams' injuries"""
        try:
            injuries = []
            
            # Find table rows
            rows = table.find_all('tr')
            if len(rows) < 2:  # Need header + data rows
                return injuries
            
            # Look for the team header and extract injuries until the next team header
            current_team = None
            in_target_team_section = False
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 4:  # Need at least 4 columns
                    
                    # Check if this row is a team header
                    first_cell_text = cells[0].get_text(strip=True)
                    
                    if self._is_team_header(first_cell_text, team_name):
                        # Found our target team's section
                        current_team = team_name
                        in_target_team_section = True
                        continue
                    elif self._is_team_header(first_cell_text, None):
                        # Found a different team's section
                        if in_target_team_section:
                            break  # We've moved to the next team, stop processing
                        current_team = None
                        in_target_team_section = False
                        continue
                    
                    # If we're in the target team's section, parse the injury
                    if in_target_team_section and current_team == team_name:
                        injury = self._parse_injury_row(cells, team_name)
                        if injury:
                            injuries.append(injury)
            
            return injuries
            
        except Exception as e:
            logger.error(f"Error extracting injuries for {team_name}: {e}")
            return []
    
    def _extract_team_injuries(self, table, team_name: str) -> List[Dict]:
        """Extract injuries for a specific team from a table that contains only that team's injuries (legacy method)"""
        try:
            injuries = []
            
            # Find table rows
            rows = table.find_all('tr')
            if len(rows) < 2:  # Need header + data rows
                return injuries
            
            # Skip header row (first row)
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 4:  # Need at least 4 columns
                    injury = self._parse_injury_row(cells, team_name)
                    if injury:
                        injuries.append(injury)
            
            return injuries
            
        except Exception as e:
            logger.error(f"Error extracting injuries for {team_name}: {e}")
            return []
    
    def _is_team_header(self, text: str, target_team: Optional[str]) -> bool:
        """Check if text is a team header"""
        if not text:
            return False
        
        # Check for team abbreviations
        for city_name, abbr in self.all_teams.items():
            if abbr in text:
                if target_team is None or city_name == target_team:
                    return True
        
        # Check for team names
        team_names = {
            'Bills': 'Buffalo', 'Dolphins': 'Miami', 'Patriots': 'New England',
            'Jets': 'New York Jets', 'Ravens': 'Baltimore', 'Bengals': 'Cincinnati',
            'Browns': 'Cleveland', 'Steelers': 'Pittsburgh', 'Texans': 'Houston',
            'Colts': 'Indianapolis', 'Jaguars': 'Jacksonville', 'Titans': 'Tennessee',
            'Broncos': 'Denver', 'Chiefs': 'Kansas City', 'Raiders': 'Las Vegas',
            'Chargers': 'Los Angeles Chargers', 'Cowboys': 'Dallas', 'Giants': 'New York Giants',
            'Eagles': 'Philadelphia', 'Commanders': 'Washington', 'Bears': 'Chicago',
            'Lions': 'Detroit', 'Packers': 'Green Bay', 'Vikings': 'Minnesota',
            'Falcons': 'Atlanta', 'Panthers': 'Carolina', 'Saints': 'New Orleans',
            'Buccaneers': 'Tampa Bay', 'Cardinals': 'Arizona', 'Rams': 'Los Angeles Rams',
            '49ers': 'San Francisco', 'Seahawks': 'Seattle'
        }
        
        for team_name, city_name in team_names.items():
            if team_name in text:
                if target_team is None or city_name == target_team:
                    return True
        
        return False
    
    def _parse_injury_row(self, cells, team_name: str) -> Optional[Dict]:
        """Parse a single injury row"""
        try:
            # Extract data from cells
            player_name = cells[0].get_text(strip=True)
            position = cells[1].get_text(strip=True)
            injury_type = cells[2].get_text(strip=True)
            practice_status = cells[3].get_text(strip=True)
            game_status = cells[4].get_text(strip=True) if len(cells) > 4 else ""
            
            # Parse game status
            status_info = self._parse_game_status(game_status)
            
            if status_info:
                return {
                    'player': player_name,
                    'position': position,
                    'injury_type': injury_type,
                    'practice_status': practice_status,
                    'game_status': game_status,
                    'status': status_info['status'],
                    'team': team_name
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing injury row: {e}")
            return None
    
    def _parse_game_status(self, status_text: str) -> Optional[Dict]:
        """Parse game status text"""
        try:
            status_text = status_text.strip()
            
            # If game status is empty, treat as healthy (not injured)
            if status_text == '':
                return None  # Don't include in injury list
            
            # Determine status based on NFL.com format
            if 'out' in status_text.lower():
                status = 'OUT'
            elif 'doubtful' in status_text.lower():
                status = 'DOUBTFUL'
            elif 'questionable' in status_text.lower():
                status = 'QUESTIONABLE'
            elif 'probable' in status_text.lower():
                status = 'PROBABLE'
            elif status_text.lower() == 'active':
                return None  # Active players are not injured
            else:
                # Default to not including if unclear
                return None
            
            return {
                'status': status
            }
            
        except Exception as e:
            logger.error(f"Error parsing game status: {e}")
            return None
    
    def get_team_injuries(self, team_name: str) -> List[Dict]:
        """Get injuries for a specific team"""
        all_injuries = self.scrape_all_injuries()
        return all_injuries.get(team_name, [])
    
    def get_injury_summary(self, team_name: str) -> Dict:
        """Get injury summary for a team"""
        injuries = self.get_team_injuries(team_name)
        
        if not injuries:
            return {
                'total_injuries': 0,
                'significant_injuries': 0,
                'injuries': []
            }
        
        # Count significant injuries (OUT, DOUBTFUL)
        significant_injuries = [
            inj for inj in injuries 
            if inj['status'] in ['OUT', 'DOUBTFUL']
        ]
        
        return {
            'total_injuries': len(injuries),
            'significant_injuries': len(significant_injuries),
            'injuries': injuries,
            'significant_injuries_list': significant_injuries
        }

if __name__ == "__main__":
    # Test the scraper
    scraper = ComprehensiveNFLInjuryScraper()
    
    print("🔍 Testing Comprehensive NFL.com Injury Scraper")
    print("=" * 60)
    
    # Test with Buffalo Bills
    bills_injuries = scraper.get_team_injuries('Buffalo')
    print(f"\nBuffalo Bills Injuries ({len(bills_injuries)}):")
    for injury in bills_injuries:
        print(f"  {injury['player']} ({injury['position']}) - {injury['status']}: {injury['game_status']}")
    
    # Test with Miami Dolphins
    dolphins_injuries = scraper.get_team_injuries('Miami')
    print(f"\nMiami Dolphins Injuries ({len(dolphins_injuries)}):")
    for injury in dolphins_injuries:
        print(f"  {injury['player']} ({injury['position']}) - {injury['status']}: {injury['game_status']}")
    
    # Test with a team that might not have injuries
    steelers_injuries = scraper.get_team_injuries('Pittsburgh')
    print(f"\nPittsburgh Steelers Injuries ({len(steelers_injuries)}):")
    for injury in steelers_injuries:
        print(f"  {injury['player']} ({injury['position']}) - {injury['status']}: {injury['game_status']}")
    
    print("\n✅ Comprehensive NFL.com Injury Scraper Test Complete")
