"""
Player Team Mapper - Maps injured players to their correct teams using NFL.com rosters
"""
import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Set
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PlayerTeamMapper:
    """
    Maps injured players to their correct teams using NFL.com roster data
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Team mapping from NFL.com format to our format
        self.team_mapping = {
            'Arizona Cardinals': 'Arizona',
            'Atlanta Falcons': 'Atlanta', 
            'Baltimore Ravens': 'Baltimore',
            'Buffalo Bills': 'Buffalo',
            'Carolina Panthers': 'Carolina',
            'Chicago Bears': 'Chicago',
            'Cincinnati Bengals': 'Cincinnati',
            'Cleveland Browns': 'Cleveland',
            'Dallas Cowboys': 'Dallas',
            'Denver Broncos': 'Denver',
            'Detroit Lions': 'Detroit',
            'Green Bay Packers': 'Green Bay',
            'Houston Texans': 'Houston',
            'Indianapolis Colts': 'Indianapolis',
            'Jacksonville Jaguars': 'Jacksonville',
            'Kansas City Chiefs': 'Kansas City',
            'Las Vegas Raiders': 'Las Vegas',
            'Los Angeles Chargers': 'Los Angeles Chargers',
            'Los Angeles Rams': 'Los Angeles Rams',
            'Miami Dolphins': 'Miami',
            'Minnesota Vikings': 'Minnesota',
            'New England Patriots': 'New England',
            'New Orleans Saints': 'New Orleans',
            'New York Giants': 'New York Giants',
            'New York Jets': 'New York Jets',
            'Philadelphia Eagles': 'Philadelphia',
            'Pittsburgh Steelers': 'Pittsburgh',
            'San Francisco 49ers': 'San Francisco',
            'Seattle Seahawks': 'Seattle',
            'Tampa Bay Buccaneers': 'Tampa Bay',
            'Tennessee Titans': 'Tennessee',
            'Washington Commanders': 'Washington'
        }
        
        # Cache for player-to-team mappings
        self.player_team_cache = {}
        self.team_rosters_cache = {}

    def get_team_roster(self, team_name: str) -> Set[str]:
        """
        Get the roster for a specific team from NFL.com
        """
        if team_name in self.team_rosters_cache:
            return self.team_rosters_cache[team_name]
        
        try:
            # Convert our team name to NFL.com format
            nfl_team_name = None
            for nfl_name, our_name in self.team_mapping.items():
                if our_name == team_name:
                    nfl_team_name = nfl_name
                    break
            
            if not nfl_team_name:
                logger.warning(f"Could not find NFL.com team name for: {team_name}")
                return set()
            
            # Construct the roster URL
            team_slug = nfl_team_name.lower().replace(' ', '-').replace('.', '')
            roster_url = f"https://www.nfl.com/teams/{team_slug}/roster/"
            
            logger.info(f"Fetching roster for {team_name} from {roster_url}")
            
            response = self.session.get(roster_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract player names from the roster
            player_names = set()
            
            # Look for player name elements in various possible structures
            player_elements = soup.find_all(['span', 'div', 'td'], class_=lambda x: x and any(word in str(x).lower() for word in ['player', 'name', 'roster']))
            
            for elem in player_elements:
                text = elem.get_text(strip=True)
                if text and len(text) > 2 and len(text) < 50:  # Reasonable player name length
                    # Clean up the name
                    name = text.split('\n')[0].strip()  # Take first line if multiline
                    if name and not any(char.isdigit() for char in name):  # No numbers in names
                        player_names.add(name)
            
            # Also look for table rows that might contain player names
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        # First cell often contains player name
                        first_cell = cells[0].get_text(strip=True)
                        if first_cell and len(first_cell) > 2 and len(first_cell) < 50:
                            if not any(char.isdigit() for char in first_cell):
                                player_names.add(first_cell)
            
            # Cache the result
            self.team_rosters_cache[team_name] = player_names
            logger.info(f"Found {len(player_names)} players for {team_name}")
            
            return player_names
            
        except Exception as e:
            logger.error(f"Error fetching roster for {team_name}: {e}")
            return set()

    def map_injured_players_to_teams(self, injury_data: Dict) -> Dict:
        """
        Map injured players to their correct teams using roster data
        """
        logger.info("🔍 Mapping injured players to correct teams using NFL.com rosters...")
        
        # Create a mapping of all injured players to their teams
        corrected_injury_data = {team: [] for team in self.team_mapping.values()}
        
        # Collect all injured players
        all_injured_players = []
        for team, injuries in injury_data.items():
            for injury in injuries:
                all_injured_players.append({
                    'player': injury['player'],
                    'position': injury['position'],
                    'injury': injury['injury'],
                    'status': injury['status'],
                    'current_team': team
                })
        
        logger.info(f"Found {len(all_injured_players)} injured players to map")
        
        # For each injured player, find their correct team
        for player_info in all_injured_players:
            player_name = player_info['player']
            correct_team = self.find_player_team(player_name)
            
            if correct_team:
                corrected_injury_data[correct_team].append({
                    'player': player_info['player'],
                    'position': player_info['position'],
                    'injury': player_info['injury'],
                    'status': player_info['status']
                })
                logger.info(f"✅ {player_name} ({player_info['position']}) -> {correct_team}")
            else:
                logger.warning(f"❌ Could not find team for {player_name} ({player_info['position']})")
        
        # Count results
        total_injuries = sum(len(injuries) for injuries in corrected_injury_data.values())
        teams_with_injuries = sum(1 for injuries in corrected_injury_data.values() if injuries)
        
        logger.info(f"✅ Mapped {total_injuries} injuries across {teams_with_injuries} teams")
        
        return corrected_injury_data

    def find_player_team(self, player_name: str) -> str:
        """
        Find which team a player belongs to by checking all team rosters
        """
        if player_name in self.player_team_cache:
            return self.player_team_cache[player_name]
        
        # Try exact match first
        for team_name in self.team_mapping.values():
            roster = self.get_team_roster(team_name)
            if player_name in roster:
                self.player_team_cache[player_name] = team_name
                return team_name
        
        # Try fuzzy matching for common name variations
        for team_name in self.team_mapping.values():
            roster = self.get_team_roster(team_name)
            for roster_player in roster:
                if self.names_match(player_name, roster_player):
                    self.player_team_cache[player_name] = team_name
                    return team_name
        
        # Cache negative result
        self.player_team_cache[player_name] = None
        return None

    def names_match(self, name1: str, name2: str) -> bool:
        """
        Check if two player names match (handles common variations)
        """
        # Normalize names
        n1 = name1.lower().strip()
        n2 = name2.lower().strip()
        
        # Exact match
        if n1 == n2:
            return True
        
        # Check if one name contains the other (for nicknames)
        if n1 in n2 or n2 in n1:
            return True
        
        # Split into parts and check if all parts of shorter name are in longer name
        parts1 = n1.split()
        parts2 = n2.split()
        
        if len(parts1) <= len(parts2):
            shorter, longer = parts1, parts2
        else:
            shorter, longer = parts2, parts1
        
        # Check if all parts of shorter name are in longer name
        for part in shorter:
            if not any(part in long_part for long_part in longer):
                return False
        return True

if __name__ == "__main__":
    # Test the mapper
    mapper = PlayerTeamMapper()
    
    # Test with a few players
    test_players = ["Matt Milano", "Ed Oliver", "Storm Duck", "Darren Waller"]
    
    for player in test_players:
        team = mapper.find_player_team(player)
        print(f"{player} -> {team}")
