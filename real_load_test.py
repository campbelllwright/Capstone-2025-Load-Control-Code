
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import matplotlib.pyplot as plt
import numpy as np
import time 
import pyvisa as visa 
import picotool_helper_funcs as pico
import EVolocity_EF_utils as Evo_EF
import evolocity_load as EVOload


## Config:
LOADADDR = 'ASRL26::INSTR' # change to match assigned address for your computer/load - Takes form ASRL[COM port]::INSTR

# Prog_load settings:
RMIN = 4  # ohm
RMAX = 100 # ohm
T = 0.05 # load update period 

# Board info: for calculating theoretical values
RSHUNT = 0.092 # ohm
VSUPPLY = 12 # volt

# Profile Settings:
EVENT ='Monza'
RACE_TYPE = 'Q'
YEAR = 2023
DRIVER = 'VER'
filename = f'{DRIVER}_{EVENT}_{YEAR}_{RACE_TYPE}'

# If using the picotool funcs you may need to set the energy flash region start and end addresses.


rm = visa.ResourceManager()
load = rm.open_resource(LOADADDR)

def write_load(res):
    load.write(f':RESistance {res}OHM')
    
def print_load(profile):
    print(f'T:{int(profile[0]*1000)}ms, V:{int(profile[1]*1000)}mV, I:{int(profile[2]*1000)}mA, P:{int(profile[3]*1000)}mW')


def frame_from_profile_data(profile_data, i):
    return [profile_data[0][i], profile_data[1][i],profile_data[2][i],profile_data[3][i]]


print(pico.picotool_force_reboot_ecu()) # reboot ECU before we start 
time.sleep(7)
print('Starting experiment')
load.write(':INPut ON') # turn on load 
load.write(':FUNCtion RES') # CR mode 


R = EVOload.get_Rload_from_fastf1(DRIVER, YEAR, EVENT, RACE_TYPE, RMAX, RMIN)
profile_data = EVOload.calculate_theo_load_data_from_resistance_profile(R, VSUPPLY, RSHUNT, T)
EVOload.timed_loop_with_enumerate(R,T,write_load) #change load to next R every T seconds
load.write(':INPut OFF') # ensure load off 

# print the theo data to terminal
for (i, t) in enumerate(profile_data[0]):
    print_load(frame_from_profile_data(profile_data, i)) 
    #time.sleep(0.5)
    

print(pico.picotool_force_reboot_ecu_bootsel()) #Reboot ECU into bootsel mode to dump flash
time.sleep(1) # wait for reboot
print(pico.picotool_get_dump_from_ecu("dumps/"+filename+"_Meas.bin")) # dump region of flash with energy data
time.sleep(5) # wait for dump

dump = Evo_EF.parseEFBinDump("dumps/"+filename+"_Meas.bin") #parse binary dump into lists for time, voltage, current, power

#the lists are usually off by 1-2 readings, we strip or pad to make them match for better graphing
dump = [Evo_EF.match_list_lengths(dump[0], profile_data[0]),Evo_EF.match_list_lengths(dump[1], profile_data[1]),Evo_EF.match_list_lengths(dump[2], profile_data[2]),Evo_EF.match_list_lengths(dump[3], profile_data[3])]

# graph the data
Evo_EF.graphEFDumpVsTheo(dump, profile_data, "plots/"+filename+"both.png")

#calculate energy
energy_theo = 0
for (i,p) in enumerate(profile_data[3]):
    energy_theo += p*T
energy_real = 0
for (i,p) in enumerate(dump[3]):
    energy_real += p*T

print(f"Race complete! filename:{filename}.[xyz], energy(T/R):{energy_theo}/{energy_real}j, avg power(T/R): {np.average(profile_data[3])}/{np.average(dump[3])}W")
plt.pause(300) 

load.close()

