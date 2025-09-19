#!/usr/bin/env python3
"""
NFL Predictions Website Runner
Simple script to start the Flask web application
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import pandas
        import numpy
        import requests
        import bs4
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements with: pip install -r requirements.txt")
        return False

def main():
    """Main function to run the website"""
    print("🌊 NFL Predictions Website")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("❌ app.py not found in current directory")
        sys.exit(1)
    
    print("🚀 Starting NFL Predictions Website...")
    print("📱 Website will be available at: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 40)
    
    try:
        # Run the Flask app
        os.system('python3 app.py')
    except KeyboardInterrupt:
        print("\n👋 Website stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error running website: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
