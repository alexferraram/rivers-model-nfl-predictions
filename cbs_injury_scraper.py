"""
CBS Sports Injury Scraper
Scrapes real injury data from https://www.cbssports.com/nfl/injuries/
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

class CBSInjuryScraper:
    """
    Scrapes real injury data from CBS Sports
    """
    
    def __init__(self):
        self.base_url = "https://www.cbssports.com/nfl/injuries/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Team name mapping - CBS uses city names
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
        
        # Full team name mapping for reference
        self.full_team_mapping = {
            'Buffalo': 'Buffalo Bills',
            'Miami': 'Miami Dolphins', 
            'New England': 'New England Patriots',
            'New York Jets': 'New York Jets',
            'Baltimore': 'Baltimore Ravens',
            'Cincinnati': 'Cincinnati Bengals',
            'Cleveland': 'Cleveland Browns',
            'Pittsburgh': 'Pittsburgh Steelers',
            'Houston': 'Houston Texans',
            'Indianapolis': 'Indianapolis Colts',
            'Jacksonville': 'Jacksonville Jaguars',
            'Tennessee': 'Tennessee Titans',
            'Denver': 'Denver Broncos',
            'Kansas City': 'Kansas City Chiefs',
            'Las Vegas': 'Las Vegas Raiders',
            'Los Angeles Chargers': 'Los Angeles Chargers',
            'Dallas': 'Dallas Cowboys',
            'New York Giants': 'New York Giants',
            'Philadelphia': 'Philadelphia Eagles',
            'Washington': 'Washington Commanders',
            'Chicago': 'Chicago Bears',
            'Detroit': 'Detroit Lions',
            'Green Bay': 'Green Bay Packers',
            'Minnesota': 'Minnesota Vikings',
            'Atlanta': 'Atlanta Falcons',
            'Carolina': 'Carolina Panthers',
            'New Orleans': 'New Orleans Saints',
            'Tampa Bay': 'Tampa Bay Buccaneers',
            'Arizona': 'Arizona Cardinals',
            'Los Angeles Rams': 'Los Angeles Rams',
            'San Francisco': 'San Francisco 49ers',
            'Seattle': 'Seattle Seahawks'
        }
    
    def scrape_all_injuries(self) -> Dict:
        """
        Scrape injury data for all NFL teams
        """
        logger.info("🔍 Scraping CBS Sports injury data...")
        
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all team injury tables
            injury_data = {}
            
            # Find all TableBase divs (these contain the team injury tables)
            team_sections = soup.find_all('div', class_='TableBase')
            logger.info(f"Found {len(team_sections)} TableBase sections")
            
            # Process each TableBase section
            processed_teams = set()
            
            for i, section in enumerate(team_sections):
                # Try to find team name from this section
                team_name = self._extract_team_name_from_section(section)
                
                if team_name and team_name not in processed_teams:
                    # Extract injuries for this team
                    injuries = self._extract_team_injuries(section, team_name)
                    injury_data[team_name] = injuries
                    processed_teams.add(team_name)
                    logger.info(f"✅ Found {len(injuries)} injuries for {team_name}")
                elif not team_name:
                    # If we can't find team name, try to extract from the table within this section
                    table = section.find('table')
                    if table:
                        # Try header first, then fallback to general table extraction
                        team_name = self._extract_team_name_from_table_header(table)
                        if not team_name:
                            team_name = self._extract_team_name_from_table(table)
                        
                        if team_name and team_name not in processed_teams:
                            injuries = self._extract_team_injuries(table, team_name)
                            injury_data[team_name] = injuries
                            processed_teams.add(team_name)
                            logger.info(f"✅ Found {len(injuries)} injuries for {team_name} (from table)")
                        else:
                            logger.warning(f"⚠️ Could not identify team for section {i+1}")
                else:
                    logger.warning(f"⚠️ Duplicate team {team_name} found")
            
            # Check if we have all 32 teams
            expected_teams = set(self.team_mapping.keys())
            found_teams = set(injury_data.keys())
            missing_teams = expected_teams - found_teams
            
            if missing_teams:
                logger.warning(f"⚠️ Missing injury data for {len(missing_teams)} teams: {list(missing_teams)}")
                logger.warning("Attempting to scrape individual team pages...")
                
                # Try to scrape missing teams individually
                for team_name in missing_teams:
                    team_injuries = self._scrape_individual_team(team_name)
                    if team_injuries:
                        injury_data[team_name] = team_injuries
                        logger.info(f"✅ Found {len(team_injuries)} injuries for {team_name} (individual scrape)")
            
            # If still missing teams, try alternative approach
            if len(injury_data) < 32:
                logger.warning("Still missing teams, trying alternative scraping approach...")
                alternative_data = self._scrape_alternative_approach()
                for team_name, injuries in alternative_data.items():
                    if team_name not in injury_data and injuries:
                        injury_data[team_name] = injuries
                        logger.info(f"✅ Found {len(injuries)} injuries for {team_name} (alternative approach)")
            
            logger.info(f"✅ Successfully scraped injuries for {len(injury_data)} teams")
            
            # Final check - ensure we have all 32 teams
            if len(injury_data) < 32:
                missing_count = 32 - len(injury_data)
                missing_teams = expected_teams - set(injury_data.keys())
                logger.error(f"❌ Still missing {missing_count} teams: {list(missing_teams)}")
                logger.error("❌ Cannot proceed without all 32 teams. Please check CBS Sports website structure.")
                return {}
            
            logger.info(f"✅ Successfully found all 32 NFL teams with injury data")
            return injury_data
            
        except Exception as e:
            logger.error(f"❌ Error scraping CBS injury data: {e}")
            return {}
    
    def _extract_team_name_from_section(self, section) -> Optional[str]:
        """Extract team name from section"""
        try:
            # Get all text from the section and its parents
            all_text = ""
            
            # Add section text
            all_text += " " + section.get_text(strip=True)
            
            # Add parent text
            parent = section.parent
            if parent:
                all_text += " " + parent.get_text(strip=True)
                
                # Add grandparent text
                grandparent = parent.parent
                if grandparent:
                    all_text += " " + grandparent.get_text(strip=True)
            
            # Look for team names in all text
            all_text = all_text.lower()
            
            # Check for exact city matches first
            for city_name, abbr in self.team_mapping.items():
                city_lower = city_name.lower()
                abbr_lower = abbr.lower()
                
                # Check for city name
                if city_lower in all_text:
                    return city_name
                
                # Check for abbreviation
                if abbr_lower in all_text:
                    return city_name
            
            # Check for full team names (fallback)
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
            logger.error(f"Error extracting team name: {e}")
            return None
    
    def _extract_team_injuries(self, section, team_name: str) -> List[Dict]:
        """Extract injuries for a specific team"""
        try:
            injuries = []
            
            # Find the injury table
            table = section.find('table')
            if not table:
                return injuries
            
            # Find table rows
            rows = table.find_all('tr')
            if len(rows) < 2:  # Need header + data rows
                return injuries
            
            # Skip header row
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 5:  # Need at least 5 columns
                    injury = self._parse_injury_row(cells, team_name)
                    if injury:
                        injuries.append(injury)
            
            return injuries
            
        except Exception as e:
            logger.error(f"Error extracting injuries for {team_name}: {e}")
            return []
    
    def _extract_team_name_from_table_header(self, table) -> Optional[str]:
        """Extract team name from table header specifically"""
        try:
            # Look for team name in the first row (header)
            header_row = table.find('tr')
            if header_row:
                header_cells = header_row.find_all(['th', 'td'])
                for cell in header_cells:
                    text = cell.get_text(strip=True)
                    # Check if this looks like a team name
                    for city_name, abbr in self.team_mapping.items():
                        if city_name.lower() in text.lower() or abbr.lower() in text.lower():
                            return city_name
                    
                    # Check for full team names
                    full_team_names = {
                        'buffalo bills': 'Buffalo', 'miami dolphins': 'Miami',
                        'new england patriots': 'New England', 'new york jets': 'New York Jets',
                        'baltimore ravens': 'Baltimore', 'cincinnati bengals': 'Cincinnati',
                        'cleveland browns': 'Cleveland', 'pittsburgh steelers': 'Pittsburgh',
                        'houston texans': 'Houston', 'indianapolis colts': 'Indianapolis',
                        'jacksonville jaguars': 'Jacksonville', 'tennessee titans': 'Tennessee',
                        'denver broncos': 'Denver', 'kansas city chiefs': 'Kansas City',
                        'las vegas raiders': 'Las Vegas', 'los angeles chargers': 'Los Angeles Chargers',
                        'dallas cowboys': 'Dallas', 'new york giants': 'New York Giants',
                        'philadelphia eagles': 'Philadelphia', 'washington commanders': 'Washington',
                        'chicago bears': 'Chicago', 'detroit lions': 'Detroit',
                        'green bay packers': 'Green Bay', 'minnesota vikings': 'Minnesota',
                        'atlanta falcons': 'Atlanta', 'carolina panthers': 'Carolina',
                        'new orleans saints': 'New Orleans', 'tampa bay buccaneers': 'Tampa Bay',
                        'arizona cardinals': 'Arizona', 'los angeles rams': 'Los Angeles Rams',
                        'san francisco 49ers': 'San Francisco', 'seattle seahawks': 'Seattle'
                    }
                    
                    for full_name, city_name in full_team_names.items():
                        if full_name in text.lower():
                            return city_name
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting team name from table header: {e}")
            return None
    
    def _parse_injury_row(self, cells, team_name: str) -> Optional[Dict]:
        """Parse a single injury row"""
        try:
            # Extract data from cells
            player_name = cells[0].get_text(strip=True)
            position = cells[1].get_text(strip=True)
            updated_date = cells[2].get_text(strip=True)
            injury_type = cells[3].get_text(strip=True)
            injury_status = cells[4].get_text(strip=True)
            
            # Parse injury status
            status_info = self._parse_injury_status(injury_status)
            
            if status_info:
                return {
                    'player': player_name,
                    'position': position,
                    'updated_date': updated_date,
                    'injury_type': injury_type,
                    'status': status_info['status'],
                    'status_detail': injury_status,
                    'expected_return': status_info.get('expected_return'),
                    'team': team_name
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing injury row: {e}")
            return None
    
    def _parse_injury_status(self, status_text: str) -> Optional[Dict]:
        """Parse injury status text"""
        try:
            status_text = status_text.strip()
            
            # Determine status
            if 'out for week' in status_text.lower():
                status = 'OUT'
            elif 'doubtful' in status_text.lower():
                status = 'DOUBTFUL'
            elif 'questionable' in status_text.lower():
                status = 'QUESTIONABLE'
            elif 'probable' in status_text.lower():
                status = 'PROBABLE'
            elif 'injured reserve' in status_text.lower() or 'ir' in status_text.lower():
                status = 'IR'
            elif 'physically unable to perform' in status_text.lower() or 'pup' in status_text.lower():
                status = 'PUP'
            else:
                # Default to questionable if unclear
                status = 'QUESTIONABLE'
            
            # Extract expected return
            expected_return = None
            if 'expected return' in status_text.lower():
                match = re.search(r'expected return[:\s-]*week\s*(\d+)', status_text.lower())
                if match:
                    expected_return = f"Week {match.group(1)}"
            
            return {
                'status': status,
                'expected_return': expected_return
            }
            
        except Exception as e:
            logger.error(f"Error parsing injury status: {e}")
            return None
    
    def get_team_injuries(self, team_name: str) -> List[Dict]:
        """Get injuries for a specific team"""
        all_injuries = self.scrape_all_injuries()
        return all_injuries.get(team_name, [])
    
    def _scrape_alternative_approach(self) -> Dict:
        """Try alternative scraping approach for missing teams"""
        try:
            logger.info("Trying alternative scraping approach...")
            
            # Try different URL patterns
            alternative_urls = [
                "https://www.cbssports.com/nfl/injuries/",
                "https://www.cbssports.com/nfl/injuries/?sort=team",
                "https://www.cbssports.com/nfl/injuries/?view=all"
            ]
            
            injury_data = {}
            
            for url in alternative_urls:
                try:
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for all tables
                        tables = soup.find_all('table')
                        for table in tables:
                            # Try to extract team name from table context
                            team_name = self._extract_team_name_from_table(table)
                            if team_name:
                                injuries = self._extract_team_injuries(table, team_name)
                                if injuries:
                                    injury_data[team_name] = injuries
                                    logger.info(f"✅ Alternative approach found {len(injuries)} injuries for {team_name}")
                
                except Exception as e:
                    logger.debug(f"Failed alternative URL {url}: {e}")
                    continue
            
            return injury_data
            
        except Exception as e:
            logger.error(f"Error in alternative scraping approach: {e}")
            return {}
    
    def _extract_team_name_from_table(self, table) -> Optional[str]:
        """Extract team name from table context"""
        try:
            # Get all text from table and its context
            all_text = ""
            
            # Add table text
            all_text += " " + table.get_text(strip=True)
            
            # Add header text
            header = table.find('thead')
            if header:
                all_text += " " + header.get_text(strip=True)
            
            # Add caption text
            caption = table.find('caption')
            if caption:
                all_text += " " + caption.get_text(strip=True)
            
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
    
    def _scrape_individual_team(self, team_name: str) -> List[Dict]:
        """Scrape injury data for a specific team"""
        try:
            # Convert team name to URL format
            team_url = team_name.lower().replace(' ', '-')
            team_url = team_url.replace('los-angeles', 'la')
            
            # Try different URL patterns
            urls_to_try = [
                f"https://www.cbssports.com/nfl/injuries/{team_url}/",
                f"https://www.cbssports.com/nfl/teams/{team_url}/injuries/",
                f"https://www.cbssports.com/nfl/injuries/?team={team_url}"
            ]
            
            for url in urls_to_try:
                try:
                    response = self.session.get(url, timeout=15)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for injury table
                        table = soup.find('table')
                        if table:
                            injuries = self._extract_team_injuries(table, team_name)
                            if injuries:
                                logger.info(f"✅ Individual scrape found {len(injuries)} injuries for {team_name}")
                                return injuries
                except Exception as e:
                    logger.debug(f"Failed to scrape {url}: {e}")
                    continue
            
            # If no individual page found, return empty list
            logger.warning(f"⚠️ No individual injury data found for {team_name}")
            return []
            
        except Exception as e:
            logger.error(f"Error scraping individual team {team_name}: {e}")
            return []
    
    def get_injury_summary(self, team_name: str) -> Dict:
        """Get injury summary for a team"""
        injuries = self.get_team_injuries(team_name)
        
        if not injuries:
            return {
                'total_injuries': 0,
                'significant_injuries': 0,
                'injuries': []
            }
        
        # Count significant injuries (OUT, DOUBTFUL, IR, PUP)
        significant_injuries = [
            inj for inj in injuries 
            if inj['status'] in ['OUT', 'DOUBTFUL', 'IR', 'PUP']
        ]
        
        return {
            'total_injuries': len(injuries),
            'significant_injuries': len(significant_injuries),
            'injuries': injuries,
            'significant_injuries_list': significant_injuries
        }

if __name__ == "__main__":
    # Test the scraper
    scraper = CBSInjuryScraper()
    
    print("🔍 Testing CBS Sports Injury Scraper")
    print("=" * 50)
    
    # Test with Buffalo Bills
    bills_injuries = scraper.get_team_injuries('Buffalo Bills')
    print(f"\nBuffalo Bills Injuries ({len(bills_injuries)}):")
    for injury in bills_injuries:
        print(f"  {injury['player']} ({injury['position']}) - {injury['status']}: {injury['status_detail']}")
    
    # Test with Miami Dolphins
    dolphins_injuries = scraper.get_team_injuries('Miami Dolphins')
    print(f"\nMiami Dolphins Injuries ({len(dolphins_injuries)}):")
    for injury in dolphins_injuries:
        print(f"  {injury['player']} ({injury['position']}) - {injury['status']}: {injury['status_detail']}")
    
    print("\n✅ CBS Sports Injury Scraper Test Complete")
