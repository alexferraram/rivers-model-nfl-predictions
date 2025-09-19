#!/usr/bin/env python3
"""
🚀 The RIVERS Model - AI NFL Predictions
Deployment Script for Live Website

This script helps you deploy your NFL predictions website to the internet
with a custom domain name.
"""

import os
import subprocess
import sys

def print_banner():
    print("🌊" + "="*60)
    print("🚀 THE RIVERS MODEL - AI NFL PREDICTIONS")
    print("🌊" + "="*60)
    print("Deploy your NFL predictions website to the internet!")
    print()

def check_requirements():
    """Check if all required files are present"""
    required_files = [
        'app_production.py',
        'requirements.txt',
        'templates/',
        'static/',
        'rivers_model_validated.py',
        'pff_data_system.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files present!")
    return True

def create_gitignore():
    """Create .gitignore file for deployment"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Database
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Temporary files
*.tmp
*.temp

# Local development
.env
config.local.py
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore file")

def setup_git_repo():
    """Initialize git repository if needed"""
    if not os.path.exists('.git'):
        print("📦 Setting up Git repository...")
        subprocess.run(['git', 'init'], check=True)
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit: The RIVERS Model - AI NFL Predictions'], check=True)
        print("✅ Git repository initialized")
    else:
        print("✅ Git repository already exists")

def show_deployment_options():
    """Show deployment platform options"""
    print("\n🌐 DEPLOYMENT PLATFORM OPTIONS:")
    print("="*50)
    
    print("\n🥇 RAILWAY (Recommended)")
    print("   ✅ Free tier: 500 hours/month")
    print("   ✅ Custom domains included")
    print("   ✅ Automatic deployments")
    print("   ✅ Built-in database")
    print("   💰 Cost: Free, then $5/month")
    print("   🔗 Website: https://railway.app")
    
    print("\n🥈 RENDER (Completely Free)")
    print("   ✅ 100% free tier")
    print("   ✅ Custom domains included")
    print("   ✅ Automatic SSL")
    print("   ✅ No credit card required")
    print("   💰 Cost: Completely free")
    print("   🔗 Website: https://render.com")
    
    print("\n🥉 VERCEL (Developer-Friendly)")
    print("   ✅ Free tier available")
    print("   ✅ Custom domains included")
    print("   ✅ Fast deployments")
    print("   ✅ Great performance")
    print("   💰 Cost: Free tier available")
    print("   🔗 Website: https://vercel.com")

def show_railway_steps():
    """Show Railway deployment steps"""
    print("\n🚂 RAILWAY DEPLOYMENT STEPS:")
    print("="*40)
    print("1. 🌐 Go to https://railway.app")
    print("2. 📝 Sign up with GitHub account")
    print("3. ➕ Click 'New Project'")
    print("4. 🔗 Select 'Deploy from GitHub repo'")
    print("5. 📁 Choose your NFL repository")
    print("6. ⚙️  Railway auto-detects Flask app")
    print("7. 🚀 Click 'Deploy'")
    print("8. 🌍 Your site goes live!")
    print("9. 🔗 Get your URL: https://your-app.railway.app")
    print("10. 🌐 Add custom domain in Railway dashboard")

def show_render_steps():
    """Show Render deployment steps"""
    print("\n🎨 RENDER DEPLOYMENT STEPS:")
    print("="*35)
    print("1. 🌐 Go to https://render.com")
    print("2. 📝 Sign up with GitHub account")
    print("3. ➕ Click 'New +' → 'Web Service'")
    print("4. 🔗 Connect your GitHub repository")
    print("5. ⚙️  Configure:")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: python app_production.py")
    print("6. 🚀 Click 'Create Web Service'")
    print("7. 🌍 Your site goes live!")
    print("8. 🔗 Get your URL: https://your-app.onrender.com")
    print("9. 🌐 Add custom domain in Render dashboard")

def show_custom_domain_info():
    """Show custom domain setup information"""
    print("\n🌐 CUSTOM DOMAIN SETUP:")
    print("="*30)
    print("1. 🛒 Buy domain from:")
    print("   - Namecheap.com ($8-15/year)")
    print("   - GoDaddy.com ($10-20/year)")
    print("   - Google Domains ($12/year)")
    print("   - Cloudflare ($8-12/year)")
    
    print("\n2. 🔧 Domain suggestions:")
    print("   - riversmodel.com")
    print("   - nflrivers.com")
    print("   - riverspredictions.com")
    print("   - airivers.com")
    print("   - riversai.com")
    
    print("\n3. ⚙️  DNS Configuration:")
    print("   - Add CNAME record pointing to your platform")
    print("   - Railway: your-app.railway.app")
    print("   - Render: your-app.onrender.com")
    print("   - Platform handles SSL automatically")

def main():
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Please ensure all required files are present before deploying.")
        return
    
    # Setup files
    create_gitignore()
    setup_git_repo()
    
    # Show options
    show_deployment_options()
    
    print("\n" + "="*60)
    print("🎯 RECOMMENDED NEXT STEPS:")
    print("="*60)
    
    choice = input("\nChoose deployment platform (1=Railway, 2=Render, 3=Both): ").strip()
    
    if choice == "1":
        show_railway_steps()
    elif choice == "2":
        show_render_steps()
    elif choice == "3":
        show_railway_steps()
        show_render_steps()
    else:
        print("❌ Invalid choice. Showing Railway steps by default.")
        show_railway_steps()
    
    show_custom_domain_info()
    
    print("\n" + "="*60)
    print("🎉 READY TO DEPLOY!")
    print("="*60)
    print("Your website files are ready for deployment.")
    print("Follow the steps above to make 'The RIVERS Model' live!")
    print("\n💡 Pro tip: Start with Railway for the best experience!")

if __name__ == "__main__":
    main()
