#!/usr/bin/env python3
"""
LegalCopilot - Staging Environment Setup
Creates and manages staging deployments for safe testing
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class StagingManager:
    def __init__(self):
        self.environments = {
            'staging': {
                'name': 'legalcopilot-staging',
                'branch': 'develop',
                'env_vars': {
                    'FLASK_ENV': 'staging',
                    'FLASK_DEBUG': '1',
                    'LOG_LEVEL': 'DEBUG',
                    'RATE_LIMIT_PER_HOUR': '1000',  # Higher limits for testing
                }
            },
            'production': {
                'name': 'legalcopilot-prod',
                'branch': 'main',
                'env_vars': {
                    'FLASK_ENV': 'production', 
                    'FLASK_DEBUG': '0',
                    'LOG_LEVEL': 'INFO',
                    'RATE_LIMIT_PER_HOUR': '100',
                }
            }
        }
    
    def setup_staging_environment(self):
        """Set up complete staging environment"""
        print("🚀 Setting up staging environment...")
        
        # 1. Check prerequisites
        if not self._check_railway_cli():
            return False
        
        # 2. Create staging project
        print("\n📦 Creating staging project...")
        self._create_railway_project('staging')
        
        # 3. Set environment variables
        print("\n🔧 Configuring staging environment...")
        self._set_environment_variables('staging')
        
        # 4. Create develop branch if not exists
        print("\n🌿 Setting up develop branch...")
        self._setup_git_branch('develop')
        
        # 5. Deploy to staging
        print("\n🚀 Deploying to staging...")
        self._deploy_to_staging()
        
        print("\n✅ Staging environment ready!")
        print(f"🌐 Staging URL: https://{self.environments['staging']['name']}.railway.app")
        
    def setup_production_environment(self):
        """Set up production environment"""
        print("🏭 Setting up production environment...")
        
        # 1. Create production project
        self._create_railway_project('production')
        
        # 2. Set production environment variables
        self._set_environment_variables('production')
        
        print("✅ Production environment ready!")
        
    def deploy_to_staging(self):
        """Deploy current changes to staging"""
        print("🚀 Deploying to staging...")
        
        # Ensure we're on develop branch
        self._ensure_branch('develop')
        
        # Push to staging
        self._deploy_to_staging()
        
        print("✅ Deployed to staging!")
        
    def promote_to_production(self):
        """Promote staging to production"""
        print("🚀 Promoting staging to production...")
        
        # Merge develop to main
        print("📤 Merging develop → main...")
        subprocess.run(['git', 'checkout', 'main'])
        subprocess.run(['git', 'merge', 'develop'])
        subprocess.run(['git', 'push', 'origin', 'main'])
        
        # Deploy to production
        self._deploy_to_production()
        
        print("✅ Promoted to production!")
        
    def _check_railway_cli(self):
        """Check Railway CLI installation"""
        try:
            subprocess.run(['railway', '--version'], capture_output=True)
            return True
        except FileNotFoundError:
            print("❌ Railway CLI not found. Install: npm install -g @railway/cli")
            return False
    
    def _create_railway_project(self, env_type):
        """Create Railway project for environment"""
        config = self.environments[env_type]
        
        try:
            # Create new project
            result = subprocess.run([
                'railway', 'project', 'create', config['name']
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Created {env_type} project: {config['name']}")
            else:
                print(f"📋 Project {config['name']} already exists")
                
        except Exception as e:
            print(f"❌ Error creating {env_type} project: {e}")
    
    def _set_environment_variables(self, env_type):
        """Set environment variables for specific environment"""
        config = self.environments[env_type]
        
        # Switch to project
        subprocess.run(['railway', 'project', 'use', config['name']])
        
        # Set environment-specific variables
        for var, value in config['env_vars'].items():
            subprocess.run(['railway', 'variables', 'set', f'{var}={value}'])
            print(f"  ✅ Set {var}")
        
        # Set shared variables (you'll need to input these)
        shared_vars = [
            'DEEPSEEK_API_KEY',
            'FLASK_SECRET_KEY',
            'GOOGLE_ADSENSE_CLIENT_ID'
        ]
        
        print(f"\n🔑 Please set these variables for {env_type}:")
        for var in shared_vars:
            print(f"  railway variables set {var}=your_value_here")
    
    def _setup_git_branch(self, branch_name):
        """Create and setup git branch"""
        try:
            # Check if branch exists
            result = subprocess.run([
                'git', 'rev-parse', '--verify', branch_name
            ], capture_output=True)
            
            if result.returncode != 0:
                # Create branch
                subprocess.run(['git', 'checkout', '-b', branch_name])
                subprocess.run(['git', 'push', '-u', 'origin', branch_name])
                print(f"✅ Created branch: {branch_name}")
            else:
                print(f"📋 Branch {branch_name} already exists")
                
        except Exception as e:
            print(f"❌ Error with git branch: {e}")
    
    def _ensure_branch(self, branch_name):
        """Ensure we're on the correct branch"""
        subprocess.run(['git', 'checkout', branch_name])
        subprocess.run(['git', 'pull', 'origin', branch_name])
    
    def _deploy_to_staging(self):
        """Deploy to staging environment"""
        # Switch to staging project
        subprocess.run(['railway', 'project', 'use', 'legalcopilot-staging'])
        
        # Deploy
        subprocess.run(['railway', 'up'])
    
    def _deploy_to_production(self):
        """Deploy to production environment"""
        # Switch to production project
        subprocess.run(['railway', 'project', 'use', 'legalcopilot-prod'])
        
        # Deploy
        subprocess.run(['railway', 'up'])
    
    def status(self):
        """Show status of all environments"""
        print("📊 Environment Status:")
        
        for env_type, config in self.environments.items():
            print(f"\n{env_type.upper()}:")
            print(f"  🏷️  Name: {config['name']}")
            print(f"  🌿 Branch: {config['branch']}")
            print(f"  🌐 URL: https://{config['name']}.railway.app")


def main():
    """Main CLI interface"""
    manager = StagingManager()
    
    if len(sys.argv) < 2:
        print("🔧 LegalCopilot Staging Manager")
        print("\nCommands:")
        print("  setup-staging     - Create staging environment")
        print("  setup-production  - Create production environment") 
        print("  deploy-staging    - Deploy to staging")
        print("  promote           - Promote staging → production")
        print("  status            - Show environment status")
        return
    
    command = sys.argv[1]
    
    if command == 'setup-staging':
        manager.setup_staging_environment()
    elif command == 'setup-production':
        manager.setup_production_environment()
    elif command == 'deploy-staging':
        manager.deploy_to_staging()
    elif command == 'promote':
        manager.promote_to_production()
    elif command == 'status':
        manager.status()
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == '__main__':
    main()