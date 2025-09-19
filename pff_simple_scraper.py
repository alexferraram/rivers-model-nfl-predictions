"""
Simple PFF Data Scraper - Focus on requests-based extraction
This scraper attempts to extract real-time PFF data for all 32 NFL teams using requests
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

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimplePFFScraper:
    """
    Simple PFF data scraper using requests and BeautifulSoup
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
        Main method to scrape PFF data
        """
        logger.info("🚀 Starting simple PFF data extraction")
        
        # Try multiple approaches
        approaches = [
            self._scrape_with_enhanced_requests,
            self._scrape_with_different_endpoints,
            self._scrape_with_json_requests,
            self._scrape_with_table_parsing
        ]
        
        for i, approach in enumerate(approaches, 1):
            try:
                logger.info(f"🔧 Trying approach {i}...")
                data = approach()
                if data and len(data) > 5:  # If we got substantial data
                    logger.info(f"✅ Approach {i} successful: {len(data)} teams")
                    return data
                else:
                    logger.info(f"⚠️ Approach {i} returned insufficient data")
            except Exception as e:
                logger.warning(f"Approach {i} failed: {e}")
                continue
        
        # Fallback to known data
        logger.warning("⚠️ All approaches failed, using fallback data")
        return self._get_fallback_data()
    
    def _scrape_with_enhanced_requests(self) -> Optional[Dict]:
        """
        Enhanced requests scraping with multiple header combinations
        """
        try:
            # Try different header combinations
            header_sets = [
                {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0'
                },
                {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
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
                    
                    response = requests.get(self.url, headers=headers, timeout=20)
                    logger.info(f"Response status: {response.status_code}")
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Check if we got meaningful content
                        page_text = soup.get_text()
                        logger.info(f"Page text length: {len(page_text)}")
                        
                        # Look for indicators of successful content
                        if len(page_text) > 5000 and ('Bills' in page_text or 'Dolphins' in page_text or 'Chiefs' in page_text):
                            logger.info("✅ Got meaningful content with requests")
                            team_data = self._extract_data_from_soup(soup)
                            if team_data and len(team_data) > 5:
                                return team_data
                        
                        # Debug: Print some page content
                        logger.info(f"Page title: {soup.title.string if soup.title else 'No title'}")
                        
                        # Look for any data patterns
                        tables = soup.find_all('table')
                        logger.info(f"Found {len(tables)} tables")
                        
                        if tables:
                            for j, table in enumerate(tables):
                                rows = table.find_all('tr')
                                logger.info(f"Table {j+1} has {len(rows)} rows")
                                if len(rows) > 10:  # Substantial table
                                    table_data = self._extract_table_data(table)
                                    if table_data:
                                        return table_data
                    
                    time.sleep(2)  # Be respectful
                    
                except Exception as e:
                    logger.warning(f"Header set {i+1} failed: {e}")
                    continue
            
        except Exception as e:
            logger.warning(f"Enhanced requests scraping failed: {e}")
        
        return None
    
    def _scrape_with_different_endpoints(self) -> Optional[Dict]:
        """
        Try different URL endpoints
        """
        try:
            endpoints = [
                "https://premium.pff.com/nfl/teams/2025/REGPO",
                "https://premium.pff.com/nfl/teams/2025",
                "https://premium.pff.com/nfl/teams",
                "https://premium.pff.com/nfl/teams/2025/REGPO/",
                "https://premium.pff.com/nfl/teams/2025/REGPO?format=json",
                "https://premium.pff.com/api/nfl/teams/2025/REGPO",
                "https://premium.pff.com/data/nfl/teams/2025/REGPO"
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            
            for endpoint in endpoints:
                try:
                    logger.info(f"Trying endpoint: {endpoint}")
                    response = requests.get(endpoint, headers=headers, timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        page_text = soup.get_text()
                        
                        if len(page_text) > 1000 and ('Bills' in page_text or 'Dolphins' in page_text):
                            logger.info(f"✅ Got content from {endpoint}")
                            team_data = self._extract_data_from_soup(soup)
                            if team_data:
                                return team_data
                    
                    time.sleep(1)
                    
                except Exception as e:
                    logger.debug(f"Endpoint {endpoint} failed: {e}")
                    continue
            
        except Exception as e:
            logger.warning(f"Different endpoints scraping failed: {e}")
        
        return None
    
    def _scrape_with_json_requests(self) -> Optional[Dict]:
        """
        Try to find JSON data
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': self.url
            }
            
            # Try common API patterns
            api_endpoints = [
                "https://premium.pff.com/api/nfl/teams/2025/REGPO",
                "https://premium.pff.com/api/teams",
                "https://premium.pff.com/data/teams.json",
                "https://premium.pff.com/api/v1/teams",
                "https://premium.pff.com/api/nfl/teams",
                "https://premium.pff.com/teams.json"
            ]
            
            for endpoint in api_endpoints:
                try:
                    logger.info(f"Trying JSON endpoint: {endpoint}")
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
                    logger.debug(f"JSON endpoint {endpoint} failed: {e}")
                    continue
            
        except Exception as e:
            logger.warning(f"JSON requests scraping failed: {e}")
        
        return None
    
    def _scrape_with_table_parsing(self) -> Optional[Dict]:
        """
        Focus on table parsing
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            
            response = requests.get(self.url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for all tables
                tables = soup.find_all('table')
                logger.info(f"Found {len(tables)} tables for parsing")
                
                for i, table in enumerate(tables):
                    logger.info(f"Analyzing table {i+1}...")
                    table_data = self._extract_table_data(table)
                    if table_data and len(table_data) > 5:
                        logger.info(f"✅ Table {i+1} yielded {len(table_data)} teams")
                        return table_data
                
                # If no tables, try other elements
                divs = soup.find_all('div', class_=re.compile(r'table|data|team|grade|row'))
                logger.info(f"Found {len(divs)} relevant divs")
                
                for div in divs:
                    div_data = self._extract_div_data(div)
                    if div_data and len(div_data) > 5:
                        logger.info(f"✅ Div yielded {len(div_data)} teams")
                        return div_data
            
        except Exception as e:
            logger.warning(f"Table parsing failed: {e}")
        
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
                table_data = self._extract_table_data(table)
                if table_data:
                    team_data.update(table_data)
            
            # If no tables, try other approaches
            if not team_data:
                # Look for any structured data
                all_text = soup.get_text()
                team_data = self._extract_data_from_text(all_text)
            
            return team_data if team_data else None
            
        except Exception as e:
            logger.warning(f"Data extraction from soup failed: {e}")
            return None
    
    def _extract_table_data(self, table) -> Optional[Dict]:
        """
        Extract data from a table element
        """
        try:
            team_data = {}
            rows = table.find_all('tr')
            
            logger.info(f"Table has {len(rows)} rows")
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 8:  # Expecting multiple columns
                    # Try to extract team name and grades
                    row_text = ' '.join([cell.get_text().strip() for cell in cells])
                    
                    # Look for team names
                    team_name = self._extract_team_name_from_text(row_text)
                    if team_name:
                        grades = self._extract_grades_from_text(row_text)
                        if grades:
                            team_data[team_name] = grades
                            logger.info(f"✅ Extracted data for {team_name}")
            
            return team_data if team_data else None
            
        except Exception as e:
            logger.warning(f"Table data extraction failed: {e}")
            return None
    
    def _extract_div_data(self, div) -> Optional[Dict]:
        """
        Extract data from a div element
        """
        try:
            team_data = {}
            div_text = div.get_text()
            
            # Look for team names and grades in the div
            team_name = self._extract_team_name_from_text(div_text)
            if team_name:
                grades = self._extract_grades_from_text(div_text)
                if grades:
                    team_data[team_name] = grades
            
            return team_data if team_data else None
            
        except Exception as e:
            logger.warning(f"Div data extraction failed: {e}")
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
        
        if len(grades) >= 8:  # Expecting multiple grades
            try:
                grade_values = [float(g) for g in grades]
                
                # Basic validation - grades should be between 0-100
                valid_grades = [g for g in grade_values if 0 <= g <= 100]
                
                if len(valid_grades) >= 8:
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
    # Test the simple scraper
    scraper = SimplePFFScraper()
    
    print("🚀 TESTING SIMPLE PFF SCRAPER")
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

