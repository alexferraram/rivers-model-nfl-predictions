"""
Injury Penalty System Analysis and Improvement
Analyze current system and propose enhancements for accuracy
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class InjuryPenaltyAnalysis:
    """
    Analyze and improve the injury penalty system
    """
    
    def __init__(self):
        # Current base penalties
        self.current_base_penalties = {
            'QB': -30.0,    # Highest impact
            'RB': -15.0,
            'WR': -15.0,
            'TE': -12.0,
            'OT': -10.0,
            'OG': -8.0,
            'C': -8.0,
            'DE': -10.0,
            'DT': -8.0,
            'LB': -8.0,
            'CB': -10.0,
            'S': -8.0,
            'K': -4.0,
            'P': -3.0,
            'LS': -2.0
        }
        
        # Current dynamic multipliers
        self.current_multipliers = {
            'elite_starter_poor_backup': 1.5,    # Grade diff > 20
            'good_starter_average_backup': 1.2,  # Grade diff > 10
            'starter_better_backup': 1.0,        # Grade diff > 0
            'similar_quality': 0.8,              # Grade diff > -10
            'backup_better': 0.5                 # Grade diff < -10
        }
        
        # Current status multipliers
        self.current_status_multipliers = {
            'OUT': 1.0,
            'DOUBTFUL': 0.7,
            'QUESTIONABLE': 0.0,  # Counted as healthy
            'IR': 1.0
        }
    
    def analyze_current_system(self):
        """Analyze the current injury penalty system"""
        print("🔍 CURRENT INJURY PENALTY SYSTEM ANALYSIS")
        print("=" * 60)
        
        print("\n1. BASE PENALTIES BY POSITION:")
        print("-" * 40)
        for position, penalty in sorted(self.current_base_penalties.items(), key=lambda x: x[1]):
            print(f"   {position:3}: {penalty:6.1f} points")
        
        print("\n2. DYNAMIC MULTIPLIERS:")
        print("-" * 40)
        print("   Grade Difference > 20:  1.5x (Elite starter, poor backup)")
        print("   Grade Difference > 10:  1.2x (Good starter, average backup)")
        print("   Grade Difference > 0:   1.0x (Starter better than backup)")
        print("   Grade Difference > -10: 0.8x (Similar quality)")
        print("   Grade Difference < -10: 0.5x (Backup might be better)")
        
        print("\n3. STATUS MULTIPLIERS:")
        print("-" * 40)
        for status, multiplier in self.current_status_multipliers.items():
            print(f"   {status:12}: {multiplier:.1f}x")
        
        print("\n4. CURRENT SYSTEM ISSUES:")
        print("-" * 40)
        print("   ❌ Position penalties may not reflect actual impact")
        print("   ❌ Dynamic multipliers are too simplistic")
        print("   ❌ No consideration for team depth")
        print("   ❌ No positional importance weighting")
        print("   ❌ No consideration for game situation")
        print("   ❌ No injury history consideration")
    
    def propose_improvements(self):
        """Propose improvements to the injury penalty system"""
        print("\n💡 PROPOSED IMPROVEMENTS")
        print("=" * 60)
        
        print("\n1. ENHANCED POSITION PENALTIES:")
        print("-" * 40)
        enhanced_penalties = self._calculate_enhanced_position_penalties()
        for position, penalty in sorted(enhanced_penalties.items(), key=lambda x: x[1]):
            print(f"   {position:3}: {penalty:6.1f} points")
        
        print("\n2. SOPHISTICATED DYNAMIC MULTIPLIERS:")
        print("-" * 40)
        enhanced_multipliers = self._calculate_enhanced_multipliers()
        for scenario, multiplier in enhanced_multipliers.items():
            print(f"   {scenario:25}: {multiplier:.2f}x")
        
        print("\n3. TEAM DEPTH CONSIDERATION:")
        print("-" * 40)
        print("   • Add depth quality assessment")
        print("   • Consider positional depth charts")
        print("   • Factor in backup experience")
        print("   • Account for positional versatility")
        
        print("\n4. GAME SITUATION FACTORS:")
        print("-" * 40)
        print("   • Playoff implications")
        print("   • Division rivalry games")
        print("   • Weather conditions")
        print("   • Rest advantage")
        
        print("\n5. INJURY HISTORY FACTORS:")
        print("-" * 40)
        print("   • Injury-prone players")
        print("   • Recent injury patterns")
        print("   • Recovery time expectations")
        print("   • Position-specific injury rates")
    
    def _calculate_enhanced_position_penalties(self) -> Dict[str, float]:
        """Calculate enhanced position penalties based on impact analysis"""
        
        # Position impact factors (based on NFL analytics)
        position_impact = {
            'QB': 1.0,      # Highest impact - touches ball every play
            'C': 0.8,       # Center - calls protections, snaps ball
            'OT': 0.7,      # Tackles - protect QB's blind side
            'OG': 0.6,      # Guards - interior protection
            'TE': 0.5,      # Tight ends - blocking and receiving
            'WR': 0.4,      # Receivers - passing game
            'RB': 0.4,      # Running backs - rushing game
            'DE': 0.6,      # Defensive ends - pass rush
            'DT': 0.5,      # Defensive tackles - run defense
            'LB': 0.5,      # Linebackers - run defense and coverage
            'CB': 0.4,      # Cornerbacks - pass coverage
            'S': 0.4,       # Safeties - pass coverage
            'K': 0.2,       # Kickers - special teams
            'P': 0.1,       # Punters - special teams
            'LS': 0.1        # Long snappers - special teams
        }
        
        # Base penalty scale
        base_scale = 25.0
        
        enhanced_penalties = {}
        for position, impact in position_impact.items():
            enhanced_penalties[position] = -(base_scale * impact)
        
        return enhanced_penalties
    
    def _calculate_enhanced_multipliers(self) -> Dict[str, float]:
        """Calculate enhanced dynamic multipliers"""
        
        # More sophisticated multiplier system
        enhanced_multipliers = {
            'Elite starter, poor backup (30+ diff)': 2.0,
            'Elite starter, average backup (20-29 diff)': 1.7,
            'Good starter, poor backup (15-19 diff)': 1.5,
            'Good starter, average backup (10-14 diff)': 1.3,
            'Average starter, poor backup (5-9 diff)': 1.2,
            'Starter better than backup (1-4 diff)': 1.0,
            'Similar quality (-4 to 0 diff)': 0.9,
            'Backup slightly better (-9 to -5 diff)': 0.8,
            'Backup significantly better (-14 to -10 diff)': 0.6,
            'Backup much better (-20 to -15 diff)': 0.4,
            'Backup elite level (-20+ diff)': 0.2
        }
        
        return enhanced_multipliers
    
    def create_enhanced_injury_system(self):
        """Create the enhanced injury penalty system"""
        print("\n🚀 ENHANCED INJURY PENALTY SYSTEM")
        print("=" * 60)
        
        enhanced_penalties = self._calculate_enhanced_position_penalties()
        enhanced_multipliers = self._calculate_enhanced_multipliers()
        
        print("\nENHANCED BASE PENALTIES:")
        print("-" * 30)
        for position, penalty in sorted(enhanced_penalties.items(), key=lambda x: x[1]):
            print(f"   {position:3}: {penalty:6.1f} points")
        
        print("\nENHANCED DYNAMIC MULTIPLIERS:")
        print("-" * 30)
        for scenario, multiplier in enhanced_multipliers.items():
            print(f"   {scenario:35}: {multiplier:.1f}x")
        
        print("\nENHANCED STATUS MULTIPLIERS:")
        print("-" * 30)
        enhanced_status = {
            'OUT': 1.0,
            'DOUBTFUL': 0.8,      # Increased from 0.7
            'QUESTIONABLE': 0.0,   # Still counted as healthy
            'IR': 1.0,
            'PUP': 0.9,           # Physically Unable to Perform
            'NFI': 0.9            # Non-Football Injury
        }
        
        for status, multiplier in enhanced_status.items():
            print(f"   {status:12}: {multiplier:.1f}x")
        
        print("\nNEW FEATURES:")
        print("-" * 30)
        print("   • Team depth quality assessment")
        print("   • Positional importance weighting")
        print("   • Game situation factors")
        print("   • Injury history consideration")
        print("   • Backup experience levels")
        print("   • Positional versatility factors")
    
    def calculate_penalty_examples(self):
        """Calculate examples of enhanced penalties"""
        print("\n📊 ENHANCED PENALTY EXAMPLES")
        print("=" * 60)
        
        enhanced_penalties = self._calculate_enhanced_position_penalties()
        
        examples = [
            {
                'player': 'Josh Allen',
                'position': 'QB',
                'starter_grade': 90.0,
                'backup_grade': 60.0,
                'status': 'OUT',
                'team': 'BUF'
            },
            {
                'player': 'Stefon Diggs',
                'position': 'WR',
                'starter_grade': 85.0,
                'backup_grade': 70.0,
                'status': 'DOUBTFUL',
                'team': 'BUF'
            },
            {
                'player': 'Von Miller',
                'position': 'DE',
                'starter_grade': 80.0,
                'backup_grade': 75.0,
                'status': 'OUT',
                'team': 'BUF'
            }
        ]
        
        for example in examples:
            position = example['position']
            starter_grade = example['starter_grade']
            backup_grade = example['backup_grade']
            status = example['status']
            
            # Calculate grade difference
            grade_diff = starter_grade - backup_grade
            
            # Get enhanced base penalty
            base_penalty = enhanced_penalties[position]
            
            # Get enhanced multiplier
            if grade_diff >= 30:
                multiplier = 2.0
            elif grade_diff >= 20:
                multiplier = 1.7
            elif grade_diff >= 15:
                multiplier = 1.5
            elif grade_diff >= 10:
                multiplier = 1.3
            elif grade_diff >= 5:
                multiplier = 1.2
            elif grade_diff >= 1:
                multiplier = 1.0
            elif grade_diff >= -4:
                multiplier = 0.9
            elif grade_diff >= -9:
                multiplier = 0.8
            elif grade_diff >= -14:
                multiplier = 0.6
            elif grade_diff >= -20:
                multiplier = 0.4
            else:
                multiplier = 0.2
            
            # Get status multiplier
            status_multipliers = {'OUT': 1.0, 'DOUBTFUL': 0.8, 'QUESTIONABLE': 0.0, 'IR': 1.0}
            status_mult = status_multipliers.get(status, 1.0)
            
            # Calculate final penalty
            final_penalty = base_penalty * multiplier * status_mult
            
            print(f"\n{example['player']} ({position}) - {example['team']}:")
            print(f"   Starter Grade: {starter_grade:.1f}")
            print(f"   Backup Grade: {backup_grade:.1f}")
            print(f"   Grade Difference: {grade_diff:.1f}")
            print(f"   Base Penalty: {base_penalty:.1f}")
            print(f"   Dynamic Multiplier: {multiplier:.1f}x")
            print(f"   Status Multiplier: {status_mult:.1f}x")
            print(f"   Final Penalty: {final_penalty:.1f} points")

if __name__ == "__main__":
    analyzer = InjuryPenaltyAnalysis()
    analyzer.analyze_current_system()
    analyzer.propose_improvements()
    analyzer.create_enhanced_injury_system()
    analyzer.calculate_penalty_examples()




