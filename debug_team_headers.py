"""
Debug script to examine team headers in NFL.com tables
"""

import requests
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_team_headers():
    """Debug team headers in NFL.com tables"""
    
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        response = session.get("https://www.nfl.com/injuries/", timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("🔍 DEBUGGING TEAM HEADERS IN NFL.COM TABLES")
        print("=" * 60)
        
        # Look for all tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        # Examine the first table in detail
        table = tables[0]
        print(f"\n📋 FIRST TABLE:")
        print(f"Class: {table.get('class')}")
        
        rows = table.find_all('tr')
        print(f"Rows: {len(rows)}")
        
        # Show all rows and look for team headers
        for j, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 4:
                cell_texts = [cell.get_text(strip=True) for cell in cells[:5]]
                print(f"  Row {j+1}: {cell_texts}")
                
                # Check if this looks like a team header
                first_cell = cell_texts[0]
                if any(team in first_cell for team in ['Bills', 'Dolphins', 'BUF', 'MIA', 'Buffalo', 'Miami']):
                    print(f"    ⭐ POTENTIAL TEAM HEADER: {first_cell}")
                elif first_cell in ['Dolphins', 'Bills']:
                    print(f"    🎯 EXACT TEAM HEADER: {first_cell}")
        
        print("\n✅ DEBUG COMPLETE")
        
    except Exception as e:
        logger.error(f"Error debugging team headers: {e}")

if __name__ == "__main__":
    debug_team_headers()



