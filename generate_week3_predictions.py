#!/usr/bin/env python3
"""
Generate Week 3 predictions and format them for upload to the website
"""

from rivers_model_validated import RiversModelValidated
import json

def main():
    print("🚀 Generating Week 3 predictions...")
    
    # Initialize RIVERS model
    model = RiversModelValidated()
    
    # Generate predictions
    predictions = model.generate_week3_predictions()
    
    if predictions is None:
        print("❌ No predictions generated")
        return
    
    print(f"✅ Generated {len(predictions)} predictions")
    
    # Format for upload
    upload_data = []
    for pred in predictions:
        # Format injury report
        injury_report = "Both teams healthy"
        if pred.get('home_details', {}).get('injury_details', {}).get('total_impact', 0) > 0 or \
           pred.get('away_details', {}).get('injury_details', {}).get('total_impact', 0) > 0:
            
            home_injuries = pred.get('home_details', {}).get('injury_details', {}).get('injuries', [])
            away_injuries = pred.get('away_details', {}).get('injury_details', {}).get('injuries', [])
            
            injury_parts = []
            if home_injuries:
                home_list = [f"{inj['player']} ({inj['position']}) - {inj['status']}" for inj in home_injuries]
                injury_parts.append(f"{pred['home_team']}: {', '.join(home_list)}")
            
            if away_injuries:
                away_list = [f"{inj['player']} ({inj['position']}) - {inj['status']}" for inj in away_injuries]
                injury_parts.append(f"{pred['away_team']}: {', '.join(away_list)}")
            
            if injury_parts:
                injury_report = " | ".join(injury_parts)
        
        upload_data.append({
            'home_team': pred['home_team'],
            'away_team': pred['away_team'],
            'winner': pred['winner'],
            'confidence': pred['confidence'],
            'injury_report': injury_report
        })
    
    # Save to file
    with open('week3_predictions.json', 'w') as f:
        json.dump(upload_data, f, indent=2)
    
    print("📁 Predictions saved to week3_predictions.json")
    print("\n📋 Sample predictions:")
    for i, pred in enumerate(upload_data[:3]):
        print(f"{i+1}. {pred['away_team']} @ {pred['home_team']}")
        print(f"   Winner: {pred['winner']} ({pred['confidence']*100:.1f}%)")
        print(f"   Injuries: {pred['injury_report']}")
        print()
    
    print("✅ Ready to upload to website!")

if __name__ == "__main__":
    main()
