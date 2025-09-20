"""
PFF Player Grades Scraper - Scrapes real PFF player grades from pff.com
"""
import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Optional
import time
import re

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PFFPlayerScraper:
    """
    Scrapes real PFF player grades from pff.com
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
        
        # Position URLs for PFF grades
        self.position_urls = {
            'QB': 'https://www.pff.com/nfl/grades/position/qb',
            'RB': 'https://www.pff.com/nfl/grades/position/rb',
            'WR': 'https://www.pff.com/nfl/grades/position/wr',
            'TE': 'https://www.pff.com/nfl/grades/position/te',
            'OT': 'https://www.pff.com/nfl/grades/position/ot',
            'OG': 'https://www.pff.com/nfl/grades/position/og',
            'C': 'https://www.pff.com/nfl/grades/position/c',
            'DE': 'https://www.pff.com/nfl/grades/position/de',
            'DT': 'https://www.pff.com/nfl/grades/position/dt',
            'LB': 'https://www.pff.com/nfl/grades/position/lb',
            'CB': 'https://www.pff.com/nfl/grades/position/cb',
            'S': 'https://www.pff.com/nfl/grades/position/s',
            'K': 'https://www.pff.com/nfl/grades/position/k',
            'P': 'https://www.pff.com/nfl/grades/position/p'
        }
        
        # Team name mapping for PFF
        self.team_mapping = {
            'ARI': 'Arizona Cardinals', 'ATL': 'Atlanta Falcons', 'BAL': 'Baltimore Ravens',
            'BUF': 'Buffalo Bills', 'CAR': 'Carolina Panthers', 'CHI': 'Chicago Bears',
            'CIN': 'Cincinnati Bengals', 'CLE': 'Cleveland Browns', 'DAL': 'Dallas Cowboys',
            'DEN': 'Denver Broncos', 'DET': 'Detroit Lions', 'GB': 'Green Bay Packers',
            'HOU': 'Houston Texans', 'IND': 'Indianapolis Colts', 'JAX': 'Jacksonville Jaguars',
            'KC': 'Kansas City Chiefs', 'LV': 'Las Vegas Raiders', 'LAC': 'Los Angeles Chargers',
            'LAR': 'Los Angeles Rams', 'MIA': 'Miami Dolphins', 'MIN': 'Minnesota Vikings',
            'NE': 'New England Patriots', 'NO': 'New Orleans Saints', 'NYG': 'New York Giants',
            'NYJ': 'New York Jets', 'PHI': 'Philadelphia Eagles', 'PIT': 'Pittsburgh Steelers',
            'SF': 'San Francisco 49ers', 'SEA': 'Seattle Seahawks', 'TB': 'Tampa Bay Buccaneers',
            'TEN': 'Tennessee Titans', 'WAS': 'Washington Commanders'
        }
    
    def scrape_all_player_grades(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        Scrape PFF grades for all positions
        Returns: {team_name: {position: {player_name: grade}}}
        """
        logger.info("🔍 Scraping real PFF player grades from pff.com...")
        
        all_grades = {}
        
        for position, url in self.position_urls.items():
            logger.info(f"📊 Scraping {position} grades from {url}")
            
            try:
                position_grades = self._scrape_position_grades(url, position)
                
                # Merge into all_grades
                for team, players in position_grades.items():
                    if team not in all_grades:
                        all_grades[team] = {}
                    all_grades[team][position] = players
                
                logger.info(f"✅ Scraped {len(position_grades)} teams for {position}")
                time.sleep(1)  # Be respectful to PFF servers
                
            except Exception as e:
                logger.error(f"❌ Error scraping {position}: {e}")
                continue
        
        logger.info(f"🎉 Successfully scraped PFF grades for {len(all_grades)} teams")
        return all_grades
    
    def _scrape_position_grades(self, url: str, position: str) -> Dict[str, Dict[str, float]]:
        """
        Scrape grades for a specific position
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for player data tables or lists
            # PFF typically uses tables or structured data
            players_data = {}
            
            # Try to find player tables
            tables = soup.find_all('table')
            if tables:
                logger.info(f"Found {len(tables)} tables for {position}")
                for table in tables:
                    self._parse_player_table(table, players_data, position)
            
            # Try to find player lists or divs
            player_divs = soup.find_all(['div', 'ul', 'ol'], class_=lambda x: x and any(
                keyword in str(x).lower() for keyword in ['player', 'grade', 'rank', 'list']
            ))
            
            if player_divs:
                logger.info(f"Found {len(player_divs)} player containers for {position}")
                for div in player_divs:
                    self._parse_player_container(div, players_data, position)
            
            # If no structured data found, try to extract from text
            if not players_data:
                logger.warning(f"No structured data found for {position}, trying text extraction")
                self._extract_from_text(soup, players_data, position)
            
            return players_data
            
        except Exception as e:
            logger.error(f"Error scraping {position} from {url}: {e}")
            return {}
    
    def _parse_player_table(self, table, players_data: Dict, position: str):
        """Parse player data from HTML table"""
        try:
            rows = table.find_all('tr')
            if len(rows) < 2:  # Need header + data rows
                return
            
            # Find header row to identify columns
            header_row = rows[0]
            headers = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
            
            # Look for relevant columns
            name_col = None
            team_col = None
            grade_col = None
            
            for i, header in enumerate(headers):
                if any(keyword in header for keyword in ['name', 'player']):
                    name_col = i
                elif any(keyword in header for keyword in ['team']):
                    team_col = i
                elif any(keyword in header for keyword in ['grade', 'rating', 'score']):
                    grade_col = i
            
            if name_col is None or grade_col is None:
                logger.warning(f"Could not identify name/grade columns in table for {position}")
                return
            
            # Parse data rows
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) <= max(name_col, grade_col):
                    continue
                
                player_name = cells[name_col].get_text(strip=True)
                grade_text = cells[grade_col].get_text(strip=True)
                
                # Extract team if available
                team_name = None
                if team_col is not None and team_col < len(cells):
                    team_text = cells[team_col].get_text(strip=True)
                    team_name = self._extract_team_name(team_text)
                
                # Extract grade
                grade = self._extract_grade(grade_text)
                
                if player_name and grade is not None:
                    if team_name:
                        if team_name not in players_data:
                            players_data[team_name] = {}
                        players_data[team_name][player_name] = grade
                        logger.info(f"✅ {team_name} {player_name} ({position}): {grade}")
                    else:
                        # Try to extract team from player name or context
                        logger.warning(f"Could not determine team for {player_name} ({position}): {grade}")
            
        except Exception as e:
            logger.error(f"Error parsing table for {position}: {e}")
    
    def _parse_player_container(self, container, players_data: Dict, position: str):
        """Parse player data from div/container"""
        try:
            # Look for player names and grades in the container
            text = container.get_text()
            
            # Try to find patterns like "Player Name - Team - Grade"
            # This is a simplified approach - would need to be refined based on actual PFF structure
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for grade patterns (numbers)
                grade_match = re.search(r'(\d+\.?\d*)', line)
                if grade_match:
                    grade = float(grade_match.group(1))
                    if 0 <= grade <= 100:  # Reasonable grade range
                        # Try to extract player name (everything before the grade)
                        player_text = line[:grade_match.start()].strip()
                        if player_text:
                            # Extract team and player name
                            team_name = self._extract_team_name(player_text)
                            player_name = self._clean_player_name(player_text)
                            
                            if team_name and player_name:
                                if team_name not in players_data:
                                    players_data[team_name] = {}
                                players_data[team_name][player_name] = grade
                                logger.info(f"✅ {team_name} {player_name} ({position}): {grade}")
            
        except Exception as e:
            logger.error(f"Error parsing container for {position}: {e}")
    
    def _extract_from_text(self, soup: BeautifulSoup, players_data: Dict, position: str):
        """Extract player data from page text as fallback"""
        try:
            text = soup.get_text()
            
            # Look for patterns in the text
            # This is a very basic approach - would need refinement
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or len(line) < 5:
                    continue
                
                # Look for grade patterns
                grade_match = re.search(r'(\d+\.?\d*)', line)
                if grade_match:
                    grade = float(grade_match.group(1))
                    if 50 <= grade <= 100:  # Reasonable PFF grade range
                        # Try to extract player info
                        player_text = line[:grade_match.start()].strip()
                        if player_text:
                            team_name = self._extract_team_name(player_text)
                            player_name = self._clean_player_name(player_text)
                            
                            if team_name and player_name:
                                if team_name not in players_data:
                                    players_data[team_name] = {}
                                players_data[team_name][player_name] = grade
                                logger.info(f"✅ {team_name} {player_name} ({position}): {grade}")
            
        except Exception as e:
            logger.error(f"Error extracting from text for {position}: {e}")
    
    def _extract_team_name(self, text: str) -> Optional[str]:
        """Extract team name from text"""
        text_upper = text.upper()
        
        # Look for team abbreviations
        for abbr, full_name in self.team_mapping.items():
            if abbr in text_upper:
                return full_name
        
        # Look for team city names
        team_cities = {
            'ARIZONA': 'Arizona Cardinals', 'ATLANTA': 'Atlanta Falcons', 'BALTIMORE': 'Baltimore Ravens',
            'BUFFALO': 'Buffalo Bills', 'CAROLINA': 'Carolina Panthers', 'CHICAGO': 'Chicago Bears',
            'CINCINNATI': 'Cincinnati Bengals', 'CLEVELAND': 'Cleveland Browns', 'DALLAS': 'Dallas Cowboys',
            'DENVER': 'Denver Broncos', 'DETROIT': 'Detroit Lions', 'GREEN BAY': 'Green Bay Packers',
            'HOUSTON': 'Houston Texans', 'INDIANAPOLIS': 'Indianapolis Colts', 'JACKSONVILLE': 'Jacksonville Jaguars',
            'KANSAS CITY': 'Kansas City Chiefs', 'LAS VEGAS': 'Las Vegas Raiders', 'LOS ANGELES': 'Los Angeles Chargers',
            'MIAMI': 'Miami Dolphins', 'MINNESOTA': 'Minnesota Vikings', 'NEW ENGLAND': 'New England Patriots',
            'NEW ORLEANS': 'New Orleans Saints', 'NEW YORK': 'New York Giants', 'PHILADELPHIA': 'Philadelphia Eagles',
            'PITTSBURGH': 'Pittsburgh Steelers', 'SAN FRANCISCO': 'San Francisco 49ers', 'SEATTLE': 'Seattle Seahawks',
            'TAMPA BAY': 'Tampa Bay Buccaneers', 'TENNESSEE': 'Tennessee Titans', 'WASHINGTON': 'Washington Commanders'
        }
        
        for city, full_name in team_cities.items():
            if city in text_upper:
                return full_name
        
        return None
    
    def _clean_player_name(self, text: str) -> str:
        """Clean and extract player name from text"""
        # Remove team names and extra text
        text = re.sub(r'\b[A-Z]{2,4}\b', '', text)  # Remove abbreviations
        text = re.sub(r'\b(Cardinals|Falcons|Ravens|Bills|Panthers|Bears|Bengals|Browns|Cowboys|Broncos|Lions|Packers|Texans|Colts|Jaguars|Chiefs|Raiders|Chargers|Rams|Dolphins|Vikings|Patriots|Saints|Giants|Jets|Eagles|Steelers|49ers|Seahawks|Buccaneers|Titans|Commanders)\b', '', text, flags=re.IGNORECASE)
        
        # Clean up extra spaces and punctuation
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'^[^\w]+|[^\w]+$', '', text)  # Remove leading/trailing non-word chars
        
        return text
    
    def _extract_grade(self, text: str) -> Optional[float]:
        """Extract grade from text"""
        try:
            # Look for numbers that could be grades
            grade_match = re.search(r'(\d+\.?\d*)', text)
            if grade_match:
                grade = float(grade_match.group(1))
                if 0 <= grade <= 100:  # Reasonable grade range
                    return grade
        except:
            pass
        return None

if __name__ == "__main__":
    scraper = PFFPlayerScraper()
    
    print("🔍 Testing PFF Player Grades Scraper")
    print("=" * 50)
    
    # Test scraping QB grades first
    qb_grades = scraper._scrape_position_grades('https://www.pff.com/nfl/grades/position/qb', 'QB')
    
    print(f"\n📊 QB Grades Found:")
    for team, players in qb_grades.items():
        print(f"{team}:")
        for player, grade in players.items():
            print(f"  {player}: {grade}")
        print()
    
    print(f"✅ Found QB grades for {len(qb_grades)} teams")
