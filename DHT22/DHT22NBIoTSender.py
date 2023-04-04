import sys
import configparser
import time
import json

mock_DHT = True
mock_serial = False
command_waittime_seconds = 0.1

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

    response = send_serial_command_with_returnvalue(ser, command)   
    
    if(expected_returnvalue is not None):
        if not(response.__contains__(expected_returnvalue)):
            print("Sent command " + command + " and expected return value " + expected_returnvalue + " but got " + response)
            return False
    
    return True

def send_serial_command_with_returnvalue(ser, command):
    if(mock_serial):
        return None
    
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
    time.sleep(command_waittime_seconds)
    return response

def get_signal_status(ser):
    retry = 3
    while retry > 0:
        csq = send_serial_command_with_returnvalue(ser, 'AT+CSQ')
        if csq.lower() == "error":
            retry -= 1

            if retry == 0:
                print("Cannot get signal strength")
                raise ConnectionError("Modem not connected to network")

            continue
        else:
            try:
                csq_parts = csq.split(':')
                csq_value = csq_parts[1].split(',')[0]
                return csq_value
            except:
                continue

def get_dht_values(sensor_version, pin):
    if(mock_DHT == True):
        return { "temp" : 20.4, "hum" : 62}
    temp, hum = Adafruit_DHT.read_retry(sensor_version, pin)
    return { "temp" : temp, "hum" : hum}

def send_values(ser, valuejson):
    print(f'Try to send JSON: {valuejson}')
    hexstring = valuejson.hex()


def set_modem_configuration(ser):
    #set NB IOT
    if(send_serial_command(ser, 'AT+CBANDCFG="NB-IOT",8', 'OK') == True):
        print("Modes is now configured for NB IoT")
    else:
        print("Cannot configure modem for NB IoT")
        raise ConnectionError("Modem cannot be configured for NB IoT")
        
    #set APN
    apn_cgdcont_value = f'1,"IP","{apn_config}"'
    if(send_serial_command(ser, f'AT+CGDCONT={apn_cgdcont_value}', 'OK') == True):
        print(f'Set APN to {apn_cgdcont_value}')
    else:
        print('Cannot set APN value')
        raise ConnectionError("Modem APN cannot be configured like set in config.ini")

    apn_cncfg = f'0,1,"{apn_config}"'
    if(send_serial_command(ser, f'AT+CNCFG={apn_cncfg}', 'OK') == True):
        print('Modem APN was configured like in config.ini')
    else:
        print('Cannot set APN value')
        raise ConnectionError("Modem APN cannot be configured like set in config.ini")


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
    set_operator = (config["nbiot"]["set_operator"]).lower() == 'true'
    udp_ip_address = config["nbiot"]["udp_ip_address"]
    udp_port = config["nbiot"]["udp_port"]
    
    #check if modem is configured properly otherwise set correct values
    print("Started DHT22NBIoTSender script")
    ser = connect_serial(serialport, baudrate)
    print("Successfully created serial communication")
    if(send_serial_command(ser, "AT", "OK") == True):
        print("Succesfully initialized modem connection")
    else:
        print("Modem was not correct initialized.")
        raise ConnectionError("Modem is not available")

    if set_operator == True:
        set_modem_configuration(ser)

    #check network connection
    if(send_serial_command(ser, "AT+CGATT?", "1") != True):
        print("Modem is not connected to the network")
        raise ConnectionError("Modem is not connected to the network")
    
    #check signal status
    csq = get_signal_status(ser)
    print(f'Modem network connected. Signal strength: {csq}')
    
    #connect to UDP server
    if(send_serial_command(ser, 'AT+CACID=0,1', '0,ACTIVE') != True):
        print("Cannot open PDP mode")
        raise ConnectionError("Cannot open PDP port for UDP communication")
    
    caopen_command = f'0,0,"UDP","{udp_ip_address}",{udp_port}'
    if(send_serial_command(ser, f'AT+CAOPEN={caopen_command}', 'OK') != True):
        print("Cannot connect to UDP server")
        raise ConnectionError("Cannot open UDP connection")
    
    while True:
        dht_res = get_dht_values(sensor, pin)
        print("Read from DHT " + json.dumps(dht_res))
        send_values(ser, dht_res)

        #wait till the next run
        time.sleep(sendintervall)