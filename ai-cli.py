#!/usr/bin/env python3
"""
AI CLI - A production-ready AI-powered command line interface
that converts natural language to safe bash commands.
"""

import os
import sys
import json
import logging
import subprocess
import argparse
from pathlib import Path
from typing import Optional, Dict, Any, List
import openai
from openai import OpenAI
import shlex
import re
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai-cli.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages configuration for the AI CLI tool."""
    
    def __init__(self, config_path: str = "ai-cli-config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        default_config = {
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
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
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    default_config.update(loaded_config)
                    return default_config
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Error loading config: {e}. Using defaults.")
                return default_config
        else:
            # Create default config file
            self._save_config(default_config)
            return default_config
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            logger.error(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value and save."""
        self.config[key] = value
        self._save_config(self.config)

class CommandValidator:
    """Validates and sanitizes commands for safety."""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.allowed_commands = set(config.get("allowed_commands", []))
        self.forbidden_commands = set(config.get("forbidden_commands", []))
        self.max_length = config.get("max_command_length", 500)
    
    def validate_command(self, command: str) -> tuple[bool, str]:
        """
        Validate command for safety.
        Returns (is_safe, error_message)
        """
        if not command.strip():
            return False, "Empty command"
        
        if len(command) > self.max_length:
            return False, f"Command too long (max {self.max_length} characters)"
        
        # Check for forbidden patterns
        command_lower = command.lower()
        for forbidden in self.forbidden_commands:
            if forbidden in command_lower:
                return False, f"Forbidden command pattern detected: {forbidden}"
        
        # Check for dangerous patterns
        dangerous_patterns = [
            r'rm\s+-rf\s+/',
            r'dd\s+if=.*\s+of=/dev/',
            r'mkfs\s+.*',
            r'fdisk\s+.*',
            r'shutdown\s+.*',
            r'reboot\s+.*',
            r'killall\s+.*',
            r'pkill\s+.*',
            r'>\s*/dev/',
            r'>>\s*/dev/',
            r'|\s*tee\s+/dev/',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command_lower):
                return False, f"Dangerous command pattern detected: {pattern}"
        
        # Check if command starts with allowed commands
        parts = shlex.split(command)
        if parts and parts[0] not in self.allowed_commands:
            return False, f"Command '{parts[0]}' not in allowed list"
        
        return True, ""
    
    def sanitize_command(self, command: str) -> str:
        """Sanitize command by removing potentially dangerous parts."""
        # Remove any attempts to redirect to system files
        command = re.sub(r'[>|]\s*/dev/[a-zA-Z]+', '', command)
        command = re.sub(r'[>|]\s*/etc/', '', command)
        command = re.sub(r'[>|]\s*/var/', '', command)
        command = re.sub(r'[>|]\s*/usr/', '', command)
        
        return command.strip()

class AICommandGenerator:
    """Generates bash commands from natural language using AI."""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        api_key = config.get("openai_api_key")
        if not api_key:
            raise ValueError("OpenAI API key not configured. Please set it in the config file.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = config.get("model", "gpt-4o-mini")
        self.max_tokens = config.get("max_tokens", 1000)
        self.temperature = config.get("temperature", 0.1)
    
    def generate_command(self, user_input: str) -> str:
        """Generate bash command from natural language input."""
        system_prompt = """You are a helpful AI assistant that converts natural language requests into safe bash commands.

IMPORTANT RULES:
1. Only generate safe, non-destructive commands
2. Use standard Unix/Linux commands
3. Avoid commands that can delete files without confirmation
4. Prefer commands that show information rather than modify files
5. If the request is unclear or potentially dangerous, ask for clarification
6. Return ONLY the command, no explanations unless clarification is needed

Common safe commands: ls, pwd, cat, head, tail, grep, find, ps, df, du, git status, etc.

If the request is unclear or potentially dangerous, respond with: "CLARIFICATION_NEEDED: [explanation]"

User request: """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            command = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if command.startswith("```") and command.endswith("```"):
                command = command[3:-3].strip()
            elif command.startswith("```bash"):
                command = command[7:].strip()
                if command.endswith("```"):
                    command = command[:-3].strip()
            
            return command
            
        except Exception as e:
            logger.error(f"Error generating command: {e}")
            return f"ERROR: Failed to generate command - {str(e)}"

class CommandExecutor:
    """Executes commands safely with proper error handling."""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.validator = CommandValidator(config)
    
    def execute_command(self, command: str) -> tuple[str, int]:
        """
        Execute command safely.
        Returns (output, exit_code)
        """
        # Validate command
        is_safe, error_msg = self.validator.validate_command(command)
        if not is_safe:
            return f"ERROR: {error_msg}", 1
        
        # Sanitize command
        sanitized_command = self.validator.sanitize_command(command)
        
        try:
            # Execute command
            result = subprocess.run(
                sanitized_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"
            
            return output, result.returncode
            
        except subprocess.TimeoutExpired:
            return "ERROR: Command timed out after 30 seconds", 1
        except Exception as e:
            logger.error(f"Error executing command '{command}': {e}")
            return f"ERROR: Failed to execute command - {str(e)}", 1

class HistoryManager:
    """Manages command history."""
    
    def __init__(self, history_file: str):
        self.history_file = Path(history_file)
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load command history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def add_entry(self, user_input: str, generated_command: str, output: str, exit_code: int):
        """Add a new entry to history."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "generated_command": generated_command,
            "output": output,
            "exit_code": exit_code
        }
        self.history.append(entry)
        self._save_history()
    
    def _save_history(self):
        """Save history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except IOError as e:
            logger.error(f"Error saving history: {e}")
    
    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent history entries."""
        return self.history[-limit:]

class AICLI:
    """Main AI CLI application."""
    
    def __init__(self):
        self.config = ConfigManager()
        self.validator = CommandValidator(self.config)
        self.ai_generator = AICommandGenerator(self.config)
        self.executor = CommandExecutor(self.config)
        self.history = HistoryManager(self.config.get("history_file", "ai-cli-history.json"))
    
    def setup(self):
        """Initial setup and configuration check."""
        api_key = self.config.get("openai_api_key")
        if not api_key:
            print("⚠️  OpenAI API key not configured!")
            print("Please set your OpenAI API key in the config file.")
            print(f"Config file: {self.config.config_path}")
            return False
        
        try:
            # Test API connection
            test_response = self.ai_generator.generate_command("list current directory")
            if test_response.startswith("ERROR:"):
                print(f"❌ API connection failed: {test_response}")
                return False
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
        
        print("✅ AI CLI initialized successfully!")
        return True
    
    def run(self):
        """Main application loop."""
        print("🤖 AI CLI - Natural Language to Bash Commands")
        print("Type 'exit' to quit, 'help' for commands, 'history' for recent commands")
        print("Commands starting with '!' are executed directly")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("🤖 > ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == "exit":
                    print("👋 Goodbye!")
                    break
                
                if user_input.lower() == "help":
                    self.show_help()
                    continue
                
                if user_input.lower() == "history":
                    self.show_history()
                    continue
                
                if user_input.lower() == "config":
                    self.show_config()
                    continue
                
                # Handle direct command execution
                if user_input.startswith("!"):
                    command = user_input[1:].strip()
                    output, exit_code = self.executor.execute_command(command)
                    print(f"Output:\n{output}")
                    if exit_code != 0:
                        print(f"Exit code: {exit_code}")
                    continue
                
                # Generate and execute AI command
                print("🤔 Generating command...")
                generated_command = self.ai_generator.generate_command(user_input)
                
                if generated_command.startswith("CLARIFICATION_NEEDED:"):
                    print(f"❓ {generated_command}")
                    continue
                
                if generated_command.startswith("ERROR:"):
                    print(f"❌ {generated_command}")
                    continue
                
                print(f"🔧 Generated command: {generated_command}")
                
                # Ask for confirmation if safe mode is enabled
                if self.config.get("safe_mode", True):
                    confirm = input("Execute this command? (y/n): ").strip().lower()
                    if confirm not in ['y', 'yes']:
                        print("❌ Command cancelled")
                        continue
                
                # Execute command
                print("⚡ Executing command...")
                output, exit_code = self.executor.execute_command(generated_command)
                
                # Store in history
                self.history.add_entry(user_input, generated_command, output, exit_code)
                
                # Display output
                print(f"📋 Output:\n{output}")
                if exit_code != 0:
                    print(f"⚠️  Exit code: {exit_code}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                print(f"❌ Unexpected error: {e}")
    
    def show_help(self):
        """Show help information."""
        help_text = """
🤖 AI CLI Help

Commands:
  <natural language>  - Convert to bash command and execute
  !<command>         - Execute bash command directly
  help               - Show this help
  history            - Show recent command history
  config             - Show current configuration
  exit               - Exit the application

Examples:
  "list files in current directory"
  "find all Python files"
  "show disk usage"
  "!ls -la"         (direct command)

Safety Features:
  - Commands are validated for safety
  - Dangerous commands are blocked
  - Confirmation required in safe mode
  - Command history is logged
        """
        print(help_text)
    
    def show_history(self):
        """Show recent command history."""
        recent = self.history.get_recent(5)
        if not recent:
            print("📝 No command history found")
            return
        
        print("📝 Recent Commands:")
        for i, entry in enumerate(recent, 1):
            print(f"{i}. {entry['timestamp']}")
            print(f"   Input: {entry['user_input']}")
            print(f"   Command: {entry['generated_command']}")
            print(f"   Exit Code: {entry['exit_code']}")
            print()
    
    def show_config(self):
        """Show current configuration."""
        print("⚙️  Current Configuration:")
        for key, value in self.config.config.items():
            if key == "openai_api_key":
                # Mask API key for security
                masked_key = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"  {key}: {masked_key}")
            else:
                print(f"  {key}: {value}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="AI CLI - Natural Language to Bash Commands")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--no-safe-mode", action="store_true", help="Disable safe mode")
    args = parser.parse_args()
    
    try:
        cli = AICLI()
        
        # Override config if specified
        if args.config:
            cli.config = ConfigManager(args.config)
        if args.no_safe_mode:
            cli.config.set("safe_mode", False)
        
        if cli.setup():
            cli.run()
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()







