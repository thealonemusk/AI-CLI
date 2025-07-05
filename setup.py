#!/usr/bin/env python3
"""
Setup script for AI CLI tool.
"""

import os
import sys
import json
from pathlib import Path

def create_config_file():
    """Create default configuration file."""
    config = {
        "openai_api_key": "",
        "model": "gpt-4o-mini",
        "max_tokens": 1000,
        "temperature": 0.1,
        "safe_mode": True,
        "allowed_commands": [
            "ls", "pwd", "cd", "cat", "head", "tail", "grep", "find",
            "mkdir", "rmdir", "cp", "mv", "rm", "chmod", "chown",
            "ps", "top", "df", "du", "tar", "zip", "unzip",
            "git", "docker", "kubectl", "aws", "terraform"
        ],
        "forbidden_commands": [
            "rm -rf /", "dd", "mkfs", "fdisk", "format",
            "shutdown", "reboot", "init", "killall", "pkill"
        ],
        "max_command_length": 500,
        "history_file": "ai-cli-history.json"
    }
    
    config_path = Path("ai-cli-config.json")
    if not config_path.exists():
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print("✅ Created default configuration file: ai-cli-config.json")
    else:
        print("ℹ️  Configuration file already exists: ai-cli-config.json")

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import openai
        print("✅ OpenAI library is installed")
    except ImportError:
        print("❌ OpenAI library not found. Please run: pip install -r requirements.txt")
        return False
    
    try:
        import pathlib
        print("✅ Pathlib library is available")
    except ImportError:
        print("❌ Pathlib library not found. Please run: pip install -r requirements.txt")
        return False
    
    return True

def get_api_key():
    """Get OpenAI API key from user."""
    print("\n🔑 OpenAI API Key Setup")
    print("You need an OpenAI API key to use this tool.")
    print("Get one from: https://platform.openai.com/api-keys")
    
    api_key = input("Enter your OpenAI API key: ").strip()
    
    if api_key:
        # Update config file
        config_path = Path("ai-cli-config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            config["openai_api_key"] = api_key
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print("✅ API key saved to configuration file")
        else:
            print("❌ Configuration file not found. Please run setup again.")
    else:
        print("⚠️  No API key provided. You'll need to set it manually in ai-cli-config.json")

def main():
    """Main setup function."""
    print("🚀 AI CLI Setup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Setup failed. Please install dependencies first.")
        sys.exit(1)
    
    # Create config file
    create_config_file()
    
    # Get API key
    get_api_key()
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Edit ai-cli-config.json if you need to customize settings")
    print("2. Run: python ai-cli.py")
    print("3. Type 'help' for available commands")
    print("\nHappy coding! 🚀")

if __name__ == "__main__":
    main() 