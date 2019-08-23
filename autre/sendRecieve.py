import serial,time

ser = serial.Serial('/dev/ttyAMA0',9600, 

parity=serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS,
timeout=0.5)
s = [0]
i=0

#ser.write(b"|R4331312081|")



#ser.write(b"|CAPTEUR|")
#time.sleep(2)
#time.sleep(2)
#ser.write('|HC12eau60|'.encode())
#exit()



#ser.write(b"|HC12eau60|")

#ser.write(b"CAPTEUR")
#while !ser.readline():
#	print(ser.readline())


while True:

	read = ser.readline().decode("utf-8")
	if read!="":
		print(read )
		#if ser.readline():
		#	read_serial=ser.readline()
		#	print( read_serial)
		
		#time.sleep(1)
