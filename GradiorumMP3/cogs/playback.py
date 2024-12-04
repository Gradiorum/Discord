# cogs/playback.py

import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import os

class Playback(commands.Cog):
    """Commands used for playing audio"""

    def __init__(self, bot):
        self.bot = bot

    def get_guild_settings(self, guild):
        # Access settings stored in bot.guild_settings
        if hasattr(self.bot, 'guild_settings'):
            if guild.id in self.bot.guild_settings:
                return self.bot.guild_settings[guild.id]
        # Return default settings if none found
        return {
            'allowed_channels': None,
            'prevent_join_if_bot_present': False,
            'restricted_roles': []
        }

    @commands.hybrid_command(name='join', description='Makes the bot join your voice channel.')
    async def join(self, ctx):
        """Makes the bot join your voice channel."""
        settings = self.get_guild_settings(ctx.guild)

        if not ctx.author.voice:
            await ctx.send("You are not connected to a voice channel.")
            return

        channel = ctx.author.voice.channel

        # Check if bot should prevent joining if another bot is present
        if settings['prevent_join_if_bot_present']:
            for member in channel.members:
                if member.bot and member != self.bot.user:
                    await ctx.send("Cannot join the voice channel because another bot is already present.")
                    return

        # Check for restricted roles
        if settings['restricted_roles']:
            for member in channel.members:
                if any(role.id in settings['restricted_roles'] for role in member.roles):
                    await ctx.send(f"Cannot join the voice channel because {member.display_name} has a restricted role.")
                    return

        if ctx.voice_client and ctx.voice_client.channel != channel:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.send(f"Joined {channel.name}")

    @commands.hybrid_command(name='leave', description='Makes the bot leave the voice channel.')
    async def leave(self, ctx):
        """Makes the bot leave the voice channel."""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected from the voice channel.")
        else:
            await ctx.send("I am not connected to any voice channel.")

    @commands.hybrid_command(name='playnow', description='Plays an MP3 file from the local music directory immediately.')
    async def playnow(self, ctx, *, query: str):
        """Plays an MP3 file from the local music directory immediately."""
        # Check if the user is in a voice channel
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to play music.")
            return

        voice_client = ctx.voice_client
        if not voice_client:
            channel = ctx.author.voice.channel
            await channel.connect()
            voice_client = ctx.voice_client
        elif voice_client.channel != ctx.author.voice.channel:
            await voice_client.move_to(ctx.author.voice.channel)

        # Check if the query is a file in the music directory
        audio_path = os.path.join('music', f'{query}.mp3')
        if os.path.isfile(audio_path):
            source = FFmpegPCMAudio(audio_path)
            voice_client.stop()
            voice_client.play(source)
            await ctx.send(f'Now playing: {query}')
        else:
            await ctx.send(f'Could not find the track: {query}')

    @commands.hybrid_command(name='pause', description='Pauses the current track.')
    async def pause(self, ctx):
        """Pauses the current track."""
        voice_client = ctx.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await ctx.send("Playback paused.")
        else:
            await ctx.send("Nothing is playing right now.")

    @commands.hybrid_command(name='resume', description='Resumes the current track.')
    async def resume(self, ctx):
        """Resumes the current track."""
        voice_client = ctx.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await ctx.send("Playback resumed.")
        else:
            await ctx.send("Playback is not paused.")

    @commands.hybrid_command(name='stop', description='Stops the current track.')
    async def stop(self, ctx):
        """Stops the current track."""
        voice_client = ctx.voice_client
        if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
            voice_client.stop()
            await ctx.send("Playback stopped.")
        else:
            await ctx.send("Nothing is playing right now.")

async def setup(bot):
    await bot.add_cog(Playback(bot))
