# cogs/info.py

import discord
from discord.ext import commands

class Info(commands.Cog):
    """Information related commands and settings"""

    def __init__(self, bot):
        self.bot = bot
        # Initialize guild-specific settings
        if not hasattr(bot, 'guild_settings'):
            bot.guild_settings = {}
        self.guild_settings = bot.guild_settings

    def get_guild_settings(self, guild):
        if guild.id not in self.guild_settings:
            # Default settings for the guild
            self.guild_settings[guild.id] = {
                'allowed_channels': None,  # None means all channels are allowed
                'prevent_join_if_bot_present': False,
                'restricted_roles': []  # Roles that prevent the bot from joining
            }
        return self.guild_settings[guild.id]

    # Command to display the help message
    @commands.hybrid_command(name='help', description='Displays the help message.')
    async def help(self, ctx):
        """Displays the help message."""
        settings = self.get_guild_settings(ctx.guild)
        allowed_channels = settings['allowed_channels']
        if allowed_channels and ctx.channel.id not in allowed_channels:
            return  # Do not respond if channel is not allowed

        embed = discord.Embed(title="Help", description="List of available commands:", color=0x00ff00)
        for command in self.bot.commands:
            if command.hidden:
                continue  # Skip hidden commands
            embed.add_field(name=f"{self.bot.command_prefix}{command.name}", value=command.help, inline=False)
        await ctx.send(embed=embed)

    # Command to get the bot's latency
    @commands.hybrid_command(name='ping', description="Get the bot's current latency.")
    async def ping(self, ctx):
        """Get the bot's current latency."""
        settings = self.get_guild_settings(ctx.guild)
        allowed_channels = settings['allowed_channels']
        if allowed_channels and ctx.channel.id not in allowed_channels:
            return

        latency = round(self.bot.latency * 1000)
        await ctx.send(f'Pong! Latency: {latency}ms')

    # Command to get information about the bot
    @commands.hybrid_command(name='about', description='Get information about the bot.')
    async def about(self, ctx):
        """Get information about the bot."""
        settings = self.get_guild_settings(ctx.guild)
        allowed_channels = settings['allowed_channels']
        if allowed_channels and ctx.channel.id not in allowed_channels:
            return

        embed = discord.Embed(title="About the Bot", description="This is a custom MP3 bot.", color=0x00ff00)
        embed.add_field(name="Developer", value="Your Name")
        await ctx.send(embed=embed)

    # Command to get the bot's statistics
    @commands.hybrid_command(name='stats', description='Get stats about the bot.')
    async def stats(self, ctx):
        """Get stats about the bot."""
        settings = self.get_guild_settings(ctx.guild)
        allowed_channels = settings['allowed_channels']
        if allowed_channels and ctx.channel.id not in allowed_channels:
            return

        embed = discord.Embed(title="Bot Statistics", color=0x00ff00)
        embed.add_field(name="Servers", value=f"{len(self.bot.guilds)}")
        embed.add_field(name="Users", value=f"{len(set(self.bot.get_all_members()))}")
        await ctx.send(embed=embed)

    # Command to set allowed text channels
    @commands.hybrid_command(
        name='set_allowed_channels',
        description='Sets channels where the bot is allowed to respond.'
    )
    @commands.has_permissions(administrator=True)
    async def set_allowed_channels(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        """Sets the channels where the bot is allowed to respond. Use without arguments to allow all channels."""
        settings = self.get_guild_settings(ctx.guild)
        if channels:
            settings['allowed_channels'] = [channel.id for channel in channels]
            channel_mentions = ', '.join(channel.mention for channel in channels)
            await ctx.send(f"Bot will now respond only in the following channels: {channel_mentions}")
        else:
            settings['allowed_channels'] = None
            await ctx.send("Bot will now respond in all channels.")

    # Command to toggle checking for other bots in voice channels
    @commands.hybrid_command(
        name='toggle_bot_check',
        description='Toggles whether the bot checks for other bots before joining voice channels.'
    )
    @commands.has_permissions(administrator=True)
    async def toggle_bot_check(self, ctx):
        """Toggles whether the bot should check for other bots in voice channels before joining."""
        settings = self.get_guild_settings(ctx.guild)
        settings['prevent_join_if_bot_present'] = not settings['prevent_join_if_bot_present']
        status = "enabled" if settings['prevent_join_if_bot_present'] else "disabled"
        await ctx.send(f"Preventing join if another bot is present is now **{status}**.")

    # Command to set roles that prevent the bot from joining a voice channel
    @commands.hybrid_command(
        name='set_restricted_roles',
        description='Sets roles that prevent the bot from joining if users with these roles are in voice.'
    )
    @commands.has_permissions(administrator=True)
    async def set_restricted_roles(self, ctx, roles: commands.Greedy[discord.Role]):
        """Sets roles that prevent the bot from joining if a user with one of these roles is in the voice channel."""
        settings = self.get_guild_settings(ctx.guild)
        if roles:
            settings['restricted_roles'] = [role.id for role in roles]
            role_names = ', '.join(role.name for role in roles)
            await ctx.send(f"Bot will not join if users with the following roles are in the voice channel: {role_names}")
        else:
            settings['restricted_roles'] = []
            await ctx.send("Bot will now join regardless of user roles in the voice channel.")

async def setup(bot):
    await bot.add_cog(Info(bot))

