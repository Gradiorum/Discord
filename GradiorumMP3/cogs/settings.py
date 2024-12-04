# cogs/settings.py

import discord
from discord.ext import commands

class Settings(commands.Cog):
    """Commands used for configuring settings"""

    def __init__(self, bot):
        self.bot = bot
        self.settings = {}  # Guild-specific settings

    def get_settings(self, guild):
        if guild.id not in self.settings:
            self.settings[guild.id] = {'volume': 1.0}
        return self.settings[guild.id]

    @commands.hybrid_command(name='volume', description='Changes the playback volume (0-100).')
    async def volume(self, ctx, volume: int):
        """Changes the playback volume (0-100)."""
        if 0 <= volume <= 100:
            settings = self.get_settings(ctx.guild)
            settings['volume'] = volume / 100.0
            voice_client = ctx.voice_client
            if voice_client and voice_client.source:
                voice_client.source.volume = settings['volume']
            await ctx.send(f"Volume set to {volume}%")
        else:
            await ctx.send("Please enter a value between 0 and 100.")

async def setup(bot):
    await bot.add_cog(Settings(bot))
