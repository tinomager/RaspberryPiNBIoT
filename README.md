# RaspberryPiNBIoT

This is repository for script(s) to connect Raspberry Pi with NB IoT to IoT Creators (https://iotcreators.com/).
The scripts are implemented to connect a modem via serial interface.
As NB IoT modem the SIMCOM7070G from Waveshare was used (https://www.waveshare.com/wiki/SIM7070G_Cat-M/NB-IoT/GPRS_HAT). 

## DHT22 to NB IoT

The folder DHT22 contains a Python3 script to capture data from DHT22 sensor and send it via NB IoT to IoT Creators APN.


### Prerequisites

The script requires Python3 installed.
To read data from DHT22 you need to install Adafruit_DHT with:
```
pip3 install Adafruit_DHT
```
Also pySerial is required for serial communication with the NB IoT modem:

```
pip3 install pyserial
```