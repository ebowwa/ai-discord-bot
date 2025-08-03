import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
import logging
from ai_proxy_core import CompletionClient

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COMMAND_PREFIX = '!ai'
MAX_MESSAGE_LENGTH = 2000

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

ai_client = CompletionClient()

@bot.event
async def on_ready():
    logger.info(f'✅ Bot is ready! Logged in as {bot.user}')
    logger.info('🤖 AI Discord Bridge is now active')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for AI requests..."))

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.content.startswith(COMMAND_PREFIX):
        prompt = message.content[len(COMMAND_PREFIX):].strip()
        
        if not prompt:
            await message.reply('Please provide a message for the AI. Example: `!ai Hello, how are you?`')
            return

        try:
            async with message.channel.typing():
                response = await ai_client.create_completion(
                    model="gemini-1.5-flash",
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )

            ai_response = response["choices"][0]["message"]["content"]
            
            if len(ai_response) > MAX_MESSAGE_LENGTH:
                chunks = split_message(ai_response, MAX_MESSAGE_LENGTH - 100)
                
                for i, chunk in enumerate(chunks):
                    embed = discord.Embed(
                        title='🤖 AI Response' if i == 0 else f'🤖 AI Response (Part {i + 1})',
                        description=chunk,
                        color=0x7289DA,
                        timestamp=message.created_at
                    )
                    embed.set_footer(text=f'Requested by {message.author.display_name}', icon_url=message.author.display_avatar.url)
                    
                    await message.reply(embed=embed)
            else:
                embed = discord.Embed(
                    title='🤖 AI Response',
                    description=ai_response,
                    color=0x7289DA,
                    timestamp=message.created_at
                )
                embed.set_footer(text=f'Requested by {message.author.display_name}', icon_url=message.author.display_avatar.url)
                
                await message.reply(embed=embed)

        except Exception as error:
            logger.error(f'Error calling AI API: {error}')
            
            error_embed = discord.Embed(
                title='❌ Error',
                description='Sorry, I encountered an error while processing your request. Please try again later.',
                color=0xFF0000,
                timestamp=message.created_at
            )
            
            await message.reply(embed=error_embed)

    await bot.process_commands(message)

@bot.command(name='ping')
async def ping(ctx):
    """Check if the bot is responsive"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title='🏓 Pong!',
        description=f'Bot latency: {latency}ms',
        color=0x00FF00
    )
    await ctx.send(embed=embed)

@bot.command(name='models')
async def list_models(ctx):
    """List available AI models"""
    try:
        models = await ai_client.list_models()
        
        if not models:
            await ctx.send("No models available. Please check your API keys.")
            return
            
        embed = discord.Embed(
            title='🤖 Available AI Models',
            description='Models available across all configured providers:',
            color=0x00FF00
        )
        
        # Group by provider
        providers = {}
        for model in models[:20]:  # Limit to first 20 models
            provider = model.get('provider', 'unknown')
            if provider not in providers:
                providers[provider] = []
            providers[provider].append(f"`{model['id']}` ({model.get('context_limit', 'N/A'):,} tokens)")
        
        for provider, model_list in providers.items():
            embed.add_field(
                name=f'{provider.title()} Models',
                value='\n'.join(model_list[:5]) + ('\n...' if len(model_list) > 5 else ''),
                inline=True
            )
        
        embed.set_footer(text='Use !ai_model <model_name> <message> to use a specific model')
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"Error listing models: {str(e)}")

@bot.command(name='ai_model')
async def ai_with_model(ctx, model_name: str, *, message: str):
    """Chat with AI using a specific model"""
    if not message.strip():
        await ctx.reply('Please provide a message after the model name.')
        return

    try:
        async with ctx.typing():
            response = await ai_client.create_completion(
                model=model_name,
                messages=[{
                    "role": "user",
                    "content": message
                }]
            )

        ai_response = response["choices"][0]["message"]["content"]
        
        if len(ai_response) > MAX_MESSAGE_LENGTH:
            chunks = split_message(ai_response, MAX_MESSAGE_LENGTH - 100)
            
            for i, chunk in enumerate(chunks):
                embed = discord.Embed(
                    title=f'🤖 {model_name} Response' if i == 0 else f'🤖 {model_name} Response (Part {i + 1})',
                    description=chunk,
                    color=0x7289DA,
                    timestamp=ctx.message.created_at
                )
                embed.set_footer(text=f'Requested by {ctx.author.display_name} • Model: {model_name}', icon_url=ctx.author.display_avatar.url)
                
                await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(
                title=f'🤖 {model_name} Response',
                description=ai_response,
                color=0x7289DA,
                timestamp=ctx.message.created_at
            )
            embed.set_footer(text=f'Requested by {ctx.author.display_name} • Model: {model_name}', icon_url=ctx.author.display_avatar.url)
            
            await ctx.reply(embed=embed)

    except Exception as error:
        logger.error(f'Error using model {model_name}: {error}')
        
        error_embed = discord.Embed(
            title='❌ Error',
            description=f'Sorry, I encountered an error using model `{model_name}`. Please check if the model name is correct or try a different model.',
            color=0xFF0000,
            timestamp=ctx.message.created_at
        )
        
        await ctx.reply(embed=error_embed)

@bot.command(name='help_ai')
async def help_ai(ctx):
    """Show help for AI commands"""
    embed = discord.Embed(
        title='🤖 AI Discord Bot Help',
        description='This bot provides access to multiple AI models through a unified interface!',
        color=0x7289DA
    )
    embed.add_field(
        name='Basic Usage',
        value=f'`{COMMAND_PREFIX} <your message>`\nExample: `{COMMAND_PREFIX} What is the weather like?`',
        inline=False
    )
    embed.add_field(
        name='Model Commands',
        value='`!models` - List available AI models\n`!ai_model <model> <message>` - Use specific model\nExample: `!ai_model gpt-4 Explain quantum physics`',
        inline=False
    )
    embed.add_field(
        name='Other Commands',
        value='`!ping` - Check bot responsiveness\n`!help_ai` - Show this help message',
        inline=False
    )
    embed.set_footer(text='Powered by AI Proxy Core - Supports OpenAI, Gemini, Ollama')
    
    await ctx.send(embed=embed)

def split_message(text, max_length):
    """Split a long message into chunks that fit Discord's character limit"""
    chunks = []
    current_chunk = ''
    
    lines = text.split('\n')
    
    for line in lines:
        if len(current_chunk) + len(line) + 1 <= max_length:
            current_chunk += ('\n' if current_chunk else '') + line
        else:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = line
            else:
                while len(line) > max_length:
                    chunks.append(line[:max_length])
                    line = line[max_length:]
                current_chunk = line
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

if __name__ == '__main__':
    discord_token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not discord_token:
        logger.error('❌ DISCORD_BOT_TOKEN not found in environment variables')
        exit(1)
    
    logger.info('🔄 AI Proxy Core will auto-detect available providers from environment variables')
    
    try:
        bot.run(discord_token)
    except Exception as e:
        logger.error(f'❌ Failed to start bot: {e}')