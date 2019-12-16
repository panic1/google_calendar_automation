#! /bin/bash

STATE_FILE="${1:-/usr/share/panicloud/state}"
GPIO_NUM=4

# the relay to power on the server is controller bu gpio 4
echo ${GPIO_NUM} > /sys/class/gpio/export
sleep 0.5

# trigger the relay (note that the relay is active LOW, and the gpio will always be LOW when you set the direction to "out"
echo out > /sys/class/gpio/gpio4/direction
echo 0 > /sys/class/gpio/gpio${GPIO_NUM}/value
sleep 0.5

# release the relay
echo 1 > /sys/class/gpio/gpio${GPIO_NUM}/value

# cleanup
echo in > /sys/class/gpio/gpio${GPIO_NUM}/direction
echo ${GPIO_NUM} > /sys/class/gpio/unexport

echo "1" > ${STATE_FILE}
