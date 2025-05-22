import fastf1
import numpy as np
import time

def calculate_theo_load_data_from_resistance_profile(R, Vsupply, Rshunt, timeStep):
    profile_data = [[],[],[],[]]
    for (i,r) in enumerate(R):
        load_Voltage = ((r/(Rshunt+r))*Vsupply) 
        load_Current = load_Voltage/r
        load_Voltage = load_Voltage - (Rshunt*load_Current)
        load_Power = load_Voltage*load_Current
        profile_data[0].append(i * timeStep)
        profile_data[1].append(load_Voltage)
        profile_data[2].append(load_Current)
        profile_data[3].append(load_Power)
    return profile_data

def get_Rload_from_fastf1(driver, year, event,type, RMAX, RMIN):
    # enable cache (if you want to run each race faster)
    #fastf1.Cache.enable_cache('cache')
    fastf1.set_log_level('WARNING')
    session = fastf1.get_session(year, event, type)
    session.load()
    print(f'Loading session:{driver} {type} at {event} {year}')
    lap = session.laps.pick_driver(driver).pick_fastest()
    tel = lap.get_car_data().add_distance()
    speed = tel['Speed'].values  # in km/h
    time_s = tel['Time'].dt.total_seconds().values  # in seconds
    speed_mps = speed * (1000 / 3600) # m/s
    accel = np.gradient(speed_mps, time_s) # m/s2
    accel_min = np.min(accel)
    accel_max = np.max(accel)
    accel_clipped = np.clip(accel, accel_min, accel_max)
    R = RMAX - ((accel_clipped - accel_min) / (accel_max - accel_min)) * (RMAX - RMIN)
    return R
    


def timed_loop_with_enumerate(iterable, interval_seconds, run_func):
    start_time = time.time()
    for index, item in enumerate(iterable):
        run_func(item)
        time_elapsed = time.time() - start_time
        time_to_sleep = max(0, interval_seconds - time_elapsed)
        time.sleep(time_to_sleep)
        start_time = time.time()