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
RedLED = LED("GPIO9", active_high=False, initial_value=False)
YellowLED = LED("GPIO10", active_high=False, initial_value=False)
GreenLED = LED("GPIO24", active_high=False, initial_value=False)

LED1 = LED("GPIO21", active_high=False, initial_value=False)
LED2 = LED("GPIO26", active_high=False, initial_value=False)

Switch1 = DigitalInputDevice("GPIO13", pull_up=None, active_state=True)
Switch2 = DigitalInputDevice("GPIO19", pull_up=None, active_state=True)
Switch3 = DigitalInputDevice("GPIO16", pull_up=None, active_state=True)
Switch4 = DigitalInputDevice("GPIO20", pull_up=None, active_state=True)

#Button1 = Button("GPIO11", pull_up=True, active_state=None) #start button
Button1 = Button("GPIO11", pull_up=None, active_state=False) #start button
Button2 = Button("GPIO8", pull_up=None, active_state=False) #reset button
Button3 = Button("GPIO7", pull_up=None, active_state=False)

Alert = DigitalInputDevice("GPIO22")
HighEn = DigitalOutputDevice("GPIO5", active_high=False, initial_value=True) #active low high current range relay
MidEn = DigitalOutputDevice("GPIO6", active_high=False, initial_value=True)
LowEn = DigitalOutputDevice("GPIO12", active_high=False, initial_value=True)

def SwitchState() :
    Switches = Switch1.value + Switch2.value * 2 + Switch3.value * 4 + Switch4.value * 8
    print("Test Configuration = ",Switches)
    #set test parameters based on switches
    if(Switches == 0):
        highDuration = 10 #sec
        currentMax = 200000 #uA
        currentSleep = 200 #uA
        currentAwake = 50000 #uA
    else:
        highDuration = 20 #sec
        currentMax = 400000 #uA
        currentSleep = 100 #uA
        currentAwake = 60000 #uA  

    return highDuration,currentMax,currentSleep,currentAwake

def TestResult(Result, FailCode)  :
    if Result:
        GreenLED.on()
        YellowLED.off()
        print("***** Pass *****\n")
    else:
        RedLED.on()
        YellowLED.off()         
        print(FailCode)
        print("***** Fail *****\n")
    return Result

def LEDsOff() :
    RedLED.off()
    YellowLED.off()
    GreenLED.off()
    return 1

def RelayState(Low,Mid,High) : #Boolens
    if(Low) :
        LowEn.on()
        result = 1
    else :
        LowEn.off()
        result = 0

    if(Mid) :
        MidEn.on()
        result = result + 2
    else :
        MidEn.off()

    if(High) :
        HighEn.on()
        result = result + 4
    else :
        HighEn.off()

    return result; 

#initialization

#Configure SMBus
#make sure that I2C is enabled in RPi config
I2C1 = smbus.SMBus(DEVICE_BUS) #bus 1 is pin 3 and 5 of the header
RelayState(False,False,False)
LEDsOff()
#set for continuous sampling on ADC.  Rest is defaults
I2C1.write_i2c_block_data(DEVICE_ADDR,0x01,[0x84,0x83])

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

#I2C1.write_i2c_block_data(DEVICE_ADDR,command,data)
#I2C1.write_byte_data(DEVICE_ADDR, command, value)
#data = I2C1.read_byte_data(DEVICE_ADDR, command)
 
#execution loop

while True:   
    print("Set Switches for Test Configuration, then press the Start Button to Begin")
    Button1.wait_for_press()
    #configuration switches
    LEDsOff()
    print("Starting Test")

    #Blinking Yellow LED means test in process
    YellowLED.blink(on_time=0.25,off_time=0.25)
   
    Pass = True
    
    highDuration,currentMax,currentSleep,currentAwake = SwitchState()

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
        CurrentSample = I2C1.read_i2c_block_data(DEVICE_ADDR,0x00,2)
        print("data ",CurrentSample)
        Current = CurrentSample[0] * 256 + CurrentSample[1]

        if Current > currentMax: #Overcurrent condition, stop immediately
            OverCurrent = True
            HighEn.off()
            TestResult(False, "OverCurrent\n")
            Pass = False
        else:
            CurrentSum = CurrentSum + Current
            Count = Count + 1
            HighTime = time()
    print("High Current Stage Conplete\n")

    #check if the voltage has dropped (device is asleep)
    CurrentSample = 1 #need to put I2C conversion read here

    TestResult(False, "Over Current")

