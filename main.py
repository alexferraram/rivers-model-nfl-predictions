"""
NFL Game Prediction Model - Main Application

This script demonstrates how to use the NFL prediction model.
"""

import os
import sys
import logging
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from data_collector import NFLDataCollector
from preprocessor import NFLPreprocessor
from advanced_preprocessor import AdvancedNFLPreprocessor
from fantasy_preprocessor import FantasyEnhancedPreprocessor
from model import NFLPredictionModel
from advanced_model import AdvancedNFLPredictionModel

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main application function."""
    logger.info("Starting NFL Game Prediction Model")
    
    # Create directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    # Step 1: Collect data
    logger.info("Step 1: Collecting NFL data...")
    collector = NFLDataCollector(seasons=[2022, 2023, 2024])
    
    # Check if data already exists
    data_files = ["data/schedules.csv", "data/pbp.csv", "data/teams.csv", 
                  "data/player_stats.csv", "data/injuries.csv", "data/depth_charts.csv"]
    enhanced_data_files = ["data/fantasy_data.csv", "data/opportunity_data.csv", "data/efficiency_data.csv"]
    
    if all(os.path.exists(f) for f in data_files):
        logger.info("Data files already exist, skipping data collection")
        import pandas as pd
        data = {
            'schedules': pd.read_csv("data/schedules.csv"),
            'pbp': pd.read_csv("data/pbp.csv"),
            'teams': pd.read_csv("data/teams.csv"),
            'player_stats': pd.read_csv("data/player_stats.csv"),
            'injuries': pd.read_csv("data/injuries.csv"),
            'depth_charts': pd.read_csv("data/depth_charts.csv")
        }
        
        # Load enhanced data if available
        if all(os.path.exists(f) for f in enhanced_data_files):
            data.update({
                'fantasy_data': pd.read_csv("data/fantasy_data.csv"),
                'opportunity_data': pd.read_csv("data/opportunity_data.csv"),
                'efficiency_data': pd.read_csv("data/efficiency_data.csv")
            })
            logger.info("Enhanced data files found and loaded")
    else:
        data = collector.get_all_data()
        collector.save_data(data)
    
    # Step 2: Fantasy-enhanced preprocessing
    logger.info("Step 2: Fantasy-enhanced preprocessing with comprehensive features...")
    
    # Check if we have enhanced data available
    if all(key in data for key in ['fantasy_data', 'opportunity_data', 'efficiency_data']):
        logger.info("Using fantasy-enhanced preprocessing with all data sources...")
        fantasy_preprocessor = FantasyEnhancedPreprocessor()
        
        # Create comprehensive fantasy-enhanced game features
        game_features = fantasy_preprocessor.create_comprehensive_fantasy_features(
            schedules=data['schedules'],
            pbp_data=data['pbp'],
            player_stats=data['player_stats'],
            rosters=data.get('rosters', pd.DataFrame()),
            injuries=data['injuries'],
            depth_charts=data['depth_charts'],
            fantasy_data=data['fantasy_data'],
            opportunity_data=data['opportunity_data'],
            efficiency_data=data['efficiency_data']
        )
        
        # Save processed data
        game_features.to_csv("data/fantasy_enhanced_game_features.csv", index=False)
        logger.info(f"Saved {len(game_features)} fantasy-enhanced game features to data/fantasy_enhanced_game_features.csv")
        
        # Prepare ML data
        X, y = fantasy_preprocessor.prepare_ml_data(game_features)
        
    else:
        logger.info("Using standard advanced preprocessing (enhanced data not available)...")
        advanced_preprocessor = AdvancedNFLPreprocessor()
        
        # Create comprehensive game features
        game_features = advanced_preprocessor.create_comprehensive_features(
            schedules=data['schedules'],
            pbp_data=data['pbp'],
            player_stats=data['player_stats'],
            rosters=data.get('rosters', pd.DataFrame()),
            injuries=data['injuries'],
            depth_charts=data['depth_charts']
        )
        
        if game_features.empty:
            logger.error("No game features could be created. Exiting.")
            return
        
        # Save processed data
        game_features.to_csv("data/advanced_game_features.csv", index=False)
        logger.info(f"Saved {len(game_features)} advanced game features to data/advanced_game_features.csv")
        
        # Prepare ML data
        X, y = advanced_preprocessor.prepare_ml_data(game_features)
    
    # Step 4: Train advanced models
    logger.info("Step 4: Training advanced prediction models...")
    
    # Train basic models for comparison
    basic_models = ['random_forest', 'gradient_boosting', 'logistic_regression']
    basic_results = {}
    
    for model_type in basic_models:
        logger.info(f"Training basic {model_type} model...")
        model = NFLPredictionModel(model_type=model_type)
        train_results = model.train(X, y)
        basic_results[model_type] = train_results
        
        model_path = f"models/basic_{model_type}_model.pkl"
        model.save_model(model_path)
        
        logger.info(f"Basic {model_type} - Accuracy: {train_results['accuracy']:.3f}, CV Score: {train_results['cv_mean']:.3f} ± {train_results['cv_std']:.3f}")
    
    # Train advanced models
    advanced_models = ['random_forest', 'gradient_boosting', 'extra_trees', 'neural_network']
    advanced_results = {}
    
    for model_type in advanced_models:
        logger.info(f"Training advanced {model_type} model...")
        model = AdvancedNFLPredictionModel(model_type=model_type, use_feature_selection=True)
        
        # Train model
        train_results = model.train(X, y)
        advanced_results[model_type] = train_results
        
        # Save model
        model_path = f"models/advanced_{model_type}_model.pkl"
        model.save_model(model_path)
        
        logger.info(f"Advanced {model_type} - Accuracy: {train_results['accuracy']:.3f}, AUC: {train_results['auc_score']:.3f}, CV Score: {train_results['cv_mean']:.3f} ± {train_results['cv_std']:.3f}")
    
    # Combine results
    results = {**basic_results, **advanced_results}
    
    # Step 5: Display results
    logger.info("Step 5: Model comparison results:")
    print("\n" + "="*60)
    print("MODEL PERFORMANCE COMPARISON")
    print("="*60)
    
    for model_type, result in results.items():
        print(f"\n{model_type.upper()}:")
        print(f"  Accuracy: {result['accuracy']:.3f}")
        print(f"  Cross-validation: {result['cv_mean']:.3f} ± {result['cv_std']:.3f}")
        
        # Show top 5 most important features
        if result['feature_importance']:
            print("  Top 5 Features:")
            for i, (feature, importance) in enumerate(list(result['feature_importance'].items())[:5]):
                print(f"    {i+1}. {feature}: {importance:.3f}")
    
    # Step 6: Example prediction
    logger.info("Step 6: Making example predictions...")
    
    # Use the best performing advanced model
    advanced_model_types = [k for k in results.keys() if k.startswith('advanced_')]
    if advanced_model_types:
        best_model_type = max(advanced_model_types, key=lambda k: results[k]['accuracy'])
        best_model = AdvancedNFLPredictionModel(model_type=best_model_type.replace('advanced_', ''))
        best_model.load_model(f"models/{best_model_type}_model.pkl")
    else:
        best_model_type = max(results.keys(), key=lambda k: results[k]['accuracy'])
        best_model = NFLPredictionModel(model_type=best_model_type)
        best_model.load_model(f"models/basic_{best_model_type}_model.pkl")
    
    print(f"\nUsing best model: {best_model_type}")
    
    # Example: Predict a game between two teams
    # You can modify these stats or get them from actual team data
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
    
    prediction = best_model.predict_game(home_team_stats, away_team_stats)
    
    print("\nExample Game Prediction:")
    print(f"  Home team win probability: {prediction['home_win_probability']:.3f}")
    print(f"  Away team win probability: {prediction['away_win_probability']:.3f}")
    print(f"  Predicted winner: {prediction['predicted_winner']}")
    print(f"  Confidence: {prediction['confidence']:.3f}")
    
    logger.info("NFL Game Prediction Model setup complete!")
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("Data files saved in: data/")
    print("Trained models saved in: models/")
    print("Run 'jupyter notebook' to open analysis notebooks")
    print("="*60)


if __name__ == "__main__":
    main()
