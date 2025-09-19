"""
Week 3 NFL Predictions - Enhanced Model
Using updated weights, dynamic PFF injury penalties, and current-season focus
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Optional
from enhanced_model_framework import EnhancedModelFramework

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Week3Predictions:
    """
    Generate Week 3 predictions using the enhanced model
    """
    
    def __init__(self):
        self.model = EnhancedModelFramework()
        self.week3_games = [
            # Thursday Night Football
            {"home": "BUF", "away": "MIA", "day": "Thursday", "time": "8:15 PM"},
            
            # Sunday Games
            {"home": "ATL", "away": "KC", "day": "Sunday", "time": "1:00 PM"},
            {"home": "BAL", "away": "DAL", "day": "Sunday", "time": "1:00 PM"},
            {"home": "CHI", "away": "IND", "day": "Sunday", "time": "1:00 PM"},
            {"home": "CLE", "away": "NYG", "day": "Sunday", "time": "1:00 PM"},
            {"home": "DET", "away": "ARI", "day": "Sunday", "time": "1:00 PM"},
            {"home": "GB", "away": "TEN", "day": "Sunday", "time": "1:00 PM"},
            {"home": "HOU", "away": "MIN", "day": "Sunday", "time": "1:00 PM"},
            {"home": "JAX", "away": "BUF", "day": "Sunday", "time": "1:00 PM"},
            {"home": "LV", "away": "PIT", "day": "Sunday", "time": "1:00 PM"},
            {"home": "LAC", "away": "CAR", "day": "Sunday", "time": "1:00 PM"},
            {"home": "NO", "away": "PHI", "day": "Sunday", "time": "1:00 PM"},
            {"home": "NYJ", "away": "NE", "day": "Sunday", "time": "1:00 PM"},
            {"home": "SF", "away": "LAR", "day": "Sunday", "time": "1:00 PM"},
            {"home": "TB", "away": "DEN", "day": "Sunday", "time": "1:00 PM"},
            {"home": "WAS", "away": "CIN", "day": "Sunday", "time": "1:00 PM"},
            
            # Sunday Night Football
            {"home": "SEA", "away": "MIA", "day": "Sunday", "time": "8:20 PM"},
            
            # Monday Night Football
            {"home": "NYG", "away": "WAS", "day": "Monday", "time": "8:15 PM"}
        ]
    
    def generate_week3_predictions(self):
        """Generate comprehensive Week 3 predictions"""
        print("🎯 WEEK 3 NFL PREDICTIONS - ENHANCED MODEL")
        print("=" * 80)
        print("Enhanced with PFF Integration, Dynamic Injury Penalties, and Current-Season Focus")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        predictions = []
        
        for game in self.week3_games:
            try:
                prediction = self.model.predict_game_enhanced(
                    game["home"], 
                    game["away"]
                )
                
                if prediction:
                    predictions.append({
                        'game_info': game,
                        'prediction': prediction
                    })
                    
            except Exception as e:
                logger.error(f"Error predicting {game['away']} @ {game['home']}: {e}")
        
        # Display predictions by day
        self._display_predictions_by_day(predictions)
        
        # Generate summary statistics
        self._generate_summary_stats(predictions)
        
        return predictions
    
    def _display_predictions_by_day(self, predictions: List[Dict]):
        """Display predictions organized by day"""
        
        # Group by day
        thursday_games = []
        sunday_games = []
        monday_games = []
        
        for pred in predictions:
            day = pred['game_info']['day']
            if day == 'Thursday':
                thursday_games.append(pred)
            elif day == 'Sunday':
                sunday_games.append(pred)
            elif day == 'Monday':
                monday_games.append(pred)
        
        # Thursday Night Football
        if thursday_games:
            print(f"\n🏈 THURSDAY NIGHT FOOTBALL")
            print("-" * 50)
            for pred in thursday_games:
                self._display_single_prediction(pred)
        
        # Sunday Games
        if sunday_games:
            print(f"\n🏈 SUNDAY GAMES ({len(sunday_games)} games)")
            print("-" * 50)
            for pred in sunday_games:
                self._display_single_prediction(pred)
        
        # Monday Night Football
        if monday_games:
            print(f"\n🏈 MONDAY NIGHT FOOTBALL")
            print("-" * 50)
            for pred in monday_games:
                self._display_single_prediction(pred)
    
    def _display_single_prediction(self, pred: Dict):
        """Display a single game prediction with detailed analysis"""
        game_info = pred['game_info']
        prediction = pred['prediction']
        
        home_team = prediction['home_team']
        away_team = prediction['away_team']
        home_score = prediction['home_score']
        away_score = prediction['away_score']
        home_win_prob = prediction['home_win_probability']
        away_win_prob = prediction['away_win_probability']
        confidence = prediction['confidence']
        
        # Determine winner
        winner = home_team if home_win_prob > 0.5 else away_team
        winner_prob = max(home_win_prob, away_win_prob)
        
        print(f"\n🎯 {away_team} @ {home_team}")
        print(f"   Time: {game_info['day']} {game_info['time']}")
        print(f"   Winner: {winner} ({winner_prob:.1%})")
        print(f"   Confidence: {confidence:.1f}%")
        print(f"   Score: {away_team} {away_score:.1f} @ {home_team} {home_score:.1f}")
        
        # Display key variables
        self._display_key_variables(prediction)
        
        # Display injury impact
        self._display_injury_impact(prediction)
    
    def _display_key_variables(self, prediction: Dict):
        """Display key variables that influenced the prediction"""
        home_data = prediction['home_data']
        away_data = prediction['away_data']
        
        print(f"\n   📊 KEY VARIABLES:")
        
        # Enhanced EPA Scores
        home_epa = home_data['epa_data']['enhanced_epa_score']
        away_epa = away_data['epa_data']['enhanced_epa_score']
        epa_advantage = "Home" if home_epa > away_epa else "Away"
        epa_diff = abs(home_epa - away_epa)
        print(f"   • EPA Advantage: {epa_advantage} (+{epa_diff:.1f})")
        
        # Enhanced Efficiency Scores
        home_eff = home_data['efficiency_data']['enhanced_efficiency_score']
        away_eff = away_data['efficiency_data']['enhanced_efficiency_score']
        eff_advantage = "Home" if home_eff > away_eff else "Away"
        eff_diff = abs(home_eff - away_eff)
        print(f"   • Efficiency Advantage: {eff_advantage} (+{eff_diff:.1f})")
        
        # Enhanced Yards Scores
        home_yards = home_data['yards_data']['enhanced_yards_score']
        away_yards = away_data['yards_data']['enhanced_yards_score']
        yards_advantage = "Home" if home_yards > away_yards else "Away"
        yards_diff = abs(home_yards - away_yards)
        print(f"   • Yards Advantage: {yards_advantage} (+{yards_diff:.1f})")
        
        # Enhanced Turnover Scores
        home_turnover = home_data['turnover_data']['enhanced_turnover_score']
        away_turnover = away_data['turnover_data']['enhanced_turnover_score']
        turnover_advantage = "Home" if home_turnover > away_turnover else "Away"
        turnover_diff = abs(home_turnover - away_turnover)
        print(f"   • Turnover Advantage: {turnover_advantage} (+{turnover_diff:.1f})")
        
        # PFF Matchup Analysis
        matchup_score = prediction['home_data']['matchup_data']['matchup_score']
        if matchup_score > 0:
            print(f"   • PFF Matchup Advantage: Home (+{matchup_score:.1f})")
        elif matchup_score < 0:
            print(f"   • PFF Matchup Advantage: Away (+{abs(matchup_score):.1f})")
        else:
            print(f"   • PFF Matchup Advantage: Even")
    
    def _display_injury_impact(self, prediction: Dict):
        """Display injury impact analysis"""
        home_injury = prediction['home_data']['injury_impact']
        away_injury = prediction['away_data']['injury_impact']
        
        if home_injury != 0 or away_injury != 0:
            print(f"\n   🏥 INJURY IMPACT:")
            if home_injury != 0:
                print(f"   • {prediction['home_team']}: {home_injury:+.1f} points")
            if away_injury != 0:
                print(f"   • {prediction['away_team']}: {away_injury:+.1f} points")
        else:
            print(f"\n   🏥 INJURY IMPACT: Minimal")
    
    def _generate_summary_stats(self, predictions: List[Dict]):
        """Generate summary statistics for the week"""
        print(f"\n📊 WEEK 3 SUMMARY STATISTICS")
        print("-" * 50)
        
        total_games = len(predictions)
        home_wins = sum(1 for pred in predictions if pred['prediction']['home_win_probability'] > 0.5)
        away_wins = total_games - home_wins
        
        avg_confidence = sum(pred['prediction']['confidence'] for pred in predictions) / total_games
        avg_score_diff = sum(abs(pred['prediction']['score_difference']) for pred in predictions) / total_games
        
        print(f"Total Games: {total_games}")
        print(f"Home Wins: {home_wins} ({home_wins/total_games:.1%})")
        print(f"Away Wins: {away_wins} ({away_wins/total_games:.1%})")
        print(f"Average Confidence: {avg_confidence:.1f}%")
        print(f"Average Score Difference: {avg_score_diff:.1f} points")
        
        # Confidence distribution
        high_confidence = sum(1 for pred in predictions if pred['prediction']['confidence'] >= 70)
        medium_confidence = sum(1 for pred in predictions if 60 <= pred['prediction']['confidence'] < 70)
        low_confidence = sum(1 for pred in predictions if pred['prediction']['confidence'] < 60)
        
        print(f"\nConfidence Distribution:")
        print(f"High (≥70%): {high_confidence} games")
        print(f"Medium (60-69%): {medium_confidence} games")
        print(f"Low (<60%): {low_confidence} games")
        
        # Most confident predictions
        sorted_predictions = sorted(predictions, key=lambda x: x['prediction']['confidence'], reverse=True)
        print(f"\nMost Confident Predictions:")
        for i, pred in enumerate(sorted_predictions[:3]):
            pred_data = pred['prediction']
            winner = pred_data['home_team'] if pred_data['home_win_probability'] > 0.5 else pred_data['away_team']
            print(f"{i+1}. {pred_data['away_team']} @ {pred_data['home_team']}: {winner} ({pred_data['confidence']:.1f}%)")

if __name__ == "__main__":
    # Generate Week 3 predictions
    predictor = Week3Predictions()
    predictions = predictor.generate_week3_predictions()
    
    print(f"\n✅ Week 3 Predictions Complete!")
    print(f"Enhanced Model Features:")
    print(f"• PFF-enhanced components (86% weight)")
    print(f"• Dynamic injury penalties (5% weight)")
    print(f"• PFF matchup analysis (8% weight)")
    print(f"• Current-season focus (94% weight for Week 3)")
    print(f"• Fixed injury status logic (QUESTIONABLE = healthy)")




