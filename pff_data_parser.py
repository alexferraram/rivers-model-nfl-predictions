"""
PFF Data Parser - Reads manually exported PFF data
This parser can handle CSV and JSON formats from manual exports
"""

import pandas as pd
import json
import logging
from typing import Dict, Optional
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PFFDataParser:
    """
    Parser for manually exported PFF data
    """
    
    def __init__(self):
        self.team_grades = {}
        
        # Team name mapping for consistency
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
    
    def parse_data_file(self, file_path: str) -> Dict:
        """
        Parse data from CSV or JSON file
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return self._get_fallback_data()
            
            if file_path.endswith('.csv'):
                return self._parse_csv_file(file_path)
            elif file_path.endswith('.json'):
                return self._parse_json_file(file_path)
            else:
                logger.error(f"Unsupported file format: {file_path}")
                return self._get_fallback_data()
                
        except Exception as e:
            logger.error(f"Failed to parse data file: {e}")
            return self._get_fallback_data()
    
    def _parse_csv_file(self, file_path: str) -> Dict:
        """
        Parse CSV file with PFF data
        """
        try:
            logger.info(f"📊 Parsing CSV file: {file_path}")
            
            # Read CSV file
            df = pd.read_csv(file_path)
            logger.info(f"✅ Loaded CSV with {len(df)} rows and columns: {list(df.columns)}")
            
            team_data = {}
            
            for _, row in df.iterrows():
                # Get team name (try different column names)
                team_name = None
                for col in ['Team Name', 'Team', 'team', 'team_name']:
                    if col in df.columns:
                        team_name = row[col]
                        break
                
                if not team_name or pd.isna(team_name):
                    logger.warning(f"Skipping row with no team name: {row}")
                    continue
                
                # Clean team name
                team_name = str(team_name).strip()
                
                # Extract grades (try different column names)
                grades = self._extract_grades_from_row(row, df.columns)
                
                if grades:
                    team_data[team_name] = grades
                    logger.info(f"✅ Parsed data for {team_name}")
                else:
                    logger.warning(f"⚠️ No valid grades found for {team_name}")
            
            logger.info(f"✅ Successfully parsed {len(team_data)} teams from CSV")
            return team_data
            
        except Exception as e:
            logger.error(f"CSV parsing failed: {e}")
            return self._get_fallback_data()
    
    def _parse_json_file(self, file_path: str) -> Dict:
        """
        Parse JSON file with PFF data
        """
        try:
            logger.info(f"📊 Parsing JSON file: {file_path}")
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            logger.info(f"✅ Loaded JSON with {len(data)} teams")
            
            # Validate and clean the data
            team_data = {}
            for team_name, team_grades in data.items():
                if isinstance(team_grades, dict):
                    # Clean team name
                    clean_name = str(team_name).strip()
                    
                    # Validate grades
                    validated_grades = self._validate_grades(team_grades)
                    
                    if validated_grades:
                        team_data[clean_name] = validated_grades
                        logger.info(f"✅ Parsed data for {clean_name}")
                    else:
                        logger.warning(f"⚠️ Invalid grades for {clean_name}")
            
            logger.info(f"✅ Successfully parsed {len(team_data)} teams from JSON")
            return team_data
            
        except Exception as e:
            logger.error(f"JSON parsing failed: {e}")
            return self._get_fallback_data()
    
    def _extract_grades_from_row(self, row: pd.Series, columns: list) -> Optional[Dict]:
        """
        Extract grades from a CSV row
        """
        try:
            # Map column names to grade types - Updated for your specific CSV format
            grade_mapping = {
                'overall': ['OVER', 'Overall', 'overall', 'Overall Grade'],
                'offense_overall': ['OFF', 'Offense', 'offense', 'Offense Overall', 'offense_overall'],
                'passing': ['PASS', 'Passing', 'passing', 'Pass Grade'],
                'pass_blocking': ['PBLK', 'Pass Blocking', 'pass_blocking', 'Pass Block', 'pass_block'],
                'receiving': ['RECV', 'Receiving', 'receiving', 'Receive Grade'],
                'rushing': ['RUN', 'Rushing', 'rushing', 'Rush Grade'],
                'run_blocking': ['RBLK', 'Run Blocking', 'run_blocking', 'Run Block', 'run_block'],
                'defense_overall': ['DEF', 'Defense', 'defense', 'Defense Overall', 'defense_overall'],
                'run_defense': ['RDEF', 'Run Defense', 'run_defense', 'Run Def'],
                'tackling': ['TACK', 'Tackling', 'tackling', 'Tackle Grade'],
                'pass_rush': ['PRSH', 'Pass Rush', 'pass_rush', 'Pass Rush Grade'],
                'coverage': ['COV', 'Coverage', 'coverage', 'Coverage Grade'],
                'special_teams': ['SPEC', 'Special Teams', 'special_teams', 'Special Teams Grade', 'ST']
            }
            
            grades = {}
            
            for grade_type, possible_columns in grade_mapping.items():
                value = None
                
                # Try to find the value in any of the possible columns
                for col in possible_columns:
                    if col in columns:
                        val = row[col]
                        if not pd.isna(val):
                            try:
                                value = float(val)
                                break
                            except (ValueError, TypeError):
                                continue
                
                # Use default if not found
                grades[grade_type] = value if value is not None else 70.0
            
            return grades
            
        except Exception as e:
            logger.error(f"Failed to extract grades from row: {e}")
            return None
    
    def _validate_grades(self, grades: Dict) -> Optional[Dict]:
        """
        Validate and clean grade data
        """
        try:
            validated = {}
            
            # Required grade types
            required_grades = [
                'overall', 'offense_overall', 'passing', 'pass_blocking',
                'receiving', 'rushing', 'run_blocking', 'defense_overall',
                'run_defense', 'tackling', 'pass_rush', 'coverage', 'special_teams'
            ]
            
            for grade_type in required_grades:
                value = grades.get(grade_type, 70.0)
                
                # Convert to float and validate range
                try:
                    float_value = float(value)
                    if 0 <= float_value <= 100:
                        validated[grade_type] = float_value
                    else:
                        logger.warning(f"Grade {grade_type} out of range: {float_value}")
                        validated[grade_type] = 70.0
                except (ValueError, TypeError):
                    logger.warning(f"Invalid grade value for {grade_type}: {value}")
                    validated[grade_type] = 70.0
            
            return validated
            
        except Exception as e:
            logger.error(f"Grade validation failed: {e}")
            return None
    
    def convert_to_nested_format(self, flat_data: Dict) -> Dict:
        """
        Convert flat data structure to nested format for compatibility
        """
        nested_data = {}
        
        for team_name, team_data in flat_data.items():
            nested_data[team_name] = {
                'overall': team_data.get('overall', 70.0),
                'offense': {
                    'overall': team_data.get('offense_overall', 70.0),
                    'passing': team_data.get('passing', 70.0),
                    'pass_blocking': team_data.get('pass_blocking', 70.0),
                    'receiving': team_data.get('receiving', 70.0),
                    'rushing': team_data.get('rushing', 70.0),
                    'run_blocking': team_data.get('run_blocking', 70.0)
                },
                'defense': {
                    'overall': team_data.get('defense_overall', 70.0),
                    'run_defense': team_data.get('run_defense', 70.0),
                    'tackling': team_data.get('tackling', 70.0),
                    'pass_rush': team_data.get('pass_rush', 70.0),
                    'coverage': team_data.get('coverage', 70.0)
                },
                'special_teams': {
                    'overall': team_data.get('special_teams', 70.0)
                }
            }
        
        return nested_data
    
    def _get_fallback_data(self) -> Dict:
        """
        Get fallback data when parsing fails
        """
        logger.info("📊 Using fallback data")
        
        # Return minimal data structure for all teams
        fallback_data = {}
        
        all_teams = [
            'Arizona Cardinals', 'Atlanta Falcons', 'Baltimore Ravens', 'Buffalo Bills',
            'Carolina Panthers', 'Chicago Bears', 'Cincinnati Bengals', 'Cleveland Browns',
            'Dallas Cowboys', 'Denver Broncos', 'Detroit Lions', 'Green Bay Packers',
            'Houston Texans', 'Indianapolis Colts', 'Jacksonville Jaguars', 'Kansas City Chiefs',
            'Las Vegas Raiders', 'Los Angeles Chargers', 'Los Angeles Rams', 'Miami Dolphins',
            'Minnesota Vikings', 'New England Patriots', 'New Orleans Saints', 'New York Giants',
            'New York Jets', 'Philadelphia Eagles', 'Pittsburgh Steelers', 'San Francisco 49ers',
            'Seattle Seahawks', 'Tampa Bay Buccaneers', 'Tennessee Titans', 'Washington Commanders'
        ]
        
        for team in all_teams:
            fallback_data[team] = {
                'overall': 70.0,
                'offense_overall': 70.0,
                'passing': 70.0,
                'pass_blocking': 70.0,
                'receiving': 70.0,
                'rushing': 70.0,
                'run_blocking': 70.0,
                'defense_overall': 70.0,
                'run_defense': 70.0,
                'tackling': 70.0,
                'pass_rush': 70.0,
                'coverage': 70.0,
                'special_teams': 70.0
            }
        
        return fallback_data
    
    def save_parsed_data(self, data: Dict, output_file: str):
        """
        Save parsed data to a file
        """
        try:
            if output_file.endswith('.json'):
                with open(output_file, 'w') as f:
                    json.dump(data, f, indent=2)
            elif output_file.endswith('.csv'):
                # Convert to DataFrame and save
                rows = []
                for team_name, grades in data.items():
                    row = {'Team': team_name}
                    row.update(grades)
                    rows.append(row)
                
                df = pd.DataFrame(rows)
                df.to_csv(output_file, index=False)
            
            logger.info(f"✅ Saved parsed data to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save parsed data: {e}")

if __name__ == "__main__":
    # Test the parser
    parser = PFFDataParser()
    
    print("🚀 TESTING PFF DATA PARSER")
    print("=" * 50)
    
    # Test with your actual CSV file
    csv_file = "Week 3 PFF Team Scores.csv"
    
    if os.path.exists(csv_file):
        print(f"📊 Testing CSV parsing: {csv_file}")
        csv_data = parser.parse_data_file(csv_file)
        print(f"✅ CSV parsing result: {len(csv_data)} teams")
        
        # Convert to nested format
        nested_csv = parser.convert_to_nested_format(csv_data)
        print(f"✅ Nested format: {len(nested_csv)} teams")
        
        # Show ALL PFF scores for each team
        print("\n📊 ALL PFF SCORES EXTRACTED:")
        print("=" * 80)
        for team_name, data in nested_csv.items():
            print(f"\n{team_name}:")
            print(f"  Overall: {data['overall']}")
            print(f"  Offense Overall: {data['offense']['overall']}")
            print(f"  Passing: {data['offense']['passing']}")
            print(f"  Pass Blocking: {data['offense']['pass_blocking']}")
            print(f"  Receiving: {data['offense']['receiving']}")
            print(f"  Rushing: {data['offense']['rushing']}")
            print(f"  Run Blocking: {data['offense']['run_blocking']}")
            print(f"  Defense Overall: {data['defense']['overall']}")
            print(f"  Run Defense: {data['defense']['run_defense']}")
            print(f"  Tackling: {data['defense']['tackling']}")
            print(f"  Pass Rush: {data['defense']['pass_rush']}")
            print(f"  Coverage: {data['defense']['coverage']}")
            print(f"  Special Teams: {data['special_teams']['overall']}")
            print("-" * 40)
    
    print("\n✅ Parser testing completed!")
