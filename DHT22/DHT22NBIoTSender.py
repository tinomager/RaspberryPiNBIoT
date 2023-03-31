import serial
import sys
import configparser
import time
import json
import Adafruit_DHT

run_test = True

def connect_serial(serialport, baudrate):
    if(run_test == True):
        return None
    
    print("Try to connect to serial port at: " + serialport + " with baudrate " + baudrate)
    s = serial.Serial(serialport, baudrate)
    if (s is None):
        raise ConnectionError("Cannot connect to serial port at " + serialport + " with baudrate " + baudrate)
    else:
        return s
    

def get_dht_values(sensor_version, pin):
    if(run_test == True):
        return { "temp" : 20.4, "hum" : 62}
    temp, hum = Adafruit_DHT.read_retry(sensor_version, pin)
    return { "temp" : temp, "hum" : hum}

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    serialport = config["serial"]["port"]
    baudrate = config["serial"]["baudrate"]
    sendintervall = config["common"]["send_intervall_seconds"]
    sensor = config["dht"]["dht_sensortype"] 
    pin = config["dht"]["dht_pin"]
    print("Started DHT22NBIoTSender script")
    ser = connect_serial(serialport, baudrate)
    while True:
        dht_res = get_dht_values(sensor, pin)
        print("Read from DHT " + json.dumps(dht_res))
        time.sleep(sendintervall)