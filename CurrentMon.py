#imports
from gpiozero import Button
from gpiozero import LED
from gpiozero import DigitalInputDevice
from gpiozero import DigitalOutputDevice

import smbus

# Constants
DEVICE_BUS = 1
DEVICE_ADDR = 0x48

#GPIO Mapping
RedLED = LED("GPIO24")
YellowLED = LED("GPIO10")
GreenLED = LED("GPIO21")

Switch1 = Button("GPIO13")
Switch2 = Button("GPIO19")
Switch3 = Button("GPIO16")
Switch4 = Button("GPIO20")

Button1 = Button("GPIO11")
Button2 = Button("GPIO8")
Button3 = Button("GPIO7")

Alert = DigitalInputDevice("GPIO22")
HighEn = DigitalOutputDevice("GPIO5")
MidEn = DigitalOutputDevice("GPIO6")
LowEn = DigitalOutputDevice("GPIO12")

#Configure SMBus
#make sure that I2C is enabled in RPi config
I2C = smbus.SMBus(DEVICE_BUS)

#command = 0x00
#value = 0x01
#bus.write_byte_data(DEVICE_ADDR, command, value)
#data = bus.read_byte_data(DEVICE_ADDR, command)


