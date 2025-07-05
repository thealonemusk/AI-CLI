#!/usr/bin/env python3
"""
Test script to verify AI CLI installation.
"""

import sys
import json
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import openai
        print("✅ OpenAI library imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import OpenAI: {e}")
        return False
    
    try:
        import subprocess
        print("✅ Subprocess module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import subprocess: {e}")
        return False
    
    try:
        import json
        print("✅ JSON module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import JSON: {e}")
        return False
    
    try:
        import logging
        print("✅ Logging module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import logging: {e}")
        return False
    
    try:
        from pathlib import Path
        print("✅ Pathlib module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pathlib: {e}")
        return False
    
    return True

def test_config_file():
    """Test if configuration file exists and is valid."""
    print("\n🔍 Testing configuration file...")
    
    config_path = Path("ai-cli-config.json")
    if not config_path.exists():
        print("❌ Configuration file not found: ai-cli-config.json")
        print("   Run: python setup.py to create it")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print("✅ Configuration file loaded successfully")
        
        # Check for required fields
        required_fields = ["openai_api_key", "model", "safe_mode"]
        for field in required_fields:
            if field not in config:
                print(f"❌ Missing required field: {field}")
                return False
        
        print("✅ All required configuration fields present")
        
        # Check API key
        api_key = config.get("openai_api_key", "")
        if not api_key:
            print("⚠️  OpenAI API key not set")
            print("   Please set it in ai-cli-config.json or run setup.py")
        else:
            print("✅ OpenAI API key is configured")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading configuration file: {e}")
        return False

def test_main_module():
    """Test if the main AI CLI module can be imported."""
    print("\n🔍 Testing main module...")
    
    try:
        # Import the main module
        import ai_cli
        print("✅ Main module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import main module: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing main module: {e}")
        return False

def test_file_structure():
    """Test if all required files exist."""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        "ai-cli.py",
        "requirements.txt",
        "README.md"
    ]
    
    optional_files = [
        "setup.py",
        "ai-cli-config.json"
    ]
    
    all_good = True
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ Required file exists: {file}")
        else:
            print(f"❌ Required file missing: {file}")
            all_good = False
    
    for file in optional_files:
        if Path(file).exists():
            print(f"✅ Optional file exists: {file}")
        else:
            print(f"ℹ️  Optional file not found: {file}")
    
    return all_good

def main():
    """Run all tests."""
    print("🧪 AI CLI Installation Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("File Structure Test", test_file_structure),
        ("Configuration Test", test_config_file),
        ("Main Module Test", test_main_module)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your AI CLI is ready to use.")
        print("\nNext steps:")
        print("1. Set your OpenAI API key in ai-cli-config.json")
        print("2. Run: python ai-cli.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Run: python setup.py")
        print("3. Check that all files are present")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 