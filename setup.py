"""
Installation and Setup Guide for Multi-Agent System

This guide walks through setting up and running the multi-agent system.
"""

import subprocess
import sys
import os


def check_python_version():
    """Verify Python version is 3.9+"""
    if sys.version_info < (3, 9):
        print(f"❌ Python 3.9+ required. Current: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")


def install_dependencies():
    """Install required packages from requirements.txt"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"
        ])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)


def verify_installation():
    """Verify all packages are installed correctly"""
    print("\n🔍 Verifying installation...")
    required_packages = ["sqlalchemy", "pydantic"]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} not found")
            sys.exit(1)


def create_directories():
    """Create necessary project directories"""
    print("\n📁 Creating directories...")
    directories = ["data", "logs"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ {directory}/")


def main():
    """Run complete setup"""
    print("=" * 70)
    print("🚀 Multi-Agent System Setup")
    print("=" * 70)
    
    check_python_version()
    install_dependencies()
    verify_installation()
    create_directories()
    
    print("\n" + "=" * 70)
    print("✅ Setup Complete!")
    print("=" * 70)
    print("\n📋 Next steps:")
    print("   1. Run demos: python main.py --demo info")
    print("   2. Read documentation: cat README.md")
    print("   3. Explore code: Check agents/ folder")
    print("=" * 70)


if __name__ == "__main__":
    main()
