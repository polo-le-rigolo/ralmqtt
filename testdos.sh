#!/bin/bash
echo -n "Enter broker IP : "
read ipaddr
counter=0

while true; do
    mosquitto_pub -h $ipaddr -t "test/dos" -m "Message $counter: broker is still up!"
    counter=$((counter+1))
    sleep 1
done
