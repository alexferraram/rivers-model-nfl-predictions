"""
Proper RIVERS Model Backtesting System
=====================================

Backtests using only data available at the time of prediction.
Tests Week 2 2025 games using only data from Week 1 and earlier.
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import nfl_data_py as nfl
from rivers_model_validated import RiversModelValidated
from sklearn.metrics import accuracy_score, log_loss, brier_score_loss

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProperBacktester:
    def __init__(self):
        """Initialize the proper backtesting system"""
        self.model = RiversModelValidated()
        self.results = []
        
    def get_week2_2025_games(self) -> List[Dict]:
        """Get Week 2 2025 games with actual results"""
        # Week 2 2025 NFL Schedule with actual results (from last week)
        week2_games = [
            {'home': 'GB', 'away': 'WAS', 'home_score': 18, 'away_score': 27, 'winner': 'WAS'},
            {'home': 'BAL', 'away': 'CLE', 'home_score': 17, 'away_score': 41, 'winner': 'CLE'},
            {'home': 'CIN', 'away': 'JAX', 'home_score': 27, 'away_score': 31, 'winner': 'JAX'},
            {'home': 'DAL', 'away': 'NYG', 'home_score': 37, 'away_score': 40, 'winner': 'NYG'},
            {'home': 'DET', 'away': 'CHI', 'home_score': 21, 'away_score': 52, 'winner': 'CHI'},
            {'home': 'MIA', 'away': 'NE', 'home_score': 33, 'away_score': 27, 'winner': 'MIA'},
            {'home': 'NO', 'away': 'SF', 'home_score': 26, 'away_score': 21, 'winner': 'NO'},
            {'home': 'NYJ', 'away': 'BUF', 'home_score': 30, 'away_score': 10, 'winner': 'NYJ'},
            {'home': 'PIT', 'away': 'SEA', 'home_score': 31, 'away_score': 17, 'winner': 'PIT'},
            {'home': 'TEN', 'away': 'LA', 'home_score': 33, 'away_score': 19, 'winner': 'TEN'},
            {'home': 'ARI', 'away': 'CAR', 'home_score': 22, 'away_score': 27, 'winner': 'CAR'},
            {'home': 'IND', 'away': 'DEN', 'home_score': 28, 'away_score': 29, 'winner': 'DEN'},
            {'home': 'KC', 'away': 'PHI', 'home_score': 20, 'away_score': 17, 'winner': 'KC'},
            {'home': 'MIN', 'away': 'ATL', 'home_score': 22, 'away_score': 6, 'winner': 'MIN'},
            {'home': 'HOU', 'away': 'TB', 'home_score': 20, 'away_score': 19, 'winner': 'HOU'},
            {'home': 'LV', 'away': 'LAC', 'home_score': 20, 'away_score': 9, 'winner': 'LV'}
        ]
        return week2_games
    
    def run_proper_backtest(self) -> Dict:
        """Run proper backtesting on Week 2 2025 games"""
        logger.info("🎯 PROPER RIVERS MODEL BACKTEST - WEEK 2 2025")
        logger.info("=" * 60)
        logger.info("Using only data available up to Week 1, 2025")
        logger.info("=" * 60)
        
        # Get Week 2 games with actual results
        week2_games = self.get_week2_2025_games()
        
        correct_predictions = 0
        total_predictions = 0
        confidence_scores = []
        actual_outcomes = []
        predicted_outcomes = []
        
        logger.info(f"🔍 Testing {len(week2_games)} Week 2 games...")
        
        for i, game in enumerate(week2_games):
            try:
                home_team = game['home']
                away_team = game['away']
                actual_winner = game['winner']
                
                logger.info(f"\n{i+1:2d}. {away_team} @ {home_team}")
                logger.info(f"    Actual Result: {actual_winner} wins")
                
                # Get model prediction for Week 2
                prediction = self.model.predict_game(home_team, away_team, week=2)
                
                if not prediction:
                    logger.warning(f"    ⚠️ No prediction available")
                    continue
                
                # Determine predicted winner
                predicted_winner = prediction['winner']
                predicted_outcome = 'HOME' if predicted_winner == home_team else 'AWAY'
                actual_outcome = 'HOME' if actual_winner == home_team else 'AWAY'
                
                # Check if prediction was correct
                is_correct = predicted_outcome == actual_outcome
                if is_correct:
                    correct_predictions += 1
                
                total_predictions += 1
                confidence_scores.append(prediction['confidence'])
                actual_outcomes.append(1 if actual_outcome == 'HOME' else 0)
                predicted_outcomes.append(1 if predicted_outcome == 'HOME' else 0)
                
                # Store detailed results
                self.results.append({
                    'game': f"{away_team} @ {home_team}",
                    'predicted_winner': predicted_winner,
                    'actual_winner': actual_winner,
                    'confidence': prediction['confidence'],
                    'correct': is_correct,
                    'home_score': prediction['home_score'],
                    'away_score': prediction['away_score'],
                    'actual_home_score': game['home_score'],
                    'actual_away_score': game['away_score']
                })
                
                logger.info(f"    Predicted: {predicted_winner} ({prediction['confidence']:.1f}%)")
                logger.info(f"    Score Prediction: {prediction['home_score']:.1f} - {prediction['away_score']:.1f}")
                logger.info(f"    Actual Score: {game['home_score']} - {game['away_score']}")
                logger.info(f"    Result: {'✅ CORRECT' if is_correct else '❌ INCORRECT'}")
                
            except Exception as e:
                logger.warning(f"⚠️ Error testing game {i+1}: {e}")
                continue
        
        # Calculate metrics
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        
        # Calculate additional metrics
        if len(confidence_scores) > 0 and len(actual_outcomes) > 0:
            # Brier Score (lower is better)
            brier_score = brier_score_loss(actual_outcomes, [c/100 for c in confidence_scores])
            
            # Log Loss
            log_loss_score = log_loss(actual_outcomes, [c/100 for c in confidence_scores])
            
            # Confidence calibration
            calibration_data = self._calculate_calibration(confidence_scores, actual_outcomes)
        else:
            brier_score = 0
            log_loss_score = 0
            calibration_data = {}
        
        # Store results
        backtest_results = {
            'total_games_tested': total_predictions,
            'correct_predictions': correct_predictions,
            'accuracy': accuracy,
            'brier_score': brier_score,
            'log_loss': log_loss_score,
            'avg_confidence': np.mean(confidence_scores) if confidence_scores else 0,
            'calibration_data': calibration_data,
            'detailed_results': self.results
        }
        
        return backtest_results
    
    def _calculate_calibration(self, confidence_scores: List[float], actual_outcomes: List[int]) -> Dict:
        """Calculate confidence calibration metrics"""
        # Group predictions by confidence ranges
        confidence_ranges = [(0, 50), (50, 60), (60, 70), (70, 80), (80, 90), (90, 100)]
        calibration = {}
        
        for min_conf, max_conf in confidence_ranges:
            range_indices = [i for i, conf in enumerate(confidence_scores) 
                            if min_conf <= conf < max_conf]
            
            if len(range_indices) > 0:
                range_outcomes = [actual_outcomes[i] for i in range_indices]
                range_confidences = [confidence_scores[i] for i in range_indices]
                
                actual_accuracy = np.mean(range_outcomes) * 100
                avg_confidence = np.mean(range_confidences)
                
                calibration[f"{min_conf}-{max_conf}"] = {
                    'count': len(range_indices),
                    'actual_accuracy': actual_accuracy,
                    'avg_confidence': avg_confidence,
                    'calibration_error': abs(actual_accuracy - avg_confidence)
                }
        
        return calibration
    
    def display_results(self, results: Dict):
        """Display comprehensive backtesting results"""
        logger.info("\n🏈 PROPER RIVERS MODEL BACKTEST RESULTS - WEEK 2 2025")
        logger.info("=" * 60)
        
        # Overall performance
        logger.info(f"📊 OVERALL PERFORMANCE:")
        logger.info(f"   Total Games Tested: {results['total_games_tested']}")
        logger.info(f"   Correct Predictions: {results['correct_predictions']}")
        logger.info(f"   Accuracy: {results['accuracy']:.1%}")
        logger.info(f"   Average Confidence: {results['avg_confidence']:.1f}%")
        
        # Advanced metrics
        logger.info(f"\n📈 ADVANCED METRICS:")
        logger.info(f"   Brier Score: {results['brier_score']:.3f} (lower is better)")
        logger.info(f"   Log Loss: {results['log_loss']:.3f} (lower is better)")
        
        # Confidence calibration
        logger.info(f"\n🎯 CONFIDENCE CALIBRATION:")
        calibration = results['calibration_data']
        for range_name, data in calibration.items():
            if data['count'] > 0:
                logger.info(f"   {range_name}%: {data['count']} games, "
                          f"Actual: {data['actual_accuracy']:.1f}%, "
                          f"Predicted: {data['avg_confidence']:.1f}%, "
                          f"Error: {data['calibration_error']:.1f}%")
        
        # Performance by confidence level
        logger.info(f"\n📊 PERFORMANCE BY CONFIDENCE LEVEL:")
        high_conf_games = [r for r in results['detailed_results'] if r['confidence'] >= 70]
        medium_conf_games = [r for r in results['detailed_results'] if 60 <= r['confidence'] < 70]
        low_conf_games = [r for r in results['detailed_results'] if r['confidence'] < 60]
        
        for conf_level, games in [("High (70%+)", high_conf_games), 
                                 ("Medium (60-70%)", medium_conf_games), 
                                 ("Low (<60%)", low_conf_games)]:
            if games:
                accuracy = sum(1 for g in games if g['correct']) / len(games)
                logger.info(f"   {conf_level}: {len(games)} games, {accuracy:.1%} accuracy")
        
        # Score prediction accuracy
        logger.info(f"\n🎯 SCORE PREDICTION ANALYSIS:")
        score_errors = []
        for result in results['detailed_results']:
            home_error = abs(result['home_score'] - result['actual_home_score'])
            away_error = abs(result['away_score'] - result['actual_away_score'])
            total_error = home_error + away_error
            score_errors.append(total_error)
        
        if score_errors:
            avg_score_error = np.mean(score_errors)
            logger.info(f"   Average Score Error: {avg_score_error:.1f} points per game")
            logger.info(f"   Best Score Prediction: {min(score_errors):.1f} points off")
            logger.info(f"   Worst Score Prediction: {max(score_errors):.1f} points off")
        
        # Detailed game results
        logger.info(f"\n📋 DETAILED GAME RESULTS:")
        logger.info("-" * 60)
        for i, result in enumerate(results['detailed_results']):
            status = "✅" if result['correct'] else "❌"
            logger.info(f"{i+1:2d}. {result['game']}")
            logger.info(f"    {status} Predicted: {result['predicted_winner']} ({result['confidence']:.1f}%)")
            logger.info(f"    📊 Score: {result['home_score']:.1f}-{result['away_score']:.1f} (Actual: {result['actual_home_score']}-{result['actual_away_score']})")

def main():
    """Run the proper backtesting system"""
    logger.info("🎯 PROPER RIVERS MODEL BACKTESTING SYSTEM")
    logger.info("=" * 60)
    
    # Initialize backtester
    backtester = ProperBacktester()
    
    # Run proper backtest
    results = backtester.run_proper_backtest()
    
    # Display results
    backtester.display_results(results)
    
    logger.info("\n✅ Proper backtesting complete!")

if __name__ == "__main__":
    main()
