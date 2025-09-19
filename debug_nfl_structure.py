"""
Debug script to examine NFL.com injury page structure
"""

import requests
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_nfl_structure():
    """Debug the NFL.com injury page structure"""
    
    try:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        response = session.get("https://www.nfl.com/injuries/", timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("🔍 DEBUGGING NFL.COM INJURY PAGE STRUCTURE")
        print("=" * 60)
        
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
        
        # Check for team names in text
        page_text = soup.get_text()
        team_names = ['Buffalo', 'Miami', 'Patriots', 'Jets', 'Ravens', 'Bengals', 'Browns', 'Steelers']
        for team in team_names:
            count = page_text.lower().count(team.lower())
            print(f"'{team}' appears {count} times in page text")
        
        # Look for specific team sections
        print("\n🔍 LOOKING FOR BUFFALO BILLS SECTION:")
        buffalo_elements = soup.find_all(string=lambda text: text and 'buffalo' in text.lower())
        print(f"Found {len(buffalo_elements)} elements containing 'buffalo'")
        
        for i, element in enumerate(buffalo_elements[:3]):
            print(f"Buffalo element {i+1}: {element.strip()[:100]}")
            if element.parent:
                print(f"  Parent: {element.parent.name} - {element.parent.get('class')}")
        
        # Look for table structure
        print("\n🔍 EXAMINING TABLE STRUCTURE:")
        for i, table in enumerate(tables[:3]):
            print(f"\nTable {i+1}:")
            print(f"  Class: {table.get('class')}")
            rows = table.find_all('tr')
            print(f"  Rows: {len(rows)}")
            if rows:
                first_row = rows[0]
                cells = first_row.find_all(['th', 'td'])
                print(f"  First row cells: {len(cells)}")
                for j, cell in enumerate(cells[:5]):
                    print(f"    Cell {j+1}: {cell.get_text(strip=True)[:50]}")
        
        # Look for team headers
        print("\n🔍 LOOKING FOR TEAM HEADERS:")
        headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for header in headers:
            text = header.get_text(strip=True)
            if any(team in text.lower() for team in ['buffalo', 'miami', 'patriots', 'jets']):
                print(f"Team header: {header.name} - {text}")
        
        # Look for team names in HTML attributes
        print("\n🔍 LOOKING FOR TEAM NAMES IN HTML ATTRIBUTES:")
        elements_with_team_names = soup.find_all(attrs={'class': lambda x: x and any(team in str(x).lower() for team in ['buffalo', 'miami', 'patriots', 'jets'])})
        print(f"Found {len(elements_with_team_names)} elements with team names in class")
        
        # Look for team names in data attributes
        elements_with_data = soup.find_all(attrs={'data-team': True})
        print(f"Found {len(elements_with_data)} elements with data-team attribute")
        for elem in elements_with_data[:5]:
            print(f"  data-team: {elem.get('data-team')}")
        
        # Look for team names in id attributes
        elements_with_id = soup.find_all(attrs={'id': lambda x: x and any(team in str(x).lower() for team in ['buffalo', 'miami', 'patriots', 'jets'])})
        print(f"Found {len(elements_with_id)} elements with team names in id")
        
        # Look for team names in text content more broadly
        print("\n🔍 LOOKING FOR TEAM NAMES IN TEXT CONTENT:")
        all_text_elements = soup.find_all(string=True)
        team_mentions = []
        for text_elem in all_text_elements:
            text = text_elem.strip()
            if any(team in text.lower() for team in ['buffalo', 'miami', 'patriots', 'jets', 'bills', 'dolphins']):
                team_mentions.append(text)
        
        print(f"Found {len(team_mentions)} text elements mentioning teams")
        for mention in team_mentions[:5]:
            print(f"  '{mention[:100]}'")
        
        # Look for specific table context
        print("\n🔍 EXAMINING TABLE CONTEXT:")
        for i, table in enumerate(tables[:3]):
            print(f"\nTable {i+1} context:")
            # Look at parent elements
            parent = table.parent
            if parent:
                print(f"  Parent: {parent.name} - {parent.get('class')}")
                parent_text = parent.get_text(strip=True)
                if any(team in parent_text.lower() for team in ['buffalo', 'miami', 'patriots', 'jets', 'bills', 'dolphins']):
                    print(f"  Parent contains team name: {parent_text[:100]}")
            
            # Look at siblings
            if table.previous_sibling:
                prev_text = table.previous_sibling.get_text(strip=True) if hasattr(table.previous_sibling, 'get_text') else str(table.previous_sibling)
                if any(team in prev_text.lower() for team in ['buffalo', 'miami', 'patriots', 'jets', 'bills', 'dolphins']):
                    print(f"  Previous sibling contains team name: {prev_text[:100]}")
            
            # Look at grandparent elements
            if parent and parent.parent:
                grandparent = parent.parent
                print(f"  Grandparent: {grandparent.name} - {grandparent.get('class')}")
                grandparent_text = grandparent.get_text(strip=True)
                if any(team in grandparent_text.lower() for team in ['buffalo', 'miami', 'patriots', 'jets', 'bills', 'dolphins']):
                    print(f"  Grandparent contains team name: {grandparent_text[:100]}")
        
        # Look for team names that appear before tables
        print("\n🔍 LOOKING FOR TEAM NAMES BEFORE TABLES:")
        for i, table in enumerate(tables[:5]):
            # Find all text elements before this table
            all_elements = soup.find_all()
            table_index = all_elements.index(table) if table in all_elements else -1
            
            if table_index > 0:
                # Look at elements before the table
                for j in range(max(0, table_index - 10), table_index):
                    elem = all_elements[j]
                    if hasattr(elem, 'get_text'):
                        text = elem.get_text(strip=True)
                        if any(team in text.lower() for team in ['bills', 'dolphins', 'patriots', 'jets', 'ravens', 'bengals']):
                            print(f"  Table {i+1} - Found team name '{text}' in {elem.name} element")
                            break
        
        print("\n✅ DEBUG COMPLETE")
        
    except Exception as e:
        logger.error(f"Error debugging NFL structure: {e}")

if __name__ == "__main__":
    debug_nfl_structure()
