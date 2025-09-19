"""
Get the correct Week 3 NFL schedule
"""

import nfl_data_py as nfl
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_correct_week3_schedule():
    """Get the correct Week 3 NFL schedule"""
    
    try:
        # Get 2025 schedule
        schedule = nfl.import_schedules([2025])
        
        # Filter for Week 3
        week3_games = schedule[schedule['week'] == 3]
        
        logger.info(f"Found {len(week3_games)} games in Week 3")
        
        # Display the games
        print("\n🏈 CORRECT WEEK 3 NFL SCHEDULE")
        print("=" * 50)
        
        for _, game in week3_games.iterrows():
            away_team = game['away_team']
            home_team = game['home_team']
            game_time = game['gameday']
            
            print(f"📅 {game_time}")
            print(f"🏈 {away_team} @ {home_team}")
            print()
        
        return week3_games
        
    except Exception as e:
        logger.error(f"Error getting Week 3 schedule: {e}")
        return None

if __name__ == "__main__":
    get_correct_week3_schedule()



