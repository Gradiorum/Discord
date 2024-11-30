# cogs/info.py

import discord
from discord.ext import commands

class Info(commands.Cog):
    """Information related commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        """Displays the help message."""
        # Generate a help message dynamically
        embed = discord.Embed(title="Help", description="List of available commands:", color=0x00ff00)
        for command in self.bot.commands:
            embed.add_field(name=f"{self.bot.command_prefix}{command.name}", value=command.help, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        """Get the bot's current latency."""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'Pong! Latency: {latency}ms')

    @commands.command()
    async def about(self, ctx):
        """Get information about the bot."""
        embed = discord.Embed(title="About the Bot", description="This is a custom MP3 bot.", color=0x00ff00)
        embed.add_field(name="Developer", value="Your Name")
        await ctx.send(embed=embed)

    @commands.command()
    async def stats(self, ctx):
        """Get stats about the bot."""
        embed = discord.Embed(title="Bot Statistics", color=0x00ff00)
        embed.add_field(name="Servers", value=f"{len(self.bot.guilds)}")
        embed.add_field(name="Users", value=f"{len(set(self.bot.get_all_members()))}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))
