#!/usr/bin/env python3
"""
Comprehensive Weather Data System
Extracts and processes weather data from play-by-play data.
"""

import pandas as pd
import numpy as np
import nfl_data_py as nfl
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WeatherDataSystem:
    """Comprehensive weather data system using PBP data"""
    
    def __init__(self, seasons: List[int] = None):
        """Initialize weather data system"""
        if seasons is None:
            seasons = [datetime.now().year]
        
        self.seasons = seasons
        self.pbp_data = None
        self.weather_cache = {}
        self.load_data()
    
    def load_data(self):
        """Load play-by-play data"""
        logger.info(f"Loading PBP data for seasons: {self.seasons}")
        try:
            self.pbp_data = nfl.import_pbp_data(self.seasons)
            logger.info(f"✅ Loaded {len(self.pbp_data):,} plays")
            
            # Analyze weather data completeness
            self._analyze_weather_completeness()
            
        except Exception as e:
            logger.error(f"Error loading PBP data: {e}")
            self.pbp_data = None
    
    def _analyze_weather_completeness(self):
        """Analyze completeness of weather data in PBP"""
        if self.pbp_data is None:
            return
        
        logger.info("🌤️ Analyzing weather data completeness...")
        
        # Weather data analysis
        weather_data = self.pbp_data[['game_id', 'weather', 'temp', 'wind']].copy()
        weather_data = weather_data.dropna(subset=['weather', 'temp', 'wind'], how='all')
        
        logger.info(f"Weather data coverage: {len(weather_data):,}/{len(self.pbp_data):,} plays ({len(weather_data)/len(self.pbp_data)*100:.1f}%)")
        
        # Temperature data
        temp_data = weather_data['temp'].notna().sum()
        logger.info(f"Temperature data: {temp_data:,}/{len(weather_data):,} plays ({temp_data/len(weather_data)*100:.1f}%)")
        
        # Wind data
        wind_data = weather_data['wind'].notna().sum()
        logger.info(f"Wind data: {wind_data:,}/{len(weather_data):,} plays ({wind_data/len(weather_data)*100:.1f}%)")
        
        # Weather conditions
        weather_conditions = weather_data['weather'].notna().sum()
        logger.info(f"Weather conditions: {weather_conditions:,}/{len(weather_data):,} plays ({weather_conditions/len(weather_data)*100:.1f}%)")
    
    def parse_weather_description(self, weather_desc: str) -> Dict:
        """Parse weather description to extract structured data"""
        if pd.isna(weather_desc):
            return {}
        
        weather_info = {
            'condition': None,
            'temperature': None,
            'humidity': None,
            'wind_speed': None,
            'wind_direction': None,
            'is_dome': False,
            'is_rain': False,
            'is_snow': False,
            'is_clear': False,
            'is_cloudy': False
        }
        
        # Check for dome/indoor games
        if 'N/A Indoors' in weather_desc or 'Dome' in weather_desc:
            weather_info['is_dome'] = True
            weather_info['condition'] = 'Dome'
            return weather_info
        
        # Extract temperature (multiple patterns)
        temp_patterns = [
            r'Temp:\s*(\d+)°?\s*F',  # "Temp: 72°F"
            r'(\d+)°F',              # "72°F"
            r'(\d+)\s*degrees?\s*F',  # "72 degrees F"
            r'(\d+)\s*F'              # "72 F"
        ]
        
        for pattern in temp_patterns:
            temp_match = re.search(pattern, weather_desc)
            if temp_match:
                weather_info['temperature'] = int(temp_match.group(1))
                break
        
        # Extract humidity
        humidity_match = re.search(r'Humidity:\s*(\d+)%', weather_desc)
        if humidity_match:
            weather_info['humidity'] = int(humidity_match.group(1))
        
        # Extract wind speed and direction (multiple patterns)
        wind_patterns = [
            r'Wind:\s*([A-Z]+)\s*(\d+)\s*mph',  # "Wind: NW 15 mph"
            r'Wind:\s*(\d+)\s*mph',             # "Wind: 15 mph"
            r'(\d+)\s*mph',                     # "15 mph"
            r'Wind\s*(\d+)',                    # "Wind 15"
            r'(\d+)\s*mph\s*wind'               # "15 mph wind"
        ]
        
        for pattern in wind_patterns:
            wind_match = re.search(pattern, weather_desc)
            if wind_match:
                if len(wind_match.groups()) == 2:  # Has direction and speed
                    weather_info['wind_direction'] = wind_match.group(1)
                    weather_info['wind_speed'] = int(wind_match.group(2))
                else:  # Only has speed
                    weather_info['wind_speed'] = int(wind_match.group(1))
                break
        
        # Extract weather condition
        condition = weather_desc.split(' Temp:')[0].strip()
        weather_info['condition'] = condition
        
        # Determine weather type
        condition_lower = condition.lower()
        if 'rain' in condition_lower:
            weather_info['is_rain'] = True
        elif 'snow' in condition_lower:
            weather_info['is_snow'] = True
        elif 'clear' in condition_lower or 'sunny' in condition_lower:
            weather_info['is_clear'] = True
        elif 'cloudy' in condition_lower:
            weather_info['is_cloudy'] = True
        
        return weather_info
    
    def get_game_weather(self, game_id: str) -> Dict:
        """Get comprehensive weather data for a specific game"""
        if self.pbp_data is None:
            return {}
        
        # Get weather data for the game
        game_data = self.pbp_data[self.pbp_data['game_id'] == game_id]
        
        if game_data.empty:
            logger.warning(f"No data found for game {game_id}")
            return {}
        
        # Get weather information
        weather_desc = game_data['weather'].iloc[0] if 'weather' in game_data.columns else None
        temp = game_data['temp'].iloc[0] if 'temp' in game_data.columns else None
        wind = game_data['wind'].iloc[0] if 'wind' in game_data.columns else None
        
        # Parse weather description
        parsed_weather = self.parse_weather_description(weather_desc)
        
        # Create comprehensive weather data
        weather_data = {
            'game_id': game_id,
            'raw_weather': weather_desc,
            'temperature': temp if pd.notna(temp) else parsed_weather.get('temperature'),
            'wind_speed': wind if pd.notna(wind) else parsed_weather.get('wind_speed'),
            'wind_direction': parsed_weather.get('wind_direction'),
            'humidity': parsed_weather.get('humidity'),
            'condition': parsed_weather.get('condition'),
            'is_dome': parsed_weather.get('is_dome', False),
            'is_rain': parsed_weather.get('is_rain', False),
            'is_snow': parsed_weather.get('is_snow', False),
            'is_clear': parsed_weather.get('is_clear', False),
            'is_cloudy': parsed_weather.get('is_cloudy', False),
            'weather_impact_score': self._calculate_weather_impact_score(parsed_weather, temp, wind)
        }
        
        logger.info(f"🌤️ {game_id}: {weather_data['condition']}, {weather_data['temperature']}°F, {weather_data['wind_speed']} mph")
        return weather_data
    
    def get_team_weather_stats(self, team: str, season: int = None) -> Dict:
        """Get weather statistics for a team's games"""
        if self.pbp_data is None:
            return {}
        
        # Filter data for team
        team_data = self.pbp_data[
            (self.pbp_data['home_team'] == team) | 
            (self.pbp_data['away_team'] == team)
        ].copy()
        
        if season:
            team_data = team_data[team_data['season'] == season]
        
        # Get unique games
        games = team_data['game_id'].unique()
        
        weather_stats = {
            'team': team,
            'season': season,
            'total_games': len(games),
            'dome_games': 0,
            'outdoor_games': 0,
            'rain_games': 0,
            'snow_games': 0,
            'clear_games': 0,
            'cloudy_games': 0,
            'avg_temperature': 0,
            'avg_wind_speed': 0,
            'avg_humidity': 0,
            'weather_conditions': {},
            'temperature_range': {'min': 0, 'max': 0},
            'wind_range': {'min': 0, 'max': 0}
        }
        
        temperatures = []
        wind_speeds = []
        humidities = []
        
        for game_id in games:
            game_weather = self.get_game_weather(game_id)
            
            if game_weather.get('is_dome'):
                weather_stats['dome_games'] += 1
            else:
                weather_stats['outdoor_games'] += 1
            
            if game_weather.get('is_rain'):
                weather_stats['rain_games'] += 1
            if game_weather.get('is_snow'):
                weather_stats['snow_games'] += 1
            if game_weather.get('is_clear'):
                weather_stats['clear_games'] += 1
            if game_weather.get('is_cloudy'):
                weather_stats['cloudy_games'] += 1
            
            # Collect numeric data
            if game_weather.get('temperature'):
                temperatures.append(game_weather['temperature'])
            if game_weather.get('wind_speed'):
                wind_speeds.append(game_weather['wind_speed'])
            if game_weather.get('humidity'):
                humidities.append(game_weather['humidity'])
            
            # Count weather conditions
            condition = game_weather.get('condition', 'Unknown')
            weather_stats['weather_conditions'][condition] = weather_stats['weather_conditions'].get(condition, 0) + 1
        
        # Calculate averages
        if temperatures:
            weather_stats['avg_temperature'] = np.mean(temperatures)
            weather_stats['temperature_range'] = {'min': min(temperatures), 'max': max(temperatures)}
        
        if wind_speeds:
            weather_stats['avg_wind_speed'] = np.mean(wind_speeds)
            weather_stats['wind_range'] = {'min': min(wind_speeds), 'max': max(wind_speeds)}
        
        if humidities:
            weather_stats['avg_humidity'] = np.mean(humidities)
        
        logger.info(f"🌤️ {team} weather stats: {weather_stats['dome_games']} dome, {weather_stats['outdoor_games']} outdoor, avg temp {weather_stats['avg_temperature']:.1f}°F")
        return weather_stats
    
    def get_weather_impact_analysis(self, game_id: str) -> Dict:
        """Analyze weather impact on game performance"""
        if self.pbp_data is None:
            return {}
        
        # Get weather data
        weather_data = self.get_game_weather(game_id)
        
        # Get game data
        game_data = self.pbp_data[self.pbp_data['game_id'] == game_id]
        
        if game_data.empty:
            return {}
        
        # Analyze performance by weather conditions
        analysis = {
            'game_id': game_id,
            'weather': weather_data,
            'total_plays': len(game_data),
            'passing_plays': len(game_data[game_data['play_type'] == 'pass']),
            'rushing_plays': len(game_data[game_data['play_type'] == 'run']),
            'pass_completion_rate': game_data[game_data['play_type'] == 'pass']['complete_pass'].mean(),
            'avg_pass_yards': game_data[game_data['play_type'] == 'pass']['passing_yards'].mean(),
            'avg_rush_yards': game_data[game_data['play_type'] == 'run']['rushing_yards'].mean(),
            'turnovers': game_data['interception'].sum() + game_data['fumble_lost'].sum(),
            'weather_impact': self._assess_weather_impact(weather_data, game_data)
        }
        
        return analysis
    
    def _calculate_weather_impact_score(self, parsed_weather: Dict, temp: float, wind: float) -> float:
        """Calculate weather impact score (0-10, higher = more impact)"""
        score = 0
        
        # Temperature impact
        if temp:
            if temp < 32:  # Freezing
                score += 3
            elif temp < 45:  # Cold
                score += 2
            elif temp > 85:  # Hot
                score += 1
        
        # Wind impact
        if wind:
            if wind > 15:  # Strong wind
                score += 3
            elif wind > 10:  # Moderate wind
                score += 2
            elif wind > 5:  # Light wind
                score += 1
        
        # Precipitation impact
        if parsed_weather.get('is_rain'):
            score += 2
        if parsed_weather.get('is_snow'):
            score += 3
        
        # Dome games have no impact
        if parsed_weather.get('is_dome'):
            score = 0
        
        return min(score, 10)  # Cap at 10
    
    def _assess_weather_impact(self, weather_data: Dict, game_data: pd.DataFrame) -> Dict:
        """Assess weather impact on game performance"""
        impact = {
            'level': 'None',
            'factors': [],
            'recommendations': []
        }
        
        score = weather_data.get('weather_impact_score', 0)
        
        if score >= 7:
            impact['level'] = 'High'
        elif score >= 4:
            impact['level'] = 'Medium'
        elif score >= 1:
            impact['level'] = 'Low'
        else:
            impact['level'] = 'None'
        
        # Identify specific factors
        if weather_data.get('is_rain'):
            impact['factors'].append('Rain affects passing accuracy and ball handling')
            impact['recommendations'].append('Expect lower completion rates and more fumbles')
        
        if weather_data.get('is_snow'):
            impact['factors'].append('Snow significantly impacts visibility and footing')
            impact['recommendations'].append('Expect reduced passing efficiency and increased rushing')
        
        if weather_data.get('wind_speed', 0) > 10:
            impact['factors'].append('Strong wind affects passing accuracy')
            impact['recommendations'].append('Expect lower completion rates and more interceptions')
        
        if weather_data.get('temperature', 0) < 32:
            impact['factors'].append('Freezing temperatures affect ball handling')
            impact['recommendations'].append('Expect more fumbles and reduced passing efficiency')
        
        if weather_data.get('temperature', 0) > 85:
            impact['factors'].append('Hot temperatures affect player endurance')
            impact['recommendations'].append('Expect reduced performance in second half')
        
        if weather_data.get('is_dome'):
            impact['factors'].append('Dome conditions provide optimal playing environment')
            impact['recommendations'].append('No weather impact expected')
        
        return impact
    
    def get_weather_trends(self, team: str, seasons: List[int] = None) -> Dict:
        """Get weather trends for a team over multiple seasons"""
        if seasons is None:
            seasons = self.seasons
        
        trends = {
            'team': team,
            'seasons': seasons,
            'season_stats': {},
            'overall_trends': {}
        }
        
        for season in seasons:
            season_stats = self.get_team_weather_stats(team, season)
            trends['season_stats'][season] = season_stats
        
        # Calculate overall trends
        all_temps = []
        all_winds = []
        all_humidities = []
        
        for season_stats in trends['season_stats'].values():
            if season_stats['avg_temperature'] > 0:
                all_temps.append(season_stats['avg_temperature'])
            if season_stats['avg_wind_speed'] > 0:
                all_winds.append(season_stats['avg_wind_speed'])
            if season_stats['avg_humidity'] > 0:
                all_humidities.append(season_stats['avg_humidity'])
        
        if all_temps:
            trends['overall_trends']['avg_temperature'] = np.mean(all_temps)
            trends['overall_trends']['temperature_range'] = {'min': min(all_temps), 'max': max(all_temps)}
        
        if all_winds:
            trends['overall_trends']['avg_wind_speed'] = np.mean(all_winds)
            trends['overall_trends']['wind_range'] = {'min': min(all_winds), 'max': max(all_winds)}
        
        if all_humidities:
            trends['overall_trends']['avg_humidity'] = np.mean(all_humidities)
        
        return trends

def main():
    """Main function to demonstrate weather data system"""
    logger.info("🌤️ Weather Data System Starting...")
    
    # Create weather data system
    weather_system = WeatherDataSystem()
    
    if weather_system.pbp_data is None:
        logger.error("Failed to load PBP data. Exiting.")
        return
    
    # Test with specific games
    test_games = [
        '2025_01_ARI_NO',
        '2025_01_BAL_BUF',
        '2025_01_DAL_PHI',
        '2025_01_CIN_CLE'
    ]
    
    for game_id in test_games:
        print(f"\n🌤️ {game_id} - WEATHER ANALYSIS")
        print("=" * 50)
        
        # Get weather data
        weather_data = weather_system.get_game_weather(game_id)
        
        if weather_data:
            print(f"Weather Condition: {weather_data['condition']}")
            print(f"Temperature: {weather_data['temperature']}°F")
            print(f"Wind: {weather_data['wind_speed']} mph {weather_data['wind_direction']}")
            print(f"Humidity: {weather_data['humidity']}%")
            print(f"Dome Game: {weather_data['is_dome']}")
            print(f"Weather Impact Score: {weather_data['weather_impact_score']}/10")
            
            # Get weather impact analysis
            impact_analysis = weather_system.get_weather_impact_analysis(game_id)
            if impact_analysis:
                print(f"\nWeather Impact Analysis:")
                print(f"Impact Level: {impact_analysis['weather_impact']['level']}")
                print(f"Factors: {', '.join(impact_analysis['weather_impact']['factors'])}")
                print(f"Recommendations: {', '.join(impact_analysis['weather_impact']['recommendations'])}")
    
    # Test team weather stats
    print(f"\n🏈 TEAM WEATHER STATISTICS")
    print("=" * 40)
    
    test_teams = ['BUF', 'MIA', 'ARI', 'NO']
    
    for team in test_teams:
        print(f"\n🌤️ {team} Weather Stats:")
        print("-" * 25)
        
        team_stats = weather_system.get_team_weather_stats(team)
        
        print(f"Total Games: {team_stats['total_games']}")
        print(f"Dome Games: {team_stats['dome_games']}")
        print(f"Outdoor Games: {team_stats['outdoor_games']}")
        print(f"Rain Games: {team_stats['rain_games']}")
        print(f"Snow Games: {team_stats['snow_games']}")
        print(f"Clear Games: {team_stats['clear_games']}")
        print(f"Cloudy Games: {team_stats['cloudy_games']}")
        print(f"Average Temperature: {team_stats['avg_temperature']:.1f}°F")
        print(f"Average Wind Speed: {team_stats['avg_wind_speed']:.1f} mph")
        print(f"Average Humidity: {team_stats['avg_humidity']:.1f}%")
        print(f"Temperature Range: {team_stats['temperature_range']['min']}°F - {team_stats['temperature_range']['max']}°F")
        print(f"Wind Range: {team_stats['wind_range']['min']} mph - {team_stats['wind_range']['max']} mph")
    
    logger.info("\n✅ Weather data system demonstration completed!")

if __name__ == "__main__":
    main()
