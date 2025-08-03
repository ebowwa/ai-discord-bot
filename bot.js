const { Client, GatewayIntentBits, EmbedBuilder } = require('discord.js');
const Anthropic = require('@anthropic-ai/sdk');
require('dotenv').config();

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.DirectMessages
    ]
});

const anthropic = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY,
});

const COMMAND_PREFIX = '!claude';
const MAX_MESSAGE_LENGTH = 2000;

client.once('ready', () => {
    console.log(`✅ Bot is ready! Logged in as ${client.user.tag}`);
    console.log(`🤖 Claude Discord Bridge is now active`);
    
    client.user.setActivity('Waiting for Claude requests...', { type: 'WATCHING' });
});

client.on('messageCreate', async (message) => {
    if (message.author.bot) return;
    
    if (message.content.startsWith(COMMAND_PREFIX)) {
        const prompt = message.content.slice(COMMAND_PREFIX.length).trim();
        
        if (!prompt) {
            return message.reply('Please provide a message for Claude. Example: `!claude Hello, how are you?`');
        }

        try {
            const typingInterval = setInterval(() => {
                message.channel.sendTyping().catch(() => {});
            }, 5000);

            await message.channel.sendTyping();

            const response = await anthropic.messages.create({
                model: 'claude-3-5-sonnet-20241022',
                max_tokens: 4000,
                messages: [{
                    role: 'user',
                    content: prompt
                }]
            });

            clearInterval(typingInterval);

            const claudeResponse = response.content[0].text;
            
            if (claudeResponse.length > MAX_MESSAGE_LENGTH) {
                const chunks = splitMessage(claudeResponse, MAX_MESSAGE_LENGTH - 100);
                
                for (let i = 0; i < chunks.length; i++) {
                    const embed = new EmbedBuilder()
                        .setColor(0x7289DA)
                        .setTitle(i === 0 ? '🤖 Claude Response' : `🤖 Claude Response (Part ${i + 1})`)
                        .setDescription(chunks[i])
                        .setTimestamp()
                        .setFooter({ text: `Requested by ${message.author.username}`, iconURL: message.author.displayAvatarURL() });
                    
                    await message.reply({ embeds: [embed] });
                }
            } else {
                const embed = new EmbedBuilder()
                    .setColor(0x7289DA)
                    .setTitle('🤖 Claude Response')
                    .setDescription(claudeResponse)
                    .setTimestamp()
                    .setFooter({ text: `Requested by ${message.author.username}`, iconURL: message.author.displayAvatarURL() });
                
                await message.reply({ embeds: [embed] });
            }

        } catch (error) {
            console.error('Error calling Claude API:', error);
            
            const errorEmbed = new EmbedBuilder()
                .setColor(0xFF0000)
                .setTitle('❌ Error')
                .setDescription('Sorry, I encountered an error while processing your request. Please try again later.')
                .setTimestamp();
            
            await message.reply({ embeds: [errorEmbed] });
        }
    }
});

client.on('error', error => {
    console.error('Discord client error:', error);
});

client.on('warn', warning => {
    console.warn('Discord client warning:', warning);
});

function splitMessage(text, maxLength) {
    const chunks = [];
    let currentChunk = '';
    
    const lines = text.split('\n');
    
    for (const line of lines) {
        if (currentChunk.length + line.length + 1 <= maxLength) {
            currentChunk += (currentChunk ? '\n' : '') + line;
        } else {
            if (currentChunk) {
                chunks.push(currentChunk);
                currentChunk = line;
            } else {
                while (line.length > maxLength) {
                    chunks.push(line.substring(0, maxLength));
                    line = line.substring(maxLength);
                }
                currentChunk = line;
            }
        }
    }
    
    if (currentChunk) {
        chunks.push(currentChunk);
    }
    
    return chunks;
}

process.on('unhandledRejection', error => {
    console.error('Unhandled promise rejection:', error);
});

client.login(process.env.DISCORD_BOT_TOKEN);