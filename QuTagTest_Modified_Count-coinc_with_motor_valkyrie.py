# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 10:13:40 2020

@author: Denis
"""

# -*- coding: utf-8 -*-
import numpy as np
import time
import QuTAG
import serial

import os



os.add_dll_directory("C:/Users/bmx/Desktop/Python modules/quTAG-Software_Python-examples-20220711/DLL_64bit")

devID = 1 # quTAG ID is 1
expTime = 20000 # in ms
numExposures = 30 # number of times to loop exposures

numExposures_pause= 5 # How many exposures you want to take after both motor 1 moves and motor 2 moves
file_path = "E:/MZI/monochromatic/mono_MZI_12/" # Path to folder where files will be written
file_name = "monochromatic_MZI" # What name you want the binary files to have, will be followed by a number indicating which exposure it is
motorStepsPerExposure= 12

#initialize qutag
qutag = QuTAG.QuTAG()
devType = qutag.getDeviceType()
    
if (devType == qutag.DEVTYPE_QUTAG):
    print("found quTAG!")
else:
    print("no suitable device found - demo mode activated")
	
print("Device timebase:" + str(qutag.getTimebase()))



#set exposure time
qutag.setExposureTime(expTime)

qutag.setSignalConditioning(1, 3, True, 0.1)
qutag.setSignalConditioning(2, 3, True, 0.1)
qutag.setSignalConditioning(3, 3, True, 0.1)
qutag.setSignalConditioning(4, 3, True, 0.1)



#stop writing Timestamps
qutag.writeTimestamps('',qutag.FILEFORMAT_NONE)

#Setup Serial Link
ser=serial.Serial('COM4',115200,timeout=5)

# Step 1. Move motor 2 forward 10 um at a time 

#With 1 exposure being 1 minute, this allows for 6 motor steps of 10 um each separated by 10 sec
#Currently 2.5 um a step, steps every second for 6 minutes

ser.write(b'setMotor 2\r\n')
for i in range(numExposures):
    qutag.writeTimestamps(file_path+"{}_{}.bin".format(file_name, i),qutag.FILEFORMAT_BINARY)
    
    for j in range(motorStepsPerExposure):  
        time.sleep(expTime/1000/motorStepsPerExposure)
        ser.write(b'steps -32\r\n')
    qutag.writeTimestamps('',qutag.FILEFORMAT_NONE)
    print("Step 1. file num:", i)
    
# Step 1.5  Wait for numExposures_pause exposures between stages    
for i in range (numExposures_pause):
    qutag.writeTimestamps(file_path+"{}_{}.bin".format(file_name, i+numExposures),qutag.FILEFORMAT_BINARY)
    time.sleep(expTime/1000)
    qutag.writeTimestamps('',qutag.FILEFORMAT_NONE)
    print("Pause after step 1. file num:", i+numExposures)


# Step 2. Same as step 1 but now with motor 1    
ser.write(b'setMotor 1\r\n')    
for i in range (numExposures):
    qutag.writeTimestamps(file_path+"{}_{}.bin".format(file_name, i+numExposures+numExposures_pause),qutag.FILEFORMAT_BINARY)
    
    for j in range(motorStepsPerExposure):  
        time.sleep(expTime/1000/motorStepsPerExposure)
        ser.write(b'steps -32\r\n')
    qutag.writeTimestamps('',qutag.FILEFORMAT_NONE)
    print("Step 2. file num:", i+numExposures+numExposures_pause)
    
# Step 2.5  Wait for numExposures_pause exposures after all the stages 
for i in range (numExposures_pause):
    qutag.writeTimestamps(file_path+"{}_{}.bin".format(file_name, i+numExposures*2+numExposures_pause),qutag.FILEFORMAT_BINARY)
    time.sleep(expTime/1000)
    qutag.writeTimestamps('',qutag.FILEFORMAT_NONE)
    print("Pause after step 2. file num:", i+numExposures*2+numExposures_pause)
    
    

#Step 3 Move Motors back

motor_reset = numExposures * motorStepsPerExposure * 32

reset_string = f'steps {motor_reset}\r\n'

ser.write(b'setMotor 1\r\n')
time.sleep(1)
ser.write(reset_string.encode()) #11520 = 30 * 12 * 32 | b'steps 11520\r\n'

time.sleep(2)

ser.write(b'setMotor 2\r\n')
time.sleep(1)
ser.write(reset_string.encode())

ser.close()

print('Deinitializing quTag...')
qutag.deInitialize()
