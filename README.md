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

### Discovery

Do discord show in the traffic infornation about:

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

- [ ] Analyze what type of data discord makes
- [ ] Evaluate what data can be collected

### How to produce data (TODO: Update)

- [ ] Check out discord API
- [ ] Check out ways to make automated data collection (e.g. AutoHotKeys, Discord Webhooks)
- [ ] Make tree types of bots
  - [ ] Periodically easy to detect
  - [ ] Randomly in a period of time, intermediate to detect
  - [ ] Exfiltration through embedded images, hard (almost impossible) to detect
