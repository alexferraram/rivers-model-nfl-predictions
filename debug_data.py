#!/usr/bin/env python3
"""
Debug script to check NFL data structure
"""

import pandas as pd
import nfl_data_py as nfl

def debug_nfl_data():
    """Debug NFL data structure"""
    print("🔍 Debugging NFL data structure...")
    
    try:
        # Load schedules
        print("\n📅 Loading schedules...")
        schedules = nfl.import_schedules([2024])
        print(f"Schedules shape: {schedules.shape}")
        print(f"Schedules columns: {list(schedules.columns)}")
        print("\nFirst few rows:")
        print(schedules.head())
        
        # Load play-by-play
        print("\n🏈 Loading play-by-play data...")
        pbp = nfl.import_pbp_data([2024])
        print(f"PBP shape: {pbp.shape}")
        print(f"PBP columns: {list(pbp.columns)[:20]}...")  # First 20 columns
        
        # Check game data
        print("\n🎯 Sample game data:")
        sample_game = pbp[pbp['game_id'] == pbp['game_id'].iloc[0]].copy()
        print(f"Sample game plays: {len(sample_game)}")
        print(f"Sample game columns: {list(sample_game.columns)[:15]}...")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_nfl_data()





