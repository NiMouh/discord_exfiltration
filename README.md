# Data Exfiltration Detection in Discord using ML

## Authors

- Ana Vidal
- Simão Andrade

## Phase 1: Problem Brainstorm

### Problem

- Discord is a popular communication platform that can be used to exfiltrate data
- Data exfiltration can be done in many ways, such as:
  - Sending messages
  - Sending files
  - Using voice channels
  
#### Why is it difficult to solve?

One of the biggest challenges in detecting data exfiltration via Discord is the fact that all communication is encrypted. When data is sent to a webhook, Discord uses HTTPS (HTTP over TLS), which means that the data is encrypted during transmission. This encryption makes it impossible for most network security devices, such as firewalls and Deep Packet Inspection (DPI) systems, which analyze individual packets to identify suspicious content, to directly inspect the content of the traffic. So, although it is possible to see that there is communication with Discord, it is not possible to analyze or filter the content of the data sent due to encryption, which makes this channel an ideal vehicle for exfiltrating data undetected.

Firewalls and SIEM systems based on fixed rules face a critical limitation here. Without access to the encrypted content of the packets, these systems can only monitor basic metadata, such as the destination IP address, the port, and the volume of data. However, as Discord is widely used and permitted on many corporate networks, this traffic appears legitimate and doesn't immediately raise suspicions.

Data exfiltration via Discord webhooks is a very popular technique because of the way it takes advantage of the platform's infrastructure to mask malicious activity. These features, designed to facilitate automated integrations and notifications, end up being exploited in cyber attacks, allowing sensitive information to be sent outside the network undetected.

> [!NOTE]
> Although Discord made some updates regarding security ([link](https://discord.com/blog/discord-update-september-26-2024-changelog)), malicious users still take advantage of tools that allow development of plugins.

### Real life examples

Some examples of data exfiltration using Discord:

- [The Hacker News - NS Stealer Uses Discord Bots to Exfiltrate Data](https://thehackernews.com/2024/01/ns-stealer-uses-discord-bots-to.html)
- [Intel471 - How Discord is Abused for Cybercrime](https://intel471.com/blog/how-discord-is-abused-for-cybercrime)

### Discovery

- It has a built-in function that enables automated messages sent to a text channel in the server (Webhooks) and a API for bot creation (discord.py).
- Allows the upload of a variety file types (e.g. PNG, PDF, MP4).
- The **maximum file upload** is 10MB.

### Filtering

- **Network Pool:** `162.159.0.0/16` - Owned by Cloudflare, Inc.

> Reference: [NsLookup.io](https://www.nslookup.io/domains/discordapp.com/webservers/)

- **Protocols Used for communication:** `TCP`
  - **Destination Port(s):** TCP/80 and TCP/443
  - **Source Port(s):** UDP/50000-65535
- **Protocols Used for voice-communication/attachments:** `QUIC`

> [!NOTE]
> Additional information to look for:
>
> - [ ] Sender's user data
> - [ ] Receiver's user data
> - [ ] Server where the message is sent through
> - [ ] Type of data sended
> - [ ] Notifications received

### Aggregation

To perform the analysis, the following data will be extracted:

- **Group and Private Conversations** – the conversation type is obtained at the packet level (uploads/downloads)
- **Daily and Weekly message flow with various formats of files** – analyzing the timestamps of interactions (uploads/downloads)

### Collection

In a **testing context** we are going to use:

- **Wireshark:** For network analysis
- **Burp Suite:** Proxy tools for traffic capturing

But in a **real life** context, we could use:

- **Syslog and Agents:** To obtain data from endpoints and discord activity
- **Suricata or Palo Alto Networks Firewalls:** To monitor ports and protocols in use, e.g. TCP and QUIC, and detect unusual or unauthorized traffic.

### Sampling and Processing

We are going to focus on **packet data**, since there's **no abundance of flows used**, where it has the following fields:

- **IP Source**
- **IP Destination**
- **Packet Size (in bytes)**
- **Packet Timestamp (in seconds)**
- **IP Protocol Number**

In order to convert our **qualitative** data into **quantitive** data, we chosen a **sampling interval of 1 second**.

> This allows a balance between the level of detail needed to capture relevant events and the volume of data generated

This metrics obtained in the sampling interval are:

- **Download/Upload Size of TCP Packets (in bytes)**
- **Download/Upload Size of UDP Packets (in bytes)**
- **Download/Upload Number of TCP Packets**
- **Download/Upload Number of UDP Packets**

> In the following order: `tcp_upload_packets, tcp_upload_bytes, udp_upload_packets, udp_upload_bytes, tcp_download_packets, tcp_download_bytes, udp_download_packets, udp_download_bytes`

### Feature Extraction

This function extracts the following features:

- **Mean and Variance of silence and activity times**
- **Mean, standard deviation and 25th, 50th and 75th quartiles of upload and download bytes for TCP and UDP (separately)**
- **Mean and standard deviation of total bytes**
- **Mean and standard deviation of number of packets**

> In the following order: `mean_silence_duration, variance_silence_duration, mean_activity_duration, variance_activity_duration, quartiles_activity_duration,tcp_upload_bytes_std_dev, tcp_download_bytes_std_dev, udp_upload_bytes_std_dev, udp_download_bytes_std_dev,tcp_upload_bytes_mean, tcp_download_bytes_mean, udp_upload_bytes_mean, udp_download_bytes_mean,quartiles_upload_bytes, quartiles_download_bytes,bytes_mean, bytes_std_dev,packets_mean, packets_std_dev`

> [!IMPORTANT]
> Threshold of silence activity (number of packets) is tbc.

### Production

**Benign Behavior:** It will be done by performing normal usage of the application, made by:

- Humans: sending messages and files as usual
- Bots: made by plugins added to the server

**Malicious Behavior:** It will be done using tree types of bots:

- Easy to Detect:
  - Size: 10MB
  - Frequency: Periodically (40s)
- Intermediate to Detect:
  - Size: 1-10MB
  - Frequency: Same variance as a normal behavior
- Hard (almost impossible) to Detect: Through embedded images, using Discord CDN

> [!NOTE]
> Command to make random files: `dd if=/dev/urandom of=file.txt bs=1M count=10` (10MB)

The files used in the exfiltration process will be located in the `data` folder.

### Tasks to be done

- [x] Problem Brainstorm
- [ ] Data Collection
- [x] Define the Features
- [ ] Data Processing
- [ ] Choose the Models and define the parameters
- [ ] Model Training
- [ ] Model Evaluation

## Phase 2: Project Development

### Project Structure

```bash
.
├── presentation/ (folder with the slides)
│
├── src/
│   ├── .env (file with the Discord Token)
│   ├── data_sampling.py (script to sample the data)
│   ├── data_processing.py (script to extract the features)
│   ├── exfiltration_bot.py
│   ├── model.ipynb (notebook with the model selection)
│   ├── data/ (folder with the data to be exfiltrated)
│   ├── captures/ (folder with the captured data)
│   ├── samples/ (folder with the sampled data)
│   ├── features/ (folder with the extracted features)
│   └── requirements.txt
│
└── README.md
```

### Bot Creation

References:

- Portal to build the bot: <https://discord.com/developers/applications>
- Tutorial in python: <https://www.youtube.com/watch?v=UYJDKSah-Ww>

### Setting up the environment

1. Add virtual environment:

```bash
python -m venv venv
```

2. Enable the virtual environment:

```bash
venv\Scripts\activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Add the `DISCORD_TOKEN` in the `.env` file:

```bash
echo "DISCORD_TOKEN=<your_token>" >> .env
```

> The `.env` file should be in the `src` folder

### Running the bot

To run the simpler version of the bot, that uses no prior behavior to exfiltrate data, run the following command:

```bash
python simple_exfiltration_bot.py
```

To run the bot that uses the prior behavior to exfiltrate data, run the following command:

```bash
python complex_exfiltration_bot.py --input <input_file> 
```

Where the `<input_file>` is a CSV file with the packet capture data.

### Sampling the data

This is the command to sample the data (with a sampling interval of 1 second), given the `discord_capture.pcap` file:

```bash
python data_sampling.py --format 3 --input discord_capture.pcap --output <output_file> --delta 1 --cnet <client_network_pool> --snet 0.0.0.0/0
```

### Extracting the features

This is the command to extract the features using the multi-slide observation window (observation window of **5 minutes width** and window **slide of 30 seconds**), given the `output_file.txt` file:

```bash
python data_processing.py --input output_file.txt --method 3 --width 300 --slide 30
```

> [!NOTE]
> Since the sampling interval is 1 second, the width and slide of the observation window are given in seconds

### Detection using Machine Learning (Unsupervised Learning)

#### Model Selection (TBD)

- [ ] Isolation Forest
- [ ] One-Class SVM
- [ ] Autoencoder

#### Data Preprocessing (TBD)

- [ ] Normalization using MinMaxScaler
- [ ] Train with normal behavior and test with 50/50 normal and malicious behavior

#### Model Evaluation (TBD)

- [ ] PCA
- [ ] Linear discriminant analysis
- [ ] Non-negative Matrix Factorization
- [ ] Generalized discriminant analysis
