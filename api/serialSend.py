#!/usr/bin/env python3
import time
import serial
import argparse

parser = argparse.ArgumentParser(description='Sends serial')
parser.add_argument("-c", "--code", default=None,help="code to send")
args = parser.parse_args()
 
ser = serial.Serial(
 port='/dev/ttyAMA0',
 baudrate = 9600,
 parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
 timeout=1
)
 

ser.write(args.code.encode())
print("send serial : "+args.code)

#for i in range(0,20):
#while 1:
#    reading = ser.read()
#    if(reading):
#        print (reading)
#time.sleep(2)
ser.close()