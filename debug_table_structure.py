"""
Debug script to examine the actual table structure on NFL.com
"""

import requests
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_table_structure():
    """Debug the actual table structure on NFL.com"""
    
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        response = session.get("https://www.nfl.com/injuries/", timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("🔍 DEBUGGING NFL.COM TABLE STRUCTURE")
        print("=" * 60)
        
        # Look for all tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        # Examine the first few tables in detail
        for i, table in enumerate(tables[:3]):
            print(f"\n📋 TABLE {i+1}:")
            print(f"Class: {table.get('class')}")
            
            rows = table.find_all('tr')
            print(f"Rows: {len(rows)}")
            
            # Show first few rows
            for j, row in enumerate(rows[:10]):
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 4:
                    cell_texts = [cell.get_text(strip=True) for cell in cells[:5]]
                    print(f"  Row {j+1}: {cell_texts}")
                    
                    # Check if this looks like a team header
                    first_cell = cell_texts[0]
                    if any(team in first_cell for team in ['Bills', 'Dolphins', 'BUF', 'MIA', 'Buffalo', 'Miami']):
                        print(f"    ⭐ POTENTIAL TEAM HEADER: {first_cell}")
        
        print("\n✅ DEBUG COMPLETE")
        
    except Exception as e:
        logger.error(f"Error debugging table structure: {e}")

if __name__ == "__main__":
    debug_table_structure()



