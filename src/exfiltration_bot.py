import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
from random import random

def get_token() -> str:
    load_dotenv()

    if 'DISCORD_TOKEN' not in os.environ:
        raise ValueError("DISCORD_TOKEN not found in environment variables.")

    return os.getenv('DISCORD_TOKEN')

TOKEN = get_token()
CHANNEL_ID = 1300145995014865053  # Replace with the actual channel ID
PATH = "data"  # Replace with the actual file path
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Intents (use default since we don't need privileged intents here)
intents = discord.Intents.default()

# Client for the bot
client = discord.Client(intents=intents)

def split_file(file_path, chunk_size=MAX_FILE_SIZE):
    with open(file_path, 'rb') as f:
        chunk_number = 0
        while chunk := f.read(chunk_size):
            with open(f"{file_path}.part{chunk_number}", 'wb') as chunk_file:
                chunk_file.write(chunk)
            chunk_number += 1
    print(f"File split into {chunk_number} parts.")

@client.event
async def on_ready():
    print(f'Bot {client.user} has connected to Discord!')

    # Get the channel
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Channel not found. Make sure the CHANNEL_ID is correct.")
        return
    
    if not os.path.exists(PATH):
        print(f"ERROR: Path {PATH} does not exist.")
        return

    sleep_interval = [20, 40]

    # Send every file in the directory PATH, but if the file is larger than 10 MB, split it
    for file in os.listdir(PATH):
        file_path = os.path.join(PATH, file)
        if os.path.isfile(file_path):
            if os.path.getsize(file_path) <= MAX_FILE_SIZE:
                await channel.send("Here is your attachment:", file=discord.File(file_path))
                print(f"Sent {file_path}")
                # Sleep for a random interval between sleep_interval[0] and sleep_interval[1]
                await asyncio.sleep(sleep_interval[0] + (sleep_interval[1] - sleep_interval[0]) * random())
            else:
                split_file(file_path)
                for part in os.listdir(PATH):
                    part_path = os.path.join(PATH, part)
                    if part.startswith(file + ".part"):
                        await channel.send("Here is your attachment:", file=discord.File(part_path))
                        print(f"Sent {part_path}")
                        os.remove(part_path)
                        # Sleep for a random interval between sleep_interval[0] and sleep_interval[1]
                        await asyncio.sleep(sleep_interval[0] + (sleep_interval[1] - sleep_interval[0]) * random())
    print("All files sent successfully.")

# Run the bot
client.run(TOKEN)