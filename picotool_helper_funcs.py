
import subprocess
import shutil
import warnings

# Helper functions to use picotool.

# NOTE - this relies on picotool being on your PATH, so add it to path or change the line below.
PICOTOOL = shutil.which("picotool")

ECU_DATA_FLASH_START = "1017F000"
ECU_DATA_FLASH_END = "101FF000"

def picotool_upload_dump_to_ecu(filename):
    try:
        
        print(f">{PICOTOOL} load -o {ECU_DATA_FLASH_START}  \"{filename}\"")
        return subprocess.run(
            [PICOTOOL, "load", "-o", ECU_DATA_FLASH_START , filename],
            check=True,
            text=True
        ).stdout
    except subprocess.CalledProcessError as e:
        return e.stderr
    
def picotool_get_dump_from_ecu(filename):
    try:
        PICOTOOL = shutil.which("PICOTOOL")
        print(f">{PICOTOOL} save -r {ECU_DATA_FLASH_START} {ECU_DATA_FLASH_END}  \"{filename}\"")
        return subprocess.run(
            [PICOTOOL, "save", "-r", ECU_DATA_FLASH_START, ECU_DATA_FLASH_END , filename],
            check=True,
            text=True
        ).stdout
    except subprocess.CalledProcessError as e:
        return e.stderr
    
def picotool_erase_ecu_data_flash():
    try:
        PICOTOOL = shutil.which("PICOTOOL")
        print(f">{PICOTOOL} erase -r {ECU_DATA_FLASH_START} {ECU_DATA_FLASH_END}")
        return subprocess.run(
            [PICOTOOL, "erase", "-r", ECU_DATA_FLASH_START, ECU_DATA_FLASH_END],
            check=True,
            text=True
        ).stdout
    except subprocess.CalledProcessError as e:
        return e.stderr
    
def picotool_force_reboot_ecu():
    try:
        PICOTOOL = shutil.which("PICOTOOL")
        print(f">{PICOTOOL} reboot -f")
        return subprocess.run(
            [PICOTOOL, "reboot", "-f"],
            check=True,
            text=True
        ).stdout
    except subprocess.CalledProcessError as e:
        return e.stderr
    
def picotool_force_reboot_ecu_bootsel():
    try:
        PICOTOOL = shutil.which("PICOTOOL")
        print(f">{PICOTOOL} reboot -f -u")
        return subprocess.run(
            [PICOTOOL, "reboot", "-f", "-u"],
            check=True,
            text=True
        ).stdout
    except subprocess.CalledProcessError as e:
        return e.stderr
    


