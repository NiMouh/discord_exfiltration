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
  
#### Por que a exfiltração de dados via Discord é díficil de detetar com regras simples

Um dos maiores desafios na deteção de exfiltração de dados através de Discord é o facto de toda a comunicação ser cifrada. Quando dados são enviados para um webhook, o Discord utiliza HTTPS (HTTP sobre TLS), o que significa que os dados são cifrados durante a transmissão. Esta cifragem impossibilita a inspeção direta do conteúdo do tráfego pela maioria dos dispositivos de segurança de rede, como firewalls e sistemas de inspeção profunda de pacotes (DPI – Deep Packet Inspection), que analisam pacotes individuais para identificar conteúdos suspeitos. Assim, embora seja possível ver que há comunicação com o Discord, não é possível analisar ou filtrar o conteúdo dos dados enviados devido à cifragem, o que transforma este canal num veículo ideal para exfiltração de dados sem ser detetado.

As firewalls e sistemas SIEM baseados em regras fixas enfrentam aqui uma limitação crítica. Sem acesso ao conteúdo cifrado dos pacotes, estes sistemas apenas conseguem monitorizar metadados básicos, como o endereço IP de destino, o porto, e o volume de dados. Contudo, como o Discord é amplamente utilizado e permitido em muitas redes empresariais, este tráfego parece legítimo e não levanta suspeitas de imediato.

A exfiltração de dados por meio de webhooks do discord é um técnica bastante popular, devido à forma como aproveita a infraestrutura da plataforma para mascarar atividades maliciosas. Estas funcionalidades, projetadas para facilitar integrações automatizadas e notificações acabam por ser exploradas em ataques cibernéticos, possibilitando que informações sensíveis sejam enviadas para fora da rede sem serem detetadas.

### Real life examples

Some examples of data exfiltration using Discord:

- [The Hacker News - NS Stealer Uses Discord Bots to Exfiltrate Data](https://thehackernews.com/2024/01/ns-stealer-uses-discord-bots-to.html)
- [Trellix - Discord I Want to Play a Game](https://www.trellix.com/blogs/research/discord-i-want-to-play-a-game/)
- [Intel471 - How Discord is Abused for Cybercrime](https://intel471.com/blog/how-discord-is-abused-for-cybercrime)
- [Cyfirma - Cyber Research on The Malicious Use of Discord](https://www.cyfirma.com/research/cyber-research-on-the-malicious-use-of-discord/)

### Discovery

Discord Network Pool: `162.159.0.0/16`

> Reference: [NsLookup.io](https://www.nslookup.io/domains/discordapp.com/webservers/)

Do discord show in the traffic information about:

- [ ] Sender's user data
- [ ] Receiver's user data
- [ ] Server where the message is sent through
- [ ] Type of data sended
- [ ] Notifications received

### What data to collect

- Types of data that can be collected:
  - Flow data
  - Packet captures
  - Discord logs
- > 1 milhão de fluxos

| **Data to Extract**                              | **Description**                                                                                 | **Purpose**                                                                                                      |
|--------------------------------------------------|-------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| **Call Duration**                                | Monitor start and end logs to calculate the total duration of each call.                        | Determine total time of activity in calls; identify short calls vs. prolonged sessions.                         |
| **Repeated Sessions and Intervals**              | Record number of interactions (calls or chats) per day and intervals between them.              | Identify activity patterns, periods of inactivity, and frequency of interactions.                               |
| **Type of Media Shared (Video, Audio, GIFs, etc.)** | Track types of media shared in chats (video, images, audio, GIFs, text).                        | Analyze communication preferences; identify high media usage that may signal certain behaviors or intents.      |
| **Participation in Group vs. Private Conversations** | Observe if the user interacts more in group or private settings.                              | Understand interaction style (collaborative vs. personal); detect differences in content shared.                |
| **Daily and Weekly Activity Patterns**           | Analyze days and times when interactions (calls, chats) are most frequent.                     | Build a profile of peak times and periods of intensive activity.                                                |
| **Message Length and Complexity**                | Monitor the average length and complexity of text messages in chats.                           | Assess communication style; detect potential indicators of focused or formal exchanges.                         |
| **Presence in Voice Channels**                   | Record periods of activity in voice channels, including duration and frequency.                | Gain insight into continuous presence and engagement level in voice interactions.                               |
| **Reaction and Engagement with Media**           | Track reactions (e.g., emoji, replies) to shared media (images, videos, audio, GIFs).          | Measure engagement and response sentiment to different media types.                                             |
| **Content Type Distribution**                    | Analyze distribution of content types (text vs. media) in interactions.                        | Identify communication trends; determine if visual content is preferred over textual exchanges.                 |


| **Data to Extract**                        | **Description**                                                                | **Purpose**                                                                                                                                |
| ------------------------------------------ | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **IP Addresses and Domains**               | Identification of IPs and domains used by Discord.                             | Enables distinction between legitimate activities and potentially suspicious ones; useful for creating a baseline of normal communication. |
| **Communication Ports**                    | Typically, Discord uses port 443 (HTTPS).                                      | Identify if there is use of unusual ports for communication; helps detect attempts to evade detection.                                     |
| **Packet Frequency and Volume**            | Quantity and frequency of packets sent/received over time.                     | Atypical behaviors in volume and frequency may indicate exfiltration. Used to train the model to detect activity peaks.                    |
| **Temporal Sending Patterns**              | Identify if there is regularity or specific intervals in packet transmissions. | Detect scheduled or automated exfiltration; useful for analyzing behavioral patterns of the machine and user.                              |
| **Packet Size**                            | Average packet size and standard deviation of packets sent.                    | Anomalies in packet size may indicate larger-than-normal data transfers; essential for identifying exfiltration.                           |
| **TLS Session Establishment and Duration** | Frequency and duration of TLS sessions established with Discord.               | Long-duration sessions may indicate continuous data uploads. Useful for temporal analysis in the ML model.                                 |
| **Response Time and Latency**              | Time between requests and responses in packets exchanged with Discord.         | Atypical behaviors may indicate the use of webhooks to quickly send data; useful for latency analysis.                                     |
| **WebSocket Session LifeSpan**             | Observation of socket handshake flows.                                         | Atypical patterns of socket sessions may indicate continuous or repeated exfiltration processes.                                           |
| **TLS Certificate Analysis**               | Information about certificates received in the TLS handshake.                  | Validates the authenticity of the connection and checks for possible proxies or MITM.                                                      |

### Data Aquisition on Real Life Context

| **Data Type**                           | **Recommended Enterprise Tools**                                | **Description**                                                                                                         |
|-----------------------------------------|-----------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| **Network Sessions and Connection Duration** | **Zeek**, **Cisco Secure Network Analytics** (Stealthwatch), **Darktrace** | Monitors and analyzes the duration and frequency of network sessions, identifying anomalous patterns and suspicious behaviors. |
| **Ports and Protocols Used**            | **Suricata**, **Cisco ASA Firewalls**, **Palo Alto Networks Firewalls** | Monitors ports and protocols in use, including WebSockets, to detect unusual or unauthorized traffic.                    |
| **Connection Attempts and Disconnections** | **Splunk**, **Elastic Stack (ELK)**, **QRadar** (SIEM)         | Logs established and closed connections, helping to identify the timing and frequency of activity on Discord.           |
| **User Activity (Session Level)**       | **SIEMs** (e.g., **Splunk**, **QRadar**, **ArcSight**), **Darktrace** | Monitors session activity to provide an overview of user behavior over time.                                             |
| **Identification of Shared Media Types** | **Next-Generation Firewalls** with **DPI** (e.g., **Palo Alto Networks**, **Fortinet**) | Uses deep packet inspection to identify media types (e.g., video, audio) shared, even in encrypted traffic.             |
| **Daily and Weekly Activity Patterns**   | **Splunk**, **Elastic Stack**, **Grafana**                      | Analyzes temporal activity patterns to identify peak times and consistent behaviors.                                     |
| **Presence in Voice Channels**           | **Next-Generation Firewalls** with continuous WebSocket monitoring support | Monitors activity in voice channels via WebSocket session analysis, providing insights on user presence and engagement.  |


### How to collect data (TODO: Update)

- [ ] Tools to collect data
  - [ ] Wireshark
  - [ ] Discord logs
- [ ] Analyze what type of data discord makes
- [ ] Evaluate what data can be collected
- [ ] Data processing (TODO: Elaborate)

### How to produce data (TODO: Update)

- [ ] Check out discord API
- [ ] Check out ways to make automated data collection (e.g. AutoHotKeys, Discord Webhooks)
- [ ] Make tree types of bots
  - [ ] Periodically easy to detect
  - [ ] Randomly in a period of time, intermediate to detect
  - [ ] Exfiltration through embedded images, hard (almost impossible) to detect
