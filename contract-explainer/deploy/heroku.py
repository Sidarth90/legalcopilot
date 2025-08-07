#!/usr/bin/env python3
"""
Contract Explainer - Heroku Deployment Script
Automated deployment to Heroku platform
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class HerokuDeployer:
    def __init__(self):
        self.app_name = "contract-explainer"
        self.required_vars = [
            "DEEPSEEK_API_KEY",
            "FLASK_SECRET_KEY", 
            "GOOGLE_ADSENSE_CLIENT_ID"
        ]
    
    def check_prerequisites(self):
        """Check if Heroku CLI is installed and user is logged in"""
        print("🔍 Checking prerequisites...")
        
        # Check Heroku CLI
        try:
            result = subprocess.run(['heroku', '--version'], 
                                  capture_output=True, text=True)
            print(f"✅ Heroku CLI: {result.stdout.strip()}")
        except FileNotFoundError:
            print("❌ Heroku CLI not found. Install from: https://devcenter.heroku.com/articles/heroku-cli")
            return False
        
        # Check login status
        try:
            result = subprocess.run(['heroku', 'auth:whoami'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Logged in as: {result.stdout.strip()}")
            else:
                print("❌ Not logged in to Heroku. Run: heroku login")
                return False
        except:
            print("❌ Could not check Heroku login status")
            return False
            
        return True
    
    def create_heroku_files(self):
        """Create Heroku-specific deployment files"""
        print("📝 Creating Heroku deployment files...")
        
        # Procfile
        procfile_content = """web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120
"""
        
        with open('Procfile', 'w') as f:
            f.write(procfile_content)
        print("✅ Created Procfile")
        
        # runtime.txt
        with open('runtime.txt', 'w') as f:
            f.write('python-3.11.7\n')
        print("✅ Created runtime.txt")
        
        # app.json for Heroku Button
        app_json = {
            "name": "Contract Explainer",
            "description": "AI-powered contract analysis in plain English",
            "repository": "https://github.com/yourusername/contract-explainer",
            "logo": "https://your-domain.com/logo.png",
            "keywords": ["legal", "ai", "contract", "analysis", "python", "flask"],
            "stack": "heroku-22",
            "env": {
                "DEEPSEEK_API_KEY": {
                    "description": "API key for Deepseek AI service",
                    "required": True
                },
                "FLASK_SECRET_KEY": {
                    "description": "Secret key for Flask sessions",
                    "generator": "secret"
                },
                "GOOGLE_ADSENSE_CLIENT_ID": {
                    "description": "Google AdSense publisher ID",
                    "required": False
                }
            },
            "formation": {
                "web": {
                    "quantity": 1,
                    "size": "basic"
                }
            },
            "addons": [
                {
                    "plan": "heroku-redis:mini",
                    "options": {}
                }
            ]
        }
        
        with open('app.json', 'w') as f:
            json.dump(app_json, f, indent=2)
        print("✅ Created app.json")
    
    def create_app(self):
        """Create Heroku app"""
        print(f"🏗️  Creating Heroku app: {self.app_name}...")
        
        try:
            result = subprocess.run([
                'heroku', 'create', self.app_name, 
                '--region', 'us',
                '--stack', 'heroku-22'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Created app: {self.app_name}")
                print(f"📱 App URL: https://{self.app_name}.herokuapp.com/")
                return True
            else:
                if "already exists" in result.stderr.lower():
                    print(f"ℹ️  App {self.app_name} already exists")
                    return True
                else:
                    print(f"❌ Failed to create app: {result.stderr}")
                    return False
        except Exception as e:
            print(f"❌ Error creating app: {e}")
            return False
    
    def add_buildpacks(self):
        """Add required buildpacks"""
        print("📦 Adding buildpacks...")
        
        buildpacks = [
            "heroku/python"
        ]
        
        for buildpack in buildpacks:
            try:
                result = subprocess.run([
                    'heroku', 'buildpacks:add', buildpack, 
                    '--app', self.app_name
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Added buildpack: {buildpack}")
                else:
                    print(f"⚠️  Buildpack might already exist: {buildpack}")
            except Exception as e:
                print(f"❌ Error adding buildpack {buildpack}: {e}")
    
    def set_environment_variables(self):
        """Set environment variables from .env file"""
        print("🔧 Setting environment variables...")
        
        # Load from .env file if exists
        env_file = Path('.env')
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key in self.required_vars or key.startswith('FLASK_'):
                            try:
                                subprocess.run([
                                    'heroku', 'config:set', f'{key}={value}',
                                    '--app', self.app_name
                                ], capture_output=True, text=True, check=True)
                                print(f"✅ Set {key}")
                            except subprocess.CalledProcessError:
                                print(f"❌ Failed to set {key}")
        
        # Set production-specific variables
        prod_vars = {
            'FLASK_ENV': 'production',
            'FLASK_DEBUG': '0',
            'FLASK_HOST': '0.0.0.0'
        }
        
        for key, value in prod_vars.items():
            try:
                subprocess.run([
                    'heroku', 'config:set', f'{key}={value}',
                    '--app', self.app_name
                ], capture_output=True, text=True, check=True)
                print(f"✅ Set {key}={value}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to set {key}")
    
    def add_addons(self):
        """Add Heroku add-ons"""
        print("🔌 Adding add-ons...")
        
        addons = [
            ('heroku-redis:mini', 'Redis for caching'),
            ('papertrail:choklad', 'Log aggregation')
        ]
        
        for addon, description in addons:
            try:
                result = subprocess.run([
                    'heroku', 'addons:create', addon,
                    '--app', self.app_name
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Added {description}: {addon}")
                else:
                    print(f"⚠️  Could not add {addon}: {result.stderr}")
            except Exception as e:
                print(f"❌ Error adding {addon}: {e}")
    
    def deploy(self):
        """Deploy to Heroku"""
        print("🚀 Deploying to Heroku...")
        
        try:
            # Initialize git if needed
            if not os.path.exists('.git'):
                subprocess.run(['git', 'init'], check=True)
                subprocess.run(['git', 'add', '.'], check=True)
                subprocess.run(['git', 'commit', '-m', 'Initial commit'], check=True)
            
            # Add Heroku remote
            subprocess.run([
                'heroku', 'git:remote', '-a', self.app_name
            ], capture_output=True)
            
            # Push to Heroku
            result = subprocess.run([
                'git', 'push', 'heroku', 'main'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Deployment successful!")
                print(f"🌐 Your app is live at: https://{self.app_name}.herokuapp.com/")
                return True
            else:
                print(f"❌ Deployment failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Deployment error: {e}")
            return False
    
    def open_app(self):
        """Open the deployed app in browser"""
        try:
            subprocess.run(['heroku', 'open', '--app', self.app_name])
        except:
            print(f"🌐 Visit your app at: https://{self.app_name}.herokuapp.com/")
    
    def run_deployment(self):
        """Run the complete deployment process"""
        print("🚀 Starting Heroku deployment for Contract Explainer\n")
        
        if not self.check_prerequisites():
            return False
        
        self.create_heroku_files()
        
        if not self.create_app():
            return False
        
        self.add_buildpacks()
        self.set_environment_variables()
        self.add_addons()
        
        if self.deploy():
            print("\n🎉 Deployment completed successfully!")
            print(f"📱 App: https://{self.app_name}.herokuapp.com/")
            print("📊 Dashboard: https://dashboard.heroku.com/apps/" + self.app_name)
            print("\n📝 Next steps:")
            print("1. Update your domain DNS if using custom domain")
            print("2. Configure Google AdSense with your publisher ID")
            print("3. Set up monitoring and alerts")
            
            return True
        
        return False

if __name__ == "__main__":
    deployer = HerokuDeployer()
    success = deployer.run_deployment()
    sys.exit(0 if success else 1)