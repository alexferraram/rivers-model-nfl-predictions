"""
NFL Predictions Website - Minimal Deployment Version
Ultra-simplified for Render deployment
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import json
import os
from datetime import datetime
import logging

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
        
        # Verify tables exist
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        logger.info(f"Tables in database: {[table[0] for table in tables]}")
        
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return False

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
    return render_template('index.html', message="Welcome to The RIVERS Model - AI NFL Predictions")

@app.route('/init-db')
def init_database():
    """Manually initialize database"""
    try:
        success = init_db()
        if success:
            flash('Database initialized successfully!', 'success')
        else:
            flash('Database initialization failed!', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Manual database init error: {e}")
        flash('Database initialization error!', 'error')
        return redirect(url_for('index'))

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
            'SELECT * FROM predictions WHERE week = ? AND season = 2025 ORDER BY home_team',
            (week,)
        ).fetchall()
        
        # Get results for the week
        results = conn.execute(
            'SELECT * FROM results WHERE week = ? AND season = 2025',
            (week,)
        ).fetchall()
        
        # Convert results to dictionary for easy lookup
        results_dict = {}
        for result in results:
            game_key = f"{result['away_team']}@{result['home_team']}"
            results_dict[game_key] = {
                'home_score': result['home_score'],
                'away_score': result['away_score'],
                'actual_winner': result['actual_winner']
            }
        
        # Get available weeks
        available_weeks = conn.execute(
            'SELECT DISTINCT week FROM predictions WHERE season = 2025 ORDER BY week'
        ).fetchall()
        
        conn.close()
        
        return render_template('week_predictions.html',
                             current_week=week,
                             predictions=predictions,
                             results=results_dict,
                             available_weeks=[w['week'] for w in available_weeks])
    except Exception as e:
        logger.error(f"Week predictions error: {e}")
        flash('Error loading predictions. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/generate_predictions/<int:week>')
def generate_predictions(week):
    """Generate predictions for a specific week"""
    try:
        # Sample predictions for Week 3
        sample_predictions = [
            {
                'home_team': 'BUF',
                'away_team': 'MIA',
                'predicted_winner': 'BUF',
                'confidence': 0.75,
                'injury_report': 'BUF: Matt Milano (LB) - OUT, Ed Oliver (DT) - OUT | MIA: Storm Duck (CB) - OUT'
            },
            {
                'home_team': 'ATL',
                'away_team': 'CAR',
                'predicted_winner': 'ATL',
                'confidence': 0.68,
                'injury_report': 'Both teams healthy'
            },
            {
                'home_team': 'GB',
                'away_team': 'CLE',
                'predicted_winner': 'GB',
                'confidence': 0.72,
                'injury_report': 'Both teams healthy'
            }
        ]
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection error. Please try again later.', 'error')
            return redirect(url_for('index'))
        
        # Clear existing predictions for this week
        conn.execute('DELETE FROM predictions WHERE week = ? AND season = 2025', (week,))
        
        # Insert new predictions
        for pred in sample_predictions:
            conn.execute('''
                INSERT INTO predictions (week, season, home_team, away_team, predicted_winner, confidence, injury_report)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (week, 2025, pred['home_team'], pred['away_team'], 
                  pred['predicted_winner'], pred['confidence'], pred['injury_report']))
        
        conn.commit()
        conn.close()
        
        flash(f'Successfully generated predictions for Week {week}!', 'success')
        return redirect(url_for('week_predictions', week=week))
        
    except Exception as e:
        logger.error(f"Generate predictions error: {e}")
        flash('Error generating predictions. Please try again.', 'error')
        return redirect(url_for('index'))

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
    port = int(os.environ.get('PORT', 8080))
    
    print(f"🌊 The RIVERS Model - AI NFL Predictions Starting...")
    print(f"📱 Visit: http://localhost:{port}")
    print("🛑 Press Ctrl+C to stop")
    
    # Run the app
    app.run(debug=False, host='0.0.0.0', port=port)
