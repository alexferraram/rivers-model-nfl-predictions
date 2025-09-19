import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DynamicInjuryTracker:
    """
    Dynamic injury tracking system that monitors injury reports
    and adjusts team scores based on player availability
    """
    
    def __init__(self):
        self.injury_data = {}
        self.last_update = None
        self.update_frequency = 3600  # Update every hour
        
        # Injury impact weights
        self.injury_impacts = {
            'QB': -20,           # Quarterback (critical)
            'WR1': -12,          # Top wide receiver
            'RB1': -12,          # Starting running back
            'TE1': -10,          # Top tight end
            'OL_STARTER': -7,    # Offensive line starter
            'DEF_STARTER': -7,   # Defensive starter
            'K': -3,             # Kicker
            'P': -3,             # Punter
            'RETURNER': -2       # Return specialist
        }
        
        # Team depth charts (simplified)
        self.depth_charts = {
            'QB': ['QB1', 'QB2', 'QB3'],
            'WR': ['WR1', 'WR2', 'WR3', 'WR4', 'WR5'],
            'RB': ['RB1', 'RB2', 'RB3'],
            'TE': ['TE1', 'TE2', 'TE3'],
            'OL': ['LT', 'LG', 'C', 'RG', 'RT'],
            'DEF': ['DE1', 'DE2', 'DT1', 'DT2', 'LB1', 'LB2', 'LB3', 'CB1', 'CB2', 'S1', 'S2'],
            'SPECIAL': ['K', 'P', 'LS']
        }
    
    def scrape_cbs_injuries(self):
        """
        Scrape injury data from CBS Sports NFL injuries page
        """
        try:
            url = "https://www.cbssports.com/nfl/injuries/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse injury data from CBS Sports
            injury_data = {}
            
            # Find team sections - CBS uses specific structure
            team_sections = soup.find_all('div', class_=lambda x: x and 'team' in x.lower())
            
            # Alternative: look for tables with injury data
            injury_tables = soup.find_all('table')
            
            for i, table in enumerate(injury_tables):
                team_name = self._extract_cbs_team_name(table, i)
                if team_name:
                    injuries = self._parse_cbs_injury_table(table)
                    if injuries:  # Only add if we found injuries
                        injury_data[team_name] = injuries
            
            self.injury_data = injury_data
            self.last_update = datetime.now()
            
            logger.info(f"Successfully scraped CBS injury data for {len(injury_data)} teams")
            return injury_data
            
        except Exception as e:
            logger.error(f"Error scraping CBS injuries: {e}")
            # Fallback to mock data if scraping fails
            return self._get_fallback_injury_data()
    
    def _get_fallback_injury_data(self):
        """Fallback injury data if CBS scraping fails"""
        mock_injury_data = {
            'Buffalo Bills': [
                {'player': 'Josh Allen', 'position': 'QB', 'status': 'Questionable', 'return_date': 'Sep 22', 'comment': 'Shoulder injury'},
                {'player': 'Stefon Diggs', 'position': 'WR', 'status': 'Probable', 'return_date': 'Sep 22', 'comment': 'Minor ankle'}
            ],
            'Miami Dolphins': [
                {'player': 'Tua Tagovailoa', 'position': 'QB', 'status': 'Probable', 'return_date': 'Sep 22', 'comment': 'Concussion protocol'},
                {'player': 'Tyreek Hill', 'position': 'WR', 'status': 'Questionable', 'return_date': 'Sep 22', 'comment': 'Hamstring'}
            ],
            'Philadelphia Eagles': [
                {'player': 'Jalen Hurts', 'position': 'QB', 'status': 'Probable', 'return_date': 'Sep 22', 'comment': 'Knee soreness'},
                {'player': 'A.J. Brown', 'position': 'WR', 'status': 'Questionable', 'return_date': 'Sep 22', 'comment': 'Back injury'}
            ],
            'Los Angeles Rams': [
                {'player': 'Matthew Stafford', 'position': 'QB', 'status': 'Probable', 'return_date': 'Sep 22', 'comment': 'Thumb injury'},
                {'player': 'Cooper Kupp', 'position': 'WR', 'status': 'Questionable', 'return_date': 'Sep 22', 'comment': 'Ankle sprain'}
            ]
        }
        
        self.injury_data = mock_injury_data
        self.last_update = datetime.now()
        
        logger.info(f"Using fallback injury data for {len(mock_injury_data)} teams")
        return mock_injury_data
    
    def _extract_team_name(self, table):
        """Extract team name from injury table"""
        try:
            # Look for team name in various elements before the table
            team_elements = table.find_previous(['h2', 'h3', 'h4', 'div'])
            if team_elements:
                team_text = team_elements.get_text().strip()
                # Extract team name from the text (usually the first part)
                team_name = team_text.split('\n')[0].strip()
                if team_name and len(team_name) > 3:  # Valid team name
                    return team_name
            
            # Alternative: look for team name in table's parent container
            parent = table.find_parent(['div', 'section'])
            if parent:
                team_header = parent.find(['h2', 'h3', 'h4'])
                if team_header:
                    return team_header.get_text().strip()
        except Exception as e:
            logger.debug(f"Error extracting team name: {e}")
        
        return None
    
    def _extract_cbs_team_name(self, table, table_index=None):
        """Extract team name from CBS Sports injury table"""
        try:
            # CBS Sports structure analysis - try multiple approaches
            
            # Approach 1: Use provided table index (most reliable)
            if table_index is not None:
                team_name = self._get_team_by_index(table_index)
                if team_name:
                    return team_name
            
            # Approach 2: Look for team name in table's data
            # Check if any player names suggest a team
            rows = table.find_all('tr')[1:]  # Skip header
            if rows:
                first_row = rows[0]
                cells = first_row.find_all(['td', 'th'])
                if cells:
                    player_name = cells[0].get_text().strip()
                    # Extract team from player context or use a mapping
                    team_name = self._infer_team_from_player(player_name)
                    if team_name:
                        return team_name
            
            # Approach 3: Look for team name in table context
            # Check table caption
            caption = table.find('caption')
            if caption:
                team_text = caption.get_text().strip()
                if team_text and len(team_text) > 3:
                    return team_text
            
            # Approach 4: Look in parent elements
            parent = table.find_parent(['div', 'section'])
            if parent:
                # Look for team indicators in parent text
                parent_text = parent.get_text()
                team_name = self._extract_team_from_text(parent_text)
                if team_name:
                    return team_name
            
            # Approach 5: Fallback - use hash-based team assignment
            return f"Team {hash(str(table)) % 32 + 1}"
                    
        except Exception as e:
            logger.debug(f"Error extracting CBS team name: {e}")
        
        return None
    
    def _infer_team_from_player(self, player_name):
        """Infer team from player name (if we have known players)"""
        # This is a fallback method - in practice, we'd need a database of players
        # For now, return None and rely on other methods
        return None
    
    def _extract_team_from_text(self, text):
        """Extract team name from text"""
        # Look for team name patterns
        team_patterns = [
            'Buffalo Bills', 'Miami Dolphins', 'Philadelphia Eagles', 'Los Angeles Rams',
            'Arizona Cardinals', 'Atlanta Falcons', 'Carolina Panthers', 'Chicago Bears',
            'Dallas Cowboys', 'Detroit Lions', 'Green Bay Packers', 'Houston Texans',
            'Indianapolis Colts', 'Jacksonville Jaguars', 'Kansas City Chiefs',
            'Las Vegas Raiders', 'Los Angeles Chargers', 'Minnesota Vikings',
            'New England Patriots', 'New Orleans Saints', 'New York Giants',
            'New York Jets', 'San Francisco 49ers', 'Seattle Seahawks',
            'Tampa Bay Buccaneers', 'Tennessee Titans', 'Washington Commanders'
        ]
        
        for team in team_patterns:
            if team in text:
                return team
        
        return None
    
    def _get_team_by_index(self, index):
        """Get team name by table index (32 teams in order)"""
        teams = [
            'Arizona Cardinals', 'Atlanta Falcons', 'Baltimore Ravens', 'Buffalo Bills',
            'Carolina Panthers', 'Chicago Bears', 'Cincinnati Bengals', 'Cleveland Browns',
            'Dallas Cowboys', 'Denver Broncos', 'Detroit Lions', 'Green Bay Packers',
            'Houston Texans', 'Indianapolis Colts', 'Jacksonville Jaguars', 'Kansas City Chiefs',
            'Las Vegas Raiders', 'Los Angeles Chargers', 'Los Angeles Rams', 'Miami Dolphins',
            'Minnesota Vikings', 'New England Patriots', 'New Orleans Saints', 'New York Giants',
            'New York Jets', 'Philadelphia Eagles', 'Pittsburgh Steelers', 'San Francisco 49ers',
            'Seattle Seahawks', 'Tampa Bay Buccaneers', 'Tennessee Titans', 'Washington Commanders'
        ]
        
        if 0 <= index < len(teams):
            return teams[index]
        
        return None
    
    def _parse_cbs_injury_table(self, table):
        """Parse CBS Sports injury table"""
        injuries = []
        try:
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 4:  # CBS has: Player, Position, Updated, Injury, Injury Status
                    player_name = cells[0].get_text().strip()
                    position = cells[1].get_text().strip()
                    updated_date = cells[2].get_text().strip()
                    injury_type = cells[3].get_text().strip()
                    injury_status = cells[4].get_text().strip() if len(cells) > 4 else ""
                    
                    # Only include significant injuries
                    if injury_status and any(status in injury_status.upper() for status in ['OUT', 'DOUBTFUL', 'QUESTIONABLE', 'IR', 'INJURED RESERVE']):
                        injuries.append({
                            'player': player_name,
                            'position': position,
                            'status': injury_status,
                            'injury_type': injury_type,
                            'updated_date': updated_date,
                            'timestamp': datetime.now()
                        })
        except Exception as e:
            logger.error(f"Error parsing CBS injury table: {e}")
        
        return injuries
    
    def _parse_injury_table(self, table):
        """Parse individual injury table"""
        injuries = []
        try:
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 4:  # ESPN has 5 columns: NAME, POS, EST. RETURN DATE, STATUS, COMMENT
                    player_name = cells[0].get_text().strip()
                    position = cells[1].get_text().strip()
                    return_date = cells[2].get_text().strip()
                    injury_status = cells[3].get_text().strip()
                    comment = cells[4].get_text().strip() if len(cells) > 4 else ""
                    
                    # Only include significant injuries
                    if injury_status and injury_status.upper() in ['OUT', 'DOUBTFUL', 'QUESTIONABLE', 'INJURED RESERVE']:
                        injuries.append({
                            'player': player_name,
                            'position': position,
                            'status': injury_status,
                            'return_date': return_date,
                            'comment': comment,
                            'timestamp': datetime.now()
                        })
        except Exception as e:
            logger.error(f"Error parsing injury table: {e}")
        
        return injuries
    
    def get_injury_impact(self, team_abbr, position_type=None):
        """
        Calculate injury impact for a team
        
        Args:
            team_abbr: Team abbreviation (e.g., 'BUF', 'MIA')
            position_type: Specific position to check (optional)
        
        Returns:
            Total injury impact points (negative number)
        """
        if not self.injury_data:
            self.scrape_cbs_injuries()
        
        team_name = self._get_team_full_name(team_abbr)
        if team_name not in self.injury_data:
            return 0
        
        total_impact = 0
        injuries = self.injury_data[team_name]
        
        for injury in injuries:
            player = injury['player']
            position = injury['position']
            status = injury['status'].upper()
            
            # Skip if not a significant injury (only skip PROBABLE, keep QUESTIONABLE)
            if status in ['PROBABLE']:
                continue
            
            # Determine injury impact based on position and status
            impact = self._calculate_player_impact(position, status)
            total_impact += impact
            
            logger.info(f"{team_abbr} {player} ({position}) - {status}: {impact} points")
        
        return total_impact
    
    def _calculate_player_impact(self, position, status):
        """Calculate impact for individual player injury"""
        position = position.upper()
        
        # Map positions to impact categories
        if position in ['QB']:
            return self.injury_impacts['QB']
        elif position in ['WR']:
            return self.injury_impacts['WR1']
        elif position in ['RB']:
            return self.injury_impacts['RB1']
        elif position in ['TE']:
            return self.injury_impacts['TE1']
        elif position in ['LT', 'LG', 'C', 'RG', 'RT']:
            return self.injury_impacts['OL_STARTER']
        elif position in ['DE', 'DT', 'LB', 'CB', 'S']:
            return self.injury_impacts['DEF_STARTER']
        elif position in ['K']:
            return self.injury_impacts['K']
        elif position in ['P']:
            return self.injury_impacts['P']
        else:
            return 0
    
    def _get_team_full_name(self, team_abbr):
        """Convert team abbreviation to full name for ESPN"""
        team_mapping = {
            'BUF': 'Buffalo Bills',
            'MIA': 'Miami Dolphins',
            'NE': 'New England Patriots',
            'NYJ': 'New York Jets',
            'BAL': 'Baltimore Ravens',
            'CIN': 'Cincinnati Bengals',
            'CLE': 'Cleveland Browns',
            'PIT': 'Pittsburgh Steelers',
            'HOU': 'Houston Texans',
            'IND': 'Indianapolis Colts',
            'JAX': 'Jacksonville Jaguars',
            'TEN': 'Tennessee Titans',
            'DEN': 'Denver Broncos',
            'KC': 'Kansas City Chiefs',
            'LV': 'Las Vegas Raiders',
            'LAC': 'Los Angeles Chargers',
            'DAL': 'Dallas Cowboys',
            'NYG': 'New York Giants',
            'PHI': 'Philadelphia Eagles',
            'WAS': 'Washington Commanders',
            'CHI': 'Chicago Bears',
            'DET': 'Detroit Lions',
            'GB': 'Green Bay Packers',
            'MIN': 'Minnesota Vikings',
            'ATL': 'Atlanta Falcons',
            'CAR': 'Carolina Panthers',
            'NO': 'New Orleans Saints',
            'TB': 'Tampa Bay Buccaneers',
            'ARI': 'Arizona Cardinals',
            'LA': 'Los Angeles Rams',
            'SF': 'San Francisco 49ers',
            'SEA': 'Seattle Seahawks'
        }
        return team_mapping.get(team_abbr, team_abbr)
    
    def update_injury_data(self):
        """Update injury data if needed"""
        if (self.last_update is None or 
            datetime.now() - self.last_update > timedelta(seconds=self.update_frequency)):
            self.scrape_cbs_injuries()
    
    def get_team_injury_summary(self, team_abbr):
        """Get summary of team injuries"""
        self.update_injury_data()
        
        team_name = self._get_team_full_name(team_abbr)
        if team_name not in self.injury_data:
            return "No injury data available"
        
        injuries = self.injury_data[team_name]
        if not injuries:
            return "No current injuries"
        
        summary = f"Injury Report for {team_abbr}:\n"
        total_impact = 0
        
        for injury in injuries:
            impact = self._calculate_player_impact(injury['position'], injury['status'])
            total_impact += impact
            
            summary += f"  {injury['player']} ({injury['position']}) - {injury['status']} ({impact} pts)\n"
        
        summary += f"Total Impact: {total_impact} points"
        return summary
    
    def apply_injury_adjustments(self, home_team, away_team, home_score, away_score):
        """
        Apply injury adjustments to team scores
        
        Args:
            home_team: Home team abbreviation
            away_team: Away team abbreviation
            home_score: Original home team score
            away_score: Original away team score
        
        Returns:
            Tuple of (adjusted_home_score, adjusted_away_score)
        """
        self.update_injury_data()
        
        home_impact = self.get_injury_impact(home_team)
        away_impact = self.get_injury_impact(away_team)
        
        adjusted_home_score = home_score + home_impact
        adjusted_away_score = away_score + away_impact
        
        logger.info(f"Injury adjustments: {home_team} {home_impact:+.1f}, {away_team} {away_impact:+.1f}")
        
        return adjusted_home_score, adjusted_away_score

def main():
    """Test the injury tracker"""
    tracker = DynamicInjuryTracker()
    
    # Test with a few teams
    test_teams = ['BUF', 'MIA', 'PHI', 'LA']
    
    for team in test_teams:
        print(f"\n{tracker.get_team_injury_summary(team)}")
    
    # Test injury impact calculation
    print(f"\nInjury Impact Test:")
    for team in test_teams:
        impact = tracker.get_injury_impact(team)
        print(f"{team}: {impact} points")

if __name__ == "__main__":
    main()

