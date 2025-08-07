#!/usr/bin/env python3
"""
Contract Explainer - Render Deployment Script
Automated deployment to Render platform
"""

import os
import sys
import subprocess
import json
import yaml
import requests
from pathlib import Path

class RenderDeployer:
    def __init__(self):
        self.service_name = "contract-explainer"
        self.required_vars = [
            "DEEPSEEK_API_KEY",
            "FLASK_SECRET_KEY",
            "GOOGLE_ADSENSE_CLIENT_ID"
        ]
    
    def create_render_files(self):
        """Create Render-specific deployment files"""
        print("📝 Creating Render deployment files...")
        
        # render.yaml - Infrastructure as Code
        render_config = {
            "services": [
                {
                    "type": "web",
                    "name": self.service_name,
                    "runtime": "python3",
                    "plan": "starter",  # Free tier
                    "buildCommand": "pip install -r requirements.txt",
                    "startCommand": "gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120",
                    "envVars": [
                        {
                            "key": "FLASK_ENV",
                            "value": "production"
                        },
                        {
                            "key": "FLASK_DEBUG", 
                            "value": "0"
                        },
                        {
                            "key": "FLASK_HOST",
                            "value": "0.0.0.0"
                        },
                        {
                            "key": "DEEPSEEK_API_KEY",
                            "sync": False  # User needs to set manually
                        },
                        {
                            "key": "FLASK_SECRET_KEY",
                            "generateValue": True
                        },
                        {
                            "key": "GOOGLE_ADSENSE_CLIENT_ID",
                            "sync": False
                        }
                    ],
                    "disk": {
                        "name": "uploads-disk",
                        "mountPath": "/app/uploads",
                        "sizeGB": 1
                    },
                    "healthCheckPath": "/health"
                }
            ],
            "databases": [
                {
                    "name": "contract-explainer-redis",
                    "plan": "starter",  # Free tier
                    "databaseName": "redis",
                    "user": "redis"
                }
            ]
        }
        
        with open('render.yaml', 'w') as f:
            yaml.dump(render_config, f, default_flow_style=False, indent=2)
        print("✅ Created render.yaml")
        
        # .renderignore
        renderignore_content = """.git/
.env*
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
deploy/
nginx.conf
"""
        
        with open('.renderignore', 'w') as f:
            f.write(renderignore_content)
        print("✅ Created .renderignore")
        
        # Build script for Render
        build_script = """#!/bin/bash
echo "🔧 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📁 Setting up directories..."
mkdir -p uploads
chmod 755 uploads

echo "✅ Build completed successfully!"
"""
        
        with open('build.sh', 'w') as f:
            f.write(build_script)
        
        # Make build script executable
        os.chmod('build.sh', 0o755)
        print("✅ Created build.sh")
    
    def create_health_endpoint(self):
        """Add health check endpoint to app.py if it doesn't exist"""
        print("🏥 Adding health check endpoint...")
        
        app_py_path = Path('app.py')
        if app_py_path.exists():
            with open(app_py_path, 'r') as f:
                content = f.read()
            
            if '/health' not in content:
                # Add health endpoint before the main block
                health_endpoint = """
@app.route('/health')
def health_check():
    '''Health check endpoint for Render'''
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': os.environ.get('RENDER_GIT_COMMIT', 'unknown')
    }), 200
"""
                
                # Find the main block and insert before it
                main_block_index = content.find("if __name__ == '__main__':")
                if main_block_index != -1:
                    new_content = (content[:main_block_index] + 
                                 health_endpoint + "\n" + 
                                 content[main_block_index:])
                    
                    with open(app_py_path, 'w') as f:
                        f.write(new_content)
                    print("✅ Added health check endpoint")
                else:
                    print("⚠️  Could not find main block in app.py")
            else:
                print("✅ Health endpoint already exists")
        else:
            print("❌ app.py not found")
    
    def setup_git_repo(self):
        """Setup git repository for Render deployment"""
        print("📦 Setting up git repository...")
        
        if not os.path.exists('.git'):
            try:
                subprocess.run(['git', 'init'], check=True)
                subprocess.run(['git', 'add', '.'], check=True)
                subprocess.run(['git', 'commit', '-m', 'Initial commit for Render deployment'], check=True)
                print("✅ Initialized git repository")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to initialize git: {e}")
                return False
        else:
            print("✅ Git repository already exists")
        
        return True
    
    def create_github_repo(self):
        """Create GitHub repository (optional but recommended)"""
        print("🐙 GitHub repository setup...")
        
        # Check if gh CLI is available
        try:
            subprocess.run(['gh', '--version'], capture_output=True, check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("⚠️  GitHub CLI not found. You'll need to create the repository manually.")
            print("📝 Instructions:")
            print("1. Go to https://github.com/new")
            print("2. Create a new repository named 'contract-explainer'")
            print("3. Push your code: git remote add origin <repo-url> && git push -u origin main")
            return False
        
        try:
            # Create GitHub repository
            result = subprocess.run([
                'gh', 'repo', 'create', self.service_name,
                '--public', '--description', 'AI-powered contract analysis in plain English'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Created GitHub repository")
                
                # Push code
                subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
                print("✅ Pushed code to GitHub")
                return True
            else:
                print(f"⚠️  GitHub repo might already exist: {result.stderr}")
                return True
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create GitHub repo: {e}")
            return False
    
    def deploy_instructions(self):
        """Show deployment instructions for Render"""
        print("\n🚀 Render Deployment Instructions:")
        print("=" * 50)
        
        print("\n1. 📂 Push code to GitHub:")
        print("   - Ensure your code is in a GitHub repository")
        print("   - Make sure render.yaml is in the root directory")
        
        print("\n2. 🌐 Deploy on Render:")
        print("   a) Go to https://render.com/")
        print("   b) Sign up/login and connect your GitHub account")
        print("   c) Click 'New' → 'Blueprint'")
        print("   d) Select your GitHub repository")
        print("   e) Render will automatically detect render.yaml")
        print("   f) Click 'Apply' to deploy")
        
        print("\n3. 🔧 Set Environment Variables:")
        print("   After deployment, set these in Render dashboard:")
        for var in self.required_vars:
            print(f"   - {var}")
        
        print("\n4. 🔗 Custom Domain (Optional):")
        print("   - Go to Settings → Custom Domains")
        print("   - Add your domain and configure DNS")
        
        print("\n📊 Render Dashboard: https://dashboard.render.com/")
        print("📖 Docs: https://render.com/docs/")
        
        return True
    
    def auto_deploy_via_api(self):
        """Attempt automated deployment via Render API (if API key is available)"""
        api_key = os.environ.get('RENDER_API_KEY')
        
        if not api_key:
            print("⚠️  RENDER_API_KEY not found. Using manual deployment instructions.")
            return self.deploy_instructions()
        
        print("🤖 Attempting automated deployment via Render API...")
        
        try:
            # This would require the Render API (currently in beta)
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Note: Render's API is still in beta, so this is placeholder code
            print("⚠️  Render API deployment not yet implemented.")
            print("📝 Using manual deployment instructions instead.")
            
            return self.deploy_instructions()
            
        except Exception as e:
            print(f"❌ API deployment failed: {e}")
            return self.deploy_instructions()
    
    def run_deployment(self):
        """Run the complete deployment process"""
        print("🚀 Starting Render deployment for Contract Explainer\n")
        
        self.create_render_files()
        self.create_health_endpoint()
        
        if not self.setup_git_repo():
            return False
        
        # Try to create GitHub repo (optional)
        self.create_github_repo()
        
        # Show deployment instructions
        success = self.auto_deploy_via_api()
        
        if success:
            print("\n🎉 Render deployment setup completed!")
            print("\n📝 Next steps after deployment:")
            print("1. Set environment variables in Render dashboard")
            print("2. Configure custom domain if needed")
            print("3. Set up monitoring and alerts")
            print("4. Test your application thoroughly")
            
            return True
        
        return False

if __name__ == "__main__":
    deployer = RenderDeployer()
    success = deployer.run_deployment()
    sys.exit(0 if success else 1)