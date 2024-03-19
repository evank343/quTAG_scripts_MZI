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
expTime = 60000 # in ms (don't go under 1000, it gets unstable)
numExposures = 60 # number of times to loop exposures

numExposures_pause= 5 # How many exposures you want to take after both motor 1 moves and motor 2 moves
file_path = "E:/MZI/dichromatic/di_MZI_4/" # Path to folder where files will be written
file_name = "dichromatic_MZI" # What name you want the binary files to have, will be followed by a number indicating which exposure it is

# One motor revolution is 0.25mm, there are 200 notches per revolution, 16 substeps per notch, meaning one 'steps 32\r\n' command moves the motor
# two notches and relates to a shift of 2.5 microns
motorMovementsPerExposure= 10

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

### COMMENTS HERE ARE OUT OF DATE ###
# Step 1. Move motor 2 forward 10 um at a time
#With 1 exposure being 1 minute, this allows for 6 motor steps of 10 um each separated by 10 sec
#Currently 2.5 um a step, steps every second for 6 minutes
### COMMENTS HERE ARE OUT OF DATE ###

# Step 1.  Wait for numExposures_pause exposures before moving motors
for i in range (numExposures_pause):
    qutag.writeTimestamps(file_path+"{}_{}.bin".format(file_name, i),qutag.FILEFORMAT_BINARY)
    time.sleep(expTime/1000)
    qutag.writeTimestamps('',qutag.FILEFORMAT_NONE)
    print("Pause during step 1. file num:", i)

# Step 2. Start moving motor 1, decreasing path length in paths 2 & 4
ser.write(b'setMotor 1\r\n')    
for i in range (numExposures):
    qutag.writeTimestamps(file_path+"{}_{}.bin".format(file_name, i+numExposures_pause),qutag.FILEFORMAT_BINARY)
    
    for j in range(motorMovementsPerExposure):  
        time.sleep(expTime/1000/motorMovementsPerExposure)
        ser.write(b'steps 32\r\n')
    qutag.writeTimestamps('',qutag.FILEFORMAT_NONE)
    print("Step 2. file num:", i+numExposures_pause)

# Step 3. Start moving motor 2 opposite direction of motor 1, increasing path length in paths 1 & 3
ser.write(b'setMotor 2\r\n')
for i in range(numExposures):
    qutag.writeTimestamps(file_path+"{}_{}.bin".format(file_name, i+numExposures+numExposures_pause),qutag.FILEFORMAT_BINARY)
    
    for j in range(motorMovementsPerExposure):  
        time.sleep(expTime/1000/motorMovementsPerExposure)
        ser.write(b'steps -32\r\n')
    qutag.writeTimestamps('',qutag.FILEFORMAT_NONE)
    print("Step 3. file num:", i+numExposures+numExposures_pause)    

# Step 4. Wait for numExposures_pause exposures after both motors have moved    
for i in range (numExposures_pause):
    qutag.writeTimestamps(file_path+"{}_{}.bin".format(file_name, i+numExposures*2+numExposures_pause),qutag.FILEFORMAT_BINARY)
    time.sleep(expTime/1000)
    qutag.writeTimestamps('',qutag.FILEFORMAT_NONE)
    print("Pause after step 3. file num:", i+numExposures*2+numExposures_pause)


#Step 5. Reset motors to original positions

motor_reset = numExposures * motorMovementsPerExposure * 32 #11520 = 30 * 12 * 32 | b'steps 11520\r\n' <--How legacy code got hardcoded value from before

reset_string_1 = f'steps -{motor_reset}\r\n'
reset_string_2 = f'steps {motor_reset}\r\n'

ser.write(b'setMotor 1\r\n')
time.sleep(1)
ser.write(reset_string_1.encode())

time.sleep(2)

ser.write(b'setMotor 2\r\n')
time.sleep(1)
ser.write(reset_string_2.encode())

ser.close()

print('Deinitializing quTag...')
qutag.deInitialize()