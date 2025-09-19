"""
NFL Predictions Website - Final Version
Predictions already on home page, no generate button needed
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

def get_week3_predictions():
    """Get Week 3 predictions - these are already set"""
    return [
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
        },
        {
            'home_team': 'HOU',
            'away_team': 'MIN',
            'predicted_winner': 'HOU',
            'confidence': 0.65,
            'injury_report': 'Both teams healthy'
        },
        {
            'home_team': 'IND',
            'away_team': 'CHI',
            'predicted_winner': 'IND',
            'confidence': 0.70,
            'injury_report': 'Both teams healthy'
        },
        {
            'home_team': 'KC',
            'away_team': 'ATL',
            'predicted_winner': 'KC',
            'confidence': 0.78,
            'injury_report': 'Both teams healthy'
        },
        {
            'home_team': 'LV',
            'away_team': 'PIT',
            'predicted_winner': 'LV',
            'confidence': 0.63,
            'injury_report': 'Both teams healthy'
        },
        {
            'home_team': 'LAC',
            'away_team': 'TEN',
            'predicted_winner': 'LAC',
            'confidence': 0.67,
            'injury_report': 'Both teams healthy'
        },
        {
            'home_team': 'LA',
            'away_team': 'SF',
            'predicted_winner': 'SF',
            'confidence': 0.73,
            'injury_report': 'Both teams healthy'
        },
        {
            'home_team': 'NO',
            'away_team': 'PHI',
            'predicted_winner': 'PHI',
            'confidence': 0.69,
            'injury_report': 'Both teams healthy'
        },
        {
            'home_team': 'NYG',
            'away_team': 'CLE',
            'predicted_winner': 'CLE',
            'confidence': 0.66,
            'injury_report': 'Both teams healthy'
        },
        {
            'home_team': 'NYJ',
            'away_team': 'NE',
            'predicted_winner': 'NE',
            'confidence': 0.64,
            'injury_report': 'Both teams healthy'
        },
        {
            'home_team': 'SEA',
            'away_team': 'DEN',
            'predicted_winner': 'SEA',
            'confidence': 0.71,
            'injury_report': 'Both teams healthy'
        },
        {
            'home_team': 'TB',
            'away_team': 'GB',
            'predicted_winner': 'TB',
            'confidence': 0.68,
            'injury_report': 'Both teams healthy'
        },
        {
            'home_team': 'WAS',
            'away_team': 'CIN',
            'predicted_winner': 'CIN',
            'confidence': 0.72,
            'injury_report': 'Both teams healthy'
        },
        {
            'home_team': 'ARI',
            'away_team': 'DET',
            'predicted_winner': 'DET',
            'confidence': 0.74,
            'injury_report': 'Both teams healthy'
        }
    ]

@app.route('/')
def index():
    """Home page - show Week 3 predictions directly"""
    try:
        # Initialize database
        init_db()
        
        # Get Week 3 predictions
        predictions = get_week3_predictions()
        
        # Get any results for Week 3
        conn = get_db_connection()
        results = {}
        if conn:
            try:
                results_data = conn.execute(
                    'SELECT * FROM results WHERE week = 3 AND season = 2025'
                ).fetchall()
                
                for result in results_data:
                    game_key = f"{result['away_team']}@{result['home_team']}"
                    results[game_key] = {
                        'home_score': result['home_score'],
                        'away_score': result['away_score'],
                        'actual_winner': result['actual_winner']
                    }
                conn.close()
            except Exception as e:
                logger.error(f"Error getting results: {e}")
                if conn:
                    conn.close()
        
        return render_template('home_with_predictions.html', 
                             predictions=predictions, 
                             results=results,
                             current_week=3)
        
    except Exception as e:
        logger.error(f"Index page error: {e}")
        return render_template('home_with_predictions.html', 
                             predictions=get_week3_predictions(), 
                             results={},
                             current_week=3)

@app.route('/stats')
def stats():
    """Display model statistics"""
    try:
        # Initialize database first
        init_db()
        
        conn = get_db_connection()
        if not conn:
            return render_template('stats_simple.html', 
                                 total_predictions=0,
                                 correct_predictions=0,
                                 accuracy=0,
                                 weekly_stats={})
        
        # Check if tables exist
        try:
            # Get all predictions with results
            stats_data = conn.execute('''
                SELECT p.*, r.home_score, r.away_score, r.actual_winner
                FROM predictions p
                LEFT JOIN results r ON p.week = r.week AND p.season = r.season 
                    AND p.home_team = r.home_team AND p.away_team = r.away_team
                WHERE p.season = 2025
                ORDER BY p.week, p.home_team
            ''').fetchall()
        except sqlite3.OperationalError as e:
            logger.error(f"Stats database error: {e}")
            conn.close()
            return render_template('stats_simple.html', 
                                 total_predictions=0,
                                 correct_predictions=0,
                                 accuracy=0,
                                 weekly_stats={})
        
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
        
        return render_template('stats_simple.html', 
                             total_predictions=total_predictions,
                             correct_predictions=correct_predictions,
                             accuracy=accuracy,
                             weekly_stats=weekly_stats)
    except Exception as e:
        logger.error(f"Stats page error: {e}")
        return render_template('stats_simple.html', 
                             total_predictions=0,
                             correct_predictions=0,
                             accuracy=0,
                             weekly_stats={})

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
