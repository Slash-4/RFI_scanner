import time
import os
import sys

import serial
from serial.tools import list_ports
from datetime import datetime
from pathlib import Path

import struct
import argparse
import copy

import json
import h5py
import csv

import numpy as np
import matplotlib.pyplot as plt

# Define the configuration parameters
# config = {     
#     "f_low": 1000,              # Example value in Hz
#     "f_high": 2000,             # Example value in Hz
#     "rbw": 10,                  # Example value in Hz
#     "points": 100,              # Example number of points
#     "verbose": 0,
#     "read_mode": "maxhold",
#     "calibration_file": "calibration.dat",  # Example calibration file path
#     "storage_file": "storage.dat",          # Example storage file path
#     "pinout": "pi",           # Example pinout configuration
#     "baudrate": 115200,           # Example baudrate
    
# }

pwd  = Path(__file__).parent
config_file = f"{pwd}/config.json"

#raspberry pi pin out
green =  17
yellow = 27
red = 22

def save_config(file_path, config):
    """Save the configuration to a JSON file."""
    with open(file_path, 'w') as json_file:
        json.dump(config, json_file, indent=4)
    print(f"Configuration saved to {file_path}")

def load_config(file_path):
    """Load the configuration from a JSON file."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"No such file: '{file_path}'")
    
    with open(file_path, 'r') as json_file:
        config = json.load(json_file)
    print(f"Configuration loaded from {file_path}")
    return config

# tinysa USB IDs
VID = 0x0483
PID = 0x5740

F_LOW = 0
F_HIGH = 350000000
POINTS = 101


# Get tinysa device automatically
def getport() -> str:
    device_list = list_ports.comports()
    for device in device_list:
        if device.vid == VID and device.pid == PID:
            return device.device
    raise OSError("device not found")


# return 1D numpy array with power as dBm
def get_tinysa_dBm( s_port, f_low=F_LOW, f_high=F_HIGH, points=POINTS, rbw=0, verbose=None, **kwargs):
    """
    Input:
    s_port: serial port of the tinySA
    f_low: lower frequency limit
    f_high: upper frequency limit
    points: number of points to sample
    rbw: resolution bandwidth
    verbose: verbosity level

    Output:
    freq: frequency array
    dBm_power: dBm power array
    
    This function communicates with the tinySA device over serial to get the dBm power values.

    """

    with serial.Serial( port=s_port, baudrate=115200 ) as tinySA:
        tinySA.timeout = 1
        while tinySA.inWaiting():
            tinySA.read_all() # keep the serial buffer clean
            time.sleep( 0.1 )

        if 0 == rbw: # use tinySA values
            rbw_k = (f_high - f_low) * 7e-6 # RBW / kHz
        else:
            rbw_k = rbw / 1e3

        if rbw_k < 3:
            rbw_k = 3
        elif rbw_k > 600:
            rbw_k = 600

        rbw_command = f'rbw {int(rbw_k)}\r'.encode()
        tinySA.write( rbw_command )
        tinySA.read_until( b'ch> ' ) # skip command echo and prompt

        # set timeout accordingly - can be very long - use a heuristic approach
        timeout = ((f_high - f_low) / 20e3) / (rbw_k ** 2) + points / 500 + 60
        tinySA.timeout = timeout * 2

        if verbose:
            sys.stderr.write( f'frequency step: {int( (f_high - f_low) / ( points-1 ) / 1e3 )} kHz\n' )
            sys.stderr.write( f'RBW: {int(rbw_k)} kHz\n' )
            sys.stderr.write( f'serial timeout: {timeout} s\n' )

        scan_command = f'scanraw {int(f_low)} {int(f_high)} {int(points)}\r'.encode()
        tinySA.write( scan_command )
        tinySA.read_until( b'{' ) # skip command echoes, TODO check if returned size > 0
        raw_data = tinySA.read_until( b'}ch> ' ) # TODO repeat until complete
        #tinySA.write( 'rbw auto\r'.encode() ) # switch to auto RBW for faster tinySA screen update

    
    #one small problem is that if points exceeds 2000 the tinySA can time out before sending the data.
    raw_data = struct.unpack( '<' + 'xH'*points, raw_data[:-5] ) # ignore trailing '}ch> '
    raw_data = np.array( raw_data, dtype=np.uint16 )
    # tinySA:  SCALE = 128
    # tinySA4: SCALE = 174
    SCALE = 174
    dBm_power = raw_data / 32 - SCALE # scale 0..4095 -> -128..-0.03 dBm
    freq  = np.linspace(f_low, f_high, points)
    
    return freq, dBm_power


def gain_calibration( freq, dBm_power, calibration_file=None, verbose=0, **kwargs):
    """
    Input: 
    freq: frequency array
    dBm_power: dBm power array
    calibration_file: path to the calibration file
    verbose: verbosity level

    Output:
    dBm_power: dBm power array after applying gain calibration

    This function applies gain calibration to the dBm power values based on the provided calibration csv file.
    
    """
    if calibration_file is None:
        return dBm_power

    with open(calibration_file, 'r') as f:
        lines = f.readlines()

    # Extract the gain values from the calibration file
    
    data  = np.loadtxt(calibration_file, delimiter=",", skiprows=1)
    
    freq_cal    = data[:, 1]
    gain_cal = data[:, 2]

    # Interpolate the gain values to match the frequency points

    dBm_power -= np.interp(freq, freq_cal, gain_cal)

    return dBm_power



def init_pins(pinout=None, **kwargs):
    """Initialize the GPIO pins for the Raspberry Pi."""
    if pinout == "pi":
        global GPIO
        import RPi.GPIO as GPIO

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(green, GPIO.OUT)
        GPIO.setup(yellow, GPIO.OUT)
        GPIO.setup(red, GPIO.OUT)
        time.sleep(0.5)
        GPIO.output(green, GPIO.HIGH)
        GPIO.output(red, GPIO.LOW)
        GPIO.output(yellow, GPIO.LOW)

def close_pins(pinout=None, **kwargs):
    """Close the GPIO pins for the Raspberry Pi."""
    if pinout == "pi":
         GPIO.output(green,  GPIO.LOW)
         GPIO.output(red,    GPIO.LOW)
         GPIO.output(yellow, GPIO.LOW)

    print("################## Halted measurement ###################")


def set_pins(state, pinout=None, verbose=0, **kwargs):
    """Set the GPIO pins based on the state."""

    if pinout == "pi":
        if state == "HIGH":

            GPIO.output(green, GPIO.LOW)
            GPIO.output(red, GPIO.HIGH)
            GPIO.output(yellow, GPIO.LOW)
        else:
            GPIO.output(green, GPIO.HIGH)
            GPIO.output(red, GPIO.LOW)
            GPIO.output(yellow, GPIO.LOW)
    
    if verbose > 0:
         print(f"State: {state}")
    else:
        print(f"{state}")


def check_level(freq, power, verbose=0, **kwargs):
    """
    Input:
    freq: frequency array
    power: dBm power array
    verbose: verbosity level

    Output:
    "HIGH" if the maximum power is greater than -70 dBm, otherwise "LOW"
    This function can be modified to use a more sophisticated evaluation method
    

    # Check if the maximum power is above -70 dBm
    # Note: The threshold can be adjusted as needed

    """

    if verbose > 0:
        print(np.max(power))

    if verbose > 1:
        print(power)

    if np.max(power) > -70:
        return "HIGH"
    else:
        return "LOW"

def save_to_file(powers, freqs, scan_id, filename, scan_dir="./", **kwargs):

    file_path = f"{pwd}/{scan_dir}/{filename}"

    write_header = not os.path.exists(file_path)

    # Open file in append mode

    if write_header:
       with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Scan ID"] + list(freqs)) 

 
    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([scan_id] + list(powers)) 

       
    
    


def main():
    loaded_config = load_config(config_file)
    
#    loaded_config = {     
#    "f_low": 0.4E6,              # Example value in Hz
#    "f_high": 2.4E6,             # Example value in Hz
#    "rbw": 100E3,                  # Example value in Hz
#    "points": 1000,              # Example number of points
#    "verbose": 0,
#    "read_mode": "maxhold",
#    "calibration_file": "calibration.dat",  # Example calibration file path
#    "storage_file": "storage.dat",          # Example storage file path
#    "pinout": "pi",           # Example pinout configuration
#    "baudrate": 115200,           # Example baudrate
#    }
    filename = datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f")[:-5]
    scan_id = 0
    
    init_pins(**loaded_config)
    
    while True:
        try :
            portSA = getport()
            break
        except OSError as E:
            print(f"{E} No tinySA connected.")
            time.sleep(1)
        
    try:
        while True:
        
            freq, dBm_power = get_tinysa_dBm(portSA, **loaded_config)
            dBm_power = gain_calibration(freq, dBm_power, **loaded_config)
            state = check_level(freq, dBm_power, **loaded_config)

            save_to_file(dBm_power,freq, scan_id, filename, **loaded_config)
            
            if loaded_config["verbose"] > 0:
                print(f"Scan ID: {scan_id}")
                print(f"Frequency: {freq}")
                print(f"Power: {dBm_power}")
                print(f"State: {state}")
            
            #print(state, np.max(dBm_power))
            set_pins(state, **loaded_config)
            scan_id += 1


    except KeyboardInterrupt:

            close_pins(**loaded_config)
            return 0 
        
        
if __name__ == "__main__":
    main()

