"""
Test script for the NFL prediction model.

This script tests the model with sample data and demonstrates its usage.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from model import NFLPredictionModel
import pandas as pd
import numpy as np


def test_model_prediction():
    """Test the model with sample team statistics."""
    
    print("Testing NFL Prediction Model")
    print("=" * 40)
    
    # Check if model exists
    model_path = "models/random_forest_model.pkl"
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        print("Please run 'python main.py' first to train the model.")
        return
    
    # Load the model
    model = NFLPredictionModel(model_type='random_forest')
    model.load_model(model_path)
    print("✓ Model loaded successfully")
    
    # Test with sample data
    print("\nTesting with sample team statistics...")
    
    # Sample team statistics (you can modify these)
    home_team_stats = {
        'games_played': 16,
        'total_plays': 1000,
        'pass_rate': 0.6,
        'rush_rate': 0.4,
        'yards_per_play': 5.5,
        'first_down_rate': 0.35,
        'turnover_rate': 0.08,
        'fg_percentage': 0.85,
        'touchdowns': 45
    }
    
    away_team_stats = {
        'games_played': 16,
        'total_plays': 950,
        'pass_rate': 0.55,
        'rush_rate': 0.45,
        'yards_per_play': 5.2,
        'first_down_rate': 0.32,
        'turnover_rate': 0.10,
        'fg_percentage': 0.80,
        'touchdowns': 42
    }
    
    # Make prediction
    prediction = model.predict_game(home_team_stats, away_team_stats)
    
    print("\nPrediction Results:")
    print(f"Home team win probability: {prediction['home_win_probability']:.3f}")
    print(f"Away team win probability: {prediction['away_win_probability']:.3f}")
    print(f"Predicted winner: {prediction['predicted_winner']}")
    print(f"Confidence: {prediction['confidence']:.3f}")
    
    # Test with different scenarios
    print("\n" + "=" * 40)
    print("Testing Different Scenarios")
    print("=" * 40)
    
    scenarios = [
        {
            'name': 'Strong Home Team vs Weak Away Team',
            'home': {
                'games_played': 16, 'total_plays': 1100, 'pass_rate': 0.65,
                'rush_rate': 0.35, 'yards_per_play': 6.2, 'first_down_rate': 0.40,
                'turnover_rate': 0.06, 'fg_percentage': 0.90, 'touchdowns': 50
            },
            'away': {
                'games_played': 16, 'total_plays': 900, 'pass_rate': 0.50,
                'rush_rate': 0.50, 'yards_per_play': 4.8, 'first_down_rate': 0.28,
                'turnover_rate': 0.12, 'fg_percentage': 0.75, 'touchdowns': 35
            }
        },
        {
            'name': 'Evenly Matched Teams',
            'home': {
                'games_played': 16, 'total_plays': 1000, 'pass_rate': 0.60,
                'rush_rate': 0.40, 'yards_per_play': 5.5, 'first_down_rate': 0.35,
                'turnover_rate': 0.08, 'fg_percentage': 0.85, 'touchdowns': 45
            },
            'away': {
                'games_played': 16, 'total_plays': 1000, 'pass_rate': 0.60,
                'rush_rate': 0.40, 'yards_per_play': 5.5, 'first_down_rate': 0.35,
                'turnover_rate': 0.08, 'fg_percentage': 0.85, 'touchdowns': 45
            }
        },
        {
            'name': 'Strong Away Team vs Weak Home Team',
            'home': {
                'games_played': 16, 'total_plays': 900, 'pass_rate': 0.50,
                'rush_rate': 0.50, 'yards_per_play': 4.8, 'first_down_rate': 0.28,
                'turnover_rate': 0.12, 'fg_percentage': 0.75, 'touchdowns': 35
            },
            'away': {
                'games_played': 16, 'total_plays': 1100, 'pass_rate': 0.65,
                'rush_rate': 0.35, 'yards_per_play': 6.2, 'first_down_rate': 0.40,
                'turnover_rate': 0.06, 'fg_percentage': 0.90, 'touchdowns': 50
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}:")
        prediction = model.predict_game(scenario['home'], scenario['away'])
        print(f"   Home win probability: {prediction['home_win_probability']:.3f}")
        print(f"   Away win probability: {prediction['away_win_probability']:.3f}")
        print(f"   Predicted winner: {prediction['predicted_winner']}")
        print(f"   Confidence: {prediction['confidence']:.3f}")
    
    print("\n" + "=" * 40)
    print("Test completed successfully!")
    print("=" * 40)


if __name__ == "__main__":
    test_model_prediction()






