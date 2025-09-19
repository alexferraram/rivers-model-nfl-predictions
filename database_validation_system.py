"""
Database Validation System
Ensures all data sources are working before generating predictions
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
import nfl_data_py as nfl
from pff_data_system import PFFDataSystem
from dynamic_injury_system import DynamicInjurySystem
from weather_data_system import WeatherDataSystem

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseValidationSystem:
    """
    Comprehensive database validation system
    """
    
    def __init__(self):
        self.pff_system = PFFDataSystem()
        self.injury_system = DynamicInjurySystem(self.pff_system)
        self.weather_system = WeatherDataSystem()
        self.validation_results = {}
    
    def validate_all_databases(self) -> Dict:
        """
        Validate all databases and data sources
        """
        logger.info("🔍 VALIDATING ALL DATABASES")
        logger.info("=" * 60)
        
        validation_results = {
            'nfl_data': self._validate_nfl_data(),
            'pff_data': self._validate_pff_data(),
            'injury_data': self._validate_injury_data(),
            'weather_data': self._validate_weather_data(),
            'overall_status': 'PASS'
        }
        
        # Check overall status
        failed_systems = [k for k, v in validation_results.items() 
                         if k != 'overall_status' and v.get('status') == 'FAIL']
        
        if failed_systems:
            validation_results['overall_status'] = 'FAIL'
            logger.error(f"❌ VALIDATION FAILED: {failed_systems}")
        else:
            logger.info("✅ ALL DATABASES VALIDATED SUCCESSFULLY")
        
        self.validation_results = validation_results
        return validation_results
    
    def _validate_nfl_data(self) -> Dict:
        """Validate NFL data sources"""
        logger.info("📊 Validating NFL Data...")
        
        try:
            # Test loading recent seasons
            seasons = [2023, 2024, 2025]
            pbp_data = []
            schedules = []
            
            for season in seasons:
                try:
                    pbp = nfl.import_pbp_data([season])
                    pbp_data.append(pbp)
                    logger.info(f"   ✅ {season} PBP data: {len(pbp):,} plays")
                except Exception as e:
                    logger.warning(f"   ⚠️ {season} PBP data: {e}")
            
            # Test schedule data
            try:
                schedules = nfl.import_schedules([2025])
                logger.info(f"   ✅ 2025 Schedule data: {len(schedules)} games")
            except Exception as e:
                logger.warning(f"   ⚠️ Schedule data: {e}")
            
            if pbp_data:
                total_plays = sum(len(pbp) for pbp in pbp_data)
                logger.info(f"   ✅ Total NFL data: {total_plays:,} plays")
                return {
                    'status': 'PASS',
                    'total_plays': total_plays,
                    'seasons_loaded': len(pbp_data),
                    'schedules_loaded': len(schedules) if len(schedules) > 0 else 0
                }
            else:
                logger.error("   ❌ No NFL data loaded")
                return {'status': 'FAIL', 'error': 'No NFL data loaded'}
                
        except Exception as e:
            logger.error(f"   ❌ NFL data validation failed: {e}")
            return {'status': 'FAIL', 'error': str(e)}
    
    def _validate_pff_data(self) -> Dict:
        """Validate PFF data system"""
        logger.info("🏈 Validating PFF Data...")
        
        try:
            # Check PFF system attributes
            required_attributes = ['team_grades', 'player_grades']
            missing_attributes = []
            
            for attr in required_attributes:
                if not hasattr(self.pff_system, attr):
                    missing_attributes.append(attr)
            
            if missing_attributes:
                logger.error(f"   ❌ Missing PFF attributes: {missing_attributes}")
                return {'status': 'FAIL', 'error': f'Missing attributes: {missing_attributes}'}
            
            # Check if data is populated
            team_grades = getattr(self.pff_system, 'team_grades', {})
            player_grades = getattr(self.pff_system, 'player_grades', {})
            
            logger.info(f"   ✅ PFF team grades: {len(team_grades)} teams")
            logger.info(f"   ✅ PFF player grades: {len(player_grades)} teams")
            
            # Test sample data access
            sample_team = list(team_grades.keys())[0] if team_grades else None
            if sample_team:
                sample_grades = team_grades[sample_team]
                logger.info(f"   ✅ Sample team ({sample_team}): {len(sample_grades)} grade categories")
            
            return {
                'status': 'PASS',
                'team_grades_count': len(team_grades),
                'player_grades_count': len(player_grades),
                'sample_team': sample_team
            }
            
        except Exception as e:
            logger.error(f"   ❌ PFF data validation failed: {e}")
            return {'status': 'FAIL', 'error': str(e)}
    
    def _validate_injury_data(self) -> Dict:
        """Validate injury data system"""
        logger.info("🏥 Validating Injury Data...")
        
        try:
            # Test injury data scraping
            injury_data = self.injury_system.scrape_nfl_injuries()
            
            if not injury_data:
                logger.error("   ❌ No injury data scraped")
                return {'status': 'FAIL', 'error': 'No injury data scraped'}
            
            logger.info(f"   ✅ Injury data: {len(injury_data)} teams")
            
            # Check if we have all 32 teams
            expected_teams = 32
            if len(injury_data) < expected_teams:
                missing_count = expected_teams - len(injury_data)
                logger.error(f"   ❌ Missing injury data for {missing_count} teams (only {len(injury_data)}/32)")
                return {
                    'status': 'FAIL', 
                    'error': f'Missing injury data for {missing_count} teams. Need all 32 teams.'
                }
            
            logger.info(f"   ✅ All 32 NFL teams have injury data")
            
            # Test injury impact calculation
            test_teams = list(injury_data.keys())[:2]  # Test first 2 teams
            for team in test_teams:
                team_abbr = self._get_team_abbr_from_city(team)
                impact = self.injury_system.calculate_dynamic_injury_impact(team_abbr)
                logger.info(f"   ✅ {team_abbr} injury impact: {impact['total_impact']:.2f}%")
                
                # Show significant injuries
                significant_injuries = impact.get('injuries', [])
                if significant_injuries:
                    logger.info(f"      Significant injuries: {len(significant_injuries)}")
                    for injury in significant_injuries[:3]:  # Show first 3
                        logger.info(f"        {injury['player']} ({injury['position']}) - {injury['status']}: {injury['impact']:.2f}%")
            
            return {
                'status': 'PASS',
                'teams_with_injuries': len(injury_data),
                'test_teams': test_teams,
                'all_32_teams': True
            }
            
        except Exception as e:
            logger.error(f"   ❌ Injury data validation failed: {e}")
            return {'status': 'FAIL', 'error': str(e)}
    
    def _validate_weather_data(self) -> Dict:
        """Validate weather data system"""
        logger.info("🌤️ Validating Weather Data...")
        
        try:
            # Check weather system attributes
            required_methods = ['get_game_weather', 'parse_weather_description']
            missing_methods = []
            
            for method in required_methods:
                if not hasattr(self.weather_system, method):
                    missing_methods.append(method)
            
            if missing_methods:
                logger.error(f"   ❌ Missing weather methods: {missing_methods}")
                return {'status': 'FAIL', 'error': f'Missing methods: {missing_methods}'}
            
            # Test weather data parsing
            test_weather = "Temp: 72°F, Wind: NW 15 mph, Clear"
            parsed_weather = self.weather_system.parse_weather_description(test_weather)
            
            logger.info(f"   ✅ Weather parsing test: {parsed_weather}")
            
            return {
                'status': 'PASS',
                'parsing_test': parsed_weather
            }
            
        except Exception as e:
            logger.error(f"   ❌ Weather data validation failed: {e}")
            return {'status': 'FAIL', 'error': str(e)}
    
    def _get_team_abbr_from_city(self, city_name: str) -> str:
        """Convert city name to abbreviation"""
        team_mapping = {
            'Buffalo': 'BUF', 'Miami': 'MIA', 'Philadelphia': 'PHI',
            'Dallas': 'DAL', 'New York Giants': 'NYG', 'Washington': 'WAS',
            'Chicago': 'CHI', 'Detroit': 'DET', 'Green Bay': 'GB',
            'Minnesota': 'MIN', 'Atlanta': 'ATL', 'Carolina': 'CAR',
            'New Orleans': 'NO', 'Tampa Bay': 'TB', 'Arizona': 'ARI',
            'Los Angeles Rams': 'LAR', 'San Francisco': 'SF', 'Seattle': 'SEA',
            'Baltimore': 'BAL', 'Cincinnati': 'CIN', 'Cleveland': 'CLE',
            'Pittsburgh': 'PIT', 'Houston': 'HOU', 'Indianapolis': 'IND',
            'Jacksonville': 'JAX', 'Tennessee': 'TEN', 'Denver': 'DEN',
            'Kansas City': 'KC', 'Las Vegas': 'LV', 'Los Angeles Chargers': 'LAC',
            'New England': 'NE', 'New York Jets': 'NYJ'
        }
        return team_mapping.get(city_name, 'UNK')
    
    def display_validation_report(self):
        """Display comprehensive validation report"""
        print("\n📋 DATABASE VALIDATION REPORT")
        print("=" * 60)
        
        for system, result in self.validation_results.items():
            if system == 'overall_status':
                continue
                
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"\n{status_icon} {system.upper()}: {result['status']}")
            
            if result['status'] == 'PASS':
                for key, value in result.items():
                    if key != 'status':
                        print(f"   {key}: {value}")
            else:
                print(f"   Error: {result.get('error', 'Unknown error')}")
        
        overall_status = self.validation_results['overall_status']
        status_icon = "✅" if overall_status == 'PASS' else "❌"
        print(f"\n{status_icon} OVERALL STATUS: {overall_status}")
        
        if overall_status == 'FAIL':
            print("\n🚨 VALIDATION FAILED - DO NOT PROCEED WITH PREDICTIONS")
            print("Please fix the failing systems before generating predictions.")
        else:
            print("\n🎯 ALL SYSTEMS VALIDATED - READY FOR PREDICTIONS")

if __name__ == "__main__":
    # Test the validation system
    validator = DatabaseValidationSystem()
    results = validator.validate_all_databases()
    validator.display_validation_report()
