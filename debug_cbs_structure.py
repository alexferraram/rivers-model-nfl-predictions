"""
Debug script to examine CBS Sports injury page structure
"""

import requests
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_cbs_structure():
    """Debug the CBS Sports injury page structure"""
    
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        response = session.get("https://www.cbssports.com/nfl/injuries/", timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("🔍 DEBUGGING CBS SPORTS INJURY PAGE STRUCTURE")
        print("=" * 60)
        
        # Look for all divs with class containing 'table'
        table_divs = soup.find_all('div', class_=lambda x: x and 'table' in x.lower())
        print(f"Found {len(table_divs)} divs with 'table' in class")
        
        # Look for all tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        # Look for team-related elements
        team_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'div'], string=lambda text: text and any(team in text.lower() for team in ['buffalo', 'miami', 'patriots', 'jets', 'ravens', 'bengals']))
        print(f"Found {len(team_elements)} team-related elements")
        
        # Print first few team elements
        for i, element in enumerate(team_elements[:5]):
            print(f"Team element {i+1}: {element.name} - {element.get_text(strip=True)[:100]}")
        
        # Look for specific patterns
        print("\n🔍 LOOKING FOR SPECIFIC PATTERNS:")
        
        # Check for TableBase class
        tablebase_divs = soup.find_all('div', class_='TableBase')
        print(f"TableBase divs: {len(tablebase_divs)}")
        
        # Check for any div with team names
        all_divs = soup.find_all('div')
        team_divs = []
        for div in all_divs:
            text = div.get_text(strip=True)
            if any(team in text.lower() for team in ['buffalo', 'miami', 'patriots', 'jets']):
                team_divs.append(div)
        
        print(f"Divs containing team names: {len(team_divs)}")
        
        # Print structure of first few team divs
        for i, div in enumerate(team_divs[:3]):
            print(f"\nTeam div {i+1}:")
            print(f"  Class: {div.get('class')}")
            print(f"  Text: {div.get_text(strip=True)[:200]}")
            print(f"  Parent: {div.parent.name if div.parent else 'None'}")
            if div.parent:
                print(f"  Parent class: {div.parent.get('class')}")
        
        # Look for specific team sections
        print("\n🔍 LOOKING FOR BUFFALO BILLS SECTION:")
        buffalo_elements = soup.find_all(string=lambda text: text and 'buffalo' in text.lower())
        print(f"Found {len(buffalo_elements)} elements containing 'buffalo'")
        
        for i, element in enumerate(buffalo_elements[:3]):
            print(f"Buffalo element {i+1}: {element.strip()[:100]}")
            if element.parent:
                print(f"  Parent: {element.parent.name} - {element.parent.get('class')}")
        
        print("\n✅ DEBUG COMPLETE")
        
    except Exception as e:
        logger.error(f"Error debugging CBS structure: {e}")

if __name__ == "__main__":
    debug_cbs_structure()



