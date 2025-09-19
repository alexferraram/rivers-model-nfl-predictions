import pandas as pd
import numpy as np
import nfl_data_py as nfl
import logging
from datetime import datetime
from injury_tracker import DynamicInjuryTracker
from weather_data_system import WeatherDataSystem

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedNFLPredictorWithInjuries:
    """
    Enhanced NFL predictor with dynamic injury tracking
    """
    
    def __init__(self):
        self.injury_tracker = DynamicInjuryTracker()
        self.weather_system = WeatherDataSystem()
        self.seasons = [2022, 2023, 2024, 2025]
        
    def get_progressive_weights(self, games_played):
        """Get progressive weights based on games played"""
        if games_played <= 3:
            return (0.85, 0.10, 0.04, 0.01)  # 85%, 10%, 4%, 1%
        elif games_played <= 4:
            return (0.87, 0.10, 0.03, 0.0)   # 87%, 10%, 3%, 0%
        elif games_played <= 5:
            return (0.89, 0.09, 0.02, 0.0)   # 89%, 9%, 2%, 0%
        elif games_played <= 6:
            return (0.90, 0.08, 0.02, 0.0)   # 90%, 8%, 2%, 0%
        elif games_played <= 7:
            return (0.91, 0.07, 0.02, 0.0)   # 91%, 7%, 2%, 0%
        elif games_played <= 8:
            return (0.92, 0.06, 0.02, 0.0)   # 92%, 6%, 2%, 0%
        elif games_played <= 9:
            return (0.93, 0.05, 0.02, 0.0)   # 93%, 5%, 2%, 0%
        elif games_played <= 10:
            return (0.94, 0.04, 0.02, 0.0)   # 94%, 4%, 2%, 0%
        elif games_played <= 11:
            return (0.95, 0.03, 0.02, 0.0)   # 95%, 3%, 2%, 0%
        elif games_played <= 12:
            return (0.96, 0.02, 0.02, 0.0)   # 96%, 2%, 2%, 0%
        elif games_played <= 13:
            return (0.97, 0.01, 0.02, 0.0)   # 97%, 1%, 2%, 0%
        elif games_played <= 14:
            return (0.98, 0.0, 0.02, 0.0)    # 98%, 0%, 2%, 0%
        elif games_played <= 15:
            return (0.99, 0.0, 0.01, 0.0)    # 99%, 0%, 1%, 0%
        else:
            return (1.0, 0.0, 0.0, 0.0)      # 100%, 0%, 0%, 0%
    
    def continuity_adjust(self, weights, qb_change=False, hc_change=False):
        """Apply continuity adjustments for QB/HC changes"""
        adjusted_weights = list(weights)
        
        # QB change penalty: reduce previous season weight by 50%
        if qb_change:
            adjusted_weights[1] *= 0.5  # 2024 weight reduced by 50%
            adjusted_weights[2] *= 0.3  # 2023 weight reduced by 70%
            adjusted_weights[3] *= 0.1  # 2022 weight reduced by 90%
        
        # Head Coach change penalty: reduce previous season weight by 30%
        if hc_change:
            adjusted_weights[1] *= 0.7  # 2024 weight reduced by 30%
            adjusted_weights[2] *= 0.5  # 2023 weight reduced by 50%
            adjusted_weights[3] *= 0.2  # 2022 weight reduced by 80%
        
        # Renormalize weights
        total_weight = sum(adjusted_weights)
        adjusted_weights = [w / total_weight for w in adjusted_weights]
        
        return tuple(adjusted_weights)
    
    def calculate_weather_score(self, home_team, away_team, game_date):
        """Calculate weather impact score (0-100 scale)"""
        try:
            # Create game ID for weather lookup
            game_id = f"{game_date}_{away_team}_{home_team}"
            
            # Get weather data
            weather_data = self.weather_system.get_game_weather(game_id)
            
            if not weather_data:
                return 50, {}  # Neutral weather score if no data
            
            # Extract weather metrics
            temp = weather_data.get('temperature', 70)  # Default to 70°F
            wind = weather_data.get('wind_speed', 0)   # Default to 0 mph
            is_rain = weather_data.get('is_rain', False)
            is_snow = weather_data.get('is_snow', False)
            is_dome = weather_data.get('is_dome', False)
            
            # Calculate weather impact score (0-100)
            weather_score = 50  # Start neutral
            
            # Temperature impact
            if temp < 32:  # Freezing
                weather_score -= 15
            elif temp < 45:  # Cold
                weather_score -= 8
            elif temp > 85:  # Hot
                weather_score -= 5
            
            # Wind impact
            if wind > 15:  # High wind
                weather_score -= 12
            elif wind > 10:  # Moderate wind
                weather_score -= 6
            elif wind > 5:  # Light wind
                weather_score -= 3
            
            # Precipitation impact
            if is_snow:
                weather_score -= 10
            elif is_rain:
                weather_score -= 6
            
            # Dome games have no weather impact
            if is_dome:
                weather_score = 50
            
            # Ensure score stays within bounds
            weather_score = max(0, min(100, weather_score))
            
            return weather_score, {
                'temperature': temp,
                'wind_speed': wind,
                'is_rain': is_rain,
                'is_snow': is_snow,
                'is_dome': is_dome,
                'weather_impact': weather_score - 50  # -50 to +50 range
            }
            
        except Exception as e:
            logger.warning(f"Weather calculation error: {e}")
            return 50, {}  # Return neutral score on error
    
    def calculate_team_score_with_injuries(self, team_data, weights, qb_change=False, hc_change=False, is_home=True, team_abbr=None, weather_score=50):
        """Calculate team score with injury adjustments"""
        if team_data.empty:
            return 0, {}
        
        # Apply continuity adjustments
        adjusted_weights = self.continuity_adjust(weights, qb_change, hc_change)
        
        def calculate_weighted_metric(metric_func, team_data, weights):
            weighted_sum = 0
            total_weight = 0
            
            for i, season in enumerate(self.seasons):
                season_data = team_data[team_data['season'] == season]
                if not season_data.empty:
                    metric_value = metric_func(season_data)
                    weight = weights[i]
                    weighted_sum += metric_value * weight
                    total_weight += weight
            
            return weighted_sum / total_weight if total_weight > 0 else 0
        
        # Calculate weighted metrics
        total_epa = calculate_weighted_metric(lambda x: x['epa'].sum(), team_data, adjusted_weights)
        success_rate = calculate_weighted_metric(lambda x: x['success'].mean(), team_data, adjusted_weights)
        avg_yards = calculate_weighted_metric(lambda x: x['yards_gained'].mean(), team_data, adjusted_weights)
        turnovers = calculate_weighted_metric(lambda x: x['interception'].sum() + x['fumble_lost'].sum(), team_data, adjusted_weights)
        
        # Scale metrics to 0-100
        epa_score = max(0, min(100, (total_epa + 100) / 2))  # Scale -100 to +100 -> 0 to 100
        efficiency_score = success_rate * 100
        yards_score = max(0, min(100, avg_yards * 10))
        turnover_score = max(0, min(100, 100 - (turnovers * 2)))
        
        # Apply weights (reduced main components to make room for weather)
        base_score = (
            epa_score * 0.245 +           # EPA: 24.5% (reduced from 25%)
            efficiency_score * 0.245 +     # Efficiency: 24.5% (reduced from 25%)
            yards_score * 0.195 +         # Yards per Play: 19.5% (reduced from 20%)
            turnover_score * 0.195 +      # Turnover Avoidance: 19.5% (reduced from 20%)
            weather_score * 0.02          # Weather: 2% (new component)
        )
        
        # Home field advantage: +5 points (reduced from +10)
        if is_home:
            base_score += 5
        
        # Apply injury adjustments
        injury_impact = 0
        if team_abbr:
            injury_impact = self.injury_tracker.get_injury_impact(team_abbr)
        
        final_score = base_score + injury_impact
        
        return final_score, {
            'raw_epa': total_epa,
            'raw_success_rate': success_rate,
            'raw_yards': avg_yards,
            'raw_turnovers': turnovers,
            'adjusted_weights': adjusted_weights,
            'base_score': base_score,
            'injury_impact': injury_impact,
            'weather_score': weather_score,
            'final_score': final_score
        }
    
    def calculate_confidence(self, home_score, away_score):
        """Calculate confidence based on score difference"""
        score_diff = abs(home_score - away_score)
        
        # Pure sigmoid function for confidence
        confidence = 50 + (50 * (2 / (1 + np.exp(-score_diff / 15)) - 1))
        confidence = max(5, min(95, confidence))
        
        return confidence
    
    def predict_game_with_injuries(self, home_team, away_team, game_date, historical_pbp):
        """Predict game with injury adjustments"""
        # Get team data
        home_data = historical_pbp[historical_pbp['posteam'] == home_team]
        away_data = historical_pbp[historical_pbp['posteam'] == away_team]
        
        # Get weights (all teams have 2 games in 2025)
        weights = self.get_progressive_weights(2)
        
        # Calculate weather score
        weather_score, weather_details = self.calculate_weather_score(home_team, away_team, game_date)
        
        # TODO: Add QB/HC change detection logic here
        # For now, assume no changes
        home_qb_change = False
        home_hc_change = False
        away_qb_change = False
        away_hc_change = False
        
        # Calculate scores with injury adjustments and weather
        home_score, home_details = self.calculate_team_score_with_injuries(
            home_data, weights, home_qb_change, home_hc_change, True, home_team, weather_score
        )
        away_score, away_details = self.calculate_team_score_with_injuries(
            away_data, weights, away_qb_change, away_hc_change, False, away_team, weather_score
        )
        
        # Calculate confidence
        confidence = self.calculate_confidence(home_score, away_score)
        
        # Determine winner
        if home_score > away_score:
            predicted_winner = home_team
            home_win_prob = confidence / 100
            away_win_prob = (100 - confidence) / 100
        else:
            predicted_winner = away_team
            home_win_prob = (100 - confidence) / 100
            away_win_prob = confidence / 100
        
        return {
            'away_team': away_team,
            'home_team': home_team,
            'game_date': game_date,
            'predicted_winner': predicted_winner,
            'confidence': confidence,
            'home_win_prob': home_win_prob,
            'away_win_prob': away_win_prob,
            'home_score': home_score,
            'away_score': away_score,
            'home_details': home_details,
            'away_details': away_details,
            'weather_details': weather_details
        }
    
    def predict_week_with_injuries(self, week_num=3):
        """Predict entire week with injury tracking"""
        logger.info(f"🎯 Predicting Week {week_num} with Dynamic Injury Tracking...")
        
        # Load historical data
        historical_pbp = nfl.import_pbp_data(self.seasons)
        
        # Get week games
        current_year = 2025
        schedules = nfl.import_schedules([current_year])
        schedules = schedules[schedules['game_type'] == 'REG'].copy()
        week_games = schedules[schedules['week'] == week_num].copy()
        week_games = week_games.sort_values(by='gameday').reset_index(drop=True)
        
        logger.info(f"📅 Week {week_num} Games: {len(week_games)} games")
        
        # Predict each game
        predictions = []
        for i, (_, game) in enumerate(week_games.iterrows()):
            prediction = self.predict_game_with_injuries(
                game['home_team'],
                game['away_team'],
                game['gameday'],
                historical_pbp
            )
            predictions.append(prediction)
        
        return predictions
    
    def display_predictions_with_injuries(self, predictions):
        """Display predictions with injury information"""
        print(f'\n🎯 WEEK PREDICTIONS WITH INJURY TRACKING:')
        print('=' * 70)
        
        for i, pred in enumerate(predictions):
            print(f'\n🏟️  Game {i+1}: {pred["away_team"]} @ {pred["home_team"]}')
            print(f'   📅 Date: {pred["game_date"]}')
            print(f'   🏆 Predicted Winner: {pred["predicted_winner"]}')
            print(f'   📊 Confidence: {pred["confidence"]:.1f}%')
            print(f'   🏠 Home Win Probability: {pred["home_win_prob"]:.3f}')
            print(f'   ✈️  Away Win Probability: {pred["away_win_prob"]:.3f}')
            
            # Show injury impacts
            home_details = pred['home_details']
            away_details = pred['away_details']
            weather_details = pred['weather_details']
            
            print(f'   \n🏥 INJURY IMPACTS:')
            print(f'   {pred["home_team"]}: {home_details["injury_impact"]:+.1f} points')
            print(f'   {pred["away_team"]}: {away_details["injury_impact"]:+.1f} points')
            
            # Show weather impact
            print(f'   \n🌤️  WEATHER IMPACT:')
            if weather_details:
                temp = weather_details.get('temperature', 'N/A')
                wind = weather_details.get('wind_speed', 'N/A')
                condition = 'Dome' if weather_details.get('is_dome', False) else 'Outdoor'
                weather_impact = weather_details.get('weather_impact', 0)
                print(f'   Conditions: {condition}, {temp}°F, {wind} mph wind')
                print(f'   Weather Score: {home_details["weather_score"]:.1f} (Impact: {weather_impact:+.1f})')
            else:
                print(f'   Weather Score: {home_details["weather_score"]:.1f} (No weather data)')
            
            # Show score breakdown
            print(f'   \n📊 SCORE BREAKDOWN:')
            print(f'   {pred["home_team"]}: Base {home_details["base_score"]:.1f} + Injuries {home_details["injury_impact"]:+.1f} = {home_details["final_score"]:.1f}')
            print(f'   {pred["away_team"]}: Base {away_details["base_score"]:.1f} + Injuries {away_details["injury_impact"]:+.1f} = {away_details["final_score"]:.1f}')
            
            # Show key variables
            print(f'   \n🔑 KEY VARIABLES:')
            print(f'   EPA: {pred["home_team"]} {home_details["raw_epa"]:.1f} vs {pred["away_team"]} {away_details["raw_epa"]:.1f}')
            print(f'   Success Rate: {pred["home_team"]} {home_details["raw_success_rate"]:.1%} vs {pred["away_team"]} {away_details["raw_success_rate"]:.1%}')
            print(f'   Yards/Play: {pred["home_team"]} {home_details["raw_yards"]:.2f} vs {pred["away_team"]} {away_details["raw_yards"]:.2f}')
            print(f'   Turnovers: {pred["home_team"]} {home_details["raw_turnovers"]:.1f} vs {pred["away_team"]} {away_details["raw_turnovers"]:.1f}')

def main():
    """Test the enhanced predictor with injuries"""
    predictor = EnhancedNFLPredictorWithInjuries()
    
    # Predict Week 3 with injury tracking
    predictions = predictor.predict_week_with_injuries(3)
    
    # Display results
    predictor.display_predictions_with_injuries(predictions)
    
    # Show injury summaries for a few teams
    print(f'\n🏥 INJURY SUMMARIES:')
    print('=' * 30)
    test_teams = ['BUF', 'MIA', 'PHI', 'LA']
    for team in test_teams:
        print(f'\n{predictor.injury_tracker.get_team_injury_summary(team)}')

if __name__ == "__main__":
    main()
