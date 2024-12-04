# cogs/queue.py

import discord
from discord.ext import commands, tasks
from collections import deque
import os
import asyncio
import time
import tempfile

class Track:
    def __init__(self, file_path, repeats=1):
        self.file_path = file_path
        self.repeats = repeats

class MusicQueue:
    def __init__(self):
        self.queue = deque()

    def add(self, track):
        self.queue.append(track)

    def remove(self, index):
        try:
            removed_track = self.queue[index]
            del self.queue[index]
            return removed_track
        except IndexError:
            return None

    def clear(self):
        self.queue.clear()

    def get_next(self):
        if self.queue:
            track = self.queue[0]
            if track.repeats > 1:
                track.repeats -= 1
                return track
            else:
                return self.queue.popleft()
        else:
            return None

class Queue(commands.Cog):
    """Commands used for managing the queue"""

    def __init__(self, bot):
        self.bot = bot
        self.queues = {}  # Guild-specific queues
        self.allowed_extensions = ['.mp3', '.mp4', '.m4a', '.aac', '.wav', '.ogg']
        self.inactivity_timers = {}  # To track inactivity per guild

        self.check_inactivity.start()  # Start the background task

    def cog_unload(self):
        self.check_inactivity.cancel()  # Cancel the background task when the cog is unloaded

    def get_queue(self, guild):
        if guild.id not in self.queues:
            self.queues[guild.id] = MusicQueue()
        return self.queues[guild.id]

    @commands.hybrid_command(name='queue', description='Displays the current queue.')
    async def queue(self, ctx):
        """Displays the current queue."""
        queue = self.get_queue(ctx.guild)
        if queue.queue:
            message = "Current Queue:\n"
            for idx, track in enumerate(queue.queue):
                file_name = os.path.basename(track.file_path)
                message += f"{idx+1}. {file_name} (Repeats left: {track.repeats})\n"
            await ctx.send(message)
        else:
            await ctx.send("The queue is currently empty.")

    @commands.hybrid_command(name='skip', description='Skips the current track.')
    async def skip(self, ctx):
        """Skips the current track."""
        voice_client = ctx.guild.voice_client
        if voice_client and voice_client.is_playing():
            # Stop the current track
            voice_client.stop()
            await ctx.send("Skipped the current track.")
        else:
            await ctx.send("Nothing is playing right now.")

    @commands.hybrid_command(name='clear', description='Clears the queue.')
    async def clear(self, ctx):
        """Clears the queue."""
        queue = self.get_queue(ctx.guild)
        # Delete all files in the queue
        for track in queue.queue:
            self.delete_audio_file(track.file_path)
        queue.clear()
        await ctx.send("Cleared the queue.")

    @commands.hybrid_command(name='remove', description='Removes a track from the queue.')
    async def remove(self, ctx, index: int):
        """Removes a track from the queue."""
        queue = self.get_queue(ctx.guild)
        removed_track = queue.remove(index - 1)
        if removed_track:
            self.delete_audio_file(removed_track.file_path)
            await ctx.send(f"Removed track {index}.")
        else:
            await ctx.send(f"Could not remove track {index}.")

    @commands.hybrid_command(name='play', description='Queues attached audio files to play.')
    async def play(self, ctx, repeats: int = 1):
        """Queues attached audio files to play. Use `-r` to specify repeats (e.g., `!play -r 3`)."""
        # Ensure there is at least one attachment
        if not ctx.message.attachments:
            await ctx.send('Please attach audio file(s) to play.')
            return

        # Check if the user is in a voice channel
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to play music.")
            return

        queue = self.get_queue(ctx.guild)
        added_tracks = []

        for attachment in ctx.message.attachments:
            file_extension = os.path.splitext(attachment.filename)[1].lower()

            # Validate file extension
            if file_extension not in self.allowed_extensions:
                await ctx.send(f'Only the following file types are accepted: {", ".join(self.allowed_extensions)}')
                continue

            # Download the attached file
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, f"{ctx.message.id}_{attachment.filename}")
            try:
                await attachment.save(file_path)
            except Exception as e:
                await ctx.send(f'Failed to download the file {attachment.filename}.')
                print(f'Error downloading file: {e}')
                continue

            track = Track(file_path, repeats)
            queue.add(track)
            added_tracks.append(attachment.filename)

        if added_tracks:
            await ctx.send(f"Added {', '.join(added_tracks)} to the queue with {repeats} repeat(s).")
        else:
            await ctx.send("No valid audio files were added to the queue.")

        # If not connected, join the user's voice channel automatically
        voice_client = ctx.guild.voice_client
        if not voice_client or not voice_client.is_connected():
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                try:
                    voice_client = await channel.connect()
                except discord.ClientException:
                    pass  # Already connected to a channel
            else:
                await ctx.send('You need to be in a voice channel.')
                return
        elif voice_client.channel != ctx.author.voice.channel:
            await voice_client.move_to(ctx.author.voice.channel)

        # Start playing if not already
        if not voice_client.is_playing() and not voice_client.is_paused():
            await self.play_next(ctx)
        else:
            # Reset inactivity timer
            self.reset_inactivity_timer(ctx.guild.id)

    async def play_next(self, ctx):
        queue = self.get_queue(ctx.guild)
        next_track = queue.get_next()
        if next_track:
            if os.path.isfile(next_track.file_path):
                settings_cog = self.bot.get_cog('Settings')
                volume = settings_cog.get_settings(ctx.guild)['volume'] if settings_cog else 1.0

                source = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(
                        next_track.file_path,
                        options='-vn'  # Ignore video stream if present
                    ),
                    volume=volume
                )
                voice_client = ctx.guild.voice_client

                def after_playback(error):
                    if error:
                        print(f'Error during playback: {error}')
                    # Schedule the after_track coroutine in the event loop
                    asyncio.run_coroutine_threadsafe(self.after_track(ctx, next_track, error), self.bot.loop)

                voice_client.play(source, after=after_playback)

                file_name = os.path.basename(next_track.file_path)
                await ctx.send(f'Now playing: {file_name}')
                # Reset inactivity timer
                self.reset_inactivity_timer(ctx.guild.id)
            else:
                await ctx.send('Could not find the audio file.')
                # Play next track if available
                await self.play_next(ctx)
        else:
            await ctx.send('Queue is empty.')
            # Start inactivity timer
            self.reset_inactivity_timer(ctx.guild.id)

    async def after_track(self, ctx, track, error):
        if error:
            print(f'Error in playing track: {error}')
        # Delete the audio file after playing
        self.delete_audio_file(track.file_path)
        # Continue playing next track
        await self.play_next(ctx)

    def delete_audio_file(self, file_path):
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f'Deleted audio file: {file_path}')
            except Exception as e:
                print(f'Error deleting file {file_path}: {e}')

    def reset_inactivity_timer(self, guild_id):
        self.inactivity_timers[guild_id] = time.time()

    @tasks.loop(seconds=60)
    async def check_inactivity(self):
        current_time = time.time()
        for guild_id, last_active in list(self.inactivity_timers.items()):
            if current_time - last_active > 300:  # 300 seconds = 5 minutes
                guild = self.bot.get_guild(guild_id)
                if guild:
                    voice_client = guild.voice_client
                    if voice_client and voice_client.is_connected():
                        queue = self.get_queue(guild)
                        if not voice_client.is_playing() and not queue.queue:
                            await voice_client.disconnect()
                            print(f'Disconnected from voice channel in guild {guild.name} due to inactivity.')
                del self.inactivity_timers[guild_id]

    @check_inactivity.before_loop
    async def before_check_inactivity(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(f'Error: {error}')

async def setup(bot):
    await bot.add_cog(Queue(bot))
