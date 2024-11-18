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
            await channel.send("Here is your attachment:", file=discord.File(file))
        print(f"SUCCESS: Attachment {FILE_PATH} was sent successfully.")
    except FileNotFoundError:
        print(f"ERROR: File not found at {FILE_PATH}. Check the file path.")
    except Exception as e:
        print(f"ERROR: {e}")

# Run the bot
client.run(TOKEN)
