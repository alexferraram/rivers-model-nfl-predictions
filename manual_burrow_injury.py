"""
Manual Joe Burrow Injury Addition
Add Joe Burrow (Cincinnati Bengals QB) to injury data since he's on IR
"""
import logging
from typing import Dict

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_burrow_injury(injury_data: Dict) -> Dict:
    """
    Add Joe Burrow injury to Cincinnati Bengals injury data
    """
    logger.info("🏥 Adding Joe Burrow (QB) injury to Cincinnati Bengals...")
    
    # Add Joe Burrow to Cincinnati's injury list
    if 'Cincinnati' in injury_data:
        injury_data['Cincinnati'].append({
            'player': 'Joe Burrow',
            'position': 'QB',
            'injury': 'Wrist (IR)',
            'status': 'Out'
        })
        logger.info("✅ Added Joe Burrow (QB) - OUT to Cincinnati Bengals injury list")
    else:
        logger.warning("❌ Cincinnati not found in injury data")
    
    return injury_data

if __name__ == "__main__":
    # Test the function
    test_data = {
        'Cincinnati': [
            {'player': 'Shemar Stewart', 'position': 'DE', 'injury': 'Ankle', 'status': 'Out'},
            {'player': 'Cam Taylor-Britt', 'position': 'CB', 'injury': 'Shoulder', 'status': 'Doubtful'},
            {'player': 'DJ Turner II', 'position': 'CB', 'injury': 'Hamstring', 'status': 'Questionable'}
        ]
    }
    
    updated_data = add_burrow_injury(test_data)
    print("Updated Cincinnati injury data:")
    for injury in updated_data['Cincinnati']:
        print(f"  - {injury['player']} ({injury['position']}) - {injury['status']}")
