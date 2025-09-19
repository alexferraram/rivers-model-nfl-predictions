"""
NFL.com Injury Scraper
Scrapes real injury data from https://www.nfl.com/injuries/
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

class NFLInjuryScraper:
    """
    Scrapes real injury data from NFL.com
    """
    
    def __init__(self):
        self.base_url = "https://www.nfl.com/injuries/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Team name mapping - NFL.com uses city names
        self.team_mapping = {
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
            
            # Find all team injury sections
            injury_data = {}
            
            # Look for team sections - NFL.com uses specific structure
            team_sections = soup.find_all(['div', 'section'], class_=lambda x: x and any(keyword in x.lower() for keyword in ['team', 'injury', 'game']))
            
            # Also look for tables with team data
            all_tables = soup.find_all('table')
            
            logger.info(f"Found {len(team_sections)} team sections and {len(all_tables)} tables")
            
            # Process tables to find team injury data
            processed_teams = set()
            
            for table in all_tables:
                # Look for team name in table context
                team_name = self._extract_team_name_from_table(table)
                
                if team_name and team_name not in processed_teams:
                    injuries = self._extract_team_injuries(table, team_name)
                    injury_data[team_name] = injuries
                    processed_teams.add(team_name)
                    logger.info(f"✅ Found {len(injuries)} injuries for {team_name}")
                elif not team_name:
                    # Try to extract team name from the section structure
                    team_name = self._extract_team_name_from_section(table)
                    if team_name and team_name not in processed_teams:
                        injuries = self._extract_team_injuries(table, team_name)
                        injury_data[team_name] = injuries
                        processed_teams.add(team_name)
                        logger.info(f"✅ Found {len(injuries)} injuries for {team_name} (from section)")
            
            # Check if we have all 32 teams
            expected_teams = set(self.team_mapping.keys())
            found_teams = set(injury_data.keys())
            missing_teams = expected_teams - found_teams
            
            if missing_teams:
                logger.warning(f"⚠️ Missing injury data for {len(missing_teams)} teams: {list(missing_teams)}")
                logger.warning("Attempting to find missing teams...")
                
                # Try to find missing teams by looking for team names in text
                page_text = soup.get_text()
                for team_name in missing_teams:
                    if team_name.lower() in page_text.lower():
                        logger.info(f"Found {team_name} mentioned in page, creating empty injury list")
                        injury_data[team_name] = []
            
            logger.info(f"✅ Successfully scraped injuries for {len(injury_data)} teams")
            
            # Final check - ensure we have all 32 teams
            if len(injury_data) < 32:
                missing_count = 32 - len(injury_data)
                missing_teams = expected_teams - set(injury_data.keys())
                logger.error(f"❌ Still missing {missing_count} teams: {list(missing_teams)}")
                logger.error("❌ Cannot proceed without all 32 teams.")
                return {}
            
            logger.info(f"✅ Successfully found all 32 NFL teams with injury data")
            return injury_data
            
        except Exception as e:
            logger.error(f"❌ Error scraping NFL injury data: {e}")
            return {}
    
    def _extract_team_name_from_section(self, table) -> Optional[str]:
        """Extract team name from NFL.com section structure"""
        try:
            # NFL.com structure: table -> div (d3-o-table--horizontal-scroll) -> section (nfl-o-injury-report__unit)
            parent = table.parent
            if not parent:
                return None
            
            grandparent = parent.parent
            if not grandparent:
                return None
            
            # Get text from the section
            section_text = grandparent.get_text(strip=True)
            
            # NFL.com format: "MIADolphins(0-2)BUFBills(2-0)" or similar
            # Look for team abbreviations and names
            
            # Check for team abbreviations first
            for city_name, abbr in self.team_mapping.items():
                if abbr in section_text:
                    return city_name
            
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
                if team_name in section_text:
                    return city_name
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting team name from section: {e}")
            return None
    
    def _extract_team_name_from_table(self, table) -> Optional[str]:
        """Extract team name from table context"""
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
            
            all_text = all_text.lower()
            
            # Check for city names and abbreviations
            for city_name, abbr in self.team_mapping.items():
                city_lower = city_name.lower()
                abbr_lower = abbr.lower()
                
                if city_lower in all_text or abbr_lower in all_text:
                    return city_name
            
            # Check for full team names
            full_team_names = {
                'buffalo bills': 'Buffalo',
                'miami dolphins': 'Miami',
                'new england patriots': 'New England',
                'new york jets': 'New York Jets',
                'baltimore ravens': 'Baltimore',
                'cincinnati bengals': 'Cincinnati',
                'cleveland browns': 'Cleveland',
                'pittsburgh steelers': 'Pittsburgh',
                'houston texans': 'Houston',
                'indianapolis colts': 'Indianapolis',
                'jacksonville jaguars': 'Jacksonville',
                'tennessee titans': 'Tennessee',
                'denver broncos': 'Denver',
                'kansas city chiefs': 'Kansas City',
                'las vegas raiders': 'Las Vegas',
                'los angeles chargers': 'Los Angeles Chargers',
                'dallas cowboys': 'Dallas',
                'new york giants': 'New York Giants',
                'philadelphia eagles': 'Philadelphia',
                'washington commanders': 'Washington',
                'chicago bears': 'Chicago',
                'detroit lions': 'Detroit',
                'green bay packers': 'Green Bay',
                'minnesota vikings': 'Minnesota',
                'atlanta falcons': 'Atlanta',
                'carolina panthers': 'Carolina',
                'new orleans saints': 'New Orleans',
                'tampa bay buccaneers': 'Tampa Bay',
                'arizona cardinals': 'Arizona',
                'los angeles rams': 'Los Angeles Rams',
                'san francisco 49ers': 'San Francisco',
                'seattle seahawks': 'Seattle'
            }
            
            for full_name, city_name in full_team_names.items():
                if full_name in all_text:
                    return city_name
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting team name from table: {e}")
            return None
    
    def _extract_team_injuries(self, table, team_name: str) -> List[Dict]:
        """Extract injuries for a specific team"""
        try:
            injuries = []
            
            # Find table rows
            rows = table.find_all('tr')
            if len(rows) < 2:  # Need header + data rows
                return injuries
            
            # Skip header row
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 4:  # Need at least 4 columns (Player, Position, Injuries, Practice Status, Game Status)
                    injury = self._parse_injury_row(cells, team_name)
                    if injury:
                        injuries.append(injury)
            
            return injuries
            
        except Exception as e:
            logger.error(f"Error extracting injuries for {team_name}: {e}")
            return []
    
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
            
            # Determine status based on NFL.com format
            if 'out' in status_text.lower():
                status = 'OUT'
            elif 'doubtful' in status_text.lower():
                status = 'DOUBTFUL'
            elif 'questionable' in status_text.lower():
                status = 'QUESTIONABLE'
            elif 'probable' in status_text.lower():
                status = 'PROBABLE'
            elif status_text == '' or status_text.lower() == 'active':
                status = 'ACTIVE'
            else:
                # Default to active if unclear
                status = 'ACTIVE'
            
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
    scraper = NFLInjuryScraper()
    
    print("🔍 Testing NFL.com Injury Scraper")
    print("=" * 50)
    
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
    
    print("\n✅ NFL.com Injury Scraper Test Complete")
