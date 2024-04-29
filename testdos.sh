#!/bin/bash
echo -n "Enter broker IP : "
read ipaddr
counter=0

while true; do
    mosquitto_pub -h $ipaddr -t "test/dos" -m "Message $counter: broker is still up!"
    counter=$((counter+1))
    sleep 1
done

#in another terminal, launch this command in order to check if the broker is still up : mosquitto_sub -h broker_addr -t 'test/dos' -v
#if you don't have the mosquitto_pub/sub clients installed : sudo apt update; sudo apt install mosquitto-clients
