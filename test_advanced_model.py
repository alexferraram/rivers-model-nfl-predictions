"""
Advanced Test Script for NFL Prediction Model

This script tests the advanced model with comprehensive team statistics,
matchups, player data, injuries, and situational performance.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from advanced_model import AdvancedNFLPredictionModel
import pandas as pd
import numpy as np


def create_comprehensive_team_data():
    """Create comprehensive team data for testing."""
    
    # Strong team data (e.g., Kansas City Chiefs)
    strong_team = {
        # Basic offensive stats
        'offense_yards_per_play': 6.2,
        'offense_first_down_rate': 0.42,
        'offense_turnover_rate': 0.06,
        'offense_touchdowns': 52,
        
        # Situational stats
        'situational_third_down_rate': 0.48,
        'situational_redzone_td_rate': 0.68,
        'situational_goal_line_td_rate': 0.75,
        'situational_two_min_td_rate': 0.25,
        'situational_short_yardage_success': 0.78,
        'situational_long_yardage_success': 0.35,
        
        # Player stats
        'player_skill_player_games': 64,
        'player_total_passing_yards': 4500,
        'player_total_rushing_yards': 1800,
        'player_total_receiving_yards': 4200,
        'player_total_touchdowns': 48,
        'player_passing_yards_per_game': 281,
        'player_rushing_yards_per_game': 113,
        'player_receiving_yards_per_game': 263,
        'player_touchdowns_per_game': 3.0,
        
        # Defensive stats
        'defense_yards_per_play': 5.1,
        'defense_first_down_rate': 0.32,
        'defense_turnover_rate': 0.12,
        'defense_touchdowns': 28,
        'player_total_tackles': 850,
        'player_total_sacks': 45,
        'player_total_interceptions': 18,
        'player_total_passes_defended': 65,
        'player_tackles_per_game': 53,
        'player_sacks_per_game': 2.8,
        
        # Tendencies
        'tendencies_pass_rate': 0.65,
        'tendencies_run_rate': 0.35,
        'tendencies_shotgun_rate': 0.72,
        'tendencies_no_huddle_rate': 0.15,
        'tendencies_first_down_pass_rate': 0.68,
        'tendencies_redzone_pass_rate': 0.55,
        
        # Injury impact
        'injury_total_injuries': 8,
        'injury_key_player_injuries': 2,
        'injury_games_lost': 12,
        'injury_injury_rate': 0.15,
        'injury_key_injury_rate': 0.08,
        
        # Matchup advantages
        'matchup_yards_per_play_matchup_adv': 1.1,
        'matchup_first_down_rate_matchup_adv': 0.10,
        'matchup_turnover_rate_matchup_adv': -0.06,
        'matchup_third_down_rate_matchup_adv': 0.16,
        'matchup_redzone_td_rate_matchup_adv': 0.18,
        'matchup_passing_yards_per_game_matchup_adv': 45,
        'matchup_rushing_yards_per_game_matchup_adv': 25,
        'matchup_touchdowns_per_game_matchup_adv': 0.8,
    }
    
    # Average team data (e.g., Minnesota Vikings)
    average_team = {
        # Basic offensive stats
        'offense_yards_per_play': 5.5,
        'offense_first_down_rate': 0.35,
        'offense_turnover_rate': 0.08,
        'offense_touchdowns': 42,
        
        # Situational stats
        'situational_third_down_rate': 0.38,
        'situational_redzone_td_rate': 0.58,
        'situational_goal_line_td_rate': 0.65,
        'situational_two_min_td_rate': 0.18,
        'situational_short_yardage_success': 0.68,
        'situational_long_yardage_success': 0.28,
        
        # Player stats
        'player_skill_player_games': 60,
        'player_total_passing_yards': 3800,
        'player_total_rushing_yards': 1600,
        'player_total_receiving_yards': 3600,
        'player_total_touchdowns': 40,
        'player_passing_yards_per_game': 238,
        'player_rushing_yards_per_game': 100,
        'player_receiving_yards_per_game': 225,
        'player_touchdowns_per_game': 2.5,
        
        # Defensive stats
        'defense_yards_per_play': 5.4,
        'defense_first_down_rate': 0.35,
        'defense_turnover_rate': 0.09,
        'defense_touchdowns': 35,
        'player_total_tackles': 920,
        'player_total_sacks': 38,
        'player_total_interceptions': 15,
        'player_total_passes_defended': 58,
        'player_tackles_per_game': 58,
        'player_sacks_per_game': 2.4,
        
        # Tendencies
        'tendencies_pass_rate': 0.58,
        'tendencies_run_rate': 0.42,
        'tendencies_shotgun_rate': 0.55,
        'tendencies_no_huddle_rate': 0.08,
        'tendencies_first_down_pass_rate': 0.60,
        'tendencies_redzone_pass_rate': 0.45,
        
        # Injury impact
        'injury_total_injuries': 12,
        'injury_key_player_injuries': 3,
        'injury_games_lost': 18,
        'injury_injury_rate': 0.22,
        'injury_key_injury_rate': 0.12,
        
        # Matchup advantages
        'matchup_yards_per_play_matchup_adv': 0.1,
        'matchup_first_down_rate_matchup_adv': 0.0,
        'matchup_turnover_rate_matchup_adv': -0.01,
        'matchup_third_down_rate_matchup_adv': 0.0,
        'matchup_redzone_td_rate_matchup_adv': 0.0,
        'matchup_passing_yards_per_game_matchup_adv': 0,
        'matchup_rushing_yards_per_game_matchup_adv': 0,
        'matchup_touchdowns_per_game_matchup_adv': 0.0,
    }
    
    # Weak team data (e.g., struggling team)
    weak_team = {
        # Basic offensive stats
        'offense_yards_per_play': 4.8,
        'offense_first_down_rate': 0.28,
        'offense_turnover_rate': 0.12,
        'offense_touchdowns': 28,
        
        # Situational stats
        'situational_third_down_rate': 0.28,
        'situational_redzone_td_rate': 0.45,
        'situational_goal_line_td_rate': 0.50,
        'situational_two_min_td_rate': 0.10,
        'situational_short_yardage_success': 0.55,
        'situational_long_yardage_success': 0.18,
        
        # Player stats
        'player_skill_player_games': 55,
        'player_total_passing_yards': 3200,
        'player_total_rushing_yards': 1400,
        'player_total_receiving_yards': 3000,
        'player_total_touchdowns': 32,
        'player_passing_yards_per_game': 200,
        'player_rushing_yards_per_game': 88,
        'player_receiving_yards_per_game': 188,
        'player_touchdowns_per_game': 2.0,
        
        # Defensive stats
        'defense_yards_per_play': 5.8,
        'defense_first_down_rate': 0.38,
        'defense_turnover_rate': 0.06,
        'defense_touchdowns': 42,
        'player_total_tackles': 980,
        'player_total_sacks': 28,
        'player_total_interceptions': 10,
        'player_total_passes_defended': 45,
        'player_tackles_per_game': 61,
        'player_sacks_per_game': 1.8,
        
        # Tendencies
        'tendencies_pass_rate': 0.52,
        'tendencies_run_rate': 0.48,
        'tendencies_shotgun_rate': 0.45,
        'tendencies_no_huddle_rate': 0.05,
        'tendencies_first_down_pass_rate': 0.55,
        'tendencies_redzone_pass_rate': 0.40,
        
        # Injury impact
        'injury_total_injuries': 18,
        'injury_key_player_injuries': 5,
        'injury_games_lost': 28,
        'injury_injury_rate': 0.32,
        'injury_key_injury_rate': 0.20,
        
        # Matchup advantages
        'matchup_yards_per_play_matchup_adv': -0.7,
        'matchup_first_down_rate_matchup_adv': -0.07,
        'matchup_turnover_rate_matchup_adv': 0.06,
        'matchup_third_down_rate_matchup_adv': -0.10,
        'matchup_redzone_td_rate_matchup_adv': -0.13,
        'matchup_passing_yards_per_game_matchup_adv': -38,
        'matchup_rushing_yards_per_game_matchup_adv': -12,
        'matchup_touchdowns_per_game_matchup_adv': -0.5,
    }
    
    return strong_team, average_team, weak_team


def test_advanced_model():
    """Test the advanced NFL prediction model."""
    
    print("Testing Advanced NFL Prediction Model")
    print("=" * 50)
    
    # Check if advanced model exists
    model_path = "models/advanced_random_forest_model.pkl"
    if not os.path.exists(model_path):
        print(f"Advanced model not found at {model_path}")
        print("Please run 'python main.py' first to train the advanced models.")
        return
    
    # Load the advanced model
    model = AdvancedNFLPredictionModel(model_type='random_forest')
    model.load_model(model_path)
    print("✓ Advanced model loaded successfully")
    
    # Get model summary
    summary = model.get_model_summary()
    print(f"✓ Model type: {summary['model_type']}")
    print(f"✓ Total features: {summary['total_features']}")
    print(f"✓ Selected features: {summary['selected_features']}")
    print(f"✓ Feature selection used: {summary['use_feature_selection']}")
    
    # Create test team data
    strong_team, average_team, weak_team = create_comprehensive_team_data()
    
    print("\n" + "=" * 50)
    print("COMPREHENSIVE GAME PREDICTIONS")
    print("=" * 50)
    
    # Test different scenarios
    scenarios = [
        {
            'name': 'Elite Team vs Average Team',
            'home': strong_team,
            'away': average_team
        },
        {
            'name': 'Average Team vs Weak Team',
            'home': average_team,
            'away': weak_team
        },
        {
            'name': 'Elite Team vs Weak Team',
            'home': strong_team,
            'away': weak_team
        },
        {
            'name': 'Evenly Matched Teams',
            'home': average_team,
            'away': average_team
        },
        {
            'name': 'Weak Team vs Elite Team (Home Field Advantage)',
            'home': weak_team,
            'away': strong_team
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}:")
        print("-" * 40)
        
        prediction = model.predict_game_advanced(scenario['home'], scenario['away'])
        
        print(f"   Home team win probability: {prediction['home_win_probability']:.3f}")
        print(f"   Away team win probability: {prediction['away_win_probability']:.3f}")
        print(f"   Predicted winner: {prediction['predicted_winner']}")
        print(f"   Confidence: {prediction['confidence']:.3f}")
        
        # Show key factors
        if prediction['key_factors']:
            print("   Key factors:")
            for factor in prediction['key_factors']:
                print(f"     • {factor}")
        
        # Show top feature contributions
        if prediction['feature_contributions']:
            print("   Top contributing features:")
            for feature, importance in list(prediction['feature_contributions'].items())[:3]:
                print(f"     • {feature}: {importance:.3f}")
    
    print("\n" + "=" * 50)
    print("INJURY IMPACT ANALYSIS")
    print("=" * 50)
    
    # Test injury impact
    healthy_team = strong_team.copy()
    injured_team = strong_team.copy()
    injured_team['injury_key_player_injuries'] = 8  # High injury count
    injured_team['injury_key_injury_rate'] = 0.25
    injured_team['injury_games_lost'] = 35
    
    print("\nHealthy Elite Team vs Injured Elite Team:")
    prediction = model.predict_game_advanced(healthy_team, injured_team)
    print(f"   Home team win probability: {prediction['home_win_probability']:.3f}")
    print(f"   Away team win probability: {prediction['away_win_probability']:.3f}")
    print(f"   Predicted winner: {prediction['predicted_winner']}")
    print(f"   Confidence: {prediction['confidence']:.3f}")
    
    if prediction['key_factors']:
        print("   Key factors:")
        for factor in prediction['key_factors']:
            print(f"     • {factor}")
    
    print("\n" + "=" * 50)
    print("SITUATIONAL PERFORMANCE ANALYSIS")
    print("=" * 50)
    
    # Test situational performance
    clutch_team = average_team.copy()
    clutch_team['situational_third_down_rate'] = 0.55  # Excellent 3rd down
    clutch_team['situational_redzone_td_rate'] = 0.75   # Excellent red zone
    clutch_team['situational_two_min_td_rate'] = 0.30   # Excellent 2-minute drill
    
    non_clutch_team = average_team.copy()
    non_clutch_team['situational_third_down_rate'] = 0.25  # Poor 3rd down
    non_clutch_team['situational_redzone_td_rate'] = 0.40   # Poor red zone
    non_clutch_team['situational_two_min_td_rate'] = 0.08   # Poor 2-minute drill
    
    print("\nClutch Team vs Non-Clutch Team:")
    prediction = model.predict_game_advanced(clutch_team, non_clutch_team)
    print(f"   Home team win probability: {prediction['home_win_probability']:.3f}")
    print(f"   Away team win probability: {prediction['away_win_probability']:.3f}")
    print(f"   Predicted winner: {prediction['predicted_winner']}")
    print(f"   Confidence: {prediction['confidence']:.3f}")
    
    if prediction['key_factors']:
        print("   Key factors:")
        for factor in prediction['key_factors']:
            print(f"     • {factor}")
    
    print("\n" + "=" * 50)
    print("Test completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    test_advanced_model()






