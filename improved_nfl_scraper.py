"""
Improved NFL.com Injury Scraper
Properly extracts injury data for all 32 NFL teams from the injury report page
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

class ImprovedNFLInjuryScraper:
    """
    Improved scraper for NFL.com injury data that properly extracts all teams
    """
    
    def __init__(self):
        self.base_url = "https://www.nfl.com/injuries/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # All 32 NFL teams with their abbreviations
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
        
        # Reverse mapping for city names
        self.city_to_abbr = {city: abbr for abbr, city in self.team_mapping.items()}

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
            
            # Find all game sections
            game_sections = soup.find_all(['div', 'section'], class_=re.compile(r'.*game.*|.*matchup.*|.*team.*', re.I))
            
            # Also look for tables directly
            all_tables = soup.find_all('table')
            logger.info(f"Found {len(all_tables)} tables")
            
            # Process each table
            for table in all_tables:
                # Get the table's context to find team names
                team_names = self._extract_teams_from_context(table)
                
                if team_names:
                    # Extract injuries from this table
                    injuries = self._extract_injuries_from_table(table)
                    
                    # Assign injuries to each team found in this table's context
                    for team_name in team_names:
                        if team_name in injury_data:
                            injury_data[team_name] = injuries
                            logger.info(f"✅ Found {len(injuries)} injuries for {team_name}")
            
            # Log summary
            teams_with_injuries = sum(1 for injuries in injury_data.values() if injuries)
            logger.info(f"✅ Successfully processed {teams_with_injuries} teams with injury data")
            logger.info(f"✅ All 32 NFL teams have injury data (some may be empty)")
            
            return injury_data
            
        except Exception as e:
            logger.error(f"❌ Error scraping NFL injury data: {e}")
            return {}

    def _extract_teams_from_context(self, table) -> List[str]:
        """Extract team names from table context"""
        try:
            # Get all text from table and its surrounding context
            all_text = ""
            
            # Add table text
            all_text += " " + table.get_text(strip=True)
            
            # Add parent elements text (going up the DOM tree)
            current = table.parent
            depth = 0
            while current and depth < 5:  # Limit depth to avoid going too far up
                all_text += " " + current.get_text(strip=True)
                current = current.parent
                depth += 1
            
            found_teams = []
            
            # Look for team abbreviations in the text
            for abbr, city_name in self.team_mapping.items():
                if abbr in all_text and city_name not in found_teams:
                    found_teams.append(city_name)
            
            # Also look for team names directly
            team_name_patterns = {
                'Bills': 'Buffalo', 'Dolphins': 'Miami', 'Patriots': 'New England', 'Jets': 'New York Jets',
                'Ravens': 'Baltimore', 'Bengals': 'Cincinnati', 'Browns': 'Cleveland', 'Steelers': 'Pittsburgh',
                'Texans': 'Houston', 'Colts': 'Indianapolis', 'Jaguars': 'Jacksonville', 'Titans': 'Tennessee',
                'Broncos': 'Denver', 'Chiefs': 'Kansas City', 'Raiders': 'Las Vegas', 'Chargers': 'Los Angeles Chargers',
                'Cowboys': 'Dallas', 'Giants': 'New York Giants', 'Eagles': 'Philadelphia', 'Commanders': 'Washington',
                'Bears': 'Chicago', 'Lions': 'Detroit', 'Packers': 'Green Bay', 'Vikings': 'Minnesota',
                'Falcons': 'Atlanta', 'Panthers': 'Carolina', 'Saints': 'New Orleans', 'Buccaneers': 'Tampa Bay',
                'Cardinals': 'Arizona', 'Rams': 'Los Angeles Rams', '49ers': 'San Francisco', 'Seahawks': 'Seattle'
            }
            
            for team_name, city_name in team_name_patterns.items():
                if team_name in all_text and city_name not in found_teams:
                    found_teams.append(city_name)
            
            return found_teams
            
        except Exception as e:
            logger.error(f"Error extracting teams from context: {e}")
            return []

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
                        
                        # Only include if we have a player name and status
                        if player_name and game_status:
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
    # Test the improved scraper
    scraper = ImprovedNFLInjuryScraper()
    injuries = scraper.scrape_all_injuries()
    
    print(f"✅ Scraped injuries for {len(injuries)} teams")
    for team, team_injuries in injuries.items():
        if team_injuries:
            print(f"{team}: {len(team_injuries)} injuries")
            for injury in team_injuries[:3]:
                print(f"  - {injury['player']} ({injury['position']}) - {injury['status']}")
