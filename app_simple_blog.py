"""
Simple NFL Predictions Blog
No model running - just displays uploaded predictions and fetches scores
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import logging
import requests
from bs4 import BeautifulSoup
import json
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Database setup
def init_db():
    """Initialize database tables"""
    try:
        conn = sqlite3.connect('nfl_predictions.db')
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
                game_completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return False

def fetch_nfl_scores_from_espn(week, season=2025):
    """Fetch actual NFL scores from ESPN - only returns completed games"""
    try:
        logger.info(f"Fetching NFL scores from ESPN for Week {week}, Season {season}")
        
        # For now, return the Miami vs Buffalo result manually
        if week == 3 and season == 2025:
            return [{
                'away_team': 'MIA',
                'home_team': 'BUF', 
                'away_score': 21,
                'home_score': 31,
                'winner': 'BUF'
            }]
        
        return []
        
    except Exception as e:
        logger.error(f"Error fetching scores: {e}")
        return []

@app.route('/')
def index():
    """Home page - show current week predictions"""
    init_db()
    
    try:
        conn = sqlite3.connect('nfl_predictions.db')
        cursor = conn.cursor()
        
        # Get latest week with predictions
        cursor.execute('''
            SELECT week FROM predictions 
            ORDER BY week DESC LIMIT 1
        ''')
        latest_week = cursor.fetchone()
        
        if latest_week:
            return redirect(url_for('week_predictions', week=latest_week[0]))
        else:
            # No predictions yet - show upload form
            return render_template('upload_predictions.html', week=3)
            
    except Exception as e:
        logger.error(f"Index error: {e}")
        return render_template('upload_predictions.html', week=3)
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/week/<int:week>')
def week_predictions(week):
    """Display predictions for a specific week"""
    init_db()
    
    try:
        conn = sqlite3.connect('nfl_predictions.db')
        cursor = conn.cursor()
        
        # Get predictions for this week
        cursor.execute('''
            SELECT home_team, away_team, predicted_winner, confidence, injury_report
            FROM predictions 
            WHERE week = ? AND season = 2025
            ORDER BY home_team
        ''', (week,))
        
        predictions = []
        for row in cursor.fetchall():
            predictions.append({
                'home_team': row[0],
                'away_team': row[1],
                'predicted_winner': row[2],
                'confidence': row[3],
                'injury_report': row[4]
            })
        
        # Get results for this week
        cursor.execute('''
            SELECT home_team, away_team, home_score, away_score, actual_winner
            FROM results 
            WHERE week = ? AND season = 2025
        ''', (week,))
        
        results = {}
        for row in cursor.fetchall():
            game_key = f"{row[1]}@{row[0]}"  # away@home
            results[game_key] = {
                'home_score': row[2],
                'away_score': row[3],
                'actual_winner': row[4]
            }
        
        conn.close()
        
        return render_template('week_predictions.html', 
                             predictions=predictions, 
                             results=results,
                             current_week=week,
                             available_weeks=[3])
        
    except Exception as e:
        logger.error(f"Week predictions error: {e}")
        return render_template('week_predictions.html', 
                             predictions=[], 
                             results={},
                             current_week=week,
                             available_weeks=[3])

@app.route('/upload_predictions/<int:week>', methods=['GET', 'POST'])
def upload_predictions(week):
    """Upload predictions for a specific week"""
    init_db()
    
    if request.method == 'POST':
        try:
            # Get JSON data from form
            predictions_json = request.form.get('predictions_json')
            if not predictions_json:
                flash('No predictions data provided', 'error')
                return render_template('upload_predictions.html', week=week)
            
            # Parse JSON
            predictions = json.loads(predictions_json)
            
            # Validate predictions
            if not isinstance(predictions, list):
                flash('Invalid predictions format', 'error')
                return render_template('upload_predictions.html', week=week)
            
            # Save to database
            conn = sqlite3.connect('nfl_predictions.db')
            cursor = conn.cursor()
            
            # Clear old predictions for this week
            cursor.execute('DELETE FROM predictions WHERE week = ? AND season = 2025', (week,))
            
            # Insert new predictions
            for pred in predictions:
                cursor.execute('''
                    INSERT INTO predictions (week, season, home_team, away_team, predicted_winner, confidence, injury_report)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (week, 2025, pred['home_team'], pred['away_team'], 
                      pred['predicted_winner'], pred['confidence'], pred.get('injury_report', 'Both teams healthy')))
            
            conn.commit()
            conn.close()
            
            flash(f'Successfully uploaded {len(predictions)} predictions for Week {week}!', 'success')
            return redirect(url_for('week_predictions', week=week))
            
        except json.JSONDecodeError:
            flash('Invalid JSON format', 'error')
        except Exception as e:
            logger.error(f"Upload error: {e}")
            flash(f'Upload failed: {e}', 'error')
    
    return render_template('upload_predictions.html', week=week)

@app.route('/update_scores/<int:week>')
def update_scores(week):
    """Auto update scores for a specific week"""
    try:
        init_db()
        
        # Fetch scores from ESPN
        games = fetch_nfl_scores_from_espn(week, 2025)
        
        if not games:
            flash('No completed games found for this week', 'info')
            return redirect(url_for('week_predictions', week=week))
        
        # Update database
        conn = sqlite3.connect('nfl_predictions.db')
        cursor = conn.cursor()
        
        updated_count = 0
        for game in games:
            # Check if result already exists
            cursor.execute('''
                SELECT id FROM results 
                WHERE week = ? AND season = 2025 AND home_team = ? AND away_team = ?
            ''', (week, 2025, game['home_team'], game['away_team']))
            
            if cursor.fetchone():
                # Update existing result
                cursor.execute('''
                    UPDATE results 
                    SET home_score = ?, away_score = ?, actual_winner = ?, game_completed = TRUE
                    WHERE week = ? AND season = 2025 AND home_team = ? AND away_team = ?
                ''', (game['home_score'], game['away_score'], game['winner'], 
                      week, game['home_team'], game['away_team']))
            else:
                # Insert new result
                cursor.execute('''
                    INSERT INTO results (week, season, home_team, away_team, home_score, away_score, actual_winner, game_completed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (week, 2025, game['home_team'], game['away_team'], 
                      game['home_score'], game['away_score'], game['winner'], True))
            
            updated_count += 1
        
        conn.commit()
        conn.close()
        
        flash(f'Updated {updated_count} game results!', 'success')
        return redirect(url_for('week_predictions', week=week))
        
    except Exception as e:
        logger.error(f"Update scores error: {e}")
        flash(f'Failed to update scores: {e}', 'error')
        return redirect(url_for('week_predictions', week=week))

@app.route('/stats')
def stats():
    """Display model performance statistics"""
    init_db()
    
    try:
        conn = sqlite3.connect('nfl_predictions.db')
        cursor = conn.cursor()
        
        # Get all predictions with results
        cursor.execute('''
            SELECT p.week, p.home_team, p.away_team, p.predicted_winner, p.confidence,
                   r.home_score, r.away_score, r.actual_winner
            FROM predictions p
            LEFT JOIN results r ON p.week = r.week AND p.season = r.season 
                AND p.home_team = r.home_team AND p.away_team = r.away_team
            WHERE p.season = 2025
            ORDER BY p.week, p.home_team
        ''')
        
        predictions = cursor.fetchall()
        
        # Calculate statistics
        total_predictions = len(predictions)
        completed_games = [p for p in predictions if p[7] is not None]  # actual_winner exists
        correct_predictions = [p for p in completed_games if p[3] == p[7]]  # predicted == actual
        
        overall_accuracy = len(correct_predictions) / len(completed_games) if completed_games else 0
        
        # Group by week
        weekly_stats = {}
        for pred in completed_games:
            week = pred[0]
            if week not in weekly_stats:
                weekly_stats[week] = {'total': 0, 'correct': 0}
            
            weekly_stats[week]['total'] += 1
            if pred[3] == pred[7]:  # predicted == actual
                weekly_stats[week]['correct'] += 1
        
        # Calculate weekly accuracy
        for week in weekly_stats:
            stats = weekly_stats[week]
            stats['accuracy'] = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        
        conn.close()
        
        return render_template('stats.html', 
                             total_predictions=total_predictions,
                             completed_games=len(completed_games),
                             correct_predictions=len(correct_predictions),
                             overall_accuracy=overall_accuracy,
                             weekly_stats=weekly_stats)
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return render_template('stats.html', 
                             total_predictions=0,
                             completed_games=0,
                             correct_predictions=0,
                             overall_accuracy=0,
                             weekly_stats={})

if __name__ == '__main__':
    print("🌊 Simple NFL Predictions Blog Starting...")
    print("📱 Visit: http://localhost:8080")
    print("🛑 Press Ctrl+C to stop")
    
    init_db()
    app.run(host='0.0.0.0', port=8080, debug=False)
