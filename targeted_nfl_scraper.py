"""
Targeted NFL.com Injury Scraper
Based on the actual HTML structure of the NFL.com injury report page
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

class TargetedNFLInjuryScraper:
    """
    Targeted scraper based on the actual NFL.com injury report structure
    """
    
    def __init__(self):
        self.base_url = "https://www.nfl.com/injuries/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Team mapping from NFL.com format to our format
        self.team_mapping = {
            'BUF': 'Buffalo', 'MIA': 'Miami', 'NE': 'New England', 'NYJ': 'New York Jets',
            'BAL': 'Baltimore', 'CIN': 'Cincinnati', 'CLE': 'Cleveland', 'PIT': 'Pittsburgh',
            'HOU': 'Houston', 'IND': 'Indianapolis', 'JAX': 'Jacksonville', 'TEN': 'Tennessee',
            'DEN': 'Denver', 'KC': 'Kansas City', 'LV': 'Las Vegas', 'LAC': 'Los Angeles Chargers',
            'DAL': 'Dallas', 'NYG': 'New York Giants', 'PHI': 'Philadelphia', 'WAS': 'Washington',
            'CHI': 'Chicago', 'DET': 'Detroit', 'GB': 'Green Bay', 'MIN': 'Minnesota',
            'ATL': 'Atlanta', 'CAR': 'Carolina', 'NO': 'New Orleans', 'TB': 'Tampa Bay',
            'ARI': 'Arizona', 'LA': 'Los Angeles Rams', 'SF': 'San Francisco', 'SEA': 'Seattle'
        }

    def scrape_all_injuries(self) -> Dict:
        """
        Scrape injury data for all NFL teams from the injury report page
        """
        logger.info("🔍 Scraping NFL.com injury data...")
        
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Initialize with empty injury lists for all 32 teams
            injury_data = {city: [] for city in self.team_mapping.values()}
            
            # Find all game sections - look for sections that contain team matchups
            game_sections = soup.find_all(['div', 'section'], string=re.compile(r'[A-Z]{2,3}\s+[A-Z]{2,3}'))
            
            # Also look for all tables and process them systematically
            all_tables = soup.find_all('table')
            logger.info(f"Found {len(all_tables)} tables")
            
            # Process tables in pairs (each game has 2 tables - one for each team)
            table_index = 0
            while table_index < len(all_tables):
                # Get the next two tables (should be for the same game)
                if table_index + 1 < len(all_tables):
                    table1 = all_tables[table_index]
                    table2 = all_tables[table_index + 1]
                    
                    # Extract team names and injuries for both tables
                    team1, injuries1 = self._extract_team_and_injuries(table1, table_index)
                    team2, injuries2 = self._extract_team_and_injuries(table2, table_index + 1)
                    
                    if team1 and injuries1:
                        injury_data[team1] = injuries1
                        logger.info(f"✅ Found {len(injuries1)} injuries for {team1}")
                    
                    if team2 and injuries2:
                        injury_data[team2] = injuries2
                        logger.info(f"✅ Found {len(injuries2)} injuries for {team2}")
                    
                    table_index += 2
                else:
                    # Single table remaining
                    team, injuries = self._extract_team_and_injuries(all_tables[table_index], table_index)
                    if team and injuries:
                        injury_data[team] = injuries
                        logger.info(f"✅ Found {len(injuries)} injuries for {team}")
                    table_index += 1
            
            # Log summary
            teams_with_injuries = sum(1 for injuries in injury_data.values() if injuries)
            logger.info(f"✅ Successfully processed {teams_with_injuries} teams with injury data")
            
            return injury_data
            
        except Exception as e:
            logger.error(f"❌ Error scraping NFL injury data: {e}")
            return {}

    def _extract_team_and_injuries(self, table, table_index: int) -> tuple:
        """Extract team name and injuries from a table"""
        try:
            # Get team name from table context
            team_name = self._get_team_from_table_context(table, table_index)
            
            if not team_name:
                return None, []
            
            # Extract injuries from table
            injuries = self._extract_injuries_from_table(table)
            
            return team_name, injuries
            
        except Exception as e:
            logger.error(f"Error extracting team and injuries: {e}")
            return None, []

    def _get_team_from_table_context(self, table, table_index: int) -> Optional[str]:
        """Get team name from table context using a more systematic approach"""
        try:
            # Look at the table's parent elements for team information
            current = table.parent
            context_text = ""
            depth = 0
            
            # Go up the DOM tree to find team context
            while current and depth < 5:
                context_text += " " + current.get_text(strip=True)
                current = current.parent
                depth += 1
            
            # Look for team abbreviations first (most reliable)
            for abbr, city_name in self.team_mapping.items():
                if abbr in context_text:
                    return city_name
            
            # Look for team names
            team_names = {
                'Bills': 'Buffalo', 'Dolphins': 'Miami', 'Patriots': 'New England', 'Jets': 'New York Jets',
                'Ravens': 'Baltimore', 'Bengals': 'Cincinnati', 'Browns': 'Cleveland', 'Steelers': 'Pittsburgh',
                'Texans': 'Houston', 'Colts': 'Indianapolis', 'Jaguars': 'Jacksonville', 'Titans': 'Tennessee',
                'Broncos': 'Denver', 'Chiefs': 'Kansas City', 'Raiders': 'Las Vegas', 'Chargers': 'Los Angeles Chargers',
                'Cowboys': 'Dallas', 'Giants': 'New York Giants', 'Eagles': 'Philadelphia', 'Commanders': 'Washington',
                'Bears': 'Chicago', 'Lions': 'Detroit', 'Packers': 'Green Bay', 'Vikings': 'Minnesota',
                'Falcons': 'Atlanta', 'Panthers': 'Carolina', 'Saints': 'New Orleans', 'Buccaneers': 'Tampa Bay',
                'Cardinals': 'Arizona', 'Rams': 'Los Angeles Rams', '49ers': 'San Francisco', 'Seahawks': 'Seattle'
            }
            
            for team_name, city_name in team_names.items():
                if team_name in context_text:
                    return city_name
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting team from table context: {e}")
            return None

    def _extract_injuries_from_table(self, table) -> List[Dict]:
        """Extract injury data from a table"""
        try:
            injuries = []
            
            # Find all rows in the table
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 4:  # Need at least player, position, injury, status
                    try:
                        # Extract player name (usually first cell with a link)
                        player_cell = cells[0]
                        player_link = player_cell.find('a')
                        if player_link:
                            player_name = player_link.get_text(strip=True)
                        else:
                            player_name = player_cell.get_text(strip=True)
                        
                        # Extract position (usually second cell)
                        position = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                        
                        # Extract injury description (usually third cell)
                        injury_desc = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                        
                        # Extract game status (usually last cell)
                        game_status = cells[-1].get_text(strip=True) if cells else ""
                        
                        # Only include if we have a player name and status, and it's not a header
                        if (player_name and game_status and 
                            player_name != "Player" and 
                            game_status in ['Out', 'Doubtful', 'Questionable', 'Probable']):
                            
                            injury = {
                                'player': player_name,
                                'position': position,
                                'injury': injury_desc,
                                'status': game_status
                            }
                            injuries.append(injury)
                            
                    except Exception as e:
                        logger.debug(f"Error parsing injury row: {e}")
                        continue
            
            return injuries
            
        except Exception as e:
            logger.error(f"Error extracting injuries from table: {e}")
            return []

if __name__ == "__main__":
    # Test the targeted scraper
    scraper = TargetedNFLInjuryScraper()
    injuries = scraper.scrape_all_injuries()
    
    print(f"✅ Scraped injuries for {len(injuries)} teams")
    for team, team_injuries in injuries.items():
        if team_injuries:
            print(f"{team}: {len(team_injuries)} injuries")
            for injury in team_injuries[:3]:
                print(f"  - {injury['player']} ({injury['position']}) - {injury['status']}")
