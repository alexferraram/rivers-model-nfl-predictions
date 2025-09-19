"""
PFF (Pro Football Focus) Data Integration System
Integrates PFF Premium data for enhanced NFL predictions
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
from datetime import datetime, timedelta
import json
import re
import os
from typing import Dict, List, Optional, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PFFDataSystem:
    """
    Comprehensive PFF data integration system for NFL predictions
    """
    
    def __init__(self):
        self.team_grades = {}
        self.player_grades = {}
        self.last_update = None
        self.update_frequency = 3600  # 1 hour
        
        # Load mock data for testing
        self._load_mock_data()
        
        # PFF Grade Categories
        self.grade_categories = {
            'offense': ['passing', 'rushing', 'receiving', 'pass_blocking', 'run_blocking'],
            'defense': ['pass_rush', 'run_defense', 'coverage', 'tackling'],
            'special_teams': ['kicking', 'punting', 'return']
        }
        
        # Position importance weights for injury impact
        self.position_weights = {
            'QB': 1.0,      # Highest impact
            'RB': 0.8,      # High impact
            'WR': 0.7,      # High impact
            'TE': 0.6,      # Medium-high impact
            'OT': 0.5,      # Medium impact
            'OG': 0.4,      # Medium impact
            'C': 0.4,       # Medium impact
            'DE': 0.6,      # Medium-high impact
            'DT': 0.5,      # Medium impact
            'LB': 0.5,      # Medium impact
            'CB': 0.6,      # Medium-high impact
            'S': 0.5,       # Medium impact
            'K': 0.2,       # Low impact
            'P': 0.1,       # Low impact
            'LS': 0.1        # Low impact
        }
        
        # Team mapping for PFF data
        self.team_mapping = {
            'ARI': 'Arizona Cardinals',
            'ATL': 'Atlanta Falcons',
            'BAL': 'Baltimore Ravens',
            'BUF': 'Buffalo Bills',
            'CAR': 'Carolina Panthers',
            'CHI': 'Chicago Bears',
            'CIN': 'Cincinnati Bengals',
            'CLE': 'Cleveland Browns',
            'DAL': 'Dallas Cowboys',
            'DEN': 'Denver Broncos',
            'DET': 'Detroit Lions',
            'GB': 'Green Bay Packers',
            'HOU': 'Houston Texans',
            'IND': 'Indianapolis Colts',
            'JAX': 'Jacksonville Jaguars',
            'KC': 'Kansas City Chiefs',
            'LV': 'Las Vegas Raiders',
            'LAC': 'Los Angeles Chargers',
            'LA': 'Los Angeles Rams',
            'MIA': 'Miami Dolphins',
            'MIN': 'Minnesota Vikings',
            'NE': 'New England Patriots',
            'NO': 'New Orleans Saints',
            'NYG': 'New York Giants',
            'NYJ': 'New York Jets',
            'PHI': 'Philadelphia Eagles',
            'PIT': 'Pittsburgh Steelers',
            'SF': 'San Francisco 49ers',
            'SEA': 'Seattle Seahawks',
            'TB': 'Tampa Bay Buccaneers',
            'TEN': 'Tennessee Titans',
            'WAS': 'Washington Commanders'
        }
    
    def _load_mock_data(self):
        """Load mock PFF data for testing"""
        try:
            # Load mock team grades
            self.scrape_team_grades()
            
            # Load mock player grades
            self.scrape_player_grades()
            
            # Validate data completeness
            self._validate_pff_data()
            
            logger.info("✅ Mock PFF data loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading mock PFF data: {e}")
            # Ensure we have at least basic data
            self._ensure_basic_data()
    
    def _validate_pff_data(self):
        """Validate that PFF data is complete for all teams"""
        try:
            all_teams = [
                'Buffalo Bills', 'Miami Dolphins', 'Kansas City Chiefs', 'Baltimore Ravens',
                'San Francisco 49ers', 'Philadelphia Eagles', 'Dallas Cowboys', 'Detroit Lions',
                'Green Bay Packers', 'Cincinnati Bengals', 'Los Angeles Rams', 'Tampa Bay Buccaneers',
                'Indianapolis Colts', 'Jacksonville Jaguars', 'Houston Texans', 'New York Jets',
                'Pittsburgh Steelers', 'Cleveland Browns', 'Denver Broncos', 'Las Vegas Raiders',
                'Los Angeles Chargers', 'New England Patriots', 'Tennessee Titans', 'Washington Commanders',
                'Carolina Panthers', 'Atlanta Falcons', 'New Orleans Saints', 'Minnesota Vikings',
                'Arizona Cardinals', 'Seattle Seahawks', 'New York Giants', 'Chicago Bears'
            ]
            
            # Check team grades
            missing_teams = []
            for team in all_teams:
                if team not in self.team_grades:
                    missing_teams.append(team)
            
            if missing_teams:
                logger.warning(f"Missing team grades for: {missing_teams}")
                self._ensure_basic_data()
            
            # Check player grades
            missing_player_teams = []
            for team in all_teams:
                if team not in self.player_grades:
                    missing_player_teams.append(team)
            
            if missing_player_teams:
                logger.warning(f"Missing player grades for: {missing_player_teams}")
                self._ensure_basic_data()
            
            logger.info(f"✅ PFF data validation complete - {len(self.team_grades)} teams, {len(self.player_grades)} player datasets")
            
        except Exception as e:
            logger.error(f"Error validating PFF data: {e}")
            self._ensure_basic_data()
    
    def _ensure_basic_data(self):
        """Ensure basic PFF data is available for all teams"""
        try:
            all_teams = [
                'Buffalo Bills', 'Miami Dolphins', 'Kansas City Chiefs', 'Baltimore Ravens',
                'San Francisco 49ers', 'Philadelphia Eagles', 'Dallas Cowboys', 'Detroit Lions',
                'Green Bay Packers', 'Cincinnati Bengals', 'Los Angeles Rams', 'Tampa Bay Buccaneers',
                'Indianapolis Colts', 'Jacksonville Jaguars', 'Houston Texans', 'New York Jets',
                'Pittsburgh Steelers', 'Cleveland Browns', 'Denver Broncos', 'Las Vegas Raiders',
                'Los Angeles Chargers', 'New England Patriots', 'Tennessee Titans', 'Washington Commanders',
                'Carolina Panthers', 'Atlanta Falcons', 'New Orleans Saints', 'Minnesota Vikings',
                'Arizona Cardinals', 'Seattle Seahawks', 'New York Giants', 'Chicago Bears'
            ]
            
            # Initialize team grades if not exists
            if not hasattr(self, 'team_grades') or not self.team_grades:
                self.team_grades = {}
            
            # Initialize player grades if not exists
            if not hasattr(self, 'player_grades') or not self.player_grades:
                self.player_grades = {}
            
            # Add default data for all teams (only if they don't already have data)
            for team in all_teams:
                if team not in self.team_grades:
                    self.team_grades[team] = {
                        'overall': 75.0, 'overall_offense': 75.0, 'overall_defense': 75.0,
                        'offense': {
                            'passing': 75.0, 'rushing': 75.0, 'receiving': 75.0,
                            'pass_blocking': 75.0, 'run_blocking': 75.0
                        },
                        'defense': {
                            'pass_rush': 75.0, 'run_defense': 75.0, 'coverage': 75.0, 'tackling': 75.0
                        },
                        'special_teams': {'kicking': 75.0, 'punting': 75.0, 'return': 75.0}
                    }
                
                if team not in self.player_grades:
                    self.player_grades[team] = {
                        'QB': {'Starting QB': 75.0},
                        'RB': {'Starting RB': 75.0, 'Backup RB': 70.0},
                        'WR': {'WR1': 75.0, 'WR2': 70.0, 'WR3': 65.0},
                        'TE': {'Starting TE': 75.0, 'Backup TE': 70.0},
                        'OT': {'LT': 75.0, 'RT': 75.0},
                        'OG': {'LG': 75.0, 'RG': 75.0},
                        'C': {'Starting C': 75.0},
                        'DE': {'DE1': 75.0, 'DE2': 75.0},
                        'DT': {'DT1': 75.0, 'DT2': 75.0},
                        'LB': {'LB1': 75.0, 'LB2': 75.0},
                        'CB': {'CB1': 75.0, 'CB2': 75.0},
                        'S': {'S1': 75.0, 'S2': 75.0},
                        'K': {'Kicker': 75.0},
                        'P': {'Punter': 75.0}
                    }
            
            logger.info(f"✅ Basic PFF data ensured for all {len(all_teams)} teams")
            
        except Exception as e:
            logger.error(f"Error ensuring basic PFF data: {e}")
    
    def scrape_team_grades(self) -> Dict:
        """
        Scrape PFF team grades from premium.pff.com using live scraper
        """
        try:
            # Import the data parser
            from pff_data_parser import PFFDataParser
            
            # Use the data parser to check for exported files
            parser = PFFDataParser()
            
            # Check for exported data files (prioritize your clean CSV file)
            exported_files = [
                'Week 3 PFF Team Scores Clean.csv',  # Your clean CSV file
                'Week 3 PFF Team Scores.csv',  # Your original CSV file
                'pff_exported_data.csv',
                'pff_exported_data.json',
                'pff_data_template.csv',
                'pff_data_template.json'
            ]
            
            raw_data = None
            for file_path in exported_files:
                if os.path.exists(file_path):
                    logger.info(f"📊 Found exported data file: {file_path}")
                    raw_data = parser.parse_data_file(file_path)
                    if raw_data and len(raw_data) > 10:
                        logger.info(f"✅ Successfully parsed {len(raw_data)} teams from {file_path}")
                        break
            
            if not raw_data:
                # Fallback to authenticated scraper
                from pff_authenticated_scraper import AuthenticatedPFFScraper
                scraper = AuthenticatedPFFScraper()
                raw_data = scraper.scrape_pff_data()
            
            if raw_data:
                # Convert to nested format for compatibility
                team_grades = parser.convert_to_nested_format(raw_data)
                logger.info(f"✅ Successfully processed {len(team_grades)} teams")
                # Assign to self.team_grades to ensure it's available for validation
                self.team_grades = team_grades
                return team_grades
            
        except Exception as e:
            logger.warning(f"Live scraper failed: {e}")
        
        # Fallback to basic data if live scraper fails
        logger.info("Using fallback data structure")
        
        # Create basic data structure for all teams
        all_teams = [
            'Buffalo Bills', 'Miami Dolphins', 'Kansas City Chiefs', 'Baltimore Ravens',
            'San Francisco 49ers', 'Philadelphia Eagles', 'Dallas Cowboys', 'Detroit Lions',
            'Green Bay Packers', 'Cincinnati Bengals', 'Los Angeles Rams', 'Tampa Bay Buccaneers',
            'Indianapolis Colts', 'Jacksonville Jaguars', 'Houston Texans', 'New York Jets',
            'Pittsburgh Steelers', 'Cleveland Browns', 'Denver Broncos', 'Las Vegas Raiders',
            'Los Angeles Chargers', 'New England Patriots', 'Tennessee Titans', 'Washington Commanders',
            'Carolina Panthers', 'Atlanta Falcons', 'New Orleans Saints', 'Minnesota Vikings',
            'Arizona Cardinals', 'Seattle Seahawks', 'New York Giants', 'Chicago Bears'
        ]
        
        fallback_team_grades = {}
        for team in all_teams:
            fallback_team_grades[team] = {
                'overall': 70.0,
                'offense': {
                    'overall': 70.0,
                    'passing': 70.0,
                    'pass_blocking': 70.0,
                    'receiving': 70.0,
                    'rushing': 70.0,
                    'run_blocking': 70.0
                },
                'defense': {
                    'overall': 70.0,
                    'run_defense': 70.0,
                    'tackling': 70.0,
                    'pass_rush': 70.0,
                    'coverage': 70.0
                },
                'special_teams': {
                    'overall': 70.0
                }
            }
        
        # Assign to self.team_grades to ensure it's available for validation
        self.team_grades = fallback_team_grades
        self.last_update = datetime.now()
        
        logger.info(f"Successfully loaded fallback PFF team grades for {len(fallback_team_grades)} teams")
        return fallback_team_grades
    
    def scrape_player_grades(self, position: str = None) -> Dict:
        """
        Scrape PFF player grades from pff.com/nfl/grades/position/
        """
        try:
            # For now, return mock data structure
            # In production, this would scrape from PFF
            mock_player_grades = {
                'Buffalo Bills': {
                    'QB': {'Josh Allen': 89.2},
                    'RB': {'James Cook': 78.5, 'Latavius Murray': 72.1},
                    'WR': {'Stefon Diggs': 91.3, 'Gabe Davis': 76.8, 'Khalil Shakir': 74.2},
                    'TE': {'Dawson Knox': 79.4, 'Dalton Kincaid': 82.1},
                    'OT': {'Dion Dawkins': 85.7, 'Spencer Brown': 78.9},
                    'OG': {'Connor McGovern': 81.2, 'O\'Cyrus Torrence': 79.6},
                    'C': {'Mitch Morse': 83.4},
                    'DE': {'Von Miller': 88.1, 'Greg Rousseau': 82.7},
                    'DT': {'Ed Oliver': 86.3, 'DaQuan Jones': 79.8},
                    'LB': {'Matt Milano': 91.2, 'Terrel Bernard': 84.5},
                    'CB': {'Tre\'Davious White': 89.7, 'Taron Johnson': 82.3},
                    'S': {'Micah Hyde': 87.4, 'Jordan Poyer': 85.9},
                    'K': {'Tyler Bass': 81.5},
                    'P': {'Sam Martin': 79.2}
                },
                'Miami Dolphins': {
                    'QB': {'Tua Tagovailoa': 87.8},
                    'RB': {'Raheem Mostert': 80.2, 'De\'Von Achane': 83.7},
                    'WR': {'Tyreek Hill': 94.1, 'Jaylen Waddle': 88.6, 'Cedrick Wilson': 75.3},
                    'TE': {'Mike Gesicki': 77.9, 'Durham Smythe': 74.8},
                    'OT': {'Terron Armstead': 86.4, 'Austin Jackson': 78.1},
                    'OG': {'Robert Hunt': 82.7, 'Liam Eichenberg': 76.5},
                    'C': {'Connor Williams': 80.9},
                    'DE': {'Bradley Chubb': 85.2, 'Jaelan Phillips': 83.6},
                    'DT': {'Christian Wilkins': 87.1, 'Raekwon Davis': 78.4},
                    'LB': {'Jerome Baker': 81.8, 'Andrew Van Ginkel': 79.2},
                    'CB': {'Xavien Howard': 88.3, 'Byron Jones': 82.7},
                    'S': {'Jevon Holland': 86.5, 'Brandon Jones': 79.8},
                    'K': {'Jason Sanders': 78.9},
                    'P': {'Jake Bailey': 77.6}
                }
            }
            
            self.player_grades = mock_player_grades
            self.last_update = datetime.now()
            
            # Ensure all 32 teams have player data
            all_teams = [
                'Buffalo Bills', 'Miami Dolphins', 'Kansas City Chiefs', 'Baltimore Ravens',
                'San Francisco 49ers', 'Philadelphia Eagles', 'Dallas Cowboys', 'Detroit Lions',
                'Green Bay Packers', 'Cincinnati Bengals', 'Los Angeles Rams', 'Tampa Bay Buccaneers',
                'Indianapolis Colts', 'Jacksonville Jaguars', 'Houston Texans', 'New York Jets',
                'Pittsburgh Steelers', 'Cleveland Browns', 'Denver Broncos', 'Las Vegas Raiders',
                'Los Angeles Chargers', 'New England Patriots', 'Tennessee Titans', 'Washington Commanders',
                'Carolina Panthers', 'Atlanta Falcons', 'New Orleans Saints', 'Minnesota Vikings',
                'Arizona Cardinals', 'Seattle Seahawks', 'New York Giants', 'Chicago Bears'
            ]
            
            # Add default player data for teams not in mock_player_grades
            for team in all_teams:
                if team not in mock_player_grades:
                    mock_player_grades[team] = {
                        'QB': {'Starting QB': 75.0},
                        'RB': {'Starting RB': 75.0, 'Backup RB': 70.0},
                        'WR': {'WR1': 75.0, 'WR2': 70.0, 'WR3': 65.0},
                        'TE': {'Starting TE': 75.0, 'Backup TE': 70.0},
                        'OT': {'LT': 75.0, 'RT': 75.0},
                        'OG': {'LG': 75.0, 'RG': 75.0},
                        'C': {'Starting C': 75.0},
                        'DE': {'DE1': 75.0, 'DE2': 75.0},
                        'DT': {'DT1': 75.0, 'DT2': 75.0},
                        'LB': {'LB1': 75.0, 'LB2': 75.0},
                        'CB': {'CB1': 75.0, 'CB2': 75.0},
                        'S': {'S1': 75.0, 'S2': 75.0},
                        'K': {'Kicker': 75.0},
                        'P': {'Punter': 75.0}
                    }
            
            logger.info(f"Successfully loaded PFF player grades for {len(mock_player_grades)} teams")
            return mock_player_grades
            
        except Exception as e:
            logger.error(f"Error scraping PFF player grades: {e}")
            return {}
    
    def calculate_dynamic_injury_penalty(self, player_name: str, position: str, 
                                        team_abbr: str, injury_status: str) -> float:
        """
        Calculate dynamic injury penalty based on PFF grade
        Only counts 'OUT' status as injured
        """
        if injury_status.upper() not in ['OUT']:
            return 0.0  # Only count OUT as injured
        
        try:
            team_name = self.team_mapping.get(team_abbr)
            if not team_name or team_name not in self.player_grades:
                # Fallback to position-based penalty
                return self._get_fallback_penalty(position)
            
            team_players = self.player_grades[team_name]
            if position not in team_players:
                return self._get_fallback_penalty(position)
            
            # Find player grade
            player_grade = None
            for player, grade in team_players[position].items():
                if player_name.lower() in player.lower() or player.lower() in player_name.lower():
                    player_grade = grade
                    break
            
            if player_grade is None:
                return self._get_fallback_penalty(position)
            
            # Calculate dynamic penalty based on PFF grade
            base_penalty = self._get_base_penalty(position)
            grade_multiplier = player_grade / 100.0  # Convert to 0-1 scale
            
            # Higher graded players = higher penalty
            dynamic_penalty = base_penalty * grade_multiplier * 2.0  # Scale factor
            
            logger.info(f"{team_abbr} {player_name} ({position}) - PFF Grade: {player_grade:.1f}, Penalty: {dynamic_penalty:.1f}")
            
            return dynamic_penalty
            
        except Exception as e:
            logger.error(f"Error calculating dynamic injury penalty: {e}")
            return self._get_fallback_penalty(position)
    
    def _get_fallback_penalty(self, position: str) -> float:
        """Fallback penalty when PFF data unavailable"""
        fallback_penalties = {
            'QB': -20.0,
            'RB': -12.0,
            'WR': -12.0,
            'TE': -10.0,
            'OT': -8.0,
            'OG': -7.0,
            'C': -7.0,
            'DE': -7.0,
            'DT': -7.0,
            'LB': -7.0,
            'CB': -7.0,
            'S': -7.0,
            'K': -3.0,
            'P': -2.0,
            'LS': -1.0
        }
        return fallback_penalties.get(position, -5.0)
    
    def _get_base_penalty(self, position: str) -> float:
        """Base penalty by position"""
        base_penalties = {
            'QB': -30.0,    # Higher base for QB
            'RB': -15.0,
            'WR': -15.0,
            'TE': -12.0,
            'OT': -10.0,
            'OG': -8.0,
            'C': -8.0,
            'DE': -10.0,
            'DT': -8.0,
            'LB': -8.0,
            'CB': -10.0,
            'S': -8.0,
            'K': -4.0,
            'P': -3.0,
            'LS': -2.0
        }
        return base_penalties.get(position, -6.0)
    
    def get_team_offensive_efficiency(self, team_abbr: str) -> Dict:
        """
        Get team offensive efficiency metrics from PFF data
        """
        team_name = self.team_mapping.get(team_abbr)
        if not team_name or team_name not in self.team_grades:
            return {}
        
        team_data = self.team_grades[team_name]
        return {
            'overall_offense': team_data.get('offense', {}).get('overall', 0),
            'passing': team_data.get('offense', {}).get('passing', 0),
            'rushing': team_data.get('offense', {}).get('rushing', 0),
            'receiving': team_data.get('offense', {}).get('receiving', 0),
            'pass_blocking': team_data.get('offense', {}).get('pass_blocking', 0),
            'run_blocking': team_data.get('offense', {}).get('run_blocking', 0)
        }
    
    def get_team_defensive_efficiency(self, team_abbr: str) -> Dict:
        """
        Get team defensive efficiency metrics from PFF data
        """
        team_name = self.team_mapping.get(team_abbr)
        if not team_name or team_name not in self.team_grades:
            return {}
        
        team_data = self.team_grades[team_name]
        return {
            'overall_defense': team_data.get('defense', {}).get('overall', 0),
            'pass_rush': team_data.get('defense', {}).get('pass_rush', 0),
            'run_defense': team_data.get('defense', {}).get('run_defense', 0),
            'coverage': team_data.get('defense', {}).get('coverage', 0),
            'tackling': team_data.get('defense', {}).get('tackling', 0)
        }
    
    def analyze_matchup_advantages(self, home_team: str, away_team: str) -> Dict:
        """
        Analyze matchup advantages using PFF data
        """
        home_offense = self.get_team_offensive_efficiency(home_team)
        home_defense = self.get_team_defensive_efficiency(home_team)
        away_offense = self.get_team_offensive_efficiency(away_team)
        away_defense = self.get_team_defensive_efficiency(away_team)
        
        if not all([home_offense, home_defense, away_offense, away_defense]):
            return {}
        
        # Calculate matchup advantages
        home_pass_advantage = home_offense['passing'] - away_defense['coverage']
        home_rush_advantage = home_offense['rushing'] - away_defense['run_defense']
        away_pass_advantage = away_offense['passing'] - home_defense['coverage']
        away_rush_advantage = away_offense['rushing'] - home_defense['run_defense']
        
        return {
            'home_pass_advantage': home_pass_advantage,
            'home_rush_advantage': home_rush_advantage,
            'away_pass_advantage': away_pass_advantage,
            'away_rush_advantage': away_rush_advantage,
            'home_overall_advantage': (home_pass_advantage + home_rush_advantage) / 2,
            'away_overall_advantage': (away_pass_advantage + away_rush_advantage) / 2
        }
    
    def get_player_matchup_analysis(self, team_abbr: str, position: str) -> Dict:
        """
        Get player-specific matchup analysis
        """
        team_name = self.team_mapping.get(team_abbr)
        if not team_name or team_name not in self.player_grades:
            return {}
        
        team_players = self.player_grades[team_name]
        if position not in team_players:
            return {}
        
        players = team_players[position]
        
        # Calculate position group strength
        if players:
            avg_grade = sum(players.values()) / len(players)
            top_player = max(players.items(), key=lambda x: x[1])
            return {
                'average_grade': avg_grade,
                'top_player': top_player[0],
                'top_grade': top_player[1],
                'depth_score': len(players),
                'position_strength': avg_grade * len(players) / 10  # Normalized strength
            }
        
        return {}
    
    def update_data(self):
        """Update PFF data if needed"""
        if (self.last_update is None or 
            datetime.now() - self.last_update > timedelta(seconds=self.update_frequency)):
            self.scrape_team_grades()
            self.scrape_player_grades()

if __name__ == "__main__":
    # Test the PFF data system
    pff_system = PFFDataSystem()
    
    print("🔍 Testing PFF Data System")
    print("=" * 50)
    
    # Test team grades
    team_grades = pff_system.scrape_team_grades()
    print(f"Loaded team grades for {len(team_grades)} teams")
    
    # Test player grades
    player_grades = pff_system.scrape_player_grades()
    print(f"Loaded player grades for {len(player_grades)} teams")
    
    # Test dynamic injury penalty
    print("\n🏥 Testing Dynamic Injury Penalty:")
    test_cases = [
        ("Josh Allen", "QB", "BUF", "OUT"),
        ("Stefon Diggs", "WR", "BUF", "OUT"),
        ("Matt Milano", "LB", "BUF", "OUT"),
        ("Tua Tagovailoa", "QB", "MIA", "OUT"),
        ("Tyreek Hill", "WR", "MIA", "OUT")
    ]
    
    for player, position, team, status in test_cases:
        penalty = pff_system.calculate_dynamic_injury_penalty(player, position, team, status)
        print(f"   {player} ({position}) - {team}: {penalty:.1f} points")
    
    # Test matchup analysis
    print("\n🎯 Testing Matchup Analysis:")
    matchup = pff_system.analyze_matchup_advantages("BUF", "MIA")
    if matchup:
        print(f"   BUF vs MIA:")
        print(f"   Home Pass Advantage: {matchup['home_pass_advantage']:.1f}")
        print(f"   Home Rush Advantage: {matchup['home_rush_advantage']:.1f}")
        print(f"   Away Pass Advantage: {matchup['away_pass_advantage']:.1f}")
        print(f"   Away Rush Advantage: {matchup['away_rush_advantage']:.1f}")
