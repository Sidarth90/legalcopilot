#!/usr/bin/env python3
"""
Contract Explainer - Universal Deployment Manager
Choose and execute deployment to various cloud platforms
"""

import os
import sys
import argparse
import importlib.util
from pathlib import Path

class UniversalDeployer:
    def __init__(self):
        self.platforms = {
            'heroku': {
                'name': 'Heroku',
                'description': 'Easy deployment with add-ons, great for beginners',
                'cost': 'Free tier available, $7+/month for production',
                'features': ['Auto-scaling', 'Add-ons ecosystem', 'Git-based deployment'],
                'script': 'heroku.py'
            },
            'railway': {
                'name': 'Railway',
                'description': 'Modern platform with excellent DX, fast deployments',
                'cost': 'Usage-based pricing, generous free tier',
                'features': ['Fast deployments', 'Built-in monitoring', 'Database services'],
                'script': 'railway.py'
            },
            'render': {
                'name': 'Render',
                'description': 'Simple, reliable hosting with great free tier',
                'cost': 'Free tier for static sites, $7+/month for services',
                'features': ['Auto-deploy from Git', 'Free SSL', 'DDoS protection'],
                'script': 'render.py'
            },
            'docker': {
                'name': 'Docker Compose',
                'description': 'Local or VPS deployment using Docker',
                'cost': 'VPS costs vary ($5-20+/month)',
                'features': ['Full control', 'Any VPS provider', 'Self-hosted'],
                'script': None
            }
        }
    
    def show_platforms(self):
        """Display available deployment platforms"""
        print("🚀 Available Deployment Platforms:")
        print("=" * 60)
        
        for key, platform in self.platforms.items():
            print(f"\n📱 {platform['name']} ({key})")
            print(f"   Description: {platform['description']}")
            print(f"   Cost: {platform['cost']}")
            print(f"   Features: {', '.join(platform['features'])}")
        
        print("\n" + "=" * 60)
    
    def get_user_choice(self):
        """Get deployment platform choice from user"""
        print("\n🤔 Which platform would you like to deploy to?")
        
        choices = list(self.platforms.keys())
        for i, key in enumerate(choices, 1):
            print(f"  {i}. {self.platforms[key]['name']} ({key})")
        
        while True:
            try:
                choice = input(f"\nEnter your choice (1-{len(choices)}) or platform name: ").strip().lower()
                
                # Handle numeric choice
                if choice.isdigit():
                    index = int(choice) - 1
                    if 0 <= index < len(choices):
                        return choices[index]
                
                # Handle platform name
                if choice in choices:
                    return choice
                
                # Handle partial matches
                matches = [key for key in choices if key.startswith(choice)]
                if len(matches) == 1:
                    return matches[0]
                
                print("❌ Invalid choice. Please try again.")
                
            except (ValueError, KeyboardInterrupt):
                print("\n👋 Deployment cancelled.")
                return None
    
    def run_platform_deployer(self, platform):
        """Run the specific platform deployer"""
        script_name = self.platforms[platform]['script']
        
        if not script_name:
            if platform == 'docker':
                return self.docker_deployment_guide()
            else:
                print(f"❌ No deployment script available for {platform}")
                return False
        
        script_path = Path(__file__).parent / script_name
        
        if not script_path.exists():
            print(f"❌ Deployment script not found: {script_path}")
            return False
        
        try:
            # Import and run the platform-specific deployer
            spec = importlib.util.spec_from_file_location("deployer", script_path)
            deployer_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(deployer_module)
            
            # Get the deployer class (assuming naming convention)
            deployer_class_name = f"{platform.title()}Deployer"
            if hasattr(deployer_module, deployer_class_name):
                deployer = getattr(deployer_module, deployer_class_name)()
                return deployer.run_deployment()
            else:
                print(f"❌ Deployer class not found: {deployer_class_name}")
                return False
                
        except Exception as e:
            print(f"❌ Error running {platform} deployer: {e}")
            return False
    
    def docker_deployment_guide(self):
        """Provide Docker deployment instructions"""
        print("\n🐳 Docker Deployment Guide")
        print("=" * 40)
        
        print("\n📋 Prerequisites:")
        print("- Docker and Docker Compose installed")
        print("- VPS or local machine to run containers")
        print("- Domain name (optional)")
        
        print("\n🚀 Deployment Steps:")
        print("1. Copy .env.example to .env and fill in values:")
        print("   cp .env.example .env")
        
        print("\n2. Build and start containers:")
        print("   docker-compose up -d")
        
        print("\n3. View logs:")
        print("   docker-compose logs -f")
        
        print("\n4. For production with SSL:")
        print("   - Configure your domain DNS")
        print("   - Get SSL certificates (Let's Encrypt)")
        print("   - Update nginx.conf with your domain")
        print("   - Use docker-compose.yml with nginx service")
        
        print("\n🔧 Useful Commands:")
        print("- Stop: docker-compose down")
        print("- Rebuild: docker-compose up --build -d")
        print("- Shell access: docker-compose exec web bash")
        
        print("\n📊 Monitoring:")
        print("- Check status: docker-compose ps")
        print("- View resources: docker stats")
        
        return True
    
    def pre_deployment_check(self):
        """Check if project is ready for deployment"""
        print("🔍 Pre-deployment checklist...")
        
        required_files = [
            'app.py',
            'requirements.txt',
            'templates/index.html',
            'static/js/app.js'
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
        
        # Check for .env.example
        if not os.path.exists('.env.example'):
            print("⚠️  .env.example not found - creating one...")
            self.create_env_example()
        
        # Check for essential environment variables
        if os.path.exists('.env'):
            with open('.env') as f:
                env_content = f.read()
                if 'DEEPSEEK_API_KEY' not in env_content:
                    print("⚠️  DEEPSEEK_API_KEY not found in .env file")
        else:
            print("⚠️  .env file not found. Copy from .env.example and fill in values.")
        
        print("✅ Project structure looks good!")
        return True
    
    def create_env_example(self):
        """Create .env.example if it doesn't exist"""
        env_example_content = """# Contract Explainer - Environment Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
FLASK_SECRET_KEY=your_super_secret_key_here
GOOGLE_ADSENSE_CLIENT_ID=ca-pub-your-publisher-id
"""
        
        with open('.env.example', 'w') as f:
            f.write(env_example_content)
        print("✅ Created .env.example")
    
    def post_deployment_tips(self, platform):
        """Show post-deployment tips"""
        print(f"\n🎉 {self.platforms[platform]['name']} deployment completed!")
        print("\n📝 Post-deployment checklist:")
        print("✅ Test all core functionality")
        print("✅ Verify file uploads work")
        print("✅ Check AI analysis responses")
        print("✅ Test on mobile devices")
        print("✅ Set up monitoring/alerts")
        print("✅ Configure custom domain (if needed)")
        print("✅ Set up Google AdSense")
        print("✅ Submit to search engines")
        
        print("\n🔒 Security checklist:")
        print("✅ HTTPS is enabled")
        print("✅ Security headers are set")
        print("✅ Rate limiting is active")
        print("✅ File upload validation works")
        print("✅ Environment variables are secure")
        
        print("\n📈 Growth checklist:")
        print("✅ Analytics tracking")
        print("✅ Error monitoring")
        print("✅ Performance monitoring")
        print("✅ User feedback system")
        print("✅ SEO optimization")
    
    def run(self):
        """Main deployment orchestration"""
        print("🚀 Contract Explainer - Universal Deployment Manager")
        print("=" * 60)
        
        # Pre-deployment check
        if not self.pre_deployment_check():
            print("\n❌ Pre-deployment check failed. Please fix issues and try again.")
            return False
        
        # Show available platforms
        self.show_platforms()
        
        # Get user choice
        platform = self.get_user_choice()
        if not platform:
            return False
        
        print(f"\n🎯 Deploying to {self.platforms[platform]['name']}...")
        
        # Run platform-specific deployment
        success = self.run_platform_deployer(platform)
        
        if success:
            self.post_deployment_tips(platform)
        
        return success

def main():
    parser = argparse.ArgumentParser(
        description='Deploy Contract Explainer to various cloud platforms'
    )
    parser.add_argument(
        '--platform',
        choices=['heroku', 'railway', 'render', 'docker'],
        help='Platform to deploy to (skip interactive selection)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available platforms and exit'
    )
    
    args = parser.parse_args()
    
    deployer = UniversalDeployer()
    
    if args.list:
        deployer.show_platforms()
        return
    
    if args.platform:
        # Direct deployment to specified platform
        success = deployer.run_platform_deployer(args.platform)
        if success:
            deployer.post_deployment_tips(args.platform)
    else:
        # Interactive deployment
        success = deployer.run()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()