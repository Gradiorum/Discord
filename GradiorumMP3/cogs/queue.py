# cogs/queue.py

import discord
from discord.ext import commands
from collections import deque
import os

class MusicQueue:
    def __init__(self):
        self.queue = deque()

    def add(self, item):
        self.queue.append(item)

    def remove(self, index):
        try:
            removed_item = self.queue[index]
            del self.queue[index]
            return removed_item
        except IndexError:
            return None

    def clear(self):
        self.queue.clear()

    def get_next(self):
        if self.queue:
            return self.queue.popleft()
        else:
            return None

class Queue(commands.Cog):
    """Commands used for managing the queue"""

    def __init__(self, bot):
        self.bot = bot
        self.queues = {}  # Guild-specific queues

    def get_queue(self, guild):
        if guild.id not in self.queues:
            self.queues[guild.id] = MusicQueue()
        return self.queues[guild.id]

    @commands.command()
    async def queue(self, ctx):
        """Displays the current queue."""
        queue = self.get_queue(ctx.guild)
        if queue.queue:
            message = "Current Queue:\n"
            for idx, item in enumerate(queue.queue):
                message += f"{idx+1}. {item}\n"
            await ctx.send(message)
        else:
            await ctx.send("The queue is currently empty.")

    @commands.command()
    async def skip(self, ctx):
        """Skips the current track."""
        voice_client = ctx.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await ctx.send("Skipped the current track.")
            # Play the next track if available
            await self.play_next(ctx)
        else:
            await ctx.send("Nothing is playing right now.")

    @commands.command()
    async def clear(self, ctx):
        """Clears the queue."""
        queue = self.get_queue(ctx.guild)
        queue.clear()
        await ctx.send("Cleared the queue.")

    @commands.command()
    async def remove(self, ctx, index: int):
        """Removes a track from the queue."""
        queue = self.get_queue(ctx.guild)
        removed_item = queue.remove(index - 1)
        if removed_item:
            await ctx.send(f"Removed track {index}: {removed_item}")
        else:
            await ctx.send(f"Could not remove track {index}.")

    @commands.command(name='play', aliases=['p'])
    async def play(self, ctx, *, query: str):
        """Queues a track to play."""
        queue = self.get_queue(ctx.guild)
        queue.add(query)
        await ctx.send(f"Added {query} to the queue.")

        # If nothing is playing, start playing
        voice_client = ctx.voice_client
        if not voice_client:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                voice_client = await channel.connect()
            else:
                await ctx.send("You need to be in a voice channel.")
                return

        if not voice_client.is_playing():
            await self.play_next(ctx)

    async def play_next(self, ctx):
        queue = self.get_queue(ctx.guild)
        next_track = queue.get_next()
        if next_track:
            audio_path = os.path.join('music', f'{next_track}.mp3')
            if os.path.isfile(audio_path):
                settings = self.bot.get_cog('Settings')
                volume = settings.get_settings(ctx.guild)['volume'] if settings else 1.0

                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(audio_path), volume=volume)
                voice_client = ctx.voice_client
                voice_client.play(source, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
                await ctx.send(f"Now playing: {next_track}")
            else:
                await ctx.send(f"Could not find the track: {next_track}")
                # Play next track if available
                await self.play_next(ctx)
        else:
            await ctx.send("Queue is empty.")
            # Optionally disconnect after playback
            await ctx.voice_client.disconnect()

async def setup(bot):
    await bot.add_cog(Queue(bot))
