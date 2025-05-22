import pyvisa as visa 
import numpy as np
import time

rm = visa.ResourceManager()

LOADADDR = 'ASRL19::INSTR' # change to match assigned address for your computer/load
load = rm.open_resource(LOADADDR)

load.write(':INPut ON') # turn on load 
load.write(':FUNCtion RES') # CR mode 

START = 4  # ohm
STOP = 12 # ohm
PERIOD = 20 # s 
UPDATETIME = 1 # s
step = (STOP-START)/(PERIOD/UPDATETIME)
for load_step in np.arange(START, STOP, step): # RAMP UP
    load.write(f':RESistance {load_step}OHM')
    #print (load.query("MEAsure:CURrent:DC?"))
    time.sleep(UPDATETIME)
for load_step in np.flip(np.arange(START, STOP, step)): # RAMP DOWN
    load.write(f':RESistance {load_step}OHM')
    time.sleep(UPDATETIME)

#load.write(':INPut OFF') # ensure load off 
load.close()