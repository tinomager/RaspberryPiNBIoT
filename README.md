# RaspberryPiNBIoT
Repository for scripts to connect Raspberry Pi with NB IoT to IoT Creators (https://iotcreators.com/).

## DHT22 to NB IoT

The folder DHT22 contains a Python3 script to capture data from DHT22 sensor and send it via NB IoT to IoT Creators APN.

### Prerequisites

The script requires Python3 installed.
To read data from DHT22 you need to install Adafruit_DHT with
```
pip3 install Adafruit_DHT
```