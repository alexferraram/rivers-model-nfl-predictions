"""
Debug script to examine the section structure around NFL.com tables
"""

import requests
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_section_structure():
    """Debug the section structure around NFL.com tables"""
    
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        response = session.get("https://www.nfl.com/injuries/", timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("🔍 DEBUGGING SECTION STRUCTURE AROUND NFL.COM TABLES")
        print("=" * 60)
        
        # Look for all tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        
        # Examine the first few tables and their context
        for i, table in enumerate(tables[:3]):
            print(f"\n📋 TABLE {i+1}:")
            print(f"Class: {table.get('class')}")
            
            # Look at parent elements
            parent = table.parent
            if parent:
                print(f"Parent: {parent.name} - {parent.get('class')}")
                parent_text = parent.get_text(strip=True)
                if any(team in parent_text for team in ['Dolphins', 'Bills', 'BUF', 'MIA']):
                    print(f"Parent contains team names: {parent_text[:200]}")
            
            # Look at grandparent elements
            if parent and parent.parent:
                grandparent = parent.parent
                print(f"Grandparent: {grandparent.name} - {grandparent.get('class')}")
                grandparent_text = grandparent.get_text(strip=True)
                if any(team in grandparent_text for team in ['Dolphins', 'Bills', 'BUF', 'MIA']):
                    print(f"Grandparent contains team names: {grandparent_text[:200]}")
            
            # Look at great-grandparent elements
            if parent and parent.parent and parent.parent.parent:
                great_grandparent = parent.parent.parent
                print(f"Great-grandparent: {great_grandparent.name} - {great_grandparent.get('class')}")
                great_grandparent_text = great_grandparent.get_text(strip=True)
                if any(team in great_grandparent_text for team in ['Dolphins', 'Bills', 'BUF', 'MIA']):
                    print(f"Great-grandparent contains team names: {great_grandparent_text[:200]}")
        
        print("\n✅ DEBUG COMPLETE")
        
    except Exception as e:
        logger.error(f"Error debugging section structure: {e}")

if __name__ == "__main__":
    debug_section_structure()



