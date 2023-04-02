import sys
import configparser
import time
import json

mock_DHT = True
mock_serial = False

if(mock_DHT == False):
    import Adafruit_DHT

if(mock_serial == False):
    import serial

def connect_serial(serialport, baudrate):
    if(mock_serial == True):
        return None
    
    print('Try to connect to serial port at: ' + serialport + f' with baudrate {baudrate}')
    s = serial.Serial(serialport, baudrate, timeout=5)
    if (s is None):
        raise ConnectionError(f"Cannot connect to serial port at " + serialport + " with baudrate {baudrate}")
    else:
        return s
    
def send_serial_command(ser, command, expected_returnvalue = None):
    if(mock_serial == True):
        return True

    print("Writing to serial: " + command)
    commandbytes = (command + '\r').encode('utf-8')
    ser.write(commandbytes)

    response = ""
    quantity = 1
    while quantity > 0:
        responsebytes = ser.readline()
        response += responsebytes.decode('utf-8')
        quantity = ser.in_waiting
    print("Got response from serial: " + response)
    
    if(expected_returnvalue is not None):
        if not(response.__contains__(expected_returnvalue)):
            print("Sent command " + command + " and expected return value " + expected_returnvalue + " but got " + response)
            return False
    
    return True

def get_dht_values(sensor_version, pin):
    if(mock_DHT == True):
        return { "temp" : 20.4, "hum" : 62}
    temp, hum = Adafruit_DHT.read_retry(sensor_version, pin)
    return { "temp" : temp, "hum" : hum}

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    serialport = config["serial"]["port"]
    baudrate = int(config["serial"]["baudrate"])
    sendintervall = int(config["common"]["send_intervall_seconds"])
    sensor = config["dht"]["dht_sensortype"] 
    pin = int(config["dht"]["dht_pin"])
    print("Started DHT22NBIoTSender script")
    ser = connect_serial(serialport, baudrate)
    print("Successfully created serial communication")
    if(send_serial_command(ser, "AT", "OK") == True):
        print("Succesfully initialized modem connection")
    else:
        raise ConnectionError("Modem is not available")

    while True:
        dht_res = get_dht_values(sensor, pin)
        print("Read from DHT " + json.dumps(dht_res))
        time.sleep(sendintervall)