import pyvisa as visa 
import numpy as np
import time

rm = visa.ResourceManager()

LOADADDR = 'ASRL3::INSTR'

load = rm.open_resource(LOADADDR)

load.write(':INPut ON') # turn on load 
load.write(':FUNCtion RES') # CR mode 

START = 4  # ohm
STOP = 12 # ohm
PERIOD = 10 # s 
UPDATETIME = 0.05 # s
step = (STOP-START)/(PERIOD/UPDATETIME)
for load_step in np.arange(START, STOP, step): # RAMP UP
    load.write(f':RESistance {load_step}OHM')
    time.sleep(UPDATETIME)
for load_step in np.flip(np.arange(START, STOP, step)): # RAMP DOWN
    load.write(f':RESistance {load_step}OHM')
    time.sleep(UPDATETIME)

load.write(':INPut OFF') # ensure load off 
load.close()