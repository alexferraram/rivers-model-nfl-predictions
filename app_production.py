"""
NFL Predictions Website - Production Version
Optimized for deployment with proper error handling and configuration
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

# Use environment variable for secret key, fallback to default
app.secret_key = os.environ.get('SECRET_KEY', 'nfl_predictions_secret_key_2025_production')

# Database setup
DATABASE = os.environ.get('DATABASE_URL', 'nfl_predictions.db')

def init_db():
    """Initialize the database with required tables"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Create predictions table
        cursor.execute('''
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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week INTEGER NOT NULL,
                season INTEGER NOT NULL,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                home_score INTEGER,
                away_score INTEGER,
                actual_winner TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

def get_db_connection():
    """Get database connection with error handling"""
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

def format_injury_report(injury_data):
    """Format injury report without percentage impacts"""
    if not injury_data:
        return "Both teams healthy"
    
    try:
        formatted = []
        for team, injuries in injury_data.items():
            if injuries.get('total_impact', 0) > 0:
                injury_list = []
                for injury in injuries.get('injuries', []):
                    injury_list.append(f"{injury['player']} ({injury['position']}) - {injury['status']}")
                if injury_list:
                    formatted.append(f"{team}: {', '.join(injury_list)}")
            else:
                formatted.append(f"{team}: No significant injuries")
        
        return " | ".join(formatted) if formatted else "Both teams healthy"
    except Exception as e:
        logger.error(f"Error formatting injury report: {e}")
        return "Injury data unavailable"

def fetch_nfl_scores(week, season=2025):
    """Fetch NFL scores for a specific week from ESPN"""
    try:
        # ESPN NFL scores URL
        url = f"https://www.espn.com/nfl/scoreboard/_/week/{week}/year/{season}/seasontype/2"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple selectors for game containers
        games = []
        
        # Method 1: Look for game containers with common patterns
        game_containers = soup.find_all(['div', 'section', 'article'], class_=lambda x: x and any(word in x.lower() for word in ['game', 'matchup', 'score']))
        
        if not game_containers:
            # Method 2: Look for JSON data in script tags
            script_tags = soup.find_all('script', type='application/json')
            for script in script_tags:
                try:
                    import json
                    data = json.loads(script.string)
                    # Look for game data in the JSON
                    if 'events' in data or 'games' in data:
                        logger.info("Found JSON data with game information")
                        # Parse JSON data for games
                        break
                except:
                    continue
        
        # Method 3: Look for specific ESPN patterns
        if not games:
            # Look for team abbreviations and scores
            team_elements = soup.find_all(text=lambda text: text and any(abbr in text for abbr in ['MIA', 'BUF', 'ATL', 'CAR', 'GB', 'CLE']))
            score_elements = soup.find_all(text=lambda text: text and text.strip().isdigit() and len(text.strip()) <= 2)
            
            if team_elements and score_elements:
                logger.info(f"Found {len(team_elements)} team references and {len(score_elements)} score references")
        
        # For now, return empty list since ESPN structure has changed
        # This will be improved when we have actual game data
        logger.info(f"No games found for Week {week} - ESPN structure may have changed")
        return []
        
    except Exception as e:
        logger.error(f"Error fetching NFL scores: {e}")
        return []

def update_scores_from_espn(week, season=2025):
    """Update database with scores from ESPN"""
    try:
        games = fetch_nfl_scores(week, season)
        if not games:
            return False, "No games found or error fetching scores"
        
        conn = get_db_connection()
        if not conn:
            return False, "Database connection error"
        
        updated_count = 0
        for game in games:
            # Check if this game exists in our predictions
            existing = conn.execute('''
                SELECT id FROM predictions 
                WHERE week = ? AND season = ? AND home_team = ? AND away_team = ?
            ''', (week, season, game['home_team'], game['away_team'])).fetchone()
            
            if existing:
                # Update or insert result
                conn.execute('''
                    INSERT OR REPLACE INTO results 
                    (week, season, home_team, away_team, home_score, away_score, actual_winner, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (week, season, game['home_team'], game['away_team'], 
                      game['home_score'], game['away_score'], game['winner'], datetime.now()))
                updated_count += 1
        
        conn.commit()
        conn.close()
        
        return True, f"Updated {updated_count} games with scores"
        
    except Exception as e:
        logger.error(f"Error updating scores: {e}")
        return False, f"Error updating scores: {str(e)}"

@app.route('/')
def index():
    """Home page - show current week predictions"""
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection error. Please try again later.', 'error')
            return render_template('index.html', message="Database unavailable")
        
        # Get the latest week with predictions
        latest_week = conn.execute(
            'SELECT MAX(week) as max_week FROM predictions WHERE season = 2025'
        ).fetchone()
        
        conn.close()
        
        if latest_week['max_week']:
            return redirect(url_for('week_predictions', week=latest_week['max_week']))
        else:
            return render_template('index.html', message="No predictions available yet")
    except Exception as e:
        logger.error(f"Index page error: {e}")
        flash('An error occurred. Please try again.', 'error')
        return render_template('index.html', message="Error loading page")

@app.route('/home')
def home():
    """Direct access to home page with generate predictions form"""
    return render_template('index.html', message="Welcome to NFL Predictions")

@app.route('/week/<int:week>')
def week_predictions(week):
    """Display predictions for a specific week"""
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection error. Please try again later.', 'error')
            return redirect(url_for('index'))
        
        # Get predictions for the week
        predictions = conn.execute(
            '''SELECT * FROM predictions 
               WHERE week = ? AND season = 2025 
               ORDER BY home_team''',
            (week,)
        ).fetchall()
        
        # Get results for the week
        results = conn.execute(
            '''SELECT * FROM results 
               WHERE week = ? AND season = 2025''',
            (week,)
        ).fetchall()
        
        # Create a dictionary for easy lookup
        results_dict = {}
        for result in results:
            key = f"{result['away_team']}@{result['home_team']}"
            results_dict[key] = result
        
        # Get available weeks
        available_weeks = conn.execute(
            'SELECT DISTINCT week FROM predictions WHERE season = 2025 ORDER BY week'
        ).fetchall()
        
        conn.close()
        
        return render_template('week_predictions.html', 
                             predictions=predictions, 
                             results=results_dict,
                             current_week=week,
                             available_weeks=[w['week'] for w in available_weeks])
    except Exception as e:
        logger.error(f"Week predictions error: {e}")
        flash('Error loading predictions. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/generate_predictions/<int:week>')
def generate_predictions(week):
    """Generate predictions for a specific week using RIVERS model"""
    try:
        # Import RIVERS model
        from rivers_model_validated import RiversModelValidated
        
        # Initialize model
        model = RiversModelValidated()
        
        # Generate predictions based on week
        if week == 3:
            predictions = model.generate_week3_predictions()
        else:
            flash(f'Week {week} predictions not yet implemented.', 'error')
            return redirect(url_for('index'))
        
        if predictions is None:
            flash('Failed to generate predictions. Please check the model.', 'error')
            return redirect(url_for('index'))
        
        # Save predictions to database
        conn = get_db_connection()
        if not conn:
            flash('Database connection error. Predictions not saved.', 'error')
            return redirect(url_for('index'))
        
        try:
            # Clear existing predictions for this week
            conn.execute('DELETE FROM predictions WHERE week = ? AND season = ?', (week, 2025))
            
            for prediction in predictions:
                # Format injury report
                injury_report = format_injury_report_for_database(prediction)
                
                conn.execute(
                    '''INSERT INTO predictions 
                       (week, season, home_team, away_team, predicted_winner, confidence, injury_report)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (week, 2025, prediction['home_team'], prediction['away_team'], 
                     prediction['winner'], prediction['confidence'], injury_report)
                )
            
            conn.commit()
            conn.close()
            
            flash(f'Successfully generated and saved {len(predictions)} predictions for Week {week}!', 'success')
            return redirect(url_for('week_predictions', week=week))
            
        except Exception as e:
            conn.close()
            logger.error(f"Database save error: {e}")
            flash('Error saving predictions to database.', 'error')
            return redirect(url_for('index'))
            
    except ImportError as e:
        logger.error(f"RIVERS model import error: {e}")
        flash('RIVERS model not available. Please check the installation.', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Generate predictions error: {e}")
        flash('Error generating predictions. Please try again.', 'error')
        return redirect(url_for('index'))

def format_injury_report_for_database(prediction):
    """Format injury report for database storage"""
    home_injuries = prediction['home_details'].get('injury_details', {})
    away_injuries = prediction['away_details'].get('injury_details', {})
    
    injury_parts = []
    
    if home_injuries.get('total_impact', 0) > 0:
        injury_list = []
        for injury in home_injuries.get('injuries', []):
            injury_list.append(f"{injury['player']} ({injury['position']}) - {injury['status']}")
        if injury_list:
            injury_parts.append(f"{prediction['home_team']}: {', '.join(injury_list)}")
    
    if away_injuries.get('total_impact', 0) > 0:
        injury_list = []
        for injury in away_injuries.get('injuries', []):
            injury_list.append(f"{injury['player']} ({injury['position']}) - {injury['status']}")
        if injury_list:
            injury_parts.append(f"{prediction['away_team']}: {', '.join(injury_list)}")
    
    return " | ".join(injury_parts) if injury_parts else "No injuries"


@app.route('/update_scores/<int:week>')
def update_scores(week):
    """Automatically update scores for a specific week from ESPN"""
    try:
        success, message = update_scores_from_espn(week)
        
        if success:
            flash(f'✅ {message}', 'success')
        else:
            flash(f'❌ {message}', 'error')
            
        return redirect(url_for('week_predictions', week=week))
    except Exception as e:
        logger.error(f"Update scores error: {e}")
        flash('Error updating scores. Please try again.', 'error')
        return redirect(url_for('week_predictions', week=week))

@app.route('/stats')
def stats():
    """Display model statistics"""
    try:
        conn = get_db_connection()
        if not conn:
            flash('Database connection error. Please try again later.', 'error')
            return redirect(url_for('index'))
        
        # Get all predictions with results
        stats_data = conn.execute('''
            SELECT p.*, r.home_score, r.away_score, r.actual_winner
            FROM predictions p
            LEFT JOIN results r ON p.week = r.week AND p.season = r.season 
                AND p.home_team = r.home_team AND p.away_team = r.away_team
            WHERE p.season = 2025
            ORDER BY p.week, p.home_team
        ''').fetchall()
        
        # Calculate statistics - only count games that have been completed
        completed_games = [row for row in stats_data if row['actual_winner']]
        total_completed = len(completed_games)
        correct_predictions = sum(1 for row in completed_games if row['predicted_winner'] == row['actual_winner'])
        accuracy = (correct_predictions / total_completed * 100) if total_completed > 0 else 0
        
        # Keep total predictions for display purposes
        total_predictions = len(stats_data)
        
        # Group by week with detailed game data
        weekly_stats = {}
        for row in stats_data:
            week = row['week']
            if week not in weekly_stats:
                weekly_stats[week] = {'total': 0, 'correct': 0, 'games': []}
            
            # Prepare game data
            game_data = {
                'away_team': row['away_team'],
                'home_team': row['home_team'],
                'predicted_winner': row['predicted_winner'],
                'confidence': row['confidence'],
                'result': None
            }
            
            # Add result data if available
            if row['actual_winner']:
                game_data['result'] = {
                    'actual_winner': row['actual_winner'],
                    'away_score': row['away_score'],
                    'home_score': row['home_score']
                }
                
                # Check if prediction was correct
                if row['predicted_winner'] == row['actual_winner']:
                    weekly_stats[week]['correct'] += 1
                
                # Only count completed games in weekly totals
                weekly_stats[week]['total'] += 1
            
            weekly_stats[week]['games'].append(game_data)
        
        conn.close()
        
        return render_template('stats.html', 
                             total_predictions=total_predictions,
                             correct_predictions=correct_predictions,
                             accuracy=accuracy,
                             weekly_stats=weekly_stats)
    except Exception as e:
        logger.error(f"Stats page error: {e}")
        flash('Error loading statistics. Please try again.', 'error')
        return redirect(url_for('index'))

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
    port = int(os.environ.get('PORT', 8080))  # Changed from 5000 to 8080
    
    print(f"🌊 NFL Predictions Website Starting...")
    print(f"📱 Visit: http://localhost:{port}")
    print(f"🌐 Network access: http://192.168.1.128:{port}")
    print("🛑 Press Ctrl+C to stop")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=port)
