import pandas as pd
import numpy as np
import discord
import asyncio
from discord.ext import tasks
import argparse
from dotenv import load_dotenv
import os
from time import sleep

# Load environment variables from .env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1300145995014865053 # Replace with the actual channel ID

class TrafficSimulator(discord.Client):
    def __init__(self, counts, bin_edges, possible_file_uploads, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counts = counts
        self.bin_edges = bin_edges
        self.possible_file_uploads = possible_file_uploads

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        print(f'Starting traffic simulation...')
        await self.simulate_traffic()

    async def simulate_traffic(self):
        """
        Simulate traffic based on histogram data.
        """
        channel = self.get_channel(CHANNEL_ID)
        if not channel:
            print("Channel not found. Ensure the CHANNEL_ID is correct.")
            return

        # Given the histogram obtain the probability of each bin
        probabilities = self.counts / np.sum(self.counts)

        # Print the probabilities
        print("Probabilities:")
        print(probabilities)

        # Simulate traffic based on the probabilities of the intervals
        while True:
            # Choose an interval based on the probabilities
            interval = np.random.choice(self.bin_edges[:-1], p=probabilities)

            await channel.send(f"Simulated traffic for {interval} seconds.")

            # Wait for the next interval
            await asyncio.sleep(interval)

def process_traffic(input_file: str, silence_threshold : int = 9, packet_threshold: int = 200) -> tuple:
    # Load the CSV file exported from Wireshark (remove the index column if it exists)
    data = pd.read_csv(input_file)

    # Convert 'Time' column to seconds (assuming it's already relative to the start)
    data['Time'] = data['Time'].astype(float)

    # Define time intervals
    interval = 10  # Interval duration in seconds
    data['Time_Interval'] = (data['Time'] // interval).astype(int)

    # Calculate the start and end time of each interval
    data['Time Started'] = data['Time_Interval'] * interval
    data['Time Ended'] = (data['Time_Interval'] + 1) * interval

    # Aggregate by interval, including protocol counts
    data_summary = data.groupby(['Time Started', 'Time Ended']).size().reset_index(name='PacketCount')

    # Filter the data with more than 200 packets
    data_filtered = data_summary[data_summary['PacketCount'] > silence_threshold]

    print("Filtered Data:")
    print(data_filtered)

    # Obtain the average of the packet count (as integer)
    average_packet_count = int(data_filtered['PacketCount'].mean())

    # Print the average packet count
    print(f"Average packet count per interval: {average_packet_count}")

    data_activity = data_filtered[data_filtered['PacketCount'] > average_packet_count]

    # Obtain the intervals between each activity in an array (in seconds)
    time_between_activity = [
        data_activity.iloc[row + 1]['Time Started'] - data_activity.iloc[row]['Time Ended']
        for row in range(len(data_activity) - 1)
    ]

    # TODO: Verify if the time activity is 0 and check if the packets are below a certain threshold (200)
    possible_file_uploads = []
    for row in range(len(data_activity) - 1):
        time_gap = data_activity.iloc[row + 1]['Time Started'] - data_activity.iloc[row]['Time Ended']
        packet_count = data_activity.iloc[row]['PacketCount']
        if time_gap == 0 and packet_count >= packet_threshold:
            possible_file_uploads.append((data_activity.iloc[row]['Time Started'], packet_count))

    if possible_file_uploads:
        print("\nPossible File Uploads Detected:")
        for upload in possible_file_uploads:
            print(f"Start Time: {upload[0]}, Packet Count: {upload[1]}")
    else:
        print("\nNo file uploads detected.")


    # Compute histogram data
    counts, bin_edges = np.histogram(time_between_activity, bins=50)

    return counts, bin_edges, possible_file_uploads

def main():
    parser = argparse.ArgumentParser(description="Process Wireshark UDP traffic data and send messages via Discord.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input CSV file")
    # parser.add_argument("-c", "--client-ip", required=True, help="Client IP address")
    args = parser.parse_args()

    # Process the traffic data
    counts, bin_edges, possible_file_uploads = process_traffic(args.input)

    # Start the Discord bot
    intents = discord.Intents.default()
    intents.messages = True
    client = TrafficSimulator(counts, bin_edges, possible_file_uploads, intents=intents)
    client.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()