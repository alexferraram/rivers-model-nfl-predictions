"""
Real NFL Injury Scraper - Actually scrapes NFL.com for real injury data
"""
import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, List
import re
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealNFLInjuryScraper:
    """
    Real scraper that actually scrapes NFL.com for real injury data
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
        
        # Team mapping from NFL.com format to our format
        self.team_mapping = {
            'ARI': 'Arizona', 'ATL': 'Atlanta', 'BAL': 'Baltimore', 'BUF': 'Buffalo', 
            'CAR': 'Carolina', 'CHI': 'Chicago', 'CIN': 'Cincinnati', 'CLE': 'Cleveland', 
            'DAL': 'Dallas', 'DEN': 'Denver', 'DET': 'Detroit', 'GB': 'Green Bay', 
            'HOU': 'Houston', 'IND': 'Indianapolis', 'JAX': 'Jacksonville', 'KC': 'Kansas City', 
            'LV': 'Las Vegas', 'LAC': 'Los Angeles Chargers', 'LA': 'Los Angeles Rams', 
            'MIA': 'Miami', 'MIN': 'Minnesota', 'NE': 'New England', 'NO': 'New Orleans', 
            'NYG': 'New York Giants', 'NYJ': 'New York Jets', 'PHI': 'Philadelphia', 
            'PIT': 'Pittsburgh', 'SF': 'San Francisco', 'SEA': 'Seattle', 'TB': 'Tampa Bay', 
            'TEN': 'Tennessee', 'WAS': 'Washington'
        }

    def scrape_all_injuries(self) -> Dict:
        """
        Actually scrape real injury data for all NFL teams from NFL.com
        """
        logger.info("🔍 Scraping real NFL.com injury data...")
        
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Initialize with empty injury lists for all 32 teams
            injury_data = {city: [] for city in self.team_mapping.values()}
            
            # Debug: Save the HTML to see what we're working with
            logger.info(f"Page title: {soup.title.string if soup.title else 'No title'}")
            
            # Look for injury data in various possible structures
            injury_data = self._extract_injury_data_from_page(soup)
            
            # Count total injuries found
            total_injuries = sum(len(injuries) for injuries in injury_data.values())
            teams_with_injuries = sum(1 for injuries in injury_data.values() if injuries)
            
            if total_injuries == 0:
                logger.error("❌ No injury data found on NFL.com - this indicates the page structure has changed")
                return {}
            
            logger.info(f"✅ Successfully scraped {total_injuries} injuries for {teams_with_injuries} teams")
            return injury_data
            
        except Exception as e:
            logger.error(f"❌ Error scraping NFL injury data: {e}")
            return {}

    def _extract_injury_data_from_page(self, soup: BeautifulSoup) -> Dict:
        """Extract injury data from the NFL.com page"""
        injury_data = {city: [] for city in self.team_mapping.values()}
        
        try:
            # Method 1: Look for injury report sections
            injury_sections = soup.find_all('div', class_=lambda x: x and 'injury' in x.lower())
            logger.info(f"Found {len(injury_sections)} injury sections")
            
            # Method 2: Look for tables with injury data
            tables = soup.find_all('table')
            logger.info(f"Found {len(tables)} tables")
            
            # Method 3: Look for any element containing injury-related text
            injury_elements = soup.find_all(string=lambda text: text and any(word in text.lower() for word in ['injury', 'out', 'questionable', 'doubtful']))
            logger.info(f"Found {len(injury_elements)} injury-related text elements")
            
            # Method 4: Look for JSON data in script tags
            script_tags = soup.find_all('script')
            json_found = False
            for script in script_tags:
                if script.string and ('injury' in script.string.lower() or 'player' in script.string.lower()):
                    json_found = True
                    break
            logger.info(f"Found JSON data in scripts: {json_found}")
            
            # Method 5: Look for specific NFL.com injury report structure
            # Try to find the actual injury report content
            injury_content = soup.find('div', {'id': 'main-content'}) or soup.find('main') or soup.find('div', class_='nfl-o-main')
            
            if injury_content:
                logger.info("Found main content area")
                # Look for team-specific injury data within the main content
                team_sections = injury_content.find_all(['div', 'section'], class_=lambda x: x and any(team in str(x).lower() for team in ['team', 'game', 'matchup']))
                logger.info(f"Found {len(team_sections)} team sections")
                
                for section in team_sections:
                    # Try to extract team name and injuries from this section
                    team_name = self._extract_team_name_from_section(section)
                    if team_name:
                        injuries = self._extract_injuries_from_section(section)
                        if injuries:
                            injury_data[team_name] = injuries
                            logger.info(f"Found {len(injuries)} injuries for {team_name}")
            
            # Method 6: Look for any structured data (JSON-LD, microdata, etc.)
            structured_data = soup.find_all('script', type='application/ld+json')
            if structured_data:
                logger.info(f"Found {len(structured_data)} structured data elements")
                for data in structured_data:
                    try:
                        json_data = json.loads(data.string)
                        if isinstance(json_data, dict) and 'injury' in str(json_data).lower():
                            logger.info("Found injury data in structured JSON")
                    except:
                        continue
            
            return injury_data
            
        except Exception as e:
            logger.error(f"Error extracting injury data: {e}")
            return injury_data

    def _extract_team_name_from_section(self, section) -> str:
        """Extract team name from a section"""
        try:
            # Look for team names in headers, titles, or text
            team_elements = section.find_all(['h1', 'h2', 'h3', 'h4', 'span', 'div'], string=lambda x: x and any(team in x for team in self.team_mapping.keys()))
            
            for elem in team_elements:
                text = elem.get_text(strip=True)
                for abbr, full_name in self.team_mapping.items():
                    if abbr in text or full_name.split()[-1] in text:
                        return full_name
            
            return None
        except:
            return None

    def _extract_injuries_from_section(self, section) -> List[Dict]:
        """Extract injuries from a section"""
        injuries = []
        
        try:
            # Look for injury data in tables or lists
            tables = section.find_all('table')
            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cols = row.find_all(['td', 'th'])
                    if len(cols) >= 3:
                        try:
                            player = cols[0].get_text(strip=True)
                            position = cols[1].get_text(strip=True) if len(cols) > 1 else ''
                            status = cols[-1].get_text(strip=True) if len(cols) > 2 else ''
                            
                            if player and position and status:
                                normalized_status = self._normalize_status(status)
                                injuries.append({
                                    'player': player,
                                    'position': position,
                                    'injury': '',
                                    'status': normalized_status
                                })
                        except:
                            continue
            
            return injuries
        except:
            return injuries

    def _normalize_status(self, status: str) -> str:
        """
        Convert NFL.com status format to our expected format
        """
        status_lower = status.lower()
        
        if 'did not participate' in status_lower or 'out' in status_lower:
            return 'Out'
        elif 'limited participation' in status_lower or 'limited' in status_lower:
            return 'Limited'
        elif 'questionable' in status_lower:
            return 'Questionable'
        elif 'doubtful' in status_lower:
            return 'Doubtful'
        elif 'full participation' in status_lower or 'full' in status_lower:
            return 'Full'
        else:
            return status  # Return as-is if we can't normalize

if __name__ == "__main__":
    scraper = RealNFLInjuryScraper()
    injury_data = scraper.scrape_all_injuries()
    
    print('🔍 Real NFL Injury Data (NO FALLBACK):')
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
        print("❌ NO REAL INJURY DATA FOUND - NFL.com structure may have changed")
