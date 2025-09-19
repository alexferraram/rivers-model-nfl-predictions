# Fantasy-Enhanced NFL Game Prediction Model

This project builds a sophisticated machine learning model to predict NFL game outcomes using comprehensive team statistics, player data, injuries, situational performance, matchup analysis, fantasy football metrics, expected performance data, and efficiency analytics from multiple NFL data sources.

## 🏈 Advanced Features

### Data Collection & Processing
- **Comprehensive Data Sources**: Play-by-play, schedules, rosters, player stats, injuries, depth charts
- **Fantasy Football Data**: Player valuations, fantasy points, expected fantasy performance
- **Expected Performance Metrics**: Expected vs actual yards, fantasy points, efficiency ratings
- **Opportunity Analytics**: Target share, carry share, air yards share, high-value touches
- **Situational Statistics**: 3rd down conversion, redzone efficiency, goal line performance, 2-minute drill
- **Player-Level Analysis**: Individual player statistics aggregated by position and team
- **Injury Tracking**: Key player injuries, games lost, injury impact on team performance

### Advanced Feature Engineering
- **Fantasy Team Strength**: Position-specific fantasy performance, team fantasy efficiency
- **Expected vs Actual Analysis**: Yards over expected, fantasy efficiency, performance gaps
- **Opportunity-Based Metrics**: Target/carry share analysis, red zone opportunities
- **Efficiency Analytics**: Route efficiency, blocking efficiency, defensive efficiency
- **Matchup Analysis**: Offense vs defense rankings and advantages
- **Team Tendencies**: Play-calling patterns, formation preferences, situational tendencies
- **Performance Metrics**: Yards per play, turnover rates, scoring efficiency
- **Contextual Factors**: Home field advantage, weather impact, rest days

### Machine Learning Models
- **Advanced Algorithms**: Random Forest, Gradient Boosting, Extra Trees, Neural Networks, SVM
- **Feature Selection**: Automatic selection of most predictive features
- **Hyperparameter Optimization**: Grid search for optimal model performance
- **Cross-Validation**: Stratified k-fold validation for robust evaluation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the main application to collect data and train models:
```bash
python main.py
```

3. Test the fantasy-enhanced model:
```bash
python test_fantasy_model.py
```

4. Open Jupyter notebook for fantasy-enhanced analysis:
```bash
jupyter notebook notebooks/fantasy_nfl_analysis.ipynb
```

5. Test advanced model (for comparison):
```bash
python test_advanced_model.py
```

6. Test basic model (for comparison):
```bash
python test_model.py
```

## Project Structure

- `data/` - Raw and processed data files
- `src/` - Source code modules
  - `data_collector.py` - NFL data collection using nflverse and nflreadpy
  - `preprocessor.py` - Basic data preprocessing and feature engineering
  - `advanced_preprocessor.py` - Advanced feature engineering with situational stats, injuries, matchups
  - `fantasy_preprocessor.py` - Fantasy-enhanced preprocessing with efficiency metrics and expected performance
  - `model.py` - Basic machine learning models and prediction
  - `advanced_model.py` - Advanced ML models with feature selection and optimization
- `models/` - Trained model files (basic, advanced, and fantasy-enhanced)
- `notebooks/` - Jupyter notebooks for analysis
  - `nfl_analysis.ipynb` - Basic model analysis
  - `advanced_nfl_analysis.ipynb` - Advanced model analysis
  - `fantasy_nfl_analysis.ipynb` - Fantasy-enhanced model analysis
- `main.py` - Main application script
- `test_model.py` - Basic model testing script
- `test_advanced_model.py` - Advanced model testing script
- `test_fantasy_model.py` - Fantasy-enhanced model testing script

## Usage

### Fantasy-Enhanced Usage

```python
from src.advanced_model import AdvancedNFLPredictionModel

# Load fantasy-enhanced trained model
model = AdvancedNFLPredictionModel(model_type='random_forest')
model.load_model('models/advanced_random_forest_model.pkl')

# Comprehensive fantasy-enhanced team statistics
home_team_data = {
    # Offensive stats
    'offense_yards_per_play': 6.2,
    'offense_first_down_rate': 0.42,
    'offense_turnover_rate': 0.06,
    
    # Situational stats
    'situational_third_down_rate': 0.48,
    'situational_redzone_td_rate': 0.68,
    'situational_goal_line_td_rate': 0.75,
    
    # Player stats
    'player_passing_yards_per_game': 281,
    'player_rushing_yards_per_game': 113,
    'player_touchdowns_per_game': 3.0,
    
    # Fantasy team strength
    'fantasy_total_fantasy_points': 2800,
    'fantasy_fantasy_points_per_game': 175,
    'fantasy_team_fantasy_efficiency': 1.15,
    'fantasy_qb_fantasy_points_per_game': 22.5,
    'fantasy_rb_fantasy_points_per_game': 18.2,
    'fantasy_wr_fantasy_points_per_game': 16.8,
    'fantasy_te_fantasy_points_per_game': 12.3,
    
    # Opportunity metrics
    'opportunity_yards_over_expected': 700,
    'opportunity_yards_efficiency': 1.11,
    'opportunity_avg_target_share': 0.18,
    'opportunity_max_target_share': 0.28,
    'opportunity_high_value_touch_rate': 0.15,
    
    # Efficiency metrics
    'efficiency_weighted_yards_per_target': 8.5,
    'efficiency_weighted_success_rate': 0.54,
    'efficiency_explosive_play_rate': 0.08,
    'efficiency_avg_route_efficiency': 0.78,
    
    # Defensive stats
    'defense_yards_per_play': 5.1,
    'defense_turnover_rate': 0.12,
    
    # Tendencies
    'tendencies_pass_rate': 0.65,
    'tendencies_shotgun_rate': 0.72,
    
    # Injury impact
    'injury_key_player_injuries': 2,
    'injury_key_injury_rate': 0.08,
    
    # Fantasy matchup advantages
    'fantasy_matchup_total_fantasy_points_matchup_adv': 8,
    'fantasy_matchup_team_fantasy_efficiency_matchup_adv': 0.15
}

away_team_data = {
    # Similar structure with different values
    'offense_yards_per_play': 5.5,
    'offense_first_down_rate': 0.35,
    'offense_turnover_rate': 0.08,
    'situational_third_down_rate': 0.38,
    'situational_redzone_td_rate': 0.58,
    'situational_goal_line_td_rate': 0.65,
    'player_passing_yards_per_game': 238,
    'player_rushing_yards_per_game': 100,
    'player_touchdowns_per_game': 2.5,
    'fantasy_total_fantasy_points': 2400,
    'fantasy_fantasy_points_per_game': 150,
    'fantasy_team_fantasy_efficiency': 1.02,
    'fantasy_qb_fantasy_points_per_game': 19.0,
    'fantasy_rb_fantasy_points_per_game': 15.4,
    'fantasy_wr_fantasy_points_per_game': 14.6,
    'fantasy_te_fantasy_points_per_game': 10.5,
    'opportunity_yards_over_expected': 100,
    'opportunity_yards_efficiency': 1.02,
    'opportunity_avg_target_share': 0.15,
    'opportunity_max_target_share': 0.22,
    'opportunity_high_value_touch_rate': 0.12,
    'efficiency_weighted_yards_per_target': 7.4,
    'efficiency_weighted_success_rate': 0.49,
    'efficiency_explosive_play_rate': 0.06,
    'efficiency_avg_route_efficiency': 0.68,
    'defense_yards_per_play': 5.4,
    'defense_turnover_rate': 0.09,
    'tendencies_pass_rate': 0.58,
    'tendencies_shotgun_rate': 0.55,
    'injury_key_player_injuries': 3,
    'injury_key_injury_rate': 0.12,
    'fantasy_matchup_total_fantasy_points_matchup_adv': 0,
    'fantasy_matchup_team_fantasy_efficiency_matchup_adv': 0
}

# Make fantasy-enhanced prediction
prediction = model.predict_game_advanced(home_team_data, away_team_data)
print(f"Predicted winner: {prediction['predicted_winner']}")
print(f"Confidence: {prediction['confidence']:.3f}")
print(f"Key factors: {prediction['key_factors']}")
print(f"Top features: {list(prediction['feature_contributions'].keys())[:5]}")
```

## Model Performance

The advanced model provides comprehensive evaluation:
- **Accuracy & AUC Scores**: Multiple performance metrics
- **Cross-Validation**: Stratified k-fold validation for robust results
- **Feature Importance**: Analysis of most predictive features
- **Confusion Matrices**: Detailed classification performance
- **Key Factor Analysis**: Identification of game-deciding factors

## Fantasy-Enhanced Features Breakdown

### Fantasy Football Integration
- **Team Fantasy Strength**: Position-specific fantasy performance metrics
- **Fantasy Efficiency**: Expected vs actual fantasy point performance
- **Fantasy Consistency**: Player performance reliability metrics
- **Position Rankings**: QB, RB, WR, TE fantasy strength comparisons

### Expected Performance Analytics
- **Yards Over Expected**: Actual vs expected yardage performance
- **Fantasy Efficiency**: Fantasy points vs expected fantasy points
- **Performance Gaps**: Identification of over/under-performing teams
- **Regression Analysis**: Expected performance normalization

### Opportunity-Based Metrics
- **Target Share Analysis**: Receiving opportunity distribution
- **Carry Share Analysis**: Rushing opportunity distribution
- **Air Yards Share**: Downfield opportunity metrics
- **High-Value Touches**: Red zone and goal line opportunities
- **Snap Share**: Playing time and opportunity correlation

### Efficiency Analytics
- **Route Running Efficiency**: Receiver route effectiveness
- **Blocking Efficiency**: Offensive line performance metrics
- **Defensive Efficiency**: Tackle, pass rush, and coverage effectiveness
- **Success Rate Metrics**: Play-by-play success analysis
- **Explosive Play Rates**: Big play generation capability

### Situational Statistics
- **3rd Down Conversion**: Success rate in critical situations
- **Red Zone Efficiency**: Scoring percentage inside the 20-yard line
- **Goal Line Performance**: Success rate inside the 5-yard line
- **2-Minute Drill**: Performance in hurry-up situations
- **Short/Long Yardage**: Success rates by down and distance

### Player-Level Analysis
- **Skill Position Stats**: QB, RB, WR, TE performance metrics
- **Defensive Stats**: Tackles, sacks, interceptions, passes defended
- **Per-Game Averages**: Normalized performance metrics
- **Position-Specific Metrics**: Tailored statistics by player role

### Injury Impact Modeling
- **Key Player Injuries**: Impact of starter injuries
- **Games Lost**: Cumulative injury effect
- **Injury Rates**: Team health metrics
- **Depth Chart Analysis**: Backup player quality assessment

### Matchup Analysis
- **Offense vs Defense Rankings**: Comparative team strengths
- **Fantasy Matchup Advantages**: Position-specific matchup edges
- **Advantage Calculations**: Statistical matchup edges
- **Positional Matchups**: Specific unit comparisons
- **Historical Performance**: Head-to-head tendencies

## Data Sources

- **nflverse-data**: Core NFL data repository (https://github.com/nflverse/nflverse-data.git)
  - Play-by-play data, schedules, rosters, player stats, injuries, depth charts
  - Automated data releases via GitHub Actions
  - 273 stars, active community development
- **nfldata**: Enhanced NFL data by Lee Sharpe (https://github.com/nflverse/nfldata.git)
  - Enhanced schedules and game data with additional metadata
  - Comprehensive team and player statistics
  - 305 stars, 47,944 commits, expert-created
- **dynastyprocess**: Fantasy football data repository (https://github.com/dynastyprocess/data.git)
  - Player IDs database, fantasy points & expected points
  - Player values, trade analysis, dynasty valuations
  - Weekly updates via GitHub Actions, maintained by DynastyProcess.com
- **ffopportunity**: Expected fantasy points repository (https://github.com/ffverse/ffopportunity.git)
  - Expected Fantasy Points models using XGBoost trained on nflverse data (2006-2020)
  - Expected points data for all players and plays, opportunity analysis
  - Automated data releases via GitHub Actions, multiple formats (RDS, parquet, CSV)
  - Website: ffopportunity.ffverse.com
- **Seasons**: 2022-2024 (configurable)
- **Features**: 200+ fantasy-enhanced features including:
  - Fantasy football metrics and efficiency ratings
  - Expected vs actual performance analysis
  - Opportunity-based statistics and analytics
  - Advanced efficiency metrics and situational stats
  - Player metrics, injury data, and matchup analysis

## Requirements

- Python 3.8+
- nflverse
- nflreadpy
- pandas
- scikit-learn
- matplotlib
- seaborn
- jupyter
