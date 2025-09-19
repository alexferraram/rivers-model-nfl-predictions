#!/usr/bin/env python3
"""
Quick Deployment Script for NFL Predictions Website
This script helps you deploy your website quickly
"""

import os
import subprocess
import sys

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import flask
        print("✅ Flask is installed")
        return True
    except ImportError:
        print("❌ Flask not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "flask", "pandas", "numpy", "requests", "beautifulsoup4", "lxml"])
        return True

def get_local_ip():
    """Get local IP address for network access"""
    import socket
    try:
        # Connect to a remote server to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def run_local_server():
    """Run the website locally with network access"""
    print("🌊 NFL Predictions Website - Local Server")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("❌ Failed to install requirements")
        return
    
    # Initialize database
    try:
        from app import init_db
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return
    
    # Get IP address
    ip = get_local_ip()
    
    print(f"🚀 Starting server...")
    print(f"📱 Local access: http://localhost:5000")
    print(f"🌐 Network access: http://{ip}:5000")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Run the production app
        os.system('python3 app_production.py')
    except KeyboardInterrupt:
        print("\n👋 Server stopped!")

def show_deployment_options():
    """Show deployment options"""
    print("\n🚀 DEPLOYMENT OPTIONS")
    print("=" * 30)
    print("1. Railway (Recommended)")
    print("   - Go to railway.app")
    print("   - Connect GitHub repo")
    print("   - Auto-deploy")
    print("   - Free tier available")
    print()
    print("2. Render (Free)")
    print("   - Go to render.com")
    print("   - Create web service")
    print("   - Connect GitHub repo")
    print("   - Completely free")
    print()
    print("3. Heroku")
    print("   - Install Heroku CLI")
    print("   - heroku create your-app-name")
    print("   - git push heroku main")
    print()
    print("4. PythonAnywhere")
    print("   - Go to pythonanywhere.com")
    print("   - Upload files")
    print("   - Create web app")

def main():
    """Main function"""
    print("NFL Predictions Website - Quick Deploy")
    print("=" * 40)
    print("Choose an option:")
    print("1. Run locally (accessible on your network)")
    print("2. Show deployment options")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        run_local_server()
    elif choice == "2":
        show_deployment_options()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == '__main__':
    main()
