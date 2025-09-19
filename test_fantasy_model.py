"""
Fantasy-Enhanced NFL Prediction Model Test Script

This script tests the fantasy-enhanced model with comprehensive team statistics,
fantasy football data, expected performance metrics, and efficiency analytics.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from advanced_model import AdvancedNFLPredictionModel
import pandas as pd
import numpy as np


def create_fantasy_enhanced_team_data():
    """Create comprehensive fantasy-enhanced team data for testing."""
    
    # Elite team with strong fantasy performance (e.g., Kansas City Chiefs)
    elite_team = {
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
        
        # Player stats
        'player_passing_yards_per_game': 281,
        'player_rushing_yards_per_game': 113,
        'player_touchdowns_per_game': 3.0,
        
        # Fantasy team strength
        'fantasy_total_fantasy_points': 2800,
        'fantasy_fantasy_points_per_game': 175,
        'fantasy_team_fantasy_efficiency': 1.15,
        'fantasy_qb_fantasy_points_per_game': 22.5,
        'fantasy_rb_fantasy_points_per_game': 18.2,
        'fantasy_wr_fantasy_points_per_game': 16.8,
        'fantasy_te_fantasy_points_per_game': 12.3,
        'fantasy_fantasy_consistency': 0.78,
        
        # Opportunity metrics
        'opportunity_total_expected_yards': 6500,
        'opportunity_total_actual_yards': 7200,
        'opportunity_yards_over_expected': 700,
        'opportunity_yards_efficiency': 1.11,
        'opportunity_avg_target_share': 0.18,
        'opportunity_max_target_share': 0.28,
        'opportunity_avg_carry_share': 0.12,
        'opportunity_max_carry_share': 0.22,
        'opportunity_red_zone_targets': 45,
        'opportunity_red_zone_carries': 38,
        'opportunity_high_value_touches': 85,
        'opportunity_high_value_touch_rate': 0.15,
        
        # Efficiency metrics
        'efficiency_avg_yards_per_target': 8.2,
        'efficiency_weighted_yards_per_target': 8.5,
        'efficiency_avg_yards_per_carry': 4.8,
        'efficiency_weighted_yards_per_carry': 4.9,
        'efficiency_avg_success_rate': 0.52,
        'efficiency_weighted_success_rate': 0.54,
        'efficiency_explosive_plays': 45,
        'efficiency_explosive_play_rate': 0.08,
        'efficiency_avg_route_efficiency': 0.78,
        'efficiency_avg_pass_block_efficiency': 0.82,
        'efficiency_avg_run_block_efficiency': 0.79,
        'efficiency_avg_tackle_efficiency': 0.85,
        'efficiency_avg_pass_rush_efficiency': 0.72,
        'efficiency_avg_coverage_efficiency': 0.68,
        
        # Defensive stats
        'defense_yards_per_play': 5.1,
        'defense_turnover_rate': 0.12,
        
        # Tendencies
        'tendencies_pass_rate': 0.65,
        'tendencies_shotgun_rate': 0.72,
        
        # Injury impact
        'injury_key_player_injuries': 2,
        'injury_key_injury_rate': 0.08,
        
        # Fantasy matchup advantages
        'fantasy_matchup_total_fantasy_points_matchup_adv': 8,
        'fantasy_matchup_fantasy_points_per_game_matchup_adv': 5.2,
        'fantasy_matchup_team_fantasy_efficiency_matchup_adv': 0.15,
        'fantasy_matchup_qb_fantasy_points_per_game_matchup_adv': 3.5,
        'fantasy_matchup_rb_fantasy_points_per_game_matchup_adv': 2.8,
        'fantasy_matchup_wr_fantasy_points_per_game_matchup_adv': 2.2,
        'fantasy_matchup_te_fantasy_points_per_game_matchup_adv': 1.8,
    }
    
    # Average team with moderate fantasy performance
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
        
        # Player stats
        'player_passing_yards_per_game': 238,
        'player_rushing_yards_per_game': 100,
        'player_touchdowns_per_game': 2.5,
        
        # Fantasy team strength
        'fantasy_total_fantasy_points': 2400,
        'fantasy_fantasy_points_per_game': 150,
        'fantasy_team_fantasy_efficiency': 1.02,
        'fantasy_qb_fantasy_points_per_game': 19.0,
        'fantasy_rb_fantasy_points_per_game': 15.4,
        'fantasy_wr_fantasy_points_per_game': 14.6,
        'fantasy_te_fantasy_points_per_game': 10.5,
        'fantasy_fantasy_consistency': 0.65,
        
        # Opportunity metrics
        'opportunity_total_expected_yards': 5800,
        'opportunity_total_actual_yards': 5900,
        'opportunity_yards_over_expected': 100,
        'opportunity_yards_efficiency': 1.02,
        'opportunity_avg_target_share': 0.15,
        'opportunity_max_target_share': 0.22,
        'opportunity_avg_carry_share': 0.10,
        'opportunity_max_carry_share': 0.18,
        'opportunity_red_zone_targets': 35,
        'opportunity_red_zone_carries': 32,
        'opportunity_high_value_touches': 65,
        'opportunity_high_value_touch_rate': 0.12,
        
        # Efficiency metrics
        'efficiency_avg_yards_per_target': 7.2,
        'efficiency_weighted_yards_per_target': 7.4,
        'efficiency_avg_yards_per_carry': 4.2,
        'efficiency_weighted_yards_per_carry': 4.3,
        'efficiency_avg_success_rate': 0.48,
        'efficiency_weighted_success_rate': 0.49,
        'efficiency_explosive_plays': 32,
        'efficiency_explosive_play_rate': 0.06,
        'efficiency_avg_route_efficiency': 0.68,
        'efficiency_avg_pass_block_efficiency': 0.75,
        'efficiency_avg_run_block_efficiency': 0.72,
        'efficiency_avg_tackle_efficiency': 0.78,
        'efficiency_avg_pass_rush_efficiency': 0.65,
        'efficiency_avg_coverage_efficiency': 0.62,
        
        # Defensive stats
        'defense_yards_per_play': 5.4,
        'defense_turnover_rate': 0.09,
        
        # Tendencies
        'tendencies_pass_rate': 0.58,
        'tendencies_shotgun_rate': 0.55,
        
        # Injury impact
        'injury_key_player_injuries': 3,
        'injury_key_injury_rate': 0.12,
        
        # Fantasy matchup advantages
        'fantasy_matchup_total_fantasy_points_matchup_adv': 0,
        'fantasy_matchup_fantasy_points_per_game_matchup_adv': 0,
        'fantasy_matchup_team_fantasy_efficiency_matchup_adv': 0,
        'fantasy_matchup_qb_fantasy_points_per_game_matchup_adv': 0,
        'fantasy_matchup_rb_fantasy_points_per_game_matchup_adv': 0,
        'fantasy_matchup_wr_fantasy_points_per_game_matchup_adv': 0,
        'fantasy_matchup_te_fantasy_points_per_game_matchup_adv': 0,
    }
    
    # Weak team with poor fantasy performance
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
        
        # Player stats
        'player_passing_yards_per_game': 200,
        'player_rushing_yards_per_game': 88,
        'player_touchdowns_per_game': 2.0,
        
        # Fantasy team strength
        'fantasy_total_fantasy_points': 1800,
        'fantasy_fantasy_points_per_game': 112,
        'fantasy_team_fantasy_efficiency': 0.88,
        'fantasy_qb_fantasy_points_per_game': 14.5,
        'fantasy_rb_fantasy_points_per_game': 11.8,
        'fantasy_wr_fantasy_points_per_game': 10.2,
        'fantasy_te_fantasy_points_per_game': 7.5,
        'fantasy_fantasy_consistency': 0.52,
        
        # Opportunity metrics
        'opportunity_total_expected_yards': 4800,
        'opportunity_total_actual_yards': 4500,
        'opportunity_yards_over_expected': -300,
        'opportunity_yards_efficiency': 0.94,
        'opportunity_avg_target_share': 0.12,
        'opportunity_max_target_share': 0.18,
        'opportunity_avg_carry_share': 0.08,
        'opportunity_max_carry_share': 0.15,
        'opportunity_red_zone_targets': 22,
        'opportunity_red_zone_carries': 25,
        'opportunity_high_value_touches': 45,
        'opportunity_high_value_touch_rate': 0.08,
        
        # Efficiency metrics
        'efficiency_avg_yards_per_target': 6.1,
        'efficiency_weighted_yards_per_target': 6.3,
        'efficiency_avg_yards_per_carry': 3.8,
        'efficiency_weighted_yards_per_carry': 3.9,
        'efficiency_avg_success_rate': 0.42,
        'efficiency_weighted_success_rate': 0.43,
        'efficiency_explosive_plays': 18,
        'efficiency_explosive_play_rate': 0.04,
        'efficiency_avg_route_efficiency': 0.58,
        'efficiency_avg_pass_block_efficiency': 0.68,
        'efficiency_avg_run_block_efficiency': 0.65,
        'efficiency_avg_tackle_efficiency': 0.72,
        'efficiency_avg_pass_rush_efficiency': 0.58,
        'efficiency_avg_coverage_efficiency': 0.55,
        
        # Defensive stats
        'defense_yards_per_play': 5.8,
        'defense_turnover_rate': 0.06,
        
        # Tendencies
        'tendencies_pass_rate': 0.52,
        'tendencies_shotgun_rate': 0.45,
        
        # Injury impact
        'injury_key_player_injuries': 5,
        'injury_key_injury_rate': 0.20,
        
        # Fantasy matchup advantages
        'fantasy_matchup_total_fantasy_points_matchup_adv': -8,
        'fantasy_matchup_fantasy_points_per_game_matchup_adv': -5.2,
        'fantasy_matchup_team_fantasy_efficiency_matchup_adv': -0.15,
        'fantasy_matchup_qb_fantasy_points_per_game_matchup_adv': -3.5,
        'fantasy_matchup_rb_fantasy_points_per_game_matchup_adv': -2.8,
        'fantasy_matchup_wr_fantasy_points_per_game_matchup_adv': -2.2,
        'fantasy_matchup_te_fantasy_points_per_game_matchup_adv': -1.8,
    }
    
    return elite_team, average_team, weak_team


def test_fantasy_enhanced_model():
    """Test the fantasy-enhanced NFL prediction model."""
    
    print("Testing Fantasy-Enhanced NFL Prediction Model")
    print("=" * 60)
    
    # Check if fantasy-enhanced model exists
    model_path = "models/advanced_random_forest_model.pkl"
    if not os.path.exists(model_path):
        print(f"Advanced model not found at {model_path}")
        print("Please run 'python main.py' first to train the models.")
        return
    
    # Load the advanced model
    model = AdvancedNFLPredictionModel(model_type='random_forest')
    model.load_model(model_path)
    print("✓ Fantasy-enhanced model loaded successfully")
    
    # Get model summary
    summary = model.get_model_summary()
    print(f"✓ Model type: {summary['model_type']}")
    print(f"✓ Total features: {summary['total_features']}")
    print(f"✓ Selected features: {summary['selected_features']}")
    print(f"✓ Feature selection used: {summary['use_feature_selection']}")
    
    # Create test team data
    elite_team, average_team, weak_team = create_fantasy_enhanced_team_data()
    
    print("\n" + "=" * 60)
    print("FANTASY-ENHANCED GAME PREDICTIONS")
    print("=" * 60)
    
    # Test different scenarios
    scenarios = [
        {
            'name': 'Elite Fantasy Team vs Average Fantasy Team',
            'home': elite_team,
            'away': average_team
        },
        {
            'name': 'Average Fantasy Team vs Weak Fantasy Team',
            'home': average_team,
            'away': weak_team
        },
        {
            'name': 'Elite Fantasy Team vs Weak Fantasy Team',
            'home': elite_team,
            'away': weak_team
        },
        {
            'name': 'Evenly Matched Fantasy Teams',
            'home': average_team,
            'away': average_team
        },
        {
            'name': 'Weak Fantasy Team vs Elite Fantasy Team (Home Field Advantage)',
            'home': weak_team,
            'away': elite_team
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}:")
        print("-" * 50)
        
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
    
    print("\n" + "=" * 60)
    print("FANTASY PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    # Test fantasy efficiency impact
    efficient_team = average_team.copy()
    efficient_team['fantasy_team_fantasy_efficiency'] = 1.25  # High efficiency
    efficient_team['opportunity_yards_efficiency'] = 1.15
    efficient_team['efficiency_weighted_success_rate'] = 0.58
    
    inefficient_team = average_team.copy()
    inefficient_team['fantasy_team_fantasy_efficiency'] = 0.85  # Low efficiency
    inefficient_team['opportunity_yards_efficiency'] = 0.92
    inefficient_team['efficiency_weighted_success_rate'] = 0.42
    
    print("\nEfficient Team vs Inefficient Team:")
    prediction = model.predict_game_advanced(efficient_team, inefficient_team)
    print(f"   Home team win probability: {prediction['home_win_probability']:.3f}")
    print(f"   Away team win probability: {prediction['away_win_probability']:.3f}")
    print(f"   Predicted winner: {prediction['predicted_winner']}")
    print(f"   Confidence: {prediction['confidence']:.3f}")
    
    if prediction['key_factors']:
        print("   Key factors:")
        for factor in prediction['key_factors']:
            print(f"     • {factor}")
    
    print("\n" + "=" * 60)
    print("OPPORTUNITY-BASED ANALYSIS")
    print("=" * 60)
    
    # Test opportunity impact
    high_opportunity_team = average_team.copy()
    high_opportunity_team['opportunity_high_value_touch_rate'] = 0.18
    high_opportunity_team['opportunity_max_target_share'] = 0.28
    high_opportunity_team['opportunity_max_carry_share'] = 0.25
    
    low_opportunity_team = average_team.copy()
    low_opportunity_team['opportunity_high_value_touch_rate'] = 0.08
    low_opportunity_team['opportunity_max_target_share'] = 0.15
    low_opportunity_team['opportunity_max_carry_share'] = 0.12
    
    print("\nHigh Opportunity Team vs Low Opportunity Team:")
    prediction = model.predict_game_advanced(high_opportunity_team, low_opportunity_team)
    print(f"   Home team win probability: {prediction['home_win_probability']:.3f}")
    print(f"   Away team win probability: {prediction['away_win_probability']:.3f}")
    print(f"   Predicted winner: {prediction['predicted_winner']}")
    print(f"   Confidence: {prediction['confidence']:.3f}")
    
    if prediction['key_factors']:
        print("   Key factors:")
        for factor in prediction['key_factors']:
            print(f"     • {factor}")
    
    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_fantasy_enhanced_model()






