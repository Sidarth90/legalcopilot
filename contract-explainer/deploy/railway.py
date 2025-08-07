#!/usr/bin/env python3
"""
Contract Explainer - Railway Deployment Script
Automated deployment to Railway platform
"""

import os
import sys
import subprocess
import json
import yaml
from pathlib import Path

class RailwayDeployer:
    def __init__(self):
        self.project_name = "contract-explainer"
        self.required_vars = [
            "DEEPSEEK_API_KEY",
            "FLASK_SECRET_KEY",
            "GOOGLE_ADSENSE_CLIENT_ID"
        ]
    
    def check_prerequisites(self):
        """Check if Railway CLI is installed and user is logged in"""
        print("🔍 Checking prerequisites...")
        
        # Check Railway CLI
        try:
            result = subprocess.run(['railway', '--version'], 
                                  capture_output=True, text=True)
            print(f"✅ Railway CLI: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ Railway CLI not found. Install from: https://docs.railway.app/develop/cli")
            return False
        
        # Check login status
        try:
            result = subprocess.run(['railway', 'whoami'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Logged in as: {result.stdout.strip()}")
            else:
                print("❌ Not logged in to Railway. Run: railway login")
                return False
        except:
            print("❌ Could not check Railway login status")
            return False
            
        return True
    
    def create_railway_files(self):
        """Create Railway-specific deployment files"""
        print("📝 Creating Railway deployment files...")
        
        # railway.json
        railway_config = {
            "build": {
                "builder": "DOCKERFILE"
            },
            "deploy": {
                "startCommand": "gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120",
                "restartPolicyType": "ON_FAILURE",
                "restartPolicyMaxRetries": 10
            }
        }
        
        with open('railway.json', 'w') as f:
            json.dump(railway_config, f, indent=2)
        print("✅ Created railway.json")
        
        # .railwayignore
        railwayignore_content = """.git/
.env.example
*.md
README*
.gitignore
.dockerignore
docker-compose*.yml
.vscode/
.idea/
__pycache__/
*.pyc
*.log
uploads/*
!uploads/.gitkeep
"""
        
        with open('.railwayignore', 'w') as f:
            f.write(railwayignore_content)
        print("✅ Created .railwayignore")
    
    def create_project(self):
        """Create Railway project"""
        print(f"🏗️  Creating Railway project: {self.project_name}...")
        
        try:
            # Initialize project
            result = subprocess.run([
                'railway', 'project', 'create', '--name', self.project_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Created project: {self.project_name}")
                return True
            else:
                if "already exists" in result.stderr.lower():
                    print(f"ℹ️  Project {self.project_name} already exists")
                    return True
                else:
                    print(f"❌ Failed to create project: {result.stderr}")
                    return False
        except Exception as e:
            print(f"❌ Error creating project: {e}")
            return False
    
    def link_project(self):
        """Link to Railway project"""
        print("🔗 Linking to Railway project...")
        
        try:
            result = subprocess.run([
                'railway', 'link', self.project_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Linked to project")
                return True
            else:
                print(f"⚠️  Could not link: {result.stderr}")
                return True  # Continue even if linking fails
        except Exception as e:
            print(f"❌ Error linking project: {e}")
            return False
    
    def set_environment_variables(self):
        """Set environment variables from .env file"""
        print("🔧 Setting environment variables...")
        
        # Production environment variables
        prod_vars = {
            'FLASK_ENV': 'production',
            'FLASK_DEBUG': '0',
            'FLASK_HOST': '0.0.0.0',
            'PORT': '5001'
        }
        
        # Load from .env file if exists
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        
                        if key in self.required_vars or key.startswith('FLASK_'):
                            prod_vars[key] = value
        
        # Set all environment variables
        for key, value in prod_vars.items():
            try:
                result = subprocess.run([
                    'railway', 'variables', 'set', f'{key}={value}'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Set {key}")
                else:
                    print(f"❌ Failed to set {key}: {result.stderr}")
            except Exception as e:
                print(f"❌ Error setting {key}: {e}")
    
    def add_services(self):
        """Add Railway services (Redis, etc.)"""
        print("🔌 Adding services...")
        
        try:
            # Add Redis service
            result = subprocess.run([
                'railway', 'service', 'create', 'redis'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Added Redis service")
            else:
                print(f"⚠️  Could not add Redis: {result.stderr}")
        except Exception as e:
            print(f"❌ Error adding Redis: {e}")
    
    def deploy(self):
        """Deploy to Railway"""
        print("🚀 Deploying to Railway...")
        
        try:
            result = subprocess.run([
                'railway', 'up', '--detach'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Deployment started!")
                print("⏳ Waiting for deployment to complete...")
                
                # Get deployment status
                status_result = subprocess.run([
                    'railway', 'status'
                ], capture_output=True, text=True)
                
                if status_result.returncode == 0:
                    print("✅ Deployment successful!")
                    return True
                
            else:
                print(f"❌ Deployment failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Deployment error: {e}")
            return False
    
    def get_domain(self):
        """Get the Railway-generated domain"""
        try:
            result = subprocess.run([
                'railway', 'domain'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                domain = result.stdout.strip()
                print(f"🌐 Your app is live at: https://{domain}")
                return domain
            else:
                print("⚠️  Could not retrieve domain")
                return None
        except Exception as e:
            print(f"❌ Error getting domain: {e}")
            return None
    
    def run_deployment(self):
        """Run the complete deployment process"""
        print("🚀 Starting Railway deployment for Contract Explainer\n")
        
        if not self.check_prerequisites():
            return False
        
        self.create_railway_files()
        
        if not self.create_project():
            return False
        
        if not self.link_project():
            return False
        
        self.set_environment_variables()
        self.add_services()
        
        if self.deploy():
            domain = self.get_domain()
            print("\n🎉 Deployment completed successfully!")
            if domain:
                print(f"📱 App: https://{domain}")
            print("📊 Dashboard: https://railway.app/dashboard")
            print("\n📝 Next steps:")
            print("1. Configure custom domain if needed")
            print("2. Set up monitoring and logs")
            print("3. Configure environment-specific settings")
            
            return True
        
        return False

if __name__ == "__main__":
    deployer = RailwayDeployer()
    success = deployer.run_deployment()
    sys.exit(0 if success else 1)