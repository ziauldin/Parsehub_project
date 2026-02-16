"""
ParseHub Combined Startup Script
Starts both frontend (Next.js) and optional backend (Python) services

Usage:
    python start.py
    python start.py --backend    # Include backend services
    python start.py --help       # Show help
"""

import os
import sys
import subprocess
import argparse
import platform
from pathlib import Path

class ParseHubStarter:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.frontend_dir = self.root_dir / "frontend"
        self.backend_dir = self.root_dir / "backend"
        self.venv_dir = self.root_dir / ".venv"
        self.platform = platform.system()
        
    def print_header(self):
        print("\n" + "="*60)
        print("    ParseHub - Frontend & Backend Startup")
        print("="*60 + "\n")
    
    def check_frontend(self):
        """Check frontend setup"""
        if not self.frontend_dir.exists():
            print("❌ Error: frontend directory not found!")
            return False
        
        print("📁 Frontend folder found at: frontend/")
        
        node_modules = self.frontend_dir / "node_modules"
        if not node_modules.exists():
            print("📦 Installing frontend dependencies...")
            cmd = ["npm", "install"] if self.platform != "Windows" else ["npm.cmd", "install"]
            result = subprocess.run(
                cmd,
                cwd=str(self.frontend_dir),
                capture_output=True,
                shell=self.platform == "Windows"
            )
            if result.returncode == 0:
                print("✅ Frontend dependencies installed\n")
            else:
                print("❌ Failed to install frontend dependencies")
                print(result.stderr.decode())
                return False
        else:
            print("✅ Frontend dependencies found\n")
        
        return True
    
    def check_backend(self):
        """Check backend setup"""
        if not self.backend_dir.exists():
            print("⚠️  Backend folder not found")
            return False
        
        print("📁 Backend folder found at: backend/")
        
        env_file = self.backend_dir / ".env"
        if env_file.exists():
            print("✅ Backend .env configuration found\n")
            return True
        else:
            print("⚠️  backend/.env not found\n")
            return False
    
    def start_frontend(self):
        """Start the frontend development server"""
        print("🚀 Starting Frontend Development Server...")
        print("   Application will be available at: http://localhost:3000\n")
        print("▶️  Running: npm run dev\n")
        print("-" * 60 + "\n")
        
        try:
            # Use different command for Windows
            if self.platform == "Windows":
                cmd = ["npm.cmd", "run", "dev"]
                subprocess.run(
                    cmd,
                    cwd=str(self.frontend_dir),
                    shell=True
                )
            else:
                subprocess.run(
                    ["npm", "run", "dev"],
                    cwd=str(self.frontend_dir)
                )
        except KeyboardInterrupt:
            print("\n\n✋ Shutting down ParseHub...")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error starting frontend: {e}")
            sys.exit(1)
    
    def start_backend(self):
        """Start backend Python services (if configured)"""
        print("🐍 Backend services would start here if configured")
        print("   (Optional: Custom Python services)")
    
    def run(self, include_backend=False):
        """Run the startup sequence"""
        self.print_header()
        
        # Check frontend
        if not self.check_frontend():
            sys.exit(1)
        
        # Check backend (optional)
        if include_backend:
            self.check_backend()
        
        # Start frontend (this blocks)
        self.start_frontend()

def main():
    parser = argparse.ArgumentParser(
        description="Start ParseHub Frontend & Backend services"
    )
    parser.add_argument(
        "--backend",
        action="store_true",
        help="Include backend services"
    )
    parser.add_argument(
        "--help-detailed",
        action="store_true",
        help="Show detailed help"
    )
    
    args = parser.parse_args()
    
    if args.help_detailed:
        print(__doc__)
        sys.exit(0)
    
    starter = ParseHubStarter()
    starter.run(include_backend=args.backend)

if __name__ == "__main__":
    main()
