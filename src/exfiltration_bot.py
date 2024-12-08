import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from random import random, randint

def get_token() -> str:
    load_dotenv()

    if 'DISCORD_TOKEN' not in os.environ:
        raise ValueError("DISCORD_TOKEN not found in environment variables.")

    return os.getenv('DISCORD_TOKEN')

TOKEN = get_token()
CHANNEL_ID = 1300145995014865053  # Replace with the actual channel ID
PATH = "data"  # Replace with the actual file path
DISCORD_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
DISCORD_MIN_FILE_SIZE = 1 * 1024 * 1024  # 1 MB


configurations = {
    "sleep_interval_seconds": [20, 40],  # Normal interval between sending files
    "batch_interval_seconds": 120,  # Longer interval after reaching max files
    "max_files_per_batch": 5  # Maximum files to send before taking a longer break
}

# Intents (use default since we don't need privileged intents here)
intents = discord.Intents.default()

# Client for the bot
client = discord.Client(intents=intents)


def split_file(file_path: str, chunk_size: int = DISCORD_MAX_FILE_SIZE, min_chunk_size: int = DISCORD_MIN_FILE_SIZE) -> None:
    """
    Split a large file into smaller chunks with random sizes.
    
    Args:
        file_path (str): The path to the file to be split.
        chunk_size (int): The maximum size of any chunk (default: DISCORD_MAX_FILE_SIZE).
        min_chunk_size (int): The minimum size of any chunk (default: 1MB).
    """
    if min_chunk_size > chunk_size:
        raise ValueError("min_chunk_size cannot be greater than chunk_size.")
    
    with open(file_path, 'rb') as f:
        chunk_number = 0
        while True:
            # Generate a random size between min_chunk_size and chunk_size
            random_size = randint(min_chunk_size, chunk_size)
            chunk = f.read(random_size)
            if not chunk:
                break
            
            # Write the chunk to a new file
            chunk_file_path = f"{file_path}.part{chunk_number}"
            with open(chunk_file_path, 'wb') as chunk_file:
                chunk_file.write(chunk)
            
            print(f"Created: {chunk_file_path} with size {len(chunk) / 1024 ** 2:.2f} MB.")
            chunk_number += 1
    
    print(f"File split into {chunk_number} parts.")


@client.event
async def on_ready():
    """
    Event handler for when the bot is ready.

    This function will be called when the bot has successfully connected to Discord.
    """

    print(f'Bot {client.user} has connected to Discord!')

    # Get the channel
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Channel not found. Make sure the CHANNEL_ID is correct.")
        return
    
    if not os.path.exists(PATH):
        print(f"ERROR: Path {PATH} does not exist.")
        return

    async def send_file(file_path : str):
        """Handles sending a single file to the channel.
        
        Args:
            file_path (str): The path to the file to be sent.
        """
        await channel.send("Here is your attachment:", file=discord.File(file_path))
        print(f"Sent {file_path} with {os.path.getsize(file_path) / 1024 ** 2:.2f} MB.")

    async def handle_batch(file_paths : list):
        """Handles sending files with batching logic.
        
        Args:
            file_paths (List[str]): List of file paths to be sent.
        """
        files_sent = 0
        for file_path in file_paths:

            await send_file(file_path)
            files_sent += 1

            if files_sent >= configurations["max_files_per_batch"]:
                print(f"Batch limit reached. Sleeping for {configurations['batch_interval_seconds']} seconds.")
                await asyncio.sleep(configurations["batch_interval_seconds"])
                files_sent = 0  # Reset the counter
                continue

            await asyncio.sleep(configurations["sleep_interval_seconds"][0] + random() * (configurations["sleep_interval_seconds"][1] - configurations["sleep_interval_seconds"][0]))

    # Gather all files to send
    file_paths = []
    for file in os.listdir(PATH):
        file_path = os.path.join(PATH, file)
        if not os.path.isfile(file_path):
            continue

        if os.path.getsize(file_path) > DISCORD_MAX_FILE_SIZE:
            # Split large files and add the parts
            split_file(file_path)
            for part in os.listdir(PATH):
                part_path = os.path.join(PATH, part)
                if not part.startswith(file + ".part"):
                    continue
                file_paths.append(part_path)
            continue

        file_paths.append(file_path)

    # Send all files
    await handle_batch(file_paths)

    print(f"Cleaning all the split files from {PATH}.")

    # Cleanup split files
    for file_path in file_paths:
        if ".part" in file_path:
            os.remove(file_path)

    print(f"All files from {PATH} have been sent.")

    print("Closing the bot.")
    await client.close()

# Run the bot
client.run(TOKEN)