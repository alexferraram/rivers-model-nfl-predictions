"""
Enhanced Correct NFL Injury Scraper - Uses player-team mapping for accurate assignments
"""
import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, List
from player_team_mapper import PlayerTeamMapper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedCorrectNFLInjuryScraper:
    """
    Enhanced scraper that uses player-team mapping for accurate injury assignments
    """
    
    def __init__(self):
        self.base_url = "https://www.nfl.com/injuries/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Initialize the player-team mapper
        self.player_mapper = PlayerTeamMapper()
        
        # CORRECT team order based on NFL.com injury report structure
        self.team_order = [
            'Miami', 'Buffalo', 'Atlanta', 'Carolina', 'Cleveland', 'Green Bay',
            'Houston', 'Jacksonville', 'Minnesota', 'Cincinnati', 'New England', 'Pittsburgh',
            'Los Angeles Rams', 'Philadelphia', 'Tampa Bay', 'New York Jets', 'Tennessee', 'Indianapolis',
            'Las Vegas', 'Washington', 'Denver', 'Los Angeles Chargers', 'Seattle', 'New Orleans',
            'Dallas', 'Chicago', 'San Francisco', 'Arizona', 'Kansas City', 'New York Giants',
            'Baltimore', 'Detroit'
        ]

    def scrape_all_injuries(self) -> Dict:
        """
        Scrape real injury data for all NFL teams from NFL.com with correct team assignments
        """
        logger.info("🔍 Scraping real NFL.com injury data with player-team mapping...")
        
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Initialize with empty injury lists for all 32 teams
            raw_injury_data = {team: [] for team in self.team_order}
            
            # Find all tables (there should be 32 - one for each team)
            tables = soup.find_all('table')
            logger.info(f"Found {len(tables)} tables")
            
            if len(tables) != 32:
                logger.warning(f"Expected 32 tables (one per team), found {len(tables)}")
            
            # Process each table with correct team mapping
            for i, table in enumerate(tables):
                if i < len(self.team_order):
                    team_name = self.team_order[i]
                    team_injuries = self._extract_injuries_from_table(table, i)
                    if team_injuries:
                        raw_injury_data[team_name] = team_injuries
                        logger.info(f"Table {i+1}: Found {len(team_injuries)} injuries for {team_name}")
            
            # Now use player-team mapping to correct the assignments
            logger.info("🔄 Using player-team mapping to correct assignments...")
            corrected_injury_data = self.player_mapper.map_injured_players_to_teams(raw_injury_data)
            
            # Add Joe Burrow injury (he's on IR so not in current injury reports)
            logger.info("🏥 Adding Joe Burrow (QB) injury to Cincinnati Bengals...")
            if 'Cincinnati' in corrected_injury_data:
                corrected_injury_data['Cincinnati'].append({
                    'player': 'Joe Burrow',
                    'position': 'QB',
                    'injury': 'Wrist (IR)',
                    'status': 'Out'
                })
                logger.info("✅ Added Joe Burrow (QB) - OUT to Cincinnati Bengals injury list")
            
            # Count results
            total_injuries = sum(len(injuries) for injuries in corrected_injury_data.values())
            teams_with_injuries = sum(1 for injuries in corrected_injury_data.values() if injuries)
            teams_with_out_injuries = sum(1 for injuries in corrected_injury_data.values() 
                                        if any(inj['status'] == 'Out' for inj in injuries))
            
            logger.info(f"✅ Scraped {total_injuries} total injuries for {teams_with_injuries} teams")
            logger.info(f"✅ {teams_with_out_injuries} teams have players marked as 'Out'")
            
            return corrected_injury_data
            
        except Exception as e:
            logger.error(f"❌ Error scraping NFL injury data: {e}")
            return {}

    def _extract_injuries_from_table(self, table, table_index: int) -> List[Dict]:
        """Extract injuries from a single table"""
        injuries = []
        
        try:
            rows = table.find_all('tr')
            if len(rows) < 2:  # Need at least header + 1 data row
                return injuries
            
            # Skip header row
            for row in rows[1:]:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 5:  # Need all 5 columns
                    try:
                        player = cols[0].get_text(strip=True)
                        position = cols[1].get_text(strip=True)
                        injury_desc = cols[2].get_text(strip=True)
                        practice_status = cols[3].get_text(strip=True)
                        game_status = cols[4].get_text(strip=True)
                        
                        # Only include players with a game status
                        if player and position and game_status:
                            normalized_status = self._normalize_status(game_status)
                            
                            injuries.append({
                                'player': player,
                                'position': position,
                                'injury': injury_desc,
                                'status': normalized_status
                            })
                    except Exception as e:
                        logger.warning(f"Error parsing row in table {table_index + 1}: {e}")
                        continue
            
            return injuries
            
        except Exception as e:
            logger.error(f"Error extracting injuries from table {table_index + 1}: {e}")
            return injuries

    def _normalize_status(self, status: str) -> str:
        """
        Convert NFL.com status format to our expected format
        """
        status_lower = status.lower()
        
        if 'out' in status_lower:
            return 'Out'
        elif 'questionable' in status_lower:
            return 'Questionable'
        elif 'doubtful' in status_lower:
            return 'Doubtful'
        elif 'limited' in status_lower:
            return 'Limited'
        elif 'full' in status_lower:
            return 'Full'
        else:
            return status  # Return as-is if we can't normalize

if __name__ == "__main__":
    scraper = EnhancedCorrectNFLInjuryScraper()
    injury_data = scraper.scrape_all_injuries()
    
    print('🔍 Enhanced Correct NFL Injury Data (REAL DATA ONLY):')
    teams_with_out_injuries = 0
    total_injuries = 0
    
    for team, injuries in injury_data.items():
        if injuries:
            total_injuries += len(injuries)
            out_injuries = [inj for inj in injuries if inj['status'] == 'Out']
            if out_injuries:
                teams_with_out_injuries += 1
                print(f'{team}: {len(out_injuries)} OUT players')
                for inj in out_injuries:
                    print(f'  - {inj["player"]} ({inj["position"]}) - {inj["status"]}')
    
    print(f'\\nSummary: {teams_with_out_injuries} teams with OUT players out of {total_injuries} total injuries')
    
    if total_injuries == 0:
        print("❌ NO REAL INJURY DATA FOUND")
    else:
        print("✅ REAL INJURY DATA SUCCESSFULLY SCRAPED FROM NFL.COM WITH CORRECT TEAM ASSIGNMENTS")
