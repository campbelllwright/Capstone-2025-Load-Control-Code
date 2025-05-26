# Capstone 2025 Load Control 

This repository contains example code and resources for the Capstone 2025 course at the University of Auckland.
It is intended to assist students implementing a controller for the benchtop DC load provided in the lab using Python and provide guidance for setting up and running the required software.
The example code demonstrates a ramped constant resistance load using pyVISA.

## Installation requirements 
In order to control the DC load and provide a load profile which is representative of the EVolocity motor, two pieces of software are required. 
A VISA backend and some programming language, in this example, Python. 
[VISA](https://www.wikiwand.com/en/articles/Virtual_instrument_software_architecture) is a standardised language for controlling electronics test equipment over USB, GPIB or TCP/IP. 

### VISA Backend
VISA requires an appropriate backend to be installed. 
Two popular options are the [Keysight IO Libraries Suite](https://www.keysight.com/us/en/lib/software-detail/computer-software/io-libraries-suite-downloads-2175637.html) and [NI-VISA](https://www.ni.com/en/support/downloads/drivers/download.ni-visa.html#558610) from Keysight and National Instruments, respectively.
The Keysight IO Libraries Suite is only available for Windows but the NI-VISA backend supports Mac OS and Linux, for more information see [the documentation](https://pyvisa.readthedocs.io/en/1.8/configuring.html).
After installing either backend (the Keysight option is recommended), you may need to restart your computer before continuing with the next step. 

### Python 
The provided example code is written in Python, you can install Python 3 from [here](https://www.python.org/downloads/), note that the primary python library we want to use, [PyVISA](https://pyvisa.readthedocs.io/en/latest/), requires Python 3.10 or higher.
Most modern operating systems should have Python installed, open a Windows Terminal or Command Prompt window and enter 'python' as below, on Windows 11, if Python is not installed it will install itself from the Windows store. 
```bash
python
```
The provided code requires two additional packages, [numpy](https://numpy.org/) and [pyvisa](https://pyvisa.readthedocs.io/en/latest/). 
You can install these with the following command.
```bash
pip install numpy pyvisa
```
If you wish to develop this code further, or include it in your group git repo, you may wish to install these libraries using a [virtual environment](https://docs.python.org/3/library/venv.html).

## Running Code 
Once everything is installed (the example code was developed using Python 3.12 and pyVISA 1.14), connect the load to your personal computer with the USB cable (leave this plugged in to the load in the lab). 
After the load is connected it should appear as a VISA resource. 

### Keysight Connection Expert
If you have installed the [Keysight IO Libraries Suite](https://www.keysight.com/us/en/lib/software-detail/computer-software/io-libraries-suite-downloads-2175637.html), open [Keysight Connection Expert](https://helpfiles.keysight.com/IO_Libraries_Suite/English/IOLS_2024_U1_Windows/IOLS/Content/AboutConnectionExpert.htm) and find your connected device (it should be shown with a green tick). 
Locate the VISA address for the TENMA load (e.g. 'ASRL5::INSTR') and change the appropriate line in the example Python code (shown below). 

```python
LOADADDR = 'ASRL5::INSTR' # change to match assigned address for your computer/load
load = rm.open_resource(LOADADDR)
```

### PyVISA alternative 
If you have installed an alternative VISA backend or did not install [Keysight Connection Expert](https://helpfiles.keysight.com/IO_Libraries_Suite/English/IOLS_2024_U1_Windows/IOLS/Content/AboutConnectionExpert.htm), you can find the appropriate address by running the following commands in a Python interactive window (REPL). 
You should then see a list of the available VISA resources. 

```python
import pyvisa
rm = pyvisa.ResourceManager()
rm.list_resources()
```

## real_load_test.py usage/parameters:

This script is designed to run a 'real' load profile derived from real F1 race data on the programmable load;
Then Graph the load voltage, current, and power over time; and print the energy usage to the console.
If your ECU is compatible, this script is also designed to dump the region of flash where energy data is stored, parse it, and plot that on the same graph as the load for comparison.
(If you modify the dumper/parser to make it work with your implementation, please fork the repo and publish it so I may include it as another example).

#### This script has a number of arguments to modify the execution:

```-r, --reboot, --no-reboot``` - Reboot the pico before starting the load profile. this happens by default, to not reboot use --no-reboot.  
```-d, --dump, --no-dump``` - Reboot the pico into BOOTSEL mode and Dump energy data from flash after the run. Default yes.
```--csvout, --no-csvout``` - output the load (and ECU if available) data from the run as CSVs.   
```-l, --loadport``` - COM port number of programmable load. **Required.** (e.x. if load is COM19, run ```python real_load_test.py -l 19```)  
```--ecurate``` - ECU Storage rate (Hz). (how many samples do you store to flash per second. only needed if dumping.)  
Race/driver selection for load profile: (we use fastest lap)  
```--driver``` - F1 driver for load profile.  
```--event``` - F1 event for load profile.  
```--racetype``` - F1 event type for load profile.  
```--year``` - F1 year for load profile.  

## Issues 
For any issues specifically related to these scripts, email [campbell.wright@auckland.ac.nz](mailto:campbell.wright@auckland.ac.nz).

For any other issues, contact the course teaching staff or email [seho.kim@auckland.ac.nz](mailto:alexander.bailey@auckland.ac.nz)
