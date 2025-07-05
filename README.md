# AI CLI - Natural Language to Bash Commands

A production-ready AI-powered command line interface that converts natural language requests into safe bash commands using OpenAI's GPT models.

## 🚀 Features

- **Natural Language Processing**: Convert plain English to bash commands
- **Safety First**: Built-in command validation and sanitization
- **Production Ready**: Comprehensive error handling and logging
- **Configurable**: Easy configuration management
- **History Tracking**: Command history with timestamps
- **Safe Mode**: Optional confirmation before command execution
- **Direct Commands**: Execute commands directly with `!` prefix

## 📋 Requirements

- Python 3.7+
- OpenAI API key
- Internet connection for AI model access

## 🛠️ Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd AI-CLI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your OpenAI API key**
   
   Edit the `ai-cli-config.json` file (created automatically on first run):
   ```json
   {
     "openai_api_key": "your-openai-api-key-here",
     "model": "gpt-4o-mini",
     "safe_mode": true
   }
   ```
   
   Or set it via environment variable:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

## 🎯 Usage

### Basic Usage

```bash
python ai-cli.py
```

### Command Examples

```
🤖 > list all files in current directory
🔧 Generated command: ls -la
📋 Output: [command output]

🤖 > find all Python files
🔧 Generated command: find . -name "*.py"
📋 Output: [command output]

🤖 > show disk usage
🔧 Generated command: df -h
📋 Output: [command output]

🤖 > !ls -la
📋 Output: [direct command output]
```

### Available Commands

- **Natural language**: Describe what you want to do
- **`!command`**: Execute a bash command directly
- **`help`**: Show help information
- **`history`**: Show recent command history
- **`config`**: Show current configuration
- **`exit`**: Exit the application

## ⚙️ Configuration

The tool creates a `ai-cli-config.json` file with the following options:

```json
{
  "openai_api_key": "your-api-key",
  "model": "gpt-4o-mini",
  "max_tokens": 1000,
  "temperature": 0.1,
  "safe_mode": true,
  "allowed_commands": ["ls", "pwd", "cat", "grep", ...],
  "forbidden_commands": ["rm -rf /", "dd", "mkfs", ...],
  "max_command_length": 500,
  "history_file": "ai-cli-history.json"
}
```

### Configuration Options

- **`openai_api_key`**: Your OpenAI API key
- **`model`**: AI model to use (default: gpt-4o-mini)
- **`safe_mode`**: Require confirmation before executing commands
- **`allowed_commands`**: List of safe commands to allow
- **`forbidden_commands`**: List of dangerous commands to block
- **`max_command_length`**: Maximum length of generated commands

## 🔒 Security Features

### Command Validation
- **Whitelist**: Only allows predefined safe commands
- **Blacklist**: Blocks dangerous command patterns
- **Pattern Matching**: Detects potentially harmful commands
- **Length Limits**: Prevents overly long commands

### Safe Commands Include
- File operations: `ls`, `cat`, `head`, `tail`, `grep`, `find`
- System info: `ps`, `top`, `df`, `du`, `pwd`
- Git operations: `git status`, `git log`, `git diff`
- Docker: `docker ps`, `docker images`
- And many more...

### Blocked Commands Include
- Destructive operations: `rm -rf /`, `dd`, `mkfs`
- System commands: `shutdown`, `reboot`, `killall`
- Dangerous redirects: `> /dev/`, `>> /etc/`

## 📊 Logging

The tool logs all activities to `ai-cli.log`:
- Command generation attempts
- Execution results
- Errors and warnings
- Security violations

## 🚨 Safety Considerations

1. **Always review generated commands** before execution
2. **Use safe mode** for production environments
3. **Monitor logs** for suspicious activity
4. **Keep API keys secure** and never commit them to version control
5. **Regular updates** to maintain security

## 🛠️ Advanced Usage

### Command Line Options

```bash
python ai-cli.py --config custom-config.json
python ai-cli.py --no-safe-mode
```

### Environment Variables

```bash
export OPENAI_API_KEY="your-key"
export AI_CLI_CONFIG_PATH="custom-config.json"
```

### Custom Configuration

Create a custom config file:
```json
{
  "openai_api_key": "your-key",
  "model": "gpt-4",
  "safe_mode": false,
  "allowed_commands": ["ls", "pwd", "cat"],
  "forbidden_commands": ["rm", "dd", "mkfs"]
}
```

## 🔧 Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   ❌ OpenAI API key not configured!
   ```
   Solution: Set your API key in the config file

2. **Command Blocked**
   ```
   ❌ Command 'dangerous_command' not in allowed list
   ```
   Solution: Add the command to allowed_commands in config

3. **Network Issues**
   ```
   ❌ Failed to generate command - Connection error
   ```
   Solution: Check your internet connection

### Debug Mode

Enable debug logging by modifying the logging level in the code:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Tips

1. **Use appropriate models**: gpt-4o-mini for speed, gpt-4 for accuracy
2. **Adjust temperature**: Lower values (0.1) for consistent commands
3. **Limit max_tokens**: 1000 is usually sufficient for commands
4. **Cache common commands**: The tool remembers recent commands

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is designed for safe command generation, but users should always review generated commands before execution. The authors are not responsible for any damage caused by executed commands.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `ai-cli.log`
3. Open an issue on GitHub
4. Check the configuration file for errors

---

**Happy coding! 🚀**