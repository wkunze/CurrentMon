#imports
from gpiozero import Button
from gpiozero import LED
from gpiozero import DigitalInputDevice
from gpiozero import DigitalOutputDevice

from time import sleep

import smbus

# Constants
DEVICE_BUS = 1
DEVICE_ADDR = 0x48

#GPIO Mapping
RedLED = LED("GPIO24", active_high=False, initial_value=False)
YellowLED = LED("GPIO10", active_high=False, initial_value=False)
GreenLED = LED("GPIO9", active_high=False, initial_value=False)

LED1 = LED("GPIO21", active_high=False, initial_value=False)
LED2 = LED("GPIO26", active_high=False, initial_value=False)

Switch1 = DigitalInputDevice("GPIO13", pull_up=None, active_state=True)
Switch2 = DigitalInputDevice("GPIO19", pull_up=None, active_state=True)
Switch3 = DigitalInputDevice("GPIO16", pull_up=None, active_state=True)
Switch4 = DigitalInputDevice("GPIO20", pull_up=None, active_state=True)

Button1 = Button("GPIO11", pull_up=None, active_state=False)
Button2 = Button("GPIO8", pull_up=None, active_state=False)
Button3 = Button("GPIO7", pull_up=None, active_state=False)

Alert = DigitalInputDevice("GPIO22")
HighEn = DigitalOutputDevice("GPIO5", active_high=False, initial_value=True) #active low high current range relay
MidEn = DigitalOutputDevice("GPIO6", active_high=False, initial_value=True)
LowEn = DigitalOutputDevice("GPIO12", active_high=False, initial_value=True)

#Configure SMBus
#make sure that I2C is enabled in RPi config
I2C1 = smbus.SMBus(DEVICE_BUS) #bus 1 is pin 3 and 5 of the header

#initialization
HighEn.off()
MidEn.off()
LowEn.off()
LED1.off()
LED2.off()
RedLED.off()
YellowLED.off()
GreenLED.off()

#startup sequence
LED1.on()
sleep(0.5)
LED2.on()
sleep(0.5)
RedLED.on()
sleep(0.5)
YellowLED.on()
sleep(0.5)
GreenLED.on()
sleep(0.5)
LED1.off()
sleep(0.5)
LED2.off()
sleep(0.5)
RedLED.off()
sleep(0.5)
YellowLED.off()
sleep(0.5)
GreenLED.off()

#config the ADC
command = 0xba
value = 0xad
I2C1.write_byte_data(DEVICE_ADDR, command, value)
#data = I2C1.read_byte_data(DEVICE_ADDR, command)

 
#execution loop

start = False #button 1, used to start a test cycle

#Check the config switches
Mode = Switch1.value + Switch2.value * 2 + Switch3.value * 4 + Switch4.value * 8

print(type(Mode))
print(Mode)



# while True:
#     Mode = Switch1.value + (Switch2.value * 2) + (Switch3 * 4) + (Switch4 * 8)





# def CurrentCheck(Mode):
#     print("Current Check")




