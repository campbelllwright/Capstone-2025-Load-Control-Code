
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import matplotlib.pyplot as plt
import numpy as np
import time 
import pyvisa as visa 
import picotool_helper_funcs as pico
import EVolocity_EF_utils as Evo_EF
import evolocity_load as EVOload
import datetime as date
#import msvcrt

import argparse
arguments_parser = argparse.ArgumentParser("EVOlocity_Load_test")
arguments_parser.add_argument("-r","--reboot", action=argparse.BooleanOptionalAction, default=True, help="Reboot the pico before starting the run. Default yes.")
arguments_parser.add_argument("-d","--dump", action=argparse.BooleanOptionalAction, default=False, help = "Reboot the pico into BOOTSEL mode and Dump energy data from flash after the run. Default no.")
arguments_parser.add_argument("--csvout", action=argparse.BooleanOptionalAction, default=False, help="output the load (and ECU) data from the run as a CSV - note this may be buggy if sample and load rate are not matched.")
arguments_parser.add_argument("--load", action=argparse.BooleanOptionalAction, default=True, help="Load is connected - default TRUE")
arguments_parser.add_argument("-l","--loadport", type=int, help="COM port number of programmable load. Required.", required=True)
arguments_parser.add_argument("--driver", type=str, default='VER', help="F1 driver for load profile.")
arguments_parser.add_argument("--event", type=str, default='Monza', help="F1 event for load profile.")
arguments_parser.add_argument("--racetype", type=str, default='Q', help="F1 event type for load profile.")
arguments_parser.add_argument("--year", type=int, default=2023, help="F1 year for load profile.")
arguments_parser.add_argument("--ecurate", type=int, default=10,help="ECU Storage rate (Hz). default 10.")




arguments = arguments_parser.parse_args()
## Config:
LOADADDR = f'ASRL{arguments.loadport}::INSTR' # change to match assigned address for your computer/load - Takes form ASRL[COM port]::INSTR

# Prog_load settings:

T = 0.05 # load update period 


FRAME_RATE = arguments.ecurate #recording/transmission rate of pico
MS_PER_FRAME = 1000/FRAME_RATE
S_PER_FRAME = 1/FRAME_RATE



# Profile Settings:

filename = f'{arguments.driver}_{arguments.event}_{arguments.year}_{arguments.racetype}'

# If using the picotool funcs you may need to set the energy flash region start and end addresses.


if(arguments.load):
    load = EVOload.setup_load(LOADADDR)

R = EVOload.get_Rload_from_fastf1(arguments.driver, arguments.year, arguments.event, arguments.racetype)

#T = (100/len(R))

load_data = [[],[],[],[]]

res_data = []
def write_load(load,i,res):
    res_data.append(int(res*1000))
    
    load_data[0].append(T*i)
    load_data[1].append(float(load.query(':MEASure:VOLTage?').removesuffix("V")))
    load_data[2].append(float(load.query(':MEASure:CURRent?').removesuffix("A")))
    load_data[3].append(float(load.query(':MEASure:POWer?').removesuffix("W")))
    load.write(f':RESistance {res}OHM')
    

    
if(arguments.reboot):
    print(pico.picotool_force_reboot_ecu()) # reboot ECU before we start 
    time.sleep(7)
print('Starting experiment')
if(arguments.load):
    load.write(':INPut ON') # turn on load 
    print(f"staring load profile at dateTime {time.ctime(time.time())}")
    EVOload.timed_loop_with_enumerate(R,T, load,write_load) #change load to next R every T seconds
    print(f"stopping load profile at dateTime {time.ctime(time.time())}")
    load.write(':INPut OFF') # ensure load off 

# print the theo data to terminal
if(arguments.load): 
    load_data = Evo_EF.removeZeros(load_data)
    for (i, t) in enumerate(load_data[0]):
        print(f"{Evo_EF.print_load(Evo_EF.frame_from_profile_data(load_data, i))}, R:{res_data[i]}ohm") 
        #time.sleep(0.5)
    energy_load = Evo_EF.calc_energy_from_pwr(load_data[3], T)
else:
    energy_load = 0
    
print("press key to continue")
#msvcrt.getch()


if(arguments.dump):
    print(pico.picotool_force_reboot_ecu_bootsel()) #Reboot ECU into bootsel mode to dump flash
    time.sleep(1) # wait for reboot
    print(pico.picotool_get_dump_from_ecu(f"dumps/{filename}_Meas.bin")) # dump region of flash with energy data
    time.sleep(5) # wait for dump
    dump = Evo_EF.parseEFBinDump(f"dumps/{filename}_Meas.bin", '<HHHH', arguments.ecurate) #parse binary dump into lists for time, voltage, current, power




if((arguments.dump) and (dump != None)):
    dump = Evo_EF.removeZeros(dump)
    energy_ecu = Evo_EF.calc_energy_from_pwr(dump[3], S_PER_FRAME)
    if(arguments.load):
        Evo_EF.graphEFDumpVsTheo(dump, load_data, "plots/"+filename+"both.png") 
    else:
        Evo_EF.graphLoad(dump, "plots/"+filename+"ecu.png")    #
    print(f"Race complete! filename:{filename}.[xyz], energy(Load/ECU):{energy_load:.4f}J/{energy_ecu:.4f}J, avg power(Load/ECU): {np.average(load_data[3]):.4f}W/{np.average(dump[3]):.4f}W. accuracy = {((1-(energy_load/energy_ecu))*100):.4f}%")
else: #no dump
    Evo_EF.graphLoad(load_data, "plots/"+filename+"load.png")
    print(f"Race complete! filename:{filename}.[xyz], energy(load):{energy_load:.4f}J, avg power(load):{np.average(load_data[3]):.4f}W.")
    
# graph the data

if(arguments.csvout):
    if(arguments.load):
        Evo_EF.writeCSV_single(load_data, res_data, f"results/{filename}_load.csv")
    if((arguments.dump) and(dump != None)):
        Evo_EF.writeCSV_single(dump, res_data, f"results/{filename}_ECU.csv")
#calculate energy


plt.pause(300) 



load.close()

