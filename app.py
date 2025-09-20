"""
Working NFL Predictions Website
"""

from flask import Flask
import os

app = Flask(__name__)

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

@app.route('/')
def index():
    """Home page"""
    return redirect_to_week3()

@app.route('/week/3')
def week3():
    """Week 3 predictions"""
    predictions = get_week3_predictions()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Week 3 - The RIVERS Model</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background-color: #f8f9fa; }
            .card { border: none; box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075); }
            .card-header { background: linear-gradient(135deg, #007bff, #0056b3); color: white; }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/">The RIVERS Model</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/week/3">Week 3 Predictions</a>
                    <a class="nav-link" href="/stats">Statistics</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="card">
                <div class="card-header">
                    <h2 class="mb-0">Week 3 NFL Predictions</h2>
                </div>
                <div class="card-body">
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
                                    <p><strong>🏆 Winner:</strong> {prediction['winner']}</p>
                                    <p><strong>🎯 Confidence:</strong> {prediction['confidence']:.1f}%</p>
                                    <p><strong>🏥 Injury Report:</strong> {prediction['injury_report']}</p>
                                </div>
                            </div>
                        </div>
        """
    
    html += """
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/stats')
def stats():
    """Statistics page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Statistics - The RIVERS Model</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/">The RIVERS Model</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/week/3">Week 3 Predictions</a>
                    <a class="nav-link active" href="/stats">Statistics</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <h1>Model Statistics</h1>
            <div class="row">
                <div class="col-md-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title">Total Predictions</h5>
                            <h2 class="text-primary">16</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title">Correct Predictions</h5>
                            <h2 class="text-success">0</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title">Accuracy</h5>
                            <h2 class="text-info">0.0%</h2>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

def redirect_to_week3():
    """Redirect to week 3"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="refresh" content="0; url=/week/3">
    </head>
    <body>
        <p>Redirecting to Week 3 predictions...</p>
        <a href="/week/3">Click here if not redirected automatically</a>
    </body>
    </html>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
