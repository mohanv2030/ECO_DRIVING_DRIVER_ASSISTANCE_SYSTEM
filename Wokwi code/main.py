from hcsr04 import HCSR04
from time import sleep
from machine import sleep
import mpu6050
import machine
import urequests 
from machine import Pin, SoftI2C
import network, time



#Button part
led = Pin(12, Pin.OUT)    # 22 number in is Output
brake_push_button = Pin(13, Pin.IN)  # brake - 13 number pin is input
accelerator_push_button = Pin(15, Pin.IN)  # accelerator - 15 number pin is input
count =0 #brake count
idle_count = 0 #idle engine time
#Button part

#UltraSonic Sensor Part
sensor = HCSR04(trigger_pin=5, echo_pin=18, echo_timeout_us=10000)
i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=10000)
#UltraSonic Sensor Part

#Accelerometer Part
mpu= mpu6050.accel(i2c)
initveloc=0
#Accelerometer Part

#LCD initialization Part
import machine
from machine import Pin, SoftI2C
from lcd_api import LcdApi
from i2c_lcd import I2cLcd
from time import sleep

I2C_ADDR = 0x27
totalRows = 2
totalColumns = 16
#initializing the I2C method
i2c = SoftI2C(scl=Pin(22), sda=Pin(19), freq=1000000000)     
lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)

lcd.putstr("ECO-DRIVING\nSYSTEM")
#LCD initialization Part



# Thingspeak Part
print("Connecting to WiFi", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
  print(".", end="")
  time.sleep(0.1)
print(" Connected!")

HTTP_HEADERS = {'Content-Type': 'application/json'} 
THINGSPEAK_WRITE_API_KEY = "Z15Y9OC4BYO4L7TO" 
# Thingspeak Part"

UPDATE_TIME_INTERVAL = 10000  # in ms 
ENGINE_IDLE_TIME_INTERVAL = 30000  # in ms 
last_update = time.ticks_ms() 

while True:
    lcd.clear()
    distance = sensor.distance_cm()
    mpuval=mpu.get_values()
    acc=mpuval["AcX"]/16384
    if(distance>100):
      led.value(1)
      lcd.putstr("Obstacle at {}m\nReduce speed".format(int(distance/100)))
      sleep(1)
      lcd.clear()
    if(acc>0.15):
      led.value(1)
      lcd.putstr("Dont Accelerate too much")
      sleep(1)
      lcd.clear()
    if brake_push_button.value() == True:     # if brake pressed 
      count +=1
    if accelerator_push_button.value() == True:     # if brake pressed 
      idle_count +=1
    if time.ticks_ms() - last_update >= UPDATE_TIME_INTERVAL:
        if count>= 5:
          count=0
          led.value(1) 
          lcd.putstr("Too much brakes Reduce speed")
          sleep(2)
          lcd.clear()    
        print('Distance:', int(distance/100), 'm')
        print('Acceleration:',acc)
        if(distance>100):
          print("Obstacle is at ",int(distance/100),"m")
        if(acc>0.15):
          print("Acceleration has exceeded 1.4705 m/s^2")
        bme_readings = {'field1':distance, 'field2':acc, 'field3':distance} 
        request = urequests.post( 'http://api.thingspeak.com/update?api_key=' + THINGSPEAK_WRITE_API_KEY, json = bme_readings, headers = HTTP_HEADERS )  
        request.close() 
    if time.ticks_ms() - last_update >= ENGINE_IDLE_TIME_INTERVAL:
      if idle_count== 0 :
          lcd.putstr("Switched off \nengine")
          sleep(2)
          lcd.clear() 
    led.value(0)


