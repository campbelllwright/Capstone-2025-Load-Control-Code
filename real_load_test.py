import fastf1
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import matplotlib.pyplot as plt
import numpy as np
import time 
import pyvisa as visa 

# enable cache (if you want to run each race faster)
fastf1.Cache.enable_cache('cache')

# disable logging 
fastf1.set_log_level('WARNING')

# load a session (you can change event, year, and session type)
print('Loading session...')
session = fastf1.get_session(2023, 'Monza', 'Q')
session.load()

# Select a driver and their fastest lap
driver = 'VER'
lap = session.laps.pick_driver(driver).pick_fastest()

# Get car telemetry and add time and distance
tel = lap.get_car_data().add_distance()

speed = tel['Speed'].values  # in km/h
time_s = tel['Time'].dt.total_seconds().values  # in seconds
speed_mps = speed * (1000 / 3600) # m/s
accel = np.gradient(speed_mps, time_s) # m/s2

accel_min = np.min(accel)
accel_max = np.max(accel)
accel_clipped = np.clip(accel, accel_min, accel_max)
R = 100 - ((accel_clipped - accel_min) / (accel_max - accel_min)) * (100 - 4)


rm = visa.ResourceManager()
LOADADDR = 'ASRL5::INSTR' # change to match assigned address for your computer/load
load = rm.open_resource(LOADADDR)

plt.ion()  # turn on interactive mode
fig, ax = plt.subplots()
plt.title(f'{driver} - Simulated Load from Acceleration\n{session.event["EventName"]} {session.event.year}')
plt.xlabel('Real Time [s]')
plt.ylabel(r'Load [$\Omega$] (from acceleration data)')
plt.grid(True)

T = 0.05 # load update period 
x_data, y_data = [], []
line, = ax.plot([], [], color='red')

# set axis limits
ax.set_xlim(0, len(R) * T)
ax.set_ylim(np.min(R) - 5, np.max(R) + 5)

print('Starting experiment')
load.write(':INPut ON') # turn on load 
load.write(':FUNCtion RES') # CR mode 
for i, r in enumerate(R):
    load.write(f':RESistance {r}OHM')
    x_data.append(i * T)
    y_data.append(r)
    line.set_data(x_data, y_data)
    plt.pause(T)  # Update the plot
    time.sleep(T)

print('Race complete!')
load.write(':INPut OFF') # ensure load off 
load.close()