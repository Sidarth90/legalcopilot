#!/usr/bin/env python3
"""
Contract Explainer - Development Runner
"""
import os
import sys
from app import app

def main():
    print("Contract Explainer Starting...")
    print("=" * 50)
    print(f"Working directory: {os.getcwd()}")
    
    # Check environment
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if api_key:
        print(f"Deepseek API Key: OK - Configured ({api_key[:8]}...)")
    else:
        print("Deepseek API Key: ERROR - Missing - please check .env file")
    
    print("\nServer will be available at:")
    print("   http://localhost:5001")
    print("   http://127.0.0.1:5001")
    
    print("\nFeatures available:")
    print("   - PDF contract analysis")
    print("   - Word document analysis") 
    print("   - AI-powered explanations")
    print("   - Google AdSense integration")
    
    print("\nPress Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Run with better error handling
        app.run(
            debug=True,
            host='localhost',
            port=5001,
            use_reloader=False  # Prevent double startup
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"\nServer error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()