import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

def get_token() -> str:
    load_dotenv()
    return os.getenv('DISCORD_TOKEN')

TOKEN = get_token()
CHANNEL_ID = 1300145995014865053  # Example: 987654321098765432
FILE_PATH = "teste.txt"  # Replace with the actual file path
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

    # Send the attachment
    try:
        with open(FILE_PATH, "rb") as file:
            if os.path.getsize(FILE_PATH) > MAX_FILE_SIZE:
                split_file(FILE_PATH)
                for part in os.listdir():
                    if part.startswith(FILE_PATH) and part != FILE_PATH:
                        await channel.send("Here is your attachment:", file=discord.File(part))
                        os.remove(part)
            else:
                await channel.send("Here is your attachment:", file=discord.File(file))
        print(f"SUCCESS: Attachment {FILE_PATH} was sent successfully.")
    except FileNotFoundError:
        print(f"ERROR: File not found at {FILE_PATH}. Check the file path.")
    except Exception as e:
        print(f"ERROR: {e}")

# Run the bot
client.run(TOKEN)
