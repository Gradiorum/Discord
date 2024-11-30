# cogs/playback.py

import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import os

class Playback(commands.Cog):
    """Commands used for playing audio"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        """Makes the bot join your voice channel."""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            await ctx.send(f"Joined {channel}")
        else:
            await ctx.send("You are not connected to a voice channel.")

    @commands.command()
    async def leave(self, ctx):
        """Makes the bot leave the voice channel."""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected from the voice channel.")
        else:
            await ctx.send("I am not connected to any voice channel.")

    @commands.command()
    async def play(self, ctx, *, query: str):
        """Plays an MP3 file from the local music directory."""
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to play music.")
            return

        voice_client = ctx.voice_client
        if not voice_client:
            channel = ctx.author.voice.channel
            voice_client = await channel.connect()

        # Check if the query is a file in the music directory
        audio_path = os.path.join('music', f'{query}.mp3')
        if os.path.isfile(audio_path):
            source = FFmpegPCMAudio(audio_path)
            voice_client.play(source)
            await ctx.send(f'Now playing: {query}')
        else:
            await ctx.send(f'Could not find the track: {query}')

    @commands.command()
    async def pause(self, ctx):
        """Pauses the current track."""
        voice_client = ctx.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await ctx.send("Playback paused.")
        else:
            await ctx.send("Nothing is playing right now.")

    @commands.command()
    async def resume(self, ctx):
        """Resumes the current track."""
        voice_client = ctx.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await ctx.send("Playback resumed.")
        else:
            await ctx.send("Playback is not paused.")

    @commands.command()
    async def stop(self, ctx):
        """Stops the current track."""
        voice_client = ctx.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await ctx.send("Playback stopped.")
        else:
            await ctx.send("Nothing is playing right now.")

async def setup(bot):
    await bot.add_cog(Playback(bot))
