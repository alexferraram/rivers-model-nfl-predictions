"""
NFL Data Collection Module

This module handles downloading and caching NFL data using the nflverse package.
"""

import pandas as pd
from nflverse import (
    load_pbp_data, load_rosters, load_teams, load_schedules,
    load_player_stats, load_injuries, load_depth_charts,
    load_contracts, load_draft_picks, load_combine_data
)
# Additional data sources from nflreadpy
try:
    from nflreadpy import (
        load_schedules as load_nfldata_schedules,
        load_game_data, load_team_data, load_player_data,
        load_fantasy_data, load_opportunity_data, load_efficiency_data
    )
    NFLREADPY_AVAILABLE = True
except ImportError:
    NFLREADPY_AVAILABLE = False
    print("nflreadpy not available. Install with: pip install nflreadpy")

from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NFLDataCollector:
    """Collects NFL data using the nflverse package."""
    
    def __init__(self, seasons: Optional[List[int]] = None):
        """
        Initialize the data collector.
        
        Args:
            seasons: List of seasons to collect data for. If None, defaults to recent seasons.
        """
        self.seasons = seasons or [2022, 2023, 2024]
        self.cached_data = {}
    
    def get_teams_data(self) -> pd.DataFrame:
        """Get team information."""
        logger.info("Loading teams data...")
        teams = load_teams()
        self.cached_data['teams'] = teams
        return teams
    
    def get_schedules_data(self) -> pd.DataFrame:
        """Get game schedules for specified seasons."""
        logger.info(f"Loading schedules for seasons: {self.seasons}")
        schedules = []
        
        for season in self.seasons:
            try:
                season_schedule = load_schedules(seasons=season)
                schedules.append(season_schedule)
                logger.info(f"Loaded {len(season_schedule)} games for {season}")
            except Exception as e:
                logger.warning(f"Could not load schedule for {season}: {e}")
        
        if schedules:
            combined_schedules = pd.concat(schedules, ignore_index=True)
            self.cached_data['schedules'] = combined_schedules
            return combined_schedules
        else:
            logger.error("No schedule data could be loaded")
            return pd.DataFrame()
    
    def get_pbp_data(self, season: Optional[int] = None) -> pd.DataFrame:
        """
        Get play-by-play data for specified season(s).
        
        Args:
            season: Specific season to load. If None, loads all configured seasons.
        """
        seasons_to_load = [season] if season else self.seasons
        logger.info(f"Loading play-by-play data for seasons: {seasons_to_load}")
        
        pbp_data = []
        for season in seasons_to_load:
            try:
                season_pbp = load_pbp_data(seasons=season)
                pbp_data.append(season_pbp)
                logger.info(f"Loaded {len(season_pbp)} plays for {season}")
            except Exception as e:
                logger.warning(f"Could not load PBP data for {season}: {e}")
        
        if pbp_data:
            combined_pbp = pd.concat(pbp_data, ignore_index=True)
            self.cached_data['pbp'] = combined_pbp
            return combined_pbp
        else:
            logger.error("No play-by-play data could be loaded")
            return pd.DataFrame()
    
    def get_rosters_data(self, season: Optional[int] = None) -> pd.DataFrame:
        """
        Get roster data for specified season(s).
        
        Args:
            season: Specific season to load. If None, loads all configured seasons.
        """
        seasons_to_load = [season] if season else self.seasons
        logger.info(f"Loading roster data for seasons: {seasons_to_load}")
        
        roster_data = []
        for season in seasons_to_load:
            try:
                season_roster = load_rosters(seasons=season)
                roster_data.append(season_roster)
                logger.info(f"Loaded {len(season_roster)} roster entries for {season}")
            except Exception as e:
                logger.warning(f"Could not load roster data for {season}: {e}")
        
        if roster_data:
            combined_roster = pd.concat(roster_data, ignore_index=True)
            self.cached_data['rosters'] = combined_roster
            return combined_roster
        else:
            logger.error("No roster data could be loaded")
            return pd.DataFrame()
    
    def get_player_stats_data(self, season: Optional[int] = None) -> pd.DataFrame:
        """Get player statistics for specified season(s)."""
        seasons_to_load = [season] if season else self.seasons
        logger.info(f"Loading player statistics for seasons: {seasons_to_load}")
        
        player_stats = []
        for season in seasons_to_load:
            try:
                season_stats = load_player_stats(seasons=season)
                player_stats.append(season_stats)
                logger.info(f"Loaded player stats for {len(season_stats)} player-seasons in {season}")
            except Exception as e:
                logger.warning(f"Could not load player stats for {season}: {e}")
        
        if player_stats:
            combined_stats = pd.concat(player_stats, ignore_index=True)
            self.cached_data['player_stats'] = combined_stats
            return combined_stats
        else:
            logger.error("No player statistics could be loaded")
            return pd.DataFrame()
    
    def get_injuries_data(self, season: Optional[int] = None) -> pd.DataFrame:
        """Get injury data for specified season(s)."""
        seasons_to_load = [season] if season else self.seasons
        logger.info(f"Loading injury data for seasons: {seasons_to_load}")
        
        injuries_data = []
        for season in seasons_to_load:
            try:
                season_injuries = load_injuries(seasons=season)
                injuries_data.append(season_injuries)
                logger.info(f"Loaded {len(season_injuries)} injury records for {season}")
            except Exception as e:
                logger.warning(f"Could not load injury data for {season}: {e}")
        
        if injuries_data:
            combined_injuries = pd.concat(injuries_data, ignore_index=True)
            self.cached_data['injuries'] = combined_injuries
            return combined_injuries
        else:
            logger.error("No injury data could be loaded")
            return pd.DataFrame()
    
    def get_depth_charts_data(self, season: Optional[int] = None) -> pd.DataFrame:
        """Get depth chart data for specified season(s)."""
        seasons_to_load = [season] if season else self.seasons
        logger.info(f"Loading depth charts for seasons: {seasons_to_load}")
        
        depth_charts = []
        for season in seasons_to_load:
            try:
                season_depth = load_depth_charts(seasons=season)
                depth_charts.append(season_depth)
                logger.info(f"Loaded depth charts for {len(season_depth)} team-weeks in {season}")
            except Exception as e:
                logger.warning(f"Could not load depth charts for {season}: {e}")
        
        if depth_charts:
            combined_depth = pd.concat(depth_charts, ignore_index=True)
            self.cached_data['depth_charts'] = combined_depth
            return combined_depth
        else:
            logger.error("No depth chart data could be loaded")
            return pd.DataFrame()
    
    def get_nfldata_schedules(self) -> pd.DataFrame:
        """
        Get enhanced schedules from nfldata repository.
        
        The nfldata repository (https://github.com/nflverse/nfldata.git) provides:
        - Enhanced schedules with additional metadata
        - Game data with more context and information
        - Team data with comprehensive statistics
        - Player data with detailed performance metrics
        - Created by Lee Sharpe (@LeeSharpeNFL)
        """
        if not NFLREADPY_AVAILABLE:
            logger.warning("nflreadpy not available, skipping nfldata schedules")
            return pd.DataFrame()
        
        logger.info("Loading enhanced schedules from nfldata repository...")
        logger.info("nfldata repository: https://github.com/nflverse/nfldata.git")
        logger.info("Creator: Lee Sharpe (@LeeSharpeNFL)")
        
        schedules_data = []
        
        for season in self.seasons:
            try:
                season_schedules = load_nfldata_schedules(seasons=season)
                schedules_data.append(season_schedules)
                logger.info(f"Loaded enhanced schedules for {len(season_schedules)} games in {season}")
            except Exception as e:
                logger.warning(f"Could not load nfldata schedules for {season}: {e}")
        
        if schedules_data:
            combined_schedules = pd.concat(schedules_data, ignore_index=True)
            self.cached_data['nfldata_schedules'] = combined_schedules
            logger.info(f"Successfully integrated nfldata schedules: {len(combined_schedules)} total games")
            return combined_schedules
        else:
            logger.error("No nfldata schedules could be loaded")
            return pd.DataFrame()
    
    def get_fantasy_data(self) -> pd.DataFrame:
        """
        Get fantasy football data from dynastyprocess.
        
        The dynastyprocess/data repository (https://github.com/dynastyprocess/data.git) provides:
        - Player IDs database (db_playerids.csv)
        - Fantasy points & expected points (db_fpecr.csv.gz, db_fpecr.parquet)
        - Player values (values.csv, values-players.csv, values-picks.csv)
        - Weekly updates via GitHub Actions
        - Maintained by DynastyProcess.com
        """
        if not NFLREADPY_AVAILABLE:
            logger.warning("nflreadpy not available, skipping fantasy data")
            return pd.DataFrame()
        
        logger.info("Loading fantasy football data from dynastyprocess...")
        logger.info("dynastyprocess/data repository: https://github.com/dynastyprocess/data.git")
        logger.info("Maintained by DynastyProcess.com")
        logger.info("Weekly updates via GitHub Actions")
        
        fantasy_data = []
        
        for season in self.seasons:
            try:
                season_fantasy = load_fantasy_data(seasons=season)
                fantasy_data.append(season_fantasy)
                logger.info(f"Loaded fantasy data for {len(season_fantasy)} player-seasons in {season}")
            except Exception as e:
                logger.warning(f"Could not load fantasy data for {season}: {e}")
        
        if fantasy_data:
            combined_fantasy = pd.concat(fantasy_data, ignore_index=True)
            self.cached_data['fantasy_data'] = combined_fantasy
            logger.info(f"Successfully integrated dynastyprocess fantasy data: {len(combined_fantasy)} total records")
            return combined_fantasy
        else:
            logger.error("No fantasy data could be loaded")
            return pd.DataFrame()
    
    def get_opportunity_data(self) -> pd.DataFrame:
        """
        Get expected yards and fantasy points from ffopportunity.
        
        The ffverse/ffopportunity repository (https://github.com/ffverse/ffopportunity.git) provides:
        - Expected Fantasy Points models using XGBoost trained on nflverse data (2006-2020)
        - Expected points data for all players and plays
        - Opportunity analysis quantifying player opportunities in fantasy football
        - Automated data releases via GitHub Actions
        - Multiple data formats: RDS, parquet, and CSV
        - Website: ffopportunity.ffverse.com
        """
        if not NFLREADPY_AVAILABLE:
            logger.warning("nflreadpy not available, skipping opportunity data")
            return pd.DataFrame()
        
        logger.info("Loading expected yards and fantasy points from ffopportunity...")
        logger.info("ffverse/ffopportunity repository: https://github.com/ffverse/ffopportunity.git")
        logger.info("Models and Data for Expected Fantasy Points")
        logger.info("Website: ffopportunity.ffverse.com")
        logger.info("XGBoost models trained on nflverse data (2006-2020)")
        
        opportunity_data = []
        
        for season in self.seasons:
            try:
                season_opportunity = load_opportunity_data(seasons=season)
                opportunity_data.append(season_opportunity)
                logger.info(f"Loaded opportunity data for {len(season_opportunity)} player-seasons in {season}")
            except Exception as e:
                logger.warning(f"Could not load opportunity data for {season}: {e}")
        
        if opportunity_data:
            combined_opportunity = pd.concat(opportunity_data, ignore_index=True)
            self.cached_data['opportunity_data'] = combined_opportunity
            logger.info(f"Successfully integrated ffopportunity data: {len(combined_opportunity)} total records")
            return combined_opportunity
        else:
            logger.error("No opportunity data could be loaded")
            return pd.DataFrame()
    
    def get_efficiency_data(self) -> pd.DataFrame:
        """Get efficiency metrics and advanced statistics."""
        if not NFLREADPY_AVAILABLE:
            logger.warning("nflreadpy not available, skipping efficiency data")
            return pd.DataFrame()
        
        logger.info("Loading efficiency and advanced metrics...")
        efficiency_data = []
        
        for season in self.seasons:
            try:
                season_efficiency = load_efficiency_data(seasons=season)
                efficiency_data.append(season_efficiency)
                logger.info(f"Loaded efficiency data for {len(season_efficiency)} player-seasons in {season}")
            except Exception as e:
                logger.warning(f"Could not load efficiency data for {season}: {e}")
        
        if efficiency_data:
            combined_efficiency = pd.concat(efficiency_data, ignore_index=True)
            self.cached_data['efficiency_data'] = combined_efficiency
            return combined_efficiency
        else:
            logger.error("No efficiency data could be loaded")
            return pd.DataFrame()
    
    def get_all_data(self) -> Dict[str, pd.DataFrame]:
        """Get all available NFL data including enhanced sources."""
        logger.info("Loading all NFL data including enhanced sources...")
        
        data = {
            'teams': self.get_teams_data(),
            'schedules': self.get_schedules_data(),
            'pbp': self.get_pbp_data(),
            'rosters': self.get_rosters_data(),
            'player_stats': self.get_player_stats_data(),
            'injuries': self.get_injuries_data(),
            'depth_charts': self.get_depth_charts_data()
        }
        
        # Add enhanced data sources if available
        if NFLREADPY_AVAILABLE:
            enhanced_data = {
                'nfldata_schedules': self.get_nfldata_schedules(),
                'fantasy_data': self.get_fantasy_data(),
                'opportunity_data': self.get_opportunity_data(),
                'efficiency_data': self.get_efficiency_data()
            }
            data.update(enhanced_data)
        
        logger.info("Data collection complete!")
        return data
    
    def save_data(self, data: Dict[str, pd.DataFrame], output_dir: str = "data"):
        """Save collected data to CSV files."""
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        for name, df in data.items():
            if not df.empty:
                filepath = os.path.join(output_dir, f"{name}.csv")
                df.to_csv(filepath, index=False)
                logger.info(f"Saved {name} data to {filepath}")


if __name__ == "__main__":
    # Example usage
    collector = NFLDataCollector(seasons=[2023, 2024])
    data = collector.get_all_data()
    collector.save_data(data)
