# lhbsv1_pimax - Very simple Proof Of Concept

## LightHouse BaseStation v1 for Pimax Headsets

This tool looks for Pimax Headset (5k, 5k+, 8k) then wake up and control the timeout of LightHouse Base Stations v1

## Informations

This is really an early proof of concept script - "it works for me"
I'm not sure I can provide any support / help, but I can try. 

The purpose of this PoC is to show what is possible, to be used / included in other OpenSource tools (like Pitool in the future)

I only speak about a BaseStation in "B" mode because the "C" mode is a slave and will follow the power state of the master one shortly after.
I may (or not !) work with "A" mode.

## Requirements

 - Windows 10
 - Python 3.7
 - Python Bleak library
 - Python pywinusb library
 - Pimax Headset (5k+, not sure about others)
 - At least one HTC LighHouse BaseStation
 - Finding your BasStation MAC Address and UniqueID

## Configuration 

At this moment, you have to provide in the configuration file :
 - The MAC address of your Bas Station in "B" mode
 - The unique ID of your Bas Station in "B" mode (writtent on the back of the basestation)

It is possible to scan and find this data, may be included in new releases ?

## Usage

After having changed the values in configuration.ini file, just run the Python script, it will :
 - Search if Headset is connected
 - Wake Up the Base B - Set default timeout (60 seconds)
 - Then change the timeout to 30 seconds
 - Ping Base B each 15 seconds

## Credits

Credits to https://github.com/risa2000/lhctrl/ for the wonderful work, which has been a great inspiration
