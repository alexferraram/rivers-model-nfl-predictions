#!/usr/bin/env python3
"""
GitHub Setup Script for The RIVERS Model
This script helps you push your code to GitHub for deployment
"""

import subprocess
import os

def print_banner():
    print("🌊" + "="*60)
    print("📦 GITHUB SETUP FOR THE RIVERS MODEL")
    print("🌊" + "="*60)
    print("Let's get your code on GitHub so you can deploy it!")
    print()

def check_git_status():
    """Check if git repository is ready"""
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True, cwd='/Users/alexferraramorales/NFL')
        if result.returncode == 0:
            print("✅ Git repository is ready!")
            return True
        else:
            print("❌ Git repository not found")
            return False
    except Exception as e:
        print(f"❌ Error checking git status: {e}")
        return False

def show_github_steps():
    """Show step-by-step GitHub setup"""
    print("\n📝 STEP-BY-STEP GITHUB SETUP:")
    print("="*40)
    
    print("\n1. 🌐 Go to GitHub.com")
    print("   - Sign in to your account (or create one)")
    
    print("\n2. ➕ Create New Repository")
    print("   - Click the '+' icon in top right")
    print("   - Select 'New repository'")
    
    print("\n3. 📝 Fill Out Repository Details")
    print("   - Repository name: rivers-model-nfl-predictions")
    print("   - Description: The RIVERS Model - AI NFL Predictions Website")
    print("   - Make it PUBLIC (important for free deployment)")
    print("   - DON'T check 'Add a README file'")
    print("   - DON'T check 'Add .gitignore'")
    print("   - DON'T check 'Choose a license'")
    print("   - Click 'Create repository'")
    
    print("\n4. 🔗 Copy the Repository URL")
    print("   - GitHub will show you a URL like:")
    print("   - https://github.com/YOUR_USERNAME/rivers-model-nfl-predictions.git")
    print("   - Copy this URL!")

def show_terminal_commands():
    """Show the terminal commands to run"""
    print("\n💻 TERMINAL COMMANDS TO RUN:")
    print("="*35)
    print("After creating the GitHub repository, run these commands:")
    print()
    print("cd /Users/alexferraramorales/NFL")
    print("git remote add origin https://github.com/YOUR_USERNAME/rivers-model-nfl-predictions.git")
    print("git branch -M main")
    print("git push -u origin main")
    print()
    print("Replace YOUR_USERNAME with your actual GitHub username!")

def show_render_steps():
    """Show Render deployment steps after GitHub setup"""
    print("\n🚀 AFTER GITHUB SETUP - RENDER DEPLOYMENT:")
    print("="*50)
    print("1. 🌐 Go to https://render.com")
    print("2. 📝 Sign up with your GitHub account")
    print("3. ➕ Click 'New +' → 'Web Service'")
    print("4. 🔗 Connect GitHub Account (if not already connected)")
    print("5. 📁 Select your repository: rivers-model-nfl-predictions")
    print("6. ⚙️  Configure the service:")
    print("   - Name: rivers-model-nfl")
    print("   - Environment: Python 3")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: python app_production.py")
    print("7. 🚀 Click 'Create Web Service'")
    print("8. ⏳ Wait for deployment (5-10 minutes)")
    print("9. 🌍 Your site will be live!")

def show_railway_steps():
    """Show Railway deployment steps after GitHub setup"""
    print("\n🚂 AFTER GITHUB SETUP - RAILWAY DEPLOYMENT:")
    print("="*50)
    print("1. 🌐 Go to https://railway.app")
    print("2. 📝 Sign up with your GitHub account")
    print("3. ➕ Click 'New Project'")
    print("4. 🔗 Select 'Deploy from GitHub repo'")
    print("5. 📁 Choose your repository: rivers-model-nfl-predictions")
    print("6. ⚙️  Railway auto-detects Flask app")
    print("7. 🚀 Click 'Deploy'")
    print("8. ⏳ Wait for deployment (3-5 minutes)")
    print("9. 🌍 Your site will be live!")

def main():
    print_banner()
    
    # Check git status
    if not check_git_status():
        print("\n❌ Please run the deployment script first to set up git repository.")
        return
    
    # Show steps
    show_github_steps()
    show_terminal_commands()
    
    print("\n" + "="*60)
    print("🎯 CHOOSE YOUR DEPLOYMENT PLATFORM:")
    print("="*60)
    
    choice = input("\nWhich platform? (1=Render, 2=Railway, 3=Both): ").strip()
    
    if choice == "1":
        show_render_steps()
    elif choice == "2":
        show_railway_steps()
    elif choice == "3":
        show_render_steps()
        show_railway_steps()
    else:
        print("❌ Invalid choice. Showing Render steps by default.")
        show_render_steps()
    
    print("\n" + "="*60)
    print("🎉 READY TO DEPLOY!")
    print("="*60)
    print("1. Create GitHub repository (follow steps above)")
    print("2. Run terminal commands")
    print("3. Deploy to your chosen platform")
    print("4. Share your live website!")
    print("\n💡 Pro tip: Start with Render for completely free deployment!")

if __name__ == "__main__":
    main()
