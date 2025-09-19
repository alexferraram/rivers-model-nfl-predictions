#!/usr/bin/env python3
"""
Manual Injury Input System
Allows manual input of injury data when automatic scraping isn't available.
"""

import pandas as pd
import numpy as np
import nfl_data_py as nfl
import joblib
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ManualInjuryInputSystem:
    """System for manual injury data input and assessment"""
    
    def __init__(self, model_path='models/real_nfl_model.pkl'):
        """Initialize manual injury input system"""
        self.model_path = model_path
        self.model = None
        self.feature_names = None
        self.pbp_2025 = None
        self.depth_charts = None
        self.load_model()
        self.load_data()
        self.setup_injury_system()
    
    def load_model(self):
        """Load the trained model"""
        try:
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.feature_names = model_data['feature_names']
            logger.info(f"✅ Model loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
    
    def load_data(self):
        """Load NFL data"""
        logger.info("Loading NFL data...")
        try:
            self.pbp_2025 = nfl.import_pbp_data([2025])
            self.depth_charts = nfl.import_depth_charts([2025])
            logger.info(f"✅ Loaded {len(self.pbp_2025)} plays from 2025 season")
            logger.info(f"✅ Loaded {len(self.depth_charts)} depth chart records")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.pbp_2025 = None
            self.depth_charts = None
    
    def setup_injury_system(self):
        """Setup injury impact system"""
        self.injury_impacts = {
            'OUT': 0.70,           # Player out - 30% reduction
            'DOUBTFUL': 0.80,     # Player doubtful - 20% reduction
            'QUESTIONABLE': 0.90, # Player questionable - 10% reduction
            'PROBABLE': 0.95,     # Player probable - 5% reduction
            'HEALTHY': 1.0,       # Player healthy - no reduction
        }
        
        # Position-specific impacts
        self.position_impacts = {
            'QB': 0.95,    # QB injuries have highest impact
            'RB': 0.90,    # RB injuries moderate impact
            'WR': 0.95,    # WR injuries moderate impact
            'TE': 0.95,    # TE injuries moderate impact
            'OL': 0.90,    # OL injuries moderate impact
            'DL': 0.90,    # DL injuries moderate impact
            'LB': 0.90,    # LB injuries moderate impact
            'DB': 0.90,    # DB injuries moderate impact
            'K': 0.95,     # Kicker injuries low impact
            'P': 0.95,     # Punter injuries low impact
        }
    
    def get_team_depth_chart(self, team):
        """Get team's depth chart"""
        if self.depth_charts is None:
            return pd.DataFrame()
        
        team_depth = self.depth_charts[self.depth_charts['team'] == team].copy()
        return team_depth
    
    def display_team_depth_chart(self, team):
        """Display team's depth chart for injury input"""
        depth_chart = self.get_team_depth_chart(team)
        
        if depth_chart.empty:
            print(f"❌ No depth chart data available for {team}")
            return
        
        print(f"\n📋 {team} DEPTH CHART:")
        print("=" * 50)
        
        # Group by position
        for pos_abb in sorted(depth_chart['pos_abb'].unique()):
            pos_players = depth_chart[depth_chart['pos_abb'] == pos_abb].sort_values('pos_rank')
            
            print(f"\n{pos_abb} Position:")
            print("-" * 20)
            
            for _, player in pos_players.iterrows():
                rank = player['pos_rank']
                name = player['player_name']
                print(f"  {rank}. {name}")
    
    def input_team_injuries(self, team):
        """Interactive injury input for a team"""
        print(f"\n🏥 INJURY INPUT FOR {team}")
        print("=" * 40)
        
        # Display depth chart
        self.display_team_depth_chart(team)
        
        injuries = {}
        
        print(f"\n📝 Enter injuries for {team} (press Enter to skip):")
        print("Format: Player Name, Status (OUT/DOUBTFUL/QUESTIONABLE/PROBABLE/HEALTHY)")
        print("Example: Josh Allen, OUT")
        print("Example: Stefon Diggs, QUESTIONABLE")
        print()
        
        while True:
            injury_input = input(f"Enter injury for {team} (or 'done' to finish): ").strip()
            
            if injury_input.lower() == 'done':
                break
            
            if not injury_input:
                continue
            
            try:
                player_name, status = injury_input.split(',')
                player_name = player_name.strip()
                status = status.strip().upper()
                
                if status in self.injury_impacts:
                    injuries[player_name] = status
                    print(f"✅ Added: {player_name} - {status}")
                else:
                    print(f"❌ Invalid status: {status}. Use: OUT, DOUBTFUL, QUESTIONABLE, PROBABLE, HEALTHY")
            
            except ValueError:
                print("❌ Invalid format. Use: Player Name, Status")
        
        return injuries
    
    def assess_replacement_performance(self, team, position, starter_name):
        """Assess replacement player performance"""
        logger.info(f"🔍 Assessing replacement for {team} {position} (replacing {starter_name})")
        
        if self.depth_charts is None:
            return self._get_default_replacement_impact(position)
        
        # Get team depth chart
        team_depth = self.depth_charts[self.depth_charts['team'] == team]
        
        if team_depth.empty:
            return self._get_default_replacement_impact(position)
        
        # Find replacement player
        position_players = team_depth[team_depth['pos_abb'] == position].sort_values('pos_rank')
        
        if len(position_players) > 1:
            # Find the replacement (next player after starter)
            replacement_player = None
            for _, player in position_players.iterrows():
                if player['player_name'] != starter_name:
                    replacement_player = player['player_name']
                    break
            
            if replacement_player:
                logger.info(f"📊 Replacement player: {replacement_player}")
                
                # Get replacement player's performance
                replacement_stats = self._get_player_performance(replacement_player)
                
                if replacement_stats:
                    logger.info(f"📈 Replacement performance: {replacement_stats:.3f}")
                    return replacement_stats
                else:
                    logger.info("📊 No performance data available for replacement")
                    return self._get_default_replacement_impact(position)
            else:
                logger.info("❌ No replacement player found")
                return self._get_default_replacement_impact(position)
        else:
            logger.info("❌ No backup players available")
            return self._get_default_replacement_impact(position)
    
    def _get_player_performance(self, player_name):
        """Get individual player performance metrics"""
        if self.pbp_2025 is None:
            return None
        
        # Filter plays by player
        player_plays = self.pbp_2025[
            (self.pbp_2025['passer_player_name'] == player_name) |
            (self.pbp_2025['rusher_player_name'] == player_name) |
            (self.pbp_2025['receiver_player_name'] == player_name)
        ]
        
        if player_plays.empty:
            return None
        
        # Calculate performance metrics
        if 'passer_player_name' in player_plays.columns and player_plays['passer_player_name'].notna().any():
            # QB performance
            pass_plays = player_plays[player_plays['passer_player_name'] == player_name]
            if not pass_plays.empty:
                completion_rate = pass_plays['complete_pass'].mean()
                yards_per_attempt = pass_plays['passing_yards'].mean()
                td_rate = pass_plays['pass_touchdown'].sum() / len(pass_plays)
                int_rate = pass_plays['interception'].sum() / len(pass_plays)
                
                # Composite QB rating
                qb_rating = (completion_rate * 0.3 + 
                            (yards_per_attempt / 10) * 0.3 + 
                            td_rate * 0.2 + 
                            (1 - int_rate) * 0.2)
                return qb_rating
        
        # For other positions, use basic efficiency
        total_yards = player_plays['yards_gained'].sum()
        total_plays = len(player_plays)
        
        if total_plays > 0:
            return total_yards / total_plays
        else:
            return None
    
    def _get_default_replacement_impact(self, position):
        """Get default replacement impact based on position"""
        default_impacts = {
            'QB': 0.75,    # 25% reduction for backup QB
            'RB': 0.90,    # 10% reduction for backup RB
            'WR': 0.95,    # 5% reduction for backup WR
            'TE': 0.95,    # 5% reduction for backup TE
            'OL': 0.90,    # 10% reduction for backup OL
            'DL': 0.90,    # 10% reduction for backup DL
            'LB': 0.90,    # 10% reduction for backup LB
            'DB': 0.90,    # 10% reduction for backup DB
            'K': 0.95,     # 5% reduction for backup K
            'P': 0.95,     # 5% reduction for backup P
        }
        return default_impacts.get(position, 0.90)
    
    def get_injury_adjusted_stats(self, team, injuries):
        """Get team stats adjusted for injuries"""
        if self.pbp_2025 is None:
            return self._get_default_stats()
        
        team_games = self.pbp_2025[self.pbp_2025['posteam'] == team].copy()
        
        if team_games.empty:
            return self._get_default_stats()
        
        # Calculate base stats
        stats = {
            'yards_per_play': team_games['yards_gained'].mean(),
            'third_down_rate': len(team_games[(team_games['down'] == 3) & (team_games['first_down'] == 1)]) / max(len(team_games[team_games['down'] == 3]), 1),
            'redzone_rate': len(team_games[(team_games['yardline_100'] <= 20) & (team_games['touchdown'] == 1)]) / max(len(team_games[team_games['yardline_100'] <= 20]), 1),
            'turnovers_per_game': (team_games['interception'].sum() + team_games['fumble_lost'].sum()) / len(team_games['game_id'].unique()),
            'completion_rate': team_games[team_games['play_type'] == 'pass']['complete_pass'].mean(),
            'yards_per_pass': team_games[team_games['play_type'] == 'pass']['passing_yards'].mean(),
            'yards_per_rush': team_games[team_games['play_type'] == 'run']['rushing_yards'].mean()
        }
        
        # Apply injury adjustments
        for player_name, injury_status in injuries.items():
            if injury_status in self.injury_impacts:
                injury_multiplier = self.injury_impacts[injury_status]
                
                # Get player position
                player_position = self._get_player_position(player_name, team)
                
                if player_position:
                    # Adjust based on position and replacement performance
                    replacement_impact = self.assess_replacement_performance(team, player_position, player_name)
                    adjusted_multiplier = 1.0 - ((1.0 - injury_multiplier) * replacement_impact)
                    
                    # Apply position-specific adjustments
                    if player_position == 'QB':
                        stats['completion_rate'] *= adjusted_multiplier
                        stats['yards_per_pass'] *= adjusted_multiplier
                        stats['turnovers_per_game'] *= (2 - adjusted_multiplier)
                        stats['redzone_rate'] *= adjusted_multiplier
                    elif player_position == 'RB':
                        stats['yards_per_rush'] *= adjusted_multiplier
                        stats['redzone_rate'] *= adjusted_multiplier
                    elif player_position in ['WR', 'TE']:
                        stats['yards_per_pass'] *= adjusted_multiplier
                        stats['completion_rate'] *= adjusted_multiplier
                
                logger.info(f"📊 Applied injury adjustment for {player_name}: {injury_status} (multiplier: {adjusted_multiplier:.3f})")
        
        # Fill NaN values
        for key, value in stats.items():
            if pd.isna(value):
                stats[key] = self._get_default_stats()[key]
        
        return stats
    
    def _get_player_position(self, player_name, team):
        """Get player's position from depth chart"""
        if self.depth_charts is None:
            return None
        
        player_data = self.depth_charts[
            (self.depth_charts['player_name'] == player_name) & 
            (self.depth_charts['team'] == team)
        ]
        
        if not player_data.empty:
            return player_data.iloc[0]['pos_abb']
        else:
            return None
    
    def _get_default_stats(self):
        """Get default team statistics"""
        return {
            'yards_per_play': 5.5,
            'third_down_rate': 0.4,
            'redzone_rate': 0.6,
            'turnovers_per_game': 1.5,
            'completion_rate': 0.65,
            'yards_per_pass': 7.0,
            'yards_per_rush': 4.0
        }
    
    def predict_with_manual_injuries(self, home_team, away_team, 
                                   home_injuries=None, away_injuries=None):
        """Predict game with manually input injury data"""
        if not self.model:
            logger.error("Model not loaded")
            return {}
        
        logger.info(f"🏥 Manual injury prediction: {away_team} @ {home_team}")
        
        # Get injury-adjusted stats
        home_stats = self.get_injury_adjusted_stats(home_team, home_injuries or {})
        away_stats = self.get_injury_adjusted_stats(away_team, away_injuries or {})
        
        # Create feature vector
        features = {}
        for stat_name, home_value in home_stats.items():
            features[f'home_{stat_name}'] = home_value
        for stat_name, away_value in away_stats.items():
            features[f'away_{stat_name}'] = away_value
        
        # Convert to DataFrame
        X = pd.DataFrame([features])
        
        # Ensure all required features are present
        for feature in self.feature_names:
            if feature not in X.columns:
                X[feature] = 0
        
        # Reorder columns to match training data
        X = X[self.feature_names]
        
        # Make prediction
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        winner = home_team if prediction == 1 else away_team
        confidence = max(probabilities) * 100
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'predicted_winner': winner,
            'confidence': confidence,
            'home_win_probability': probabilities[1],
            'away_win_probability': probabilities[0],
            'home_stats': home_stats,
            'away_stats': away_stats,
            'home_injuries': home_injuries or {},
            'away_injuries': away_injuries or {},
            'injury_data_source': 'Manual Input',
            'replacement_analysis': 'Included'
        }

def main():
    """Main function for manual injury input"""
    logger.info("🏈 Manual Injury Input System Starting...")
    
    # Create manual injury input system
    system = ManualInjuryInputSystem()
    
    if not system.model:
        logger.error("Failed to load model. Exiting.")
        return
    
    # Example: MIA @ BUF with manual injury input
    home_team = 'BUF'
    away_team = 'MIA'
    
    print(f"\n🎯 MANUAL INJURY INPUT FOR {away_team} @ {home_team}")
    print("=" * 60)
    
    # Input injuries for both teams
    print("🏥 Enter injury information for both teams:")
    print("Status options: OUT, DOUBTFUL, QUESTIONABLE, PROBABLE, HEALTHY")
    print()
    
    # Get injuries for home team
    home_injuries = system.input_team_injuries(home_team)
    
    # Get injuries for away team
    away_injuries = system.input_team_injuries(away_team)
    
    # Make prediction with injuries
    prediction = system.predict_with_manual_injuries(
        home_team, away_team, home_injuries, away_injuries
    )
    
    print(f"\n🏆 PREDICTION WITH MANUAL INJURIES:")
    print("-" * 40)
    print(f"Predicted Winner: {prediction['predicted_winner']}")
    print(f"Confidence: {prediction['confidence']:.1f}%")
    print(f"Home Win Probability: {prediction['home_win_probability']:.3f}")
    print(f"Away Win Probability: {prediction['away_win_probability']:.3f}")
    print(f"Injury Data Source: {prediction['injury_data_source']}")
    print(f"Replacement Analysis: {prediction['replacement_analysis']}")
    
    if home_injuries:
        print(f"\n🏥 {home_team} Injuries:")
        for player, status in home_injuries.items():
            print(f"  {player}: {status}")
    
    if away_injuries:
        print(f"\n🏥 {away_team} Injuries:")
        for player, status in away_injuries.items():
            print(f"  {player}: {status}")
    
    logger.info("\n✅ Manual injury prediction completed!")

if __name__ == "__main__":
    main()





