#imports
from gpiozero import Button
from gpiozero import LED
from gpiozero import DigitalInputDevice
from gpiozero import DigitalOutputDevice

from time import sleep
from time import time

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

Button1 = Button("GPIO11", pull_up=True, active_state=None) #start button
#Button1 = Button("GPIO11", pull_up=None, active_state=False) #start button
Button2 = Button("GPIO8", pull_up=None, active_state=False) #reset button
Button3 = Button("GPIO7", pull_up=None, active_state=False)

Alert = DigitalInputDevice("GPIO22")
HighEn = DigitalOutputDevice("GPIO5", active_high=False, initial_value=True) #active low high current range relay
MidEn = DigitalOutputDevice("GPIO6", active_high=False, initial_value=True)
LowEn = DigitalOutputDevice("GPIO12", active_high=False, initial_value=True)

#Configure SMBus
#make sure that I2C is enabled in RPi config
I2C1 = smbus.SMBus(DEVICE_BUS) #bus 1 is pin 3 and 5 of the header

def TestResult(Result, FailCode):
    if Result:
        GreenLED.on()
        YellowLED.off()
        print("Pass\n")
    else:
        RedLED.on()
        YellowLED.off()
        print(FailCode)
    return Result
        

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
sleep(0.25)
LED2.on()
sleep(0.25)
RedLED.on()
sleep(0.25)
YellowLED.on()
sleep(0.25)
GreenLED.on()
sleep(0.25)
LED1.off()
sleep(0.25)
LED2.off()
sleep(0.25)
RedLED.off()
sleep(0.25)
YellowLED.off()
sleep(0.25)
GreenLED.off()
LED1.on()Pass omparator

#I2C1.write_i2c_block_data(DEVICE_ADDR,command,data)
#I2C1.write_byte_data(DEVICE_ADDR, command, value)
#data = I2C1.read_byte_data(DEVICE_ADDR, command)
 
#execution loop

while True:   
    Button1.wait_for_press()
    print("Starting Test\n")
    #Yellow LED means test i process
    YellowLED.blink(on_time=0.25,off_time=0.25)

    #configuration switches
    Mode = Switch1.value + (Switch2.value * 2) + (Switch3.value * 4) + (Switch4.value * 8)
    Pass = True
    
    #set test parameters based on switches
    if(Mode == 0):
        highDuration = 10 #sec
        currentMax = 200000 #uA
        currentSleep = 200 #uA
        currentAwake = 50000 #uA
    else:
        highDuration = 10 #sec
        currentMax = 200000 #uA
        currentSleep = 200 #uA
        currentAwake = 50000 #uA  

    #test high current path
    #check for mA range current during the power on init.  Current most drop (sleep) before configured end time
    CurrentSample = 0
    CurrentSum = 0
    Count = 0
    MaxCurrent = 0
    HighEn.on()
    Highstart = time()
    HighTime = time()
    OverCurrent = False

    while (not OverCurrent) and ((HighTime - Highstart) < highDuration):
        CurrentSample = 1 #need to put I2C conversion read here
        if CurrentSample > currentMax: #Overcurrent condition, stop immediately
            OverCurrent = True
            HighEn.off()
            TestResult(False, "OverCurrent\n")
            Pass = False
        else:
            CurrentSum = CurrentSum + CurrentSample
            Count = Count + 1
            HighTime = time()
    print("High Current Stage Conplete\n")


 









