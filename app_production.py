"""
Simple Blog-Style NFL Predictions Website
Just displays the RIVERS model predictions directly
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import json
import os
from datetime import datetime
import logging
import requests
from bs4 import BeautifulSoup
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

def get_db_connection():
    """Get database connection"""
    try:
        conn = sqlite3.connect('nfl_predictions.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def init_db():
    """Initialize database with tables"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Could not get database connection")
            return False
        
        logger.info("Creating database tables...")
        
        # Create predictions table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week INTEGER NOT NULL,
                season INTEGER NOT NULL,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                predicted_winner TEXT NOT NULL,
                confidence REAL NOT NULL,
                injury_report TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create results table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week INTEGER NOT NULL,
                season INTEGER NOT NULL,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                home_score INTEGER,
                away_score INTEGER,
                actual_winner TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        logger.info("Database tables created successfully")
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return False

def get_week3_predictions():
    """Get Week 3 predictions - hardcoded RIVERS model results"""
    return [
        {
            'away_team': 'MIA',
            'home_team': 'BUF',
            'winner': 'BUF',
            'confidence': 80.7,
            'injury_report': 'BUF: Matt Milano (LB) - Out, Ed Oliver (DT) - Out | MIA: Storm Duck (CB) - Out, Ifeatu Melifonwu (S) - Out, Darren Waller (TE) - Out'
        },
        {
            'away_team': 'ATL',
            'home_team': 'CAR',
            'winner': 'ATL',
            'confidence': 65.6,
            'injury_report': 'CAR: Patrick Jones II (LB) - Out, Tershawn Wharton (DT) - Out | ATL: Jamal Agnew (WR) - Out, A.J. Terrell (CB) - Out, Casey Washington (WR) - Out'
        },
        {
            'away_team': 'GB',
            'home_team': 'CLE',
            'winner': 'GB',
            'confidence': 80.4,
            'injury_report': 'CLE: Mike Hall Jr. (DT) - Out | GB: Jayden Reed (WR) - Out'
        },
        {
            'away_team': 'HOU',
            'home_team': 'JAX',
            'winner': 'JAX',
            'confidence': 68.7,
            'injury_report': 'JAX: Wyatt Milum (G) - Out | HOU: Jaylin Smith (CB) - Out'
        },
        {
            'away_team': 'CIN',
            'home_team': 'MIN',
            'winner': 'CIN',
            'confidence': 63.5,
            'injury_report': 'MIN: Ryan Kelly (C) - Out, J.J. McCarthy (QB) - Out, Justin Skule (T) - Out | CIN: Shemar Stewart (DE) - Out, Cam Taylor-Britt (CB) - Doubtful, Joe Burrow (QB) - Out'
        },
        {
            'away_team': 'PIT',
            'home_team': 'NE',
            'winner': 'NE',
            'confidence': 62.6,
            'injury_report': 'NE: No significant injuries | PIT: DeShon Elliott (S) - Out, Alex Highsmith (LB) - Out, Joey Porter Jr. (CB) - Out, Max Scharping (G) - Out'
        },
        {
            'away_team': 'LA',
            'home_team': 'PHI',
            'winner': 'PHI',
            'confidence': 53.7,
            'injury_report': 'PHI: Will Shipley (RB) - Out | LA: No significant injuries'
        },
        {
            'away_team': 'NYJ',
            'home_team': 'TB',
            'winner': 'TB',
            'confidence': 71.9,
            'injury_report': 'TB: Chris Godwin Jr. (WR) - Out, Tristan Wirfs (T) - Out | NYJ: Justin Fields (QB) - Out, Jermaine Johnson II (DE) - Out, Kene Nwangwu (RB) - Out, Josh Reynolds (WR) - Out, Jay Tufele (DT) - Out'
        },
        {
            'away_team': 'IND',
            'home_team': 'TEN',
            'winner': 'IND',
            'confidence': 89.1,
            'injury_report': 'TEN: JC Latham (T) - Out, T\'Vondre Sweat (DT) - Out, Kevin Winston Jr. (S) - Doubtful | IND: No significant injuries'
        },
        {
            'away_team': 'LV',
            'home_team': 'WAS',
            'winner': 'LV',
            'confidence': 52.3,
            'injury_report': 'WAS: John Bates (TE) - Out, Noah Brown (WR) - Out, Jayden Daniels (QB) - Out | LV: No significant injuries'
        },
        {
            'away_team': 'DEN',
            'home_team': 'LAC',
            'winner': 'LAC',
            'confidence': 68.1,
            'injury_report': 'LAC: Will Dissly (TE) - Out, Elijah Molden (S) - Out | DEN: Evan Engram (TE) - Out, Dre Greenlaw (LB) - Out'
        },
        {
            'away_team': 'NO',
            'home_team': 'SEA',
            'winner': 'SEA',
            'confidence': 51.3,
            'injury_report': 'SEA: Zach Charbonnet (RB) - Doubtful, Nick Emmanwori (S) - Doubtful, Julian Love (S) - Doubtful, Devon Witherspoon (CB) - Doubtful | NO: Dillon Radunz (G) - Out, Chase Young (DE) - Out'
        },
        {
            'away_team': 'DAL',
            'home_team': 'CHI',
            'winner': 'DAL',
            'confidence': 77.2,
            'injury_report': 'CHI: Kiran Amegadjie (G) - Out, T.J. Edwards (LB) - Out, Kyler Gordon (CB) - Out, Jaylon Johnson (CB) - Out, Jaylon Jones (CB) - Out | DAL: DaRon Bland (CB) - Out'
        },
        {
            'away_team': 'ARI',
            'home_team': 'SF',
            'winner': 'ARI',
            'confidence': 57.8,
            'injury_report': 'SF: Spencer Burford (T) - Out, Jordan Watkins (WR) - Out | ARI: Will Johnson (CB) - Doubtful'
        },
        {
            'away_team': 'KC',
            'home_team': 'NYG',
            'winner': 'KC',
            'confidence': 51.3,
            'injury_report': 'NYG: Demetrius Flannigan-Fowles (LB) - Doubtful, Darius Muasau (LB) - Out, Rakeem Nunez-Roches (DT) - Doubtful | KC: Michael Danna (DE) - Out, Kristian Fulton (CB) - Out'
        },
        {
            'away_team': 'DET',
            'home_team': 'BAL',
            'winner': 'BAL',
            'confidence': 57.4,
            'injury_report': 'BAL: No significant injuries | DET: No significant injuries'
        }
    ]

def fetch_nfl_scores_from_espn(week, season=2025):
    """Fetch actual NFL scores from ESPN"""
    try:
        logger.info(f"Fetching NFL scores from ESPN for Week {week}, Season {season}")
        
        # ESPN NFL scores URL
        url = f"https://www.espn.com/nfl/scoreboard/_/week/{week}/year/{season}/seasontype/2"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for score elements
        scores = []
        
        # Try multiple selectors for ESPN's structure
        score_selectors = [
            '.ScoreCell__Score',
            '.ScoreCell__Score--score',
            '.ScoreboardScoreCell__Score',
            '.ScoreboardScoreCell__Score--score',
            '.ScoreCell',
            '.ScoreboardScoreCell'
        ]
        
        for selector in score_selectors:
            score_elements = soup.select(selector)
            if score_elements:
                logger.info(f"Found {len(score_elements)} score elements with selector: {selector}")
                break
        
        if not score_elements:
            logger.warning("No score elements found with any selector")
            return []
        
        # Extract scores and team names
        for i in range(0, len(score_elements), 2):
            if i + 1 < len(score_elements):
                home_score = score_elements[i].get_text(strip=True)
                away_score = score_elements[i + 1].get_text(strip=True)
                
                # Try to get team names from nearby elements
                team_elements = soup.select('.ScoreCell__TeamName, .ScoreboardScoreCell__TeamName')
                if len(team_elements) >= 2:
                    home_team = team_elements[i].get_text(strip=True)
                    away_team = team_elements[i + 1].get_text(strip=True)
                    
                    scores.append({
                        'home_team': home_team,
                        'away_team': away_team,
                        'home_score': int(home_score) if home_score.isdigit() else None,
                        'away_score': int(away_score) if away_score.isdigit() else None
                    })
        
        logger.info(f"Extracted {len(scores)} scores from ESPN")
        return scores
        
    except Exception as e:
        logger.error(f"Error fetching scores from ESPN: {e}")
        return []

@app.route('/')
def index():
    """Home page - redirect to Week 3"""
    return redirect(url_for('week_predictions', week=3))

@app.route('/week/<int:week>')
def week_predictions(week):
    """Display predictions for a specific week"""
    try:
        if week != 3:
            flash(f"Week {week} predictions not available yet. Only Week 3 is available.", 'info')
            return redirect(url_for('week_predictions', week=3))
        
        # Get predictions
        predictions = get_week3_predictions()
        
        # Return simple HTML directly to avoid template issues
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Week {week} - The RIVERS Model</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-4">
                <h1>Week {week} NFL Predictions</h1>
                <div class="row">
        """
        
        for prediction in predictions:
            html += f"""
                    <div class="col-lg-6 mb-4">
                        <div class="card">
                            <div class="card-header">
                                <h5>{prediction['away_team']} @ {prediction['home_team']}</h5>
                            </div>
                            <div class="card-body">
                                <p><strong>Winner:</strong> {prediction['winner']}</p>
                                <p><strong>Confidence:</strong> {prediction['confidence']:.1f}%</p>
                                <p><strong>Injury Report:</strong> {prediction['injury_report']}</p>
                            </div>
                        </div>
                    </div>
            """
        
        html += """
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        logger.error(f"Error in week_predictions route: {e}")
        flash("Error loading predictions. Please try again.", 'error')
        return redirect(url_for('index'))

@app.route('/update_scores/<int:week>')
def update_scores(week):
    """Auto update scores for a specific week"""
    try:
        logger.info(f"Updating scores for Week {week}")
        
        # Fetch scores from ESPN
        scores = fetch_nfl_scores_from_espn(week)
        
        if not scores:
            flash("No completed games found to update.", 'info')
            return redirect(url_for('week_predictions', week=week))
        
        # Update database with scores
        conn = get_db_connection()
        if conn:
            for score in scores:
                # Determine actual winner
                if score['home_score'] and score['away_score']:
                    if score['home_score'] > score['away_score']:
                        actual_winner = score['home_team']
                    elif score['away_score'] > score['home_score']:
                        actual_winner = score['away_team']
                    else:
                        actual_winner = 'TIE'
                    
                    # Insert or update result
                    conn.execute('''
                        INSERT OR REPLACE INTO results 
                        (week, season, home_team, away_team, home_score, away_score, actual_winner)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (week, 2025, score['home_team'], score['away_team'], 
                          score['home_score'], score['away_score'], actual_winner))
            
            conn.commit()
            conn.close()
            
            flash(f"Updated {len(scores)} game results from ESPN.", 'success')
        else:
            flash("Database connection error.", 'error')
        
        return redirect(url_for('week_predictions', week=week))
        
    except Exception as e:
        logger.error(f"Error updating scores: {e}")
        flash("Error updating scores. Please try again.", 'error')
        return redirect(url_for('week_predictions', week=week))

@app.route('/stats')
def stats():
    """Display model statistics - simple version without database"""
    try:
        logger.info("Loading simple stats page")
        return render_template('stats_simple.html', 
                             total_predictions=16,
                             correct_predictions=0,
                             accuracy=0.0,
                             weekly_stats=[{
                                 'week': 3,
                                 'season': 2025,
                                 'predictions': [],
                                 'total': 16,
                                 'correct': 0,
                                 'accuracy': 0.0
                             }])
        
    except Exception as e:
        logger.error(f"Error in stats route: {e}")
        return render_template('stats_simple.html', 
                             total_predictions=16,
                             correct_predictions=0,
                             accuracy=0.0,
                             weekly_stats=[{
                                 'week': 3,
                                 'season': 2025,
                                 'predictions': [],
                                 'total': 16,
                                 'correct': 0,
                                 'accuracy': 0.0
                             }])

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Get port from environment variable (for deployment platforms)
    port = int(os.environ.get('PORT', 8080))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)