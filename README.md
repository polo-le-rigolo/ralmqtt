# ralmqtt
RALMQTT is a python based tool designed for MQTT pentesting
Made by eddym@lou // https://www.redalertlabs.com
Your IoT Cybersecurity Trusted Partner

## Table of Contents

- [About](#about)
- [Installation](#installation)
- [Usage](#usage)


## About
**RALMQTT** is designed for pentesters and aims to make MQTT Broker pentesting easier. Several modes are available:

- **Discovery**: Gathers information about the broker (authentication, version, clients, uptime, etc.).
- **Bruteforce**: Allows user-password bruteforce (default wordlist is based on mirai).
- **DoS**: Implements the method described in [this paper](https://www.mdpi.com/1424-8220/20/10/2932) by Ivan Vaccari, Maurizio Aiello, and Enrico Cambiaso.

### Attack Scenario
An attack scenario using these 3 modes could be like the following:

1. **Discovery**: Gather info on the broker, requiring user password authentication.
2. **Bruteforce**: Try to bruteforce login credentials. If successful, launch Discovery mode again with the credentials.
3. **DoS**: If bruteforce fails, sniff valid connect packets. One way is through a mitm attack (like ARP poisoning) between a client and the broker. Launch a DoS attack on the broker until keepalive messages fail forcing to stop every client-broker TCP connections. Once the attack is stopped, the client establishes a new connection and voilà ! Since a mitm is in place, we freely sniff valid credentials and clientId. 

## Installation

Installing ralmqtt is pretty straight forward : 

```bash
# Clone the repository
git clone https://github.com/polo-le-rigolo/ralmqtt

# Create a venv to use the tool
python3 -m venv VENVMQTT
source VENVMQTT/bin/activate
pip install -r requirements.txt
```
Once you are done using the tool just deactivate the venv with the command **deactivate**

## Usage

Made by eddym@lou // [https://www.redalertlabs.com](https://www.redalertlabs.com)
Your IoT Cybersecurity Trusted Partner
Bringing Trust to the Internet of Things
RALMQTT is a python based tool designed for MQTT pentesting

Usage: `python3 ralmqtt.py -m <attack mode> -a <addr> [-P <port>] [-p <password>] [-u <user>]`

Options:
- `-m, --mode`       Mode (choose from : discovery/dos/bruteforce)
- `-a, --addr`       Broker's address
- `-P, --port`       Broker's port (default value being 1883)
- `-p, --password`   Broker's password (optional)
- `-u, --user`       Broker's username (optional)
- `-w, --wordlist`   Password wordlist for bruteforce mode (default ./passwords.txt)

**Examples :**

- `python3 ralmqtt.py -a test.mosquitto.org -m discovery` 

This command runs ralmqtt in **discovery mode** to find information about the MQTT broker at `test.mosquitto.org`.

- `python3 ralmqtt.py -m bruteforce -a 192.168.246.147 -w /usr/share/wordlists/rockyou.txt`

This command runs ralmqtt in **bruteforce mode** against the MQTT broker at `192.168.246.147`, using the specified wordlist `/usr/share/wordlists/rockyou.txt`.

- `python3 ralmqtt.py -m discovery -a 192.168.246.147 -u root -p 12345`

This command runs ralmqtt in **discovery mode** against the MQTT broker at `192.168.246.147`, providing the username/password (`root`/ `12345`).

- `python3 ralmqtt.py -m dos -a 192.168.246.147`

This command runs ralmqtt in **DoS mode** to perform a Slow Denial of Service attack against the MQTT broker at `192.168.246.147`.

You will also find a `testdos.sh` script in this repository. As its name suggests, the goal of this script is to test the DoS mode of the tool. 
Download the script, change execution permission and execute it. It will publish to the topic test/dos a message saying that the broker is still up. 
On a different terminal launch the following commmand : `mosquitto_sub -h broker_addr -t 'test/dos'`

Soon to be added : 
Connect packet sniffing mode, clientId bruteforce support
