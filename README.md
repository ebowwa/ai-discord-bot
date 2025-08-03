# AI Discord Bot

A Discord bot that provides unified access to multiple AI models (OpenAI, Gemini, Ollama) through the ai-proxy-core library. Chat with different AI models seamlessly from your Discord server.

## Features

- **Multi-Provider Support**: Access OpenAI, Gemini, and Ollama models through one interface
- **Automatic Provider Detection**: ai-proxy-core auto-detects available providers from environment
- **Model Discovery**: List all available models with `!models` command
- **Specific Model Selection**: Use `!claude_model <model> <message>` for specific models
- **AI Chat Integration**: Use `!claude <message>` for default model chat
- **Rich Embed Responses**: Formatted responses with user attribution and model info
- **Long Message Handling**: Automatically splits long responses into multiple messages
- **Zero-Config Setup**: Just add your API keys and go
- **Async/Await**: Modern Python async architecture

## Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- At least one AI provider API key:
  - **Gemini API Key** (Google AI Studio)
  - **OpenAI API Key** (OpenAI Platform) 
  - **Ollama** (local installation)

## Installation

1. **Clone or download the bot files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

4. **Configure your API keys in the `.env` file**:
   ```env
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   
   # Add any of these based on which providers you want to use:
   GEMINI_API_KEY=your_gemini_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   OLLAMA_HOST=http://localhost:11434
   ```

## Getting API Keys

### Discord Bot Token

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Add Bot"
5. Copy the Token (keep this secret!)
6. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
   - Server Members Intent (optional)

### AI Provider API Keys

#### Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key"
4. Create a new API key or use an existing one
5. Copy the API key (keep this secret!)

#### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign in to your OpenAI account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the API key (keep this secret!)

#### Ollama (Local Models)
1. Install [Ollama](https://ollama.ai/)
2. Pull models: `ollama pull llama2`, `ollama pull codellama`, etc.
3. Ensure Ollama is running on `http://localhost:11434`

## Bot Permissions

When adding the bot to your server, make sure it has these permissions:
- Send Messages
- Use Slash Commands
- Read Message History
- Embed Links
- Add Reactions

## Usage

### Basic Commands

- `!claude <message>` - Chat with default AI model
- `!models` - List all available AI models
- `!claude_model <model> <message>` - Chat with specific model
- `!ping` - Check bot responsiveness
- `!help_claude` - Show help information

### Examples

```
# Basic chat (uses default model)
!claude What is the weather like today?

# List available models
!models

# Use specific models
!claude_model gpt-4 Write a Python function to calculate fibonacci numbers
!claude_model gemini-1.5-flash Explain quantum computing in simple terms
!claude_model llama2 Tell me a joke
```

## Running the Bot

```bash
python bot.py
```

The bot will start and connect to Discord. You should see:
```
✅ Bot is ready! Logged in as YourBotName#1234
🤖 Claude Discord Bridge is now active
```

## Project Structure

```
claude-discord-bot/
├── bot.py              # Main bot code
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variable template
├── .env              # Your actual environment variables (create this)
└── README.md         # This file
```

## Dependencies

- `discord.py` - Discord bot framework
- `ai-proxy-core==0.3.1` - Unified AI model integration library
- `python-dotenv` - Environment variable management

## Troubleshooting

### Bot doesn't respond
- Check that the bot has the correct permissions in your Discord server
- Verify your Discord bot token is correct
- Make sure the bot is online (green status)

### API errors
- Verify your API keys are valid (run `!models` to check)
- Check your provider quotas/billing (OpenAI, Google AI Studio)
- For Ollama, ensure it's running locally
- Ensure you have internet connectivity

### Installation issues
- Make sure you're using Python 3.8+
- Try creating a virtual environment:
  ```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
  pip install -r requirements.txt
  ```

## Advanced Features

### Model Selection
The bot automatically detects which AI providers are available based on your environment variables and lists them with the `!models` command.

### Provider Auto-Detection
ai-proxy-core automatically routes requests to the appropriate provider based on the model name:
- `gpt-4`, `gpt-3.5-turbo` → OpenAI
- `gemini-1.5-flash`, `gemini-pro` → Google Gemini
- `llama2`, `codellama` → Ollama (local)

### Zero Configuration
No complex setup required - just add your API keys and the bot handles the rest!

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License