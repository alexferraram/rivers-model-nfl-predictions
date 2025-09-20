#!/usr/bin/env python3
"""
Script to help upload files to GitHub repository
This script will create a zip file with the updated files that you can upload manually
"""

import os
import zipfile
import shutil
from datetime import datetime

def create_deployment_package():
    """Create a zip file with the files that need to be updated on GitHub"""
    
    # Files that need to be updated
    files_to_include = [
        'app_2025_week3.py',
        'dynamic_injury_system.py',
        'nfl_predictions.db',
        'requirements.txt'
    ]
    
    # Create zip file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"rivers_model_update_{timestamp}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files_to_include:
            if os.path.exists(file):
                zipf.write(file)
                print(f"✅ Added {file} to deployment package")
            else:
                print(f"❌ File {file} not found")
    
    print(f"\n📦 Deployment package created: {zip_filename}")
    print("\n📋 Instructions:")
    print("1. Go to https://github.com/alexferraram/rivers-model-nfl-predictions")
    print("2. Click 'Add file' > 'Upload files'")
    print(f"3. Upload the zip file: {zip_filename}")
    print("4. Extract and replace the files in your repository")
    print("5. Commit the changes")
    print("6. Render will automatically deploy the updates")
    
    return zip_filename

if __name__ == "__main__":
    create_deployment_package()
