
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import matplotlib.pyplot as plt
import numpy as np


import fastf1
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import matplotlib.pyplot as plt
import numpy as np
import time 
import picotool_helper_funcs as pico

import struct
import subprocess
import sys
import shutil
import os



#This is specific to Team 13's energy frame implementation, you may want to modify or replace this so it works for you.
def parseEFBinDump(filename):
    with open(filename, 'rb') as binfile:
        Frame=struct.iter_unpack('<HHHH',binfile.read())
        energy = 0
        frameList = []
        timeList,voltageList,currentList,powerList = [],[],[],[]
        pastFrame = [0,0,0,0]
        started = 0
        for (i,frame) in enumerate(Frame): 
            if((frame[0] != 65535)):
                if((started == 1) or ((frame[2] - pastFrame[2]) != 0) or (i == 0)): # check for a delta to start parsing
                    if(i != 0):
                        started = 1
                    
                    energy = energy + float(frame[3])*0.05
                    #frameList.append([frame[1][0]*20, frame[1][1], frame[1][2], frame[1][3]])
                    timeList.append(float(frame[0]*50)/1000)
                    voltageList.append(float(frame[1])/1000)
                    currentList.append(float(frame[2])/1000)
                    powerList.append(float(frame[3])/1000)
                    print(f"T:{frame[0]*50}ms, v:{frame[1]}mV, i:{frame[2]}mA, p:{frame[3]}mW, E(tot):{energy}")
            pastFrame = frame
        return [timeList,voltageList,currentList,powerList]


def graphEFDump(framedump, filename):
    plt.ion()  # turn on interactive mode
    fig, (ax_v, ax_i, ax_e) = plt.subplots(3,1)
    plt.xlabel('Real Time [s]')
    ax_v.grid(True)
    ax_i.grid(True)
    ax_e.grid(True)
    ax_v.title.set_text(r'Voltage(V)')
    ax_i.title.set_text(r'Current(A)')
    ax_e.title.set_text(r'Power(W)')
    plt.grid(True)
    plt.subplots_adjust(left=0.1,
                        bottom=0.1, 
                        right=0.9, 
                        top=0.9, 
                        wspace=0.4, 
                        hspace=0.4)

    
    v_line, = ax_v.plot([], [], color='blue')
    i_line, = ax_i.plot([], [], color='red')
    e_line, = ax_e.plot([], [], color='green')

    # set axis limits
    ax_v.set_xlim(np.min(framedump[0]), np.max(framedump[0]))
    ax_i.set_xlim(np.min(framedump[0]), np.max(framedump[0]))
    ax_e.set_xlim(np.min(framedump[0]), np.max(framedump[0]))
    
    ax_v.set_ylim(0, 13)
    ax_i.set_ylim(0, 4)
    ax_e.set_ylim(0, 36)
    
    v_line.set_data(framedump[0], framedump[1])
    i_line.set_data(framedump[0], framedump[2])
    e_line.set_data(framedump[0], framedump[3])
    fig.savefig(filename)
    #plt.pause(64)  # Update the plot
    
    

def graphEFDumpVsTheo(framedump, theoframes, filename):
    print(f'"theo length: {len(theoframes[0])}, dump len: {len(framedump[0])}')
    plt.ion()  # turn on interactive mode
    fig, (ax_v, ax_i, ax_e) = plt.subplots(3,1)
    plt.xlabel('Real Time [s]')
    ax_v.grid(True)
    ax_i.grid(True)
    ax_e.grid(True)
    ax_v.title.set_text(r'Voltage(V)')
    ax_i.title.set_text(r'Current(A)')
    ax_e.title.set_text(r'Power(W)')
    plt.grid(True)
    plt.subplots_adjust(left=0.1,
                        bottom=0.1, 
                        right=0.9, 
                        top=0.9, 
                        wspace=0.4, 
                        hspace=0.4)

    
    v_line_theo, = ax_v.plot([], [], color='blue')
    i_line_theo, = ax_i.plot([], [], color='blue')
    e_line_theo, = ax_e.plot([], [], color='blue')
    v_line_real, = ax_v.plot([], [], color='red')
    i_line_real, = ax_i.plot([], [], color='red')
    e_line_real, = ax_e.plot([], [], color='red')


    # set axis limits
    ax_v.set_xlim(min(np.min(framedump[0]),np.min(theoframes[0])), max(np.max(framedump[0]), np.max(theoframes[0])))
    ax_i.set_xlim(min(np.min(framedump[0]),np.min(theoframes[0])), max(np.max(framedump[0]), np.max(theoframes[0])))
    ax_e.set_xlim(min(np.min(framedump[0]),np.min(theoframes[0])), max(np.max(framedump[0]), np.max(theoframes[0])))
    
    ax_v.set_ylim(0, 13)
    ax_i.set_ylim(0, 4)
    ax_e.set_ylim(0, 36)
    
    v_line_real.set_data(theoframes[0], framedump[1])
    i_line_real.set_data(theoframes[0], framedump[2])
    e_line_real.set_data(theoframes[0], framedump[3])
    v_line_theo.set_data(theoframes[0], theoframes[1])
    i_line_theo.set_data(theoframes[0], theoframes[2])
    e_line_theo.set_data(theoframes[0], theoframes[3])
    fig.savefig(filename)
    #plt.pause(64)  # Update the plot
    
    
def match_list_lengths(list_a,list_b):
    if(len(list_a) > len(list_b)):
        while(len(list_a) > len(list_b)):
            list_a.pop()
    elif(len(list_a) < len(list_b)):
        while(len(list_a) < len(list_b)):
            list_a.append(list_a[len(list_a)-1])
            
    return(list_a)


