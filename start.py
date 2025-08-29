#!/usr/bin/env python3
"""
Startup script for Magical Parenting Content Automation
Run this to start the application locally
"""

import os
import sys
import uvicorn
from pathlib import Path

def main():
    """Main startup function"""
    print("🎭 Starting Magical Parenting Content Automation...")
    
    # Check if we're in the right directory
    if not Path("app").exists():
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Check for environment file
    if not Path(".env").exists():
        print("⚠️  Warning: No .env file found. Using default settings.")
        print("   Create a .env file from env.example for production use.")
    
    # Set default environment if not set
    if not os.getenv("ENVIRONMENT"):
        os.environ["ENVIRONMENT"] = "development"
    
    print(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print("🚀 Starting FastAPI server...")
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    print("🔍 Health check at: http://localhost:8000/health")
    print("=" * 60)
    
    try:
        # Start the server
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
