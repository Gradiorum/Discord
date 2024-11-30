
# bot.py
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('COMMAND_PREFIX', '!')

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
intents.voice_states = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Load cogs
initial_extensions = [
    'cogs.playback',
    'cogs.queue',
    'cogs.info',
    'cogs.settings',
]

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print(f'Connected to Discord (ID: {bot.user.id})')

bot.run(TOKEN)
