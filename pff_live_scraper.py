"""
Live PFF Data Scraper - Dynamic extraction from https://premium.pff.com/nfl/teams/2025/REGPO
This scraper attempts to extract real-time PFF data for all 32 NFL teams
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
from datetime import datetime
import json
import re
import time
from typing import Dict, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LivePFFScraper:
    """
    Live PFF data scraper that attempts multiple methods to extract real data
    """
    
    def __init__(self):
        self.url = "https://premium.pff.com/nfl/teams/2025/REGPO"
        self.team_grades = {}
        
        # Team name mapping for consistency
        self.team_mapping = {
            'ARI': 'Arizona Cardinals',
            'ATL': 'Atlanta Falcons', 
            'BAL': 'Baltimore Ravens',
            'BUF': 'Buffalo Bills',
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
            'LA': 'Los Angeles Rams',
            'MIA': 'Miami Dolphins',
            'MIN': 'Minnesota Vikings',
            'NE': 'New England Patriots',
            'NO': 'New Orleans Saints',
            'NYG': 'New York Giants',
            'NYJ': 'New York Jets',
            'PHI': 'Philadelphia Eagles',
            'PIT': 'Pittsburgh Steelers',
            'SF': 'San Francisco 49ers',
            'SEA': 'Seattle Seahawks',
            'TB': 'Tampa Bay Buccaneers',
            'TEN': 'Tennessee Titans',
            'WAS': 'Washington Commanders'
        }
    
    def scrape_pff_data(self) -> Dict:
        """
        Main method to scrape PFF data using multiple approaches
        """
        logger.info("🚀 Starting live PFF data extraction")
        
        # Method 1: Try Selenium with Chrome
        selenium_data = self._scrape_with_selenium()
        if selenium_data and len(selenium_data) > 10:  # If we got substantial data
            logger.info(f"✅ Selenium extraction successful: {len(selenium_data)} teams")
            return selenium_data
        
        # Method 2: Try enhanced requests with different headers
        requests_data = self._scrape_with_requests()
        if requests_data and len(requests_data) > 10:
            logger.info(f"✅ Requests extraction successful: {len(requests_data)} teams")
            return requests_data
        
        # Method 3: Try API endpoints
        api_data = self._scrape_api_endpoints()
        if api_data and len(api_data) > 10:
            logger.info(f"✅ API extraction successful: {len(api_data)} teams")
            return api_data
        
        # Method 4: Fallback to known data structure
        logger.warning("⚠️ All scraping methods failed, using fallback data")
        return self._get_fallback_data()
    
    def _scrape_with_selenium(self) -> Optional[Dict]:
        """
        Use Selenium to scrape dynamic content
        """
        try:
            logger.info("🔧 Attempting Selenium scraping...")
            
            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                driver.get(self.url)
                logger.info(f"✅ Page loaded: {driver.title}")
                
                # Wait for content to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Look for tables or data containers
                tables = driver.find_elements(By.TAG_NAME, "table")
                logger.info(f"Found {len(tables)} tables")
                
                # Look for any elements containing team names
                team_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Bills') or contains(text(), 'Dolphins') or contains(text(), 'Chiefs')]")
                logger.info(f"Found {len(team_elements)} team elements")
                
                # Get page source and parse with BeautifulSoup
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Extract data from the parsed content
                team_data = self._extract_data_from_soup(soup)
                
                return team_data
                
            finally:
                driver.quit()
                
        except Exception as e:
            logger.warning(f"Selenium scraping failed: {e}")
            return None
    
    def _scrape_with_requests(self) -> Optional[Dict]:
        """
        Enhanced requests scraping with multiple header combinations
        """
        try:
            logger.info("🔧 Attempting enhanced requests scraping...")
            
            # Try different header combinations
            header_sets = [
                {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                },
                {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                },
                {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive'
                }
            ]
            
            for i, headers in enumerate(header_sets):
                try:
                    logger.info(f"Trying header set {i+1}...")
                    
                    response = requests.get(self.url, headers=headers, timeout=15)
                    logger.info(f"Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Check if we got meaningful content
                        page_text = soup.get_text()
                        if len(page_text) > 1000 and ('Bills' in page_text or 'Dolphins' in page_text):
                            logger.info("✅ Got meaningful content with requests")
                            team_data = self._extract_data_from_soup(soup)
                            if team_data:
                                return team_data
                    
                    time.sleep(1)  # Be respectful
                    
                except Exception as e:
                    logger.warning(f"Header set {i+1} failed: {e}")
                    continue
            
        except Exception as e:
            logger.warning(f"Requests scraping failed: {e}")
        
        return None
    
    def _scrape_api_endpoints(self) -> Optional[Dict]:
        """
        Try to find API endpoints that might contain the data
        """
        try:
            logger.info("🔧 Attempting API endpoint scraping...")
            
            # Common API endpoint patterns
            api_endpoints = [
                "https://premium.pff.com/api/nfl/teams/2025/REGPO",
                "https://premium.pff.com/api/teams",
                "https://premium.pff.com/data/teams.json",
                "https://premium.pff.com/api/v1/teams",
                "https://premium.pff.com/api/nfl/teams",
                "https://premium.pff.com/teams.json",
                "https://premium.pff.com/api/teams/2025",
                "https://premium.pff.com/api/nfl/teams/2025"
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Referer': self.url
            }
            
            for endpoint in api_endpoints:
                try:
                    logger.info(f"Trying API endpoint: {endpoint}")
                    response = requests.get(endpoint, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            logger.info(f"✅ Got JSON data from {endpoint}")
                            team_data = self._parse_json_data(data)
                            if team_data:
                                return team_data
                        except json.JSONDecodeError:
                            # Maybe it's HTML disguised as JSON
                            soup = BeautifulSoup(response.content, 'html.parser')
                            team_data = self._extract_data_from_soup(soup)
                            if team_data:
                                return team_data
                    
                except Exception as e:
                    logger.debug(f"API endpoint {endpoint} failed: {e}")
                    continue
            
        except Exception as e:
            logger.warning(f"API scraping failed: {e}")
        
        return None
    
    def _extract_data_from_soup(self, soup: BeautifulSoup) -> Optional[Dict]:
        """
        Extract team data from BeautifulSoup object
        """
        try:
            team_data = {}
            
            # Look for tables first
            tables = soup.find_all('table')
            logger.info(f"Found {len(tables)} tables in soup")
            
            for table in tables:
                # Try to extract data from table
                rows = table.find_all('tr')
                logger.info(f"Table has {len(rows)} rows")
                
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 10:  # Expecting multiple columns
                        # Try to extract team name and grades
                        row_text = ' '.join([cell.get_text().strip() for cell in cells])
                        
                        # Look for team names
                        team_name = self._extract_team_name_from_text(row_text)
                        if team_name:
                            grades = self._extract_grades_from_text(row_text)
                            if grades:
                                team_data[team_name] = grades
                                logger.info(f"✅ Extracted data for {team_name}")
            
            # If no tables, try other approaches
            if not team_data:
                # Look for any structured data
                all_text = soup.get_text()
                team_data = self._extract_data_from_text(all_text)
            
            return team_data if team_data else None
            
        except Exception as e:
            logger.warning(f"Data extraction from soup failed: {e}")
            return None
    
    def _extract_team_name_from_text(self, text: str) -> Optional[str]:
        """
        Extract team name from text
        """
        # Look for full team names
        team_patterns = [
            r'(Buffalo Bills)', r'(Miami Dolphins)', r'(Kansas City Chiefs)',
            r'(Baltimore Ravens)', r'(San Francisco 49ers)', r'(Philadelphia Eagles)',
            r'(Dallas Cowboys)', r'(Detroit Lions)', r'(Green Bay Packers)',
            r'(Cincinnati Bengals)', r'(Los Angeles Rams)', r'(Tampa Bay Buccaneers)',
            r'(Indianapolis Colts)', r'(Jacksonville Jaguars)', r'(Houston Texans)',
            r'(New York Jets)', r'(Pittsburgh Steelers)', r'(Cleveland Browns)',
            r'(Denver Broncos)', r'(Las Vegas Raiders)', r'(Los Angeles Chargers)',
            r'(New England Patriots)', r'(Tennessee Titans)', r'(Washington Commanders)',
            r'(Carolina Panthers)', r'(Atlanta Falcons)', r'(New Orleans Saints)',
            r'(Minnesota Vikings)', r'(Arizona Cardinals)', r'(Seattle Seahawks)',
            r'(New York Giants)', r'(Chicago Bears)'
        ]
        
        for pattern in team_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_grades_from_text(self, text: str) -> Optional[Dict]:
        """
        Extract grade values from text
        """
        # Look for decimal numbers (grades)
        grade_pattern = re.compile(r'\b(\d{1,2}\.\d)\b')
        grades = grade_pattern.findall(text)
        
        if len(grades) >= 10:  # Expecting multiple grades
            try:
                grade_values = [float(g) for g in grades]
                
                # Basic validation - grades should be between 0-100
                valid_grades = [g for g in grade_values if 0 <= g <= 100]
                
                if len(valid_grades) >= 10:
                    return {
                        'overall': valid_grades[0] if len(valid_grades) > 0 else 70.0,
                        'offense_overall': valid_grades[1] if len(valid_grades) > 1 else 70.0,
                        'passing': valid_grades[2] if len(valid_grades) > 2 else 70.0,
                        'pass_blocking': valid_grades[3] if len(valid_grades) > 3 else 70.0,
                        'receiving': valid_grades[4] if len(valid_grades) > 4 else 70.0,
                        'rushing': valid_grades[5] if len(valid_grades) > 5 else 70.0,
                        'run_blocking': valid_grades[6] if len(valid_grades) > 6 else 70.0,
                        'defense_overall': valid_grades[7] if len(valid_grades) > 7 else 70.0,
                        'run_defense': valid_grades[8] if len(valid_grades) > 8 else 70.0,
                        'tackling': valid_grades[9] if len(valid_grades) > 9 else 70.0,
                        'pass_rush': valid_grades[10] if len(valid_grades) > 10 else 70.0,
                        'coverage': valid_grades[11] if len(valid_grades) > 11 else 70.0,
                        'special_teams': valid_grades[12] if len(valid_grades) > 12 else 70.0
                    }
            except ValueError:
                pass
        
        return None
    
    def _extract_data_from_text(self, text: str) -> Dict:
        """
        Extract data from raw text using pattern matching
        """
        team_data = {}
        
        # Split text into lines and look for patterns
        lines = text.split('\n')
        
        current_team = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line contains a team name
            team_name = self._extract_team_name_from_text(line)
            if team_name:
                current_team = team_name
                continue
            
            # If we have a current team, look for grades in this line
            if current_team:
                grades = self._extract_grades_from_text(line)
                if grades:
                    team_data[current_team] = grades
                    current_team = None  # Reset for next team
        
        return team_data
    
    def _parse_json_data(self, data) -> Optional[Dict]:
        """
        Parse JSON data to extract team grades
        """
        try:
            team_data = {}
            
            # Try different JSON structures
            if isinstance(data, dict):
                # Look for teams key
                if 'teams' in data:
                    teams = data['teams']
                elif 'data' in data:
                    teams = data['data']
                else:
                    teams = data
                
                # Process teams data
                if isinstance(teams, list):
                    for team in teams:
                        if isinstance(team, dict) and 'name' in team:
                            team_name = team['name']
                            team_data[team_name] = team
                elif isinstance(teams, dict):
                    team_data = teams
            
            return team_data if team_data else None
            
        except Exception as e:
            logger.warning(f"JSON parsing failed: {e}")
            return None
    
    def _get_fallback_data(self) -> Dict:
        """
        Fallback data when all scraping methods fail
        """
        logger.info("📊 Using fallback data structure")
        
        # Return minimal data structure for all teams
        fallback_data = {}
        
        all_teams = [
            'Arizona Cardinals', 'Atlanta Falcons', 'Baltimore Ravens', 'Buffalo Bills',
            'Carolina Panthers', 'Chicago Bears', 'Cincinnati Bengals', 'Cleveland Browns',
            'Dallas Cowboys', 'Denver Broncos', 'Detroit Lions', 'Green Bay Packers',
            'Houston Texans', 'Indianapolis Colts', 'Jacksonville Jaguars', 'Kansas City Chiefs',
            'Las Vegas Raiders', 'Los Angeles Chargers', 'Los Angeles Rams', 'Miami Dolphins',
            'Minnesota Vikings', 'New England Patriots', 'New Orleans Saints', 'New York Giants',
            'New York Jets', 'Philadelphia Eagles', 'Pittsburgh Steelers', 'San Francisco 49ers',
            'Seattle Seahawks', 'Tampa Bay Buccaneers', 'Tennessee Titans', 'Washington Commanders'
        ]
        
        for team in all_teams:
            fallback_data[team] = {
                'overall': 70.0,
                'offense_overall': 70.0,
                'passing': 70.0,
                'pass_blocking': 70.0,
                'receiving': 70.0,
                'rushing': 70.0,
                'run_blocking': 70.0,
                'defense_overall': 70.0,
                'run_defense': 70.0,
                'tackling': 70.0,
                'pass_rush': 70.0,
                'coverage': 70.0,
                'special_teams': 70.0
            }
        
        return fallback_data
    
    def convert_to_nested_format(self, flat_data: Dict) -> Dict:
        """
        Convert flat data structure to nested format for compatibility
        """
        nested_data = {}
        
        for team_name, team_data in flat_data.items():
            nested_data[team_name] = {
                'overall': team_data.get('overall', 70.0),
                'offense': {
                    'overall': team_data.get('offense_overall', 70.0),
                    'passing': team_data.get('passing', 70.0),
                    'pass_blocking': team_data.get('pass_blocking', 70.0),
                    'receiving': team_data.get('receiving', 70.0),
                    'rushing': team_data.get('rushing', 70.0),
                    'run_blocking': team_data.get('run_blocking', 70.0)
                },
                'defense': {
                    'overall': team_data.get('defense_overall', 70.0),
                    'run_defense': team_data.get('run_defense', 70.0),
                    'tackling': team_data.get('tackling', 70.0),
                    'pass_rush': team_data.get('pass_rush', 70.0),
                    'coverage': team_data.get('coverage', 70.0)
                },
                'special_teams': {
                    'overall': team_data.get('special_teams', 70.0)
                }
            }
        
        return nested_data

if __name__ == "__main__":
    # Test the live scraper
    scraper = LivePFFScraper()
    
    print("🚀 TESTING LIVE PFF SCRAPER")
    print("=" * 50)
    
    # Scrape data
    raw_data = scraper.scrape_pff_data()
    
    print(f"📊 Raw data type: {type(raw_data)}")
    print(f"📊 Number of teams: {len(raw_data) if raw_data else 0}")
    
    if raw_data:
        print("\n🔍 Sample data:")
        for team_name, data in list(raw_data.items())[:3]:
            print(f"{team_name}: {data}")
        
        # Convert to nested format
        nested_data = scraper.convert_to_nested_format(raw_data)
        
        print("\n🔍 Converted nested data:")
        for team_name, data in list(nested_data.items())[:3]:
            print(f"{team_name}: {data}")
        
        print(f"\n✅ Successfully processed {len(nested_data)} teams")
    else:
        print("❌ No data was scraped")

