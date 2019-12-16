#!/bin/bash

# ipaddress or hostname
IPADDRESS="${1:-panicloud}"
STATE_FILE="${2:-/usr/share/panicloud/state}"

# inactive = 0
# starting = 1
# stopping = 2
# active = 3

if [ ! -f ${STATE_FILE} ]; then
    mkdir $(dirname ${STATE_FILE})
    echo 0 > ${STATE_FILE}
fi

STATE=$(cat ${STATE_FILE})

if [ "$STATE" = "0" -o "$STATE" = "3" ]; then
    echo $STATE
    exit
fi

if [ "$STATE" = "1" ]; then
    # check whether port 22 (ssh) is open on the panicloud machine
    if nmap -p22 ${IPADDRESS} -oG - | grep -q 22/open; then 
        STATE="3"
        echo ${STATE} > ${STATE_FILE}
    fi
fi

if [ "$STATE" = "2" ]; then
    # check whether server responds to ping
    if ! ping -q -c 1 ${IPADDRESS} > /dev/null 2>&1; then
	STATE="0"
	echo ${STATE} > ${STATE_FILE}
    fi
fi

echo ${STATE}
