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

def send_values(ser, valuejson):
    print(f'Try to send JSON: {valuejson}')

if __name__ == "__main__":
    #parse config
    config = configparser.ConfigParser()
    config.read("config.ini")
    serialport = config["serial"]["port"]
    baudrate = int(config["serial"]["baudrate"])
    sendintervall = int(config["common"]["send_intervall_seconds"])
    sensor = config["dht"]["dht_sensortype"] 
    pin = int(config["dht"]["dht_pin"])
    apn_config = config["nbiot"]["apn"]
    command_waittime_seconds = float(config["serial"]["command_waittime_seconds"])
    
    #check if modem is configured properly otherwise set correct values
    print("Started DHT22NBIoTSender script")
    ser = connect_serial(serialport, baudrate)
    print("Successfully created serial communication")
    if(send_serial_command(ser, "AT", "OK") == True):
        print("Succesfully initialized modem connection")
    else:
        print("Modem was not correct initialized.")
        raise ConnectionError("Modem is not available")

    #check if modem is set for NB IoT
    if(send_serial_command(ser, 'AT+CBANDCFG?', '"NB-IOT",8') == True):
        print("Modem was already configured for NB IoT")
    else:
        time.sleep(command_waittime_seconds)
        if(send_serial_command(ser, 'AT+CBANDCFG="NB-IOT",8', 'OK') == True):
            print("Modes is now configured for NB IoT")
        else:
            print("Cannot configure modem for NB IoT")
            raise ConnectionError("Modem cannot be configured for NB IoT")
        
    #check and set APN
    apn_cgdcont_value = f'1,"IP",{apn_config}'
    if(send_serial_command(ser, 'AT+CGDCONT?', apn_cgdcont_value) == False):
        time.sleep(command_waittime_seconds)
        if(send_serial_command(ser, f'AT+CGDCONT={apn_cgdcont_value}', 'OK') == True):
            print(f'Set APN to {apn_cgdcont_value}')
        else:
            print('Cannot set APN value')
            raise ConnectionError("Modem APN cannot be configured like set in config.ini")

    apn_cncfg = f'0,1,{apn_config}'
    if(send_serial_command(ser, 'AT+CNCFG?', apn_cncfg) == True):
        print('Modem APN was configured like in config.ini')
    else:
        time.sleep(command_waittime_seconds)
        if(send_serial_command(ser, f'AT+CNCFG={apn_cncfg}', 'OK') == True):
            print('Modem APN was configured like in config.ini')
        else:
            print('Cannot set APN value')
            raise ConnectionError("Modem APN cannot be configured like set in config.ini")

    while True:
        dht_res = get_dht_values(sensor, pin)
        print("Read from DHT " + json.dumps(dht_res))
        send_values(ser, dht_res)

        #wait till the next run
        time.sleep(sendintervall)