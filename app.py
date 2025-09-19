"""
NFL Predictions Website - Flask Application
Displays RIVERS model predictions week by week with historical tracking
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import json
import os
from datetime import datetime
from rivers_model_validated import RiversModelValidated

app = Flask(__name__)
app.secret_key = 'nfl_predictions_secret_key_2025'

# Database setup
DATABASE = 'nfl_predictions.db'

def init_db():
    """Initialize the database with required tables"""
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

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def format_injury_report(injury_data):
    """Format injury report without percentage impacts"""
    if not injury_data:
        return "Both teams healthy"
    
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

@app.route('/')
def index():
    """Home page - show current week predictions"""
    conn = get_db_connection()
    
    # Get the latest week with predictions
    latest_week = conn.execute(
        'SELECT MAX(week) as max_week FROM predictions WHERE season = 2025'
    ).fetchone()
    
    if latest_week['max_week']:
        return redirect(url_for('week_predictions', week=latest_week['max_week']))
    else:
        return render_template('index.html', message="No predictions available yet")

@app.route('/week/<int:week>')
def week_predictions(week):
    """Display predictions for a specific week"""
    conn = get_db_connection()
    
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

@app.route('/generate_predictions/<int:week>')
def generate_predictions(week):
    """Generate predictions for a specific week using RIVERS model"""
    try:
        # Initialize RIVERS model
        model = RiversModelValidated()
        
        # Generate predictions
        predictions = model.generate_week3_predictions()  # This will be updated to handle different weeks
        
        # Save predictions to database
        conn = get_db_connection()
        
        for prediction in predictions:
            # Format injury report
            injury_report = format_injury_report({
                prediction['home_team']: prediction['home_details'].get('injury_details', {}),
                prediction['away_team']: prediction['away_details'].get('injury_details', {})
            })
            
            conn.execute(
                '''INSERT INTO predictions 
                   (week, season, home_team, away_team, predicted_winner, confidence, injury_report)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (week, 2025, prediction['home_team'], prediction['away_team'], 
                 prediction['winner'], prediction['confidence'], injury_report)
            )
        
        conn.commit()
        conn.close()
        
        flash(f'Successfully generated predictions for Week {week}!', 'success')
        return redirect(url_for('week_predictions', week=week))
        
    except Exception as e:
        flash(f'Error generating predictions: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/update_results/<int:week>', methods=['GET', 'POST'])
def update_results(week):
    """Update game results for a specific week"""
    if request.method == 'POST':
        conn = get_db_connection()
        
        # Get all predictions for this week
        predictions = conn.execute(
            'SELECT * FROM predictions WHERE week = ? AND season = 2025',
            (week,)
        ).fetchall()
        
        for prediction in predictions:
            home_score = request.form.get(f"home_score_{prediction['id']}")
            away_score = request.form.get(f"away_score_{prediction['id']}")
            
            if home_score and away_score:
                # Determine actual winner
                if int(home_score) > int(away_score):
                    actual_winner = prediction['home_team']
                elif int(away_score) > int(home_score):
                    actual_winner = prediction['away_team']
                else:
                    actual_winner = 'TIE'
                
                # Insert or update result
                conn.execute(
                    '''INSERT OR REPLACE INTO results 
                       (week, season, home_team, away_team, home_score, away_score, actual_winner)
                       VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (week, 2025, prediction['home_team'], prediction['away_team'], 
                     int(home_score), int(away_score), actual_winner)
                )
        
        conn.commit()
        conn.close()
        
        flash(f'Successfully updated results for Week {week}!', 'success')
        return redirect(url_for('week_predictions', week=week))
    
    # GET request - show form
    conn = get_db_connection()
    predictions = conn.execute(
        'SELECT * FROM predictions WHERE week = ? AND season = 2025 ORDER BY home_team',
        (week,)
    ).fetchall()
    conn.close()
    
    return render_template('update_results.html', predictions=predictions, week=week)

@app.route('/stats')
def stats():
    """Display model statistics"""
    conn = get_db_connection()
    
    # Get all predictions with results
    stats_data = conn.execute('''
        SELECT p.*, r.home_score, r.away_score, r.actual_winner
        FROM predictions p
        LEFT JOIN results r ON p.week = r.week AND p.season = r.season 
            AND p.home_team = r.home_team AND p.away_team = r.away_team
        WHERE p.season = 2025
        ORDER BY p.week, p.home_team
    ''').fetchall()
    
    # Calculate statistics
    total_predictions = len(stats_data)
    correct_predictions = sum(1 for row in stats_data if row['predicted_winner'] == row['actual_winner'] and row['actual_winner'])
    accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
    
    # Group by week
    weekly_stats = {}
    for row in stats_data:
        week = row['week']
        if week not in weekly_stats:
            weekly_stats[week] = {'total': 0, 'correct': 0}
        
        weekly_stats[week]['total'] += 1
        if row['predicted_winner'] == row['actual_winner'] and row['actual_winner']:
            weekly_stats[week]['correct'] += 1
    
    conn.close()
    
    return render_template('stats.html', 
                         total_predictions=total_predictions,
                         correct_predictions=correct_predictions,
                         accuracy=accuracy,
                         weekly_stats=weekly_stats)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
