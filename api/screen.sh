#!/bin/bash

if [ -z $1 ] 
then
	echo "try with ./screen.sh on/off"
else
   	if [ $1 = "on" ]; then
		gpio -g mode 22 out
		gpio -g write 22 1
		echo "screen on"
	else 
		gpio -g mode 22 out
		gpio -g write 22 0
		echo "screen off"
	fi
fi

