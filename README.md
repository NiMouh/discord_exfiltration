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
