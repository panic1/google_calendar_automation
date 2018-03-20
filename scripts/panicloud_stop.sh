#! /bin/bash

# ip address or hostname
IPADDRESS="${1:-panicloud}"
STATE_FILE="${2:-/var/run/panicloud/state}"

# this does require the user to be able to run the poweroff command as sudo without password
ssh ${IPADDRESS} sudo poweroff

echo "2" > ${STATE_FILE}
