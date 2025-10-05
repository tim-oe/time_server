import os
import glob
import time

# Initialize the GPIO and 1-Wire interface
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folders = glob.glob(base_dir + '28*')
print(f'devices: {device_folders}')


def read_temp_raw(device_file):
    f = open(device_file, 'r')
    lines = f.readlines()
    for line in lines:
        print(line)
    f.close()
    return lines


def read_temp():
    for item in device_folders:
        device_file = item + '/w1_slave'
        device_id = item.split('/')[-1]  # Extract device ID from path

        lines = read_temp_raw(device_file)
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = read_temp_raw(device_file)
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            print(f'[{device_id}] Temperature: {temp_c:.1f}°C / {temp_f:.1f}°F')


# Read temperature
while True:
    read_temp()
    time.sleep(1)
