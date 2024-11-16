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

One of the biggest challenges in detecting data exfiltration via Discord is the fact that all communication is encrypted. When data is sent to a webhook, Discord uses HTTPS (HTTP over TLS), which means that the data is encrypted during transmission. This encryption makes it impossible for most network security devices, such as firewalls and Deep Packet Inspection (DPI) systems, which analyse individual packets to identify suspicious content, to directly inspect the content of the traffic. So, although it is possible to see that there is communication with Discord, it is not possible to analyse or filter the content of the data sent due to encryption, which makes this channel an ideal vehicle for exfiltrating data undetected.

Firewalls and SIEM systems based on fixed rules face a critical limitation here. Without access to the encrypted content of the packets, these systems can only monitor basic metadata, such as the destination IP address, the port, and the volume of data. However, as Discord is widely used and permitted on many corporate networks, this traffic appears legitimate and doesn't immediately raise suspicions.

Data exfiltration via Discord webhooks is a very popular technique because of the way it takes advantage of the platform's infrastructure to mask malicious activity. These features, designed to facilitate automated integrations and notifications, end up being exploited in cyber attacks, allowing sensitive information to be sent outside the network undetected.

> [!NOTE]
> Although Discord made some updates regarding security ([link](https://discord.com/blog/discord-update-september-26-2024-changelog)), malicious users still take advantage of tools that allow development of plugins.

### Real life examples

Some examples of data exfiltration using Discord:

- [The Hacker News - NS Stealer Uses Discord Bots to Exfiltrate Data](https://thehackernews.com/2024/01/ns-stealer-uses-discord-bots-to.html)
- [Intel471 - How Discord is Abused for Cybercrime](https://intel471.com/blog/how-discord-is-abused-for-cybercrime)

### Discovery

- It has a built-in function that enables automated messages sent to a text channel in the server (Webhooks)
- Allows the upload of a variety file types (e.g. PNG, PDF, MP4)
- The maximum file upload is 10MB

### Filtering

- Network Pool: `162.159.0.0/16`

> Reference: [NsLookup.io](https://www.nslookup.io/domains/discordapp.com/webservers/)

- Protocols Used for communication: `TCP`
  - Destination Port(s): TCP/80 and TCP/443
  - Source Port(s): UDP/50000-65535
- Protocols Used for voice communication: `QUIC`

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

- Group and Private Conversations – the conversation type is obtained at the packet level (uploads/downloads)
- Daily and Weekly message flow with various formats of files – analyzing the timestamps of interactions (uploads/downloads)

> We need, at least, 1M Flows

### Collection

In a testing context we are going to use:

- Wireshark: For network analysis
- Burp Suite: Proxy tools for traffic capturing

But in a real life context, we could use:

- Syslog and Agents: To obtain data from endpoints and discord activity
- Suricata or Palo Alto Networks Firewalls: To monitor ports and protocols in use, e.g. TCP and QUIC, and detect unusual or unauthorized traffic.

### Sampling and Processing

We are going to focus on flow data, where it has the following fields:

- IP Source
- IP Destination
- Size of Exchanged Data
- Data Flow Start/End Timestamp (in seconds)
- IP Protocol Number

In order to convert our qualitative data into quantitive data, we chosed to use observation windows of 0.1 seconds and 1 second

> This allows a balance between the level of detail needed to capture relevant events and the volume of data generated

- Mean and Standard Deviation of idle times: Unusual gaps or consistency between flows.
- Number of flows: Indicating irregular usage patterns.
- Size of exchanged data (Mean/Variance): Changes in data size can point to unexpected or secretive data transfers.
  - Up/Down
- Durations of Flows

### Production

Benign Behavior: It will be done by performing normal usage of the application, made by:

- Humans: sending messages and files as usual
- Bots: made by plugins added to the server

Malicious Behavior: It will be done using tree types of bots:

- Easy to Detect:
  - Size: 10MB
  - Frequency: Periodically (40s)
- Intermediate to Detect:
  - Size: 1-10MB
  - Frequency: Same variance as a normal behavior
- Hard (almost impossible) to Detect: Through embedded images, using Discord CDN

### Tasks to be done

POR COLOCAR AQUI

## Phase 2: Project Development

### Project Structure

### Bot Creation

- Portal to build the bot: <https://discord.com/developers/applications>
- Tutorial in python: <https://www.youtube.com/watch?v=UYJDKSah-Ww>

### How to Run Scripts in the "Source" Folder

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
