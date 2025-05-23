
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import matplotlib.pyplot as plt
import numpy as np

import csv as csv

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
def parseEFBinDump(filename, frame_fmt, FRAME_RATE):
    S_PER_FRAME = 1/FRAME_RATE
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'rb') as binfile:
            Frame=struct.iter_unpack(frame_fmt,binfile.read())
            energy = 0
            timeList,voltageList,currentList,powerList = [],[],[],[]
            pastFrame = [0,0,0,0]
            started = 0
            n = 0
            for (i,frame) in enumerate(Frame): 
                if((frame[0] != 65535)):
                    if((started == 1) or ((np.abs(frame[2] - pastFrame[2]) > 1) and (i != 0))): # check for a delta to start parsing
                        if((i != 0) and (started == 0)):
                            started = 1
                            print(f"Load profile start detected at ECU timestamp {int(i*S_PER_FRAME*1000)}ms")
                        energy = energy + float(frame[3])*S_PER_FRAME
                        timeList.append(float(n*S_PER_FRAME))
                        voltageList.append(float(frame[1])/1000)
                        currentList.append(float(frame[2])/1000)
                        powerList.append(float(frame[3])/1000)
                        print(f"T:{frame[0]*50}ms, v:{frame[1]}mV, i:{frame[2]}mA, p:{frame[3]}mW, E(tot):{energy}")
                        n = n+1
                pastFrame = frame
            return [timeList,voltageList,currentList,powerList]
    except FileNotFoundError:
        return None
    


def graphLoad(theoframes, filename):
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

    # set axis limits
    ax_v.set_xlim(np.min(theoframes[0]), np.max(theoframes[0]))
    ax_i.set_xlim(np.min(theoframes[0]), np.max(theoframes[0]))
    ax_e.set_xlim(np.min(theoframes[0]), np.max(theoframes[0]))
    
    ax_v.set_ylim(0, 13)
    ax_i.set_ylim(0, 4)
    ax_e.set_ylim(0, 36)
    
    v_line_theo.set_data(theoframes[0], theoframes[1])
    i_line_theo.set_data(theoframes[0], theoframes[2])
    e_line_theo.set_data(theoframes[0], theoframes[3])
    fig.savefig(filename)
    #plt.pause(64)  # Update the plot

def graphEFDumpVsTheo(framedump, theoframes, filename):
    print(f'"theo length: {len(theoframes[0])}, dump len: {len(framedump[0])}')
    plt.ion()  # turn on interactive mode
    fig, (ax_v, ax_i, ax_e) = plt.subplots(3,1)
    ax_v_b = ax_v.twinx()
    ax_i_b = ax_i.twinx()
    ax_e_b = ax_e.twinx()
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
    v_line_real, = ax_v_b.plot([], [], color='red')
    i_line_real, = ax_i_b.plot([], [], color='red')
    e_line_real, = ax_e_b.plot([], [], color='red')


    # set axis limits
    ax_v.set_xlim(min(np.min(framedump[0]),np.min(theoframes[0])), max(np.max(framedump[0]), np.max(theoframes[0])))
    ax_i.set_xlim(min(np.min(framedump[0]),np.min(theoframes[0])), max(np.max(framedump[0]), np.max(theoframes[0])))
    ax_e.set_xlim(min(np.min(framedump[0]),np.min(theoframes[0])), max(np.max(framedump[0]), np.max(theoframes[0])))
    
    ax_v_b.set_xlim(min(np.min(framedump[0]),np.min(theoframes[0])), max(np.max(framedump[0]), np.max(theoframes[0])))
    ax_i_b.set_xlim(min(np.min(framedump[0]),np.min(theoframes[0])), max(np.max(framedump[0]), np.max(theoframes[0])))
    ax_e_b.set_xlim(min(np.min(framedump[0]),np.min(theoframes[0])), max(np.max(framedump[0]), np.max(theoframes[0])))
    
    
    ax_v.set_ylim(0, 13)
    ax_i.set_ylim(0, 4)
    ax_e.set_ylim(0, 36)
    
    ax_v_b.set_ylim(0, 13)
    ax_i_b.set_ylim(0, 4)
    ax_e_b.set_ylim(0, 36)
    
    v_line_real.set_data(framedump[0], framedump[1])
    i_line_real.set_data(framedump[0], framedump[2])
    e_line_real.set_data(framedump[0], framedump[3])
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


def frame_from_profile_data(data, i):
    return [data[0][i], data[1][i],data[2][i],data[3][i]]


def removeZeros(load_frames):
    new_load_frames = load_frames
    for (index,current) in enumerate(load_frames[2]):
        if (int(current*1000) == 0):
            del(new_load_frames[1][index])
            del(new_load_frames[2][index])
            del(new_load_frames[3][index])
            new_load_frames[0].pop()
    return new_load_frames
            

def calc_energy_from_pwr(power_frames, rate):
    energy = 0
    for (i,p) in enumerate(power_frames):
        energy += p*rate
    return energy


          
def writeCSV(load_frames, dump_frames, r_data, filename):
    if(os.path.exists(filename)):
        csvfile = open(filename, '+w', newline='')
    else:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        csvfile = open(filename, 'x', newline='')
        
    csvwriter = csv.writer(csvfile,lineterminator="\n", delimiter=',',)
    if(dump_frames != None):
        csvwriter.writerow(['Timestamp','Load Voltage','Load Current','Load Power','Load Resistance', 'ECU Voltage', 'ECU Current', 'ECU Power'])
        for (i,t) in enumerate(load_frames[0]):
            csvwriter.writerow([int(load_frames[0][i]*1000),load_frames[1][i],load_frames[2][i],load_frames[3][i], r_data[i], dump_frames[1][i],dump_frames[2][i],dump_frames[3][i]])
    else:
        csvwriter.writerow(['Timestamp','Load Voltage','Load Current','Load Power','Load Resistance'])
        for (i,t) in enumerate(load_frames[0]):
            csvwriter.writerow([int(load_frames[0][i]*1000),load_frames[1][i],load_frames[2][i],load_frames[3][i], r_data[i]])
            
def writeCSV_single(load_frames, r_data, filename):
    if(os.path.exists(filename)):
        csvfile = open(filename, '+w', newline='')
    else:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        csvfile = open(filename, 'x', newline='')
        
    csvwriter = csv.writer(csvfile,lineterminator="\n", delimiter=',',)
    csvwriter.writerow(['Timestamp','Voltage','Current','Power','Resistance'])
    for (i,t) in enumerate(load_frames[0]):
        csvwriter.writerow([int(load_frames[0][i]*1000),load_frames[1][i],load_frames[2][i],load_frames[3][i], r_data[i]])
            
            


def print_load(profile):
    return (f'T:{int(profile[0]*1000)}ms, V:{int(profile[1]*1000)}mV, I:{int(profile[2]*1000)}mA, P:{int(profile[3]*1000)}mW')
