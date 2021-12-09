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

LOWAMP = 100000
MIDAMP = 10000
HIGHAMP = 33

FSR = 4.096 #set in I2C ADC config command
        
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

Button1 = Button("GPIO11", pull_up=None, active_state=False) #start button
Button2 = Button("GPIO8", pull_up=None, active_state=False) #reset button
Button3 = Button("GPIO7", pull_up=None, active_state=False)

Alert = DigitalInputDevice("GPIO22")
HighEn = DigitalOutputDevice("GPIO5", active_high=False, initial_value=True) #active low high current range relay
MidEn = DigitalOutputDevice("GPIO6", active_high=False, initial_value=True)
LowEn = DigitalOutputDevice("GPIO12", active_high=False, initial_value=True)

#Configure SMBus
#make sure that I2C is enabled in RPi config
I2C1 = smbus.SMBus(DEVICE_BUS) #bus 1 is pin 3 and 5 of the header

def SwitchState():
    Switches = Switch1.value + Switch2.value * 2 + Switch3.value * 4 + Switch4.value * 8
    print("Test Configuration = ",Switches)
    #set test parameters based on switches
    if(Switches == 0):
        highDuration = 10 #sec
        currentMax = 60000 #uA
        currentSleep = 200 #uA
        currentAwake = 40000 #uA
    else:
        highDuration = 20 #sec
        currentMax = 80000 #uA
        currentSleep = 100 #uA
        currentAwake = 60000 #uA  

    return highDuration,currentMax,currentSleep,currentAwake

# function to turn off the three result LEDs
def LEDsOff() :
    RedLED.off()
    YellowLED.off()
    GreenLED.off()
    return 1

#set the current sense resistor relays
def RelayState(Low, Mid, High): #Boolens
    if High and Mid:
        LowEn.off()
        MidEn.on()
        HighEn.on()
        Low = 0
        Mid = 1
        High = 1

    elif Low and Mid:
        LowEn.on()
        MidEn.on()
        HighEn.off()
        Low = 1
        Mid = 1
        High = 0
    
    elif Low:
        LowEn.on()
        MidEn.off()
        HighEn.off()
        Low = 1
        Mid = 0
        High = 0

    elif Mid:
        LowEn.off()
        MidEn.on()
        HighEn.off()
        Low = 0
        Mid = 1
        High = 0

    else: #default to high on
        LowEn.off()
        MidEn.off()
        HighEn.on()
        Low = 0
        Mid = 0
        High = 1

    return Low, Mid, High

def TestResult(Result, FailCode):
    if Result:
        GreenLED.on()
        YellowLED.off()
        print("***** Pass *****")
    else:
        RedLED.on()
        YellowLED.off()         
        print(FailCode)
        print("***** Fail *****")

    RelayState(False, False, True)
        
    return Result


#read ADC and calculate current in mA
def CurrentRead(Low,Mid,High) :
    ADCSample = I2C1.read_i2c_block_data(DEVICE_ADDR,0x00,2)
    print("data ",ADCSample)
    ADCValue = ADCSample[0] * 256 + ADCSample[1] #16 bit ADC sample
    
    ADCVoltage = ADCValue/65536 * FSR #convert to voltage
    
    if Low:
        CurrentmA = (ADCVoltage * 1000000) / LOWAMP #in uA  see table on page 2 of the Current Sense schematic for shunt current to ADC voltage conversion

    elif Mid:
        CurrentmA = (ADCVoltage * 1000000) / MIDAMP #in uA

    else :
        CurrentmA = (ADCVoltage * 1000000) / HIGHAMP #in uA

    return CurrentmA


#initialization

RelayState(False, False, True)
LEDsOff()
#set for continuous sampling on ADC, FSR = +/-4.096V  Rest is defaults
I2C1.write_i2c_block_data(DEVICE_ADDR,0x01,[0x82,0x83])

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

###########################################################
# SMBus command formats
#I2C1.write_i2c_block_data(DEVICE_ADDR,command,data)
#I2C1.write_byte_data(DEVICE_ADDR, command, value)
#data = I2C1.read_byte_data(DEVICE_ADDR, command)
###########################################################


###########################################################################################################################################
# execution loop
# 1.  Wait for start button, the config switches that determine the test parameters are checked, and the DUT should be connected first
# 2.  Cycle Check awake current.  Should be below max current and drop before the specified time.  Check for sleep mode or timeout
# 3.  Check average awake current.  If max current and average awake current are ok, go to mid current sense resistor (make before break)
# 4.  Check mid range sense resistor, if ~0, switch to low (make before break so the DUT isn't power cycled.)
# 5.  Cycle Check sleep current for specified duration.  Average and max must both be below specified value.
###########################################################################################################################################

while True:   
    print("Set Switches for Test Configuration, connect DUT, then press the Start Button to Begin")
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
    Highstart = time()
    HighTime = time()
    Sleep = False
    RelayState(False, False, True)

    while (Pass) and ((HighTime - Highstart) < highDuration) and (not Sleep):
        Current = CurrentRead(False, False, True)

        if Current > currentMax: #Overcurrent condition, stop immediately
            FailText = "OverCurrent"
            Pass = False

        elif Current < 1000: #1mA
            Sleep = True

        else:
            CurrentSum = CurrentSum + Current
            Count = Count + 1
            HighTime = time()


    if not Pass:
        TestResult(False, FailText)
    
    else:
        AverageCurrent = CurrentSum/Count
        print("Average Active Current = ", AverageCurrent)

        if(AverageCurrent > currentAwake):
            FailText = "Average Awake Current Over Max"
            Pass = False

    if Pass:
        print("High Current Stage Conplete\n")
        #check if we are sleeping
        Current = CurrentRead(False, False, True)
        if Current < 1000: #1mA
            Highstart = time()
            HighTime = time()
            RelayState(False,True,True) #make before break
            RelayState(False,True,False) #switch to 330uA range
            
            while (Pass) and ((HighTime - Highstart) < highDuration) and (not Sleep):
                Current = CurrentRead(False, False, True)
                CurrentSum = CurrentSum + Current
                Count = Count + 1
                HighTime = time()          

            AverageCurrent = CurrentSum/Count
            print("Average Active Current = ", AverageCurrent)
            if(AverageCurrent > currentSleep):
                FailText = "Average Sleep Current Over Max"
                Pass = False

        else:
            FailText = "DUT is not in low power sleep state"
            Pass = False

    TestResult(Pass, FailText)



