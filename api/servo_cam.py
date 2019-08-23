import RPi.GPIO as GPIO    #Importamos la libreria RPi.GPIO
import time                #Importamos time para poder usar time.sleep

GPIO.setmode(GPIO.BCM)   #on prend par pin

# servo horizontale
GPIO.setup(12,GPIO.OUT)    #pin 21 out
p = GPIO.PWM(12,50)        #pin 21 en mode 50 pulsation par sec
p.start(7.6)               #on place la cam a la bonne position

# servo verticale
GPIO.setup(5,GPIO.OUT)    #pin 19 out
w = GPIO.PWM(5,50)        #pin 19 en mode 50 pulsation par sec
w.start(2.3)               #on place la cam a la bonne position

time.sleep(0.5)
p.ChangeDutyCycle(0) 
w.ChangeDutyCycle(0) 

vert=2.3
hor=7.6
x=1
y=1

try:                 
	
	while x!=2:
		input = raw_input("Selection: ") 
		
		# servo verticale
		if input == 'a':
			vert += 0.2
			y=1     
		if input == 'z':
			vert -= 0.2
			y=1 
		if input == 'q':
			vert += 1
			y=1 
		if input == 's':
			vert -= 1
			y=1 
			
		if vert<2.3:
			vert=2.3
		if vert>6:
			vert=6	
			
		if y:
			w.ChangeDutyCycle(vert)  
			time.sleep(0.1) 
			w.ChangeDutyCycle(0)  
			y=0
			print vert
			input = 'b'
		
			
			
		# servo horizontale	
		if input == 'e':
			hor += 0.2
			x=1     
		if input == 'r':
			hor -= 0.2
			x=1 
		if input == 'd':
			hor += 1
			x=1 
		if input == 'f':
			hor -= 1
			x=1 
			
		if hor<2.5:
			hor=2.5
		if hor>13.5:
			hor=13.5	
			
		if x:
			p.ChangeDutyCycle(hor)
			time.sleep(0.1) 
			p.ChangeDutyCycle(0)     
			x=0
			print hor
			input = 'b'
		
	
			
		if input == 'm':
			 w.ChangeDutyCycle(2.3)
			 p.ChangeDutyCycle(7.6)
			 time.sleep(0.5)
			 w.ChangeDutyCycle(0)
			 p.ChangeDutyCycle(0)
			
		if input == 'p':
			 p.stop()
			 w.stop()
			 GPIO.cleanup() 
			 x=2
			         
			         
except KeyboardInterrupt:         #si on presse ctrl^c
    p.stop()                      #on stop
    GPIO.cleanup()                #on clean
    
    
			# 2.4 max left
			# 13.6 max right
			# 7.6 midle
			

