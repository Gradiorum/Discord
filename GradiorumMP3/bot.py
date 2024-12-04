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

# List of cogs to load
initial_extensions = [
    'cogs.playback',
    'cogs.queue',
    'cogs.info',
    'cogs.settings',
]

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def setup_hook(self):
        # Load extensions
        for extension in initial_extensions:
            await self.load_extension(extension)
        # Sync commands globally
        await self.tree.sync()
        print(f'Synced application commands globally.')

bot = MyBot(command_prefix=PREFIX, intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    print(f'Connected to Discord (ID: {bot.user.id})')

if __name__ == '__main__':
    bot.run(TOKEN)

