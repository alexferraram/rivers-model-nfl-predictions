"""
RIVERS Model Backtesting System
===============================

Comprehensive backtesting to evaluate model performance on historical games.
Tests accuracy, confidence calibration, and provides detailed analysis.
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import nfl_data_py as nfl
from rivers_model_validated import RiversModelValidated
from sklearn.metrics import accuracy_score, log_loss, brier_score_loss
import matplotlib.pyplot as plt
import seaborn as sns

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RiversBacktester:
    def __init__(self, seasons: List[int] = [2023, 2024]):
        """Initialize the backtesting system"""
        self.seasons = seasons
        self.model = RiversModelValidated()
        self.results = []
        self.accuracy_by_week = {}
        self.confidence_calibration = {}
        
    def load_historical_games(self) -> pd.DataFrame:
        """Load historical game results for backtesting"""
        logger.info("📊 Loading historical game data...")
        
        all_games = []
        for season in self.seasons:
            logger.info(f"   Loading {season} season...")
            games = nfl.import_schedules([season])
            games['season'] = season
            all_games.append(games)
        
        df = pd.concat(all_games, ignore_index=True)
        logger.info(f"✅ Loaded {len(df)} historical games")
        return df
    
    def get_game_outcome(self, home_team: str, away_team: str, season: int, week: int) -> Optional[str]:
        """Get the actual outcome of a historical game"""
        try:
            # Load game data for the specific week
            games = nfl.import_schedules([season])
            game = games[(games['home_team'] == home_team) & 
                        (games['away_team'] == away_team) & 
                        (games['week'] == week)]
            
            if game.empty:
                return None
            
            home_score = game['home_score'].iloc[0]
            away_score = game['away_score'].iloc[0]
            
            if home_score > away_score:
                return 'HOME'
            elif away_score > home_score:
                return 'AWAY'
            else:
                return 'TIE'
                
        except Exception as e:
            logger.warning(f"⚠️ Error getting outcome for {away_team} @ {home_team} Week {week}: {e}")
            return None
    
    def run_backtest(self, max_games: int = 100) -> Dict:
        """Run comprehensive backtesting on historical games"""
        logger.info("🎯 STARTING RIVERS MODEL BACKTEST")
        logger.info("=" * 50)
        
        # Load historical games
        games_df = self.load_historical_games()
        
        # Filter to completed games only
        completed_games = games_df[games_df['result'].notna()]
        logger.info(f"📊 Testing on {len(completed_games)} completed games")
        
        # Limit games for testing
        test_games = completed_games.head(max_games)
        
        correct_predictions = 0
        total_predictions = 0
        confidence_scores = []
        actual_outcomes = []
        predicted_outcomes = []
        
        logger.info(f"🔍 Testing {len(test_games)} games...")
        
        for idx, game in test_games.iterrows():
            try:
                home_team = game['home_team']
                away_team = game['away_team']
                season = game['season']
                week = game['week']
                
                # Skip if we don't have enough data for this week
                if week < 3:  # Need at least 2 weeks of data
                    continue
                
                logger.info(f"   Testing: {away_team} @ {home_team} (Week {week}, {season})")
                
                # Get model prediction
                prediction = self.model.predict_game(home_team, away_team, week)
                
                if not prediction:
                    continue
                
                # Get actual outcome
                actual_outcome = self.get_game_outcome(home_team, away_team, season, week)
                
                if not actual_outcome or actual_outcome == 'TIE':
                    continue
                
                # Determine if prediction was correct
                predicted_winner = prediction['winner']
                predicted_outcome = 'HOME' if predicted_winner == home_team else 'AWAY'
                
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
                    'season': season,
                    'week': week,
                    'predicted_winner': predicted_winner,
                    'actual_outcome': actual_outcome,
                    'confidence': prediction['confidence'],
                    'correct': is_correct,
                    'home_score': prediction['home_score'],
                    'away_score': prediction['away_score']
                })
                
                logger.info(f"      Predicted: {predicted_winner} ({prediction['confidence']:.1f}%)")
                logger.info(f"      Actual: {actual_outcome}")
                logger.info(f"      Result: {'✅ CORRECT' if is_correct else '❌ INCORRECT'}")
                
            except Exception as e:
                logger.warning(f"⚠️ Error testing game {idx}: {e}")
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
        logger.info("\n🏈 RIVERS MODEL BACKTEST RESULTS")
        logger.info("=" * 50)
        
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
        
        # Recent performance
        logger.info(f"\n📅 RECENT PERFORMANCE:")
        recent_games = [r for r in results['detailed_results'] if r['season'] == 2024]
        if recent_games:
            recent_accuracy = sum(1 for g in recent_games if g['correct']) / len(recent_games)
            logger.info(f"   2024 Season: {len(recent_games)} games, {recent_accuracy:.1%} accuracy")
    
    def analyze_prediction_patterns(self, results: Dict):
        """Analyze patterns in prediction performance"""
        logger.info("\n🔍 PREDICTION PATTERN ANALYSIS")
        logger.info("=" * 40)
        
        # Home vs Away performance
        home_games = [r for r in results['detailed_results'] if r['predicted_winner'] == r['game'].split(' @ ')[1]]
        away_games = [r for r in results['detailed_results'] if r['predicted_winner'] == r['game'].split(' @ ')[0]]
        
        if home_games:
            home_accuracy = sum(1 for g in home_games if g['correct']) / len(home_games)
            logger.info(f"🏠 Home Team Predictions: {len(home_games)} games, {home_accuracy:.1%} accuracy")
        
        if away_games:
            away_accuracy = sum(1 for g in away_games if g['correct']) / len(away_games)
            logger.info(f"✈️ Away Team Predictions: {len(away_games)} games, {away_accuracy:.1%} accuracy")
        
        # Score prediction accuracy
        score_errors = []
        for result in results['detailed_results']:
            # This would require actual game scores, which we'd need to load
            pass
        
        # Week-by-week performance
        week_performance = {}
        for result in results['detailed_results']:
            week = result['week']
            if week not in week_performance:
                week_performance[week] = {'correct': 0, 'total': 0}
            week_performance[week]['total'] += 1
            if result['correct']:
                week_performance[week]['correct'] += 1
        
        logger.info(f"\n📅 WEEK-BY-WEEK PERFORMANCE:")
        for week in sorted(week_performance.keys()):
            data = week_performance[week]
            accuracy = data['correct'] / data['total']
            logger.info(f"   Week {week}: {data['total']} games, {accuracy:.1%} accuracy")

def main():
    """Run the backtesting system"""
    logger.info("🎯 RIVERS MODEL BACKTESTING SYSTEM")
    logger.info("=" * 50)
    
    # Initialize backtester
    backtester = RiversBacktester(seasons=[2023, 2024])
    
    # Run backtest
    results = backtester.run_backtest(max_games=50)  # Limit for testing
    
    # Display results
    backtester.display_results(results)
    
    # Analyze patterns
    backtester.analyze_prediction_patterns(results)
    
    logger.info("\n✅ Backtesting complete!")

if __name__ == "__main__":
    main()
