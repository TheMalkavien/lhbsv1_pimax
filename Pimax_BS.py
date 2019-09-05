#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import time
import logging
import binascii
import asyncio
import argparse
import configparser
import sys

logging.basicConfig(level=logging.DEBUG)

import pywinusb.hid as hid
from bleak import BleakClient

PIMAX_USB_VENDOR_ID = 0
SLEEP_TIME_SEC_USB_FIND = 5
DEBUG_BYPASS_USB = True

BS_CMD_BLE_ID = "0000cb01-0000-1000-8000-00805f9b34fb"
BS_CMD_ID_WAKEUP_NO_TIMEOUT = 0x1200
BS_CMD_ID_WAKEUP_DEFAULT_TIMEOUT = 0x1201
BS_CMD_ID_WAKEUP_TIMEOUT = 0x1202
BS_DEFAULT_ID = 0xffffffff
BS_TIMEOUT_IN_SEC = 30

# TO BE SCANNED AND/OR passed by cmdargs
BS_MAC_ADDRESS = "XX:XX:XX:XX:XX:XX"
BS_UNIQUE_ID = 0

def find_pimax_headset():
    all_devices = hid.HidDeviceFilter(vendor_id = PIMAX_USB_VENDOR_ID).get_devices()

    if not all_devices:
        logging.debug("USB NOT FOUND")
        return False
    else:
       for device in all_devices:
            try:
                device.open()
                logging.debug("USB FOUND : " + str(device))
            finally:
                device.close()
    return True


def build_bs_ble_cmd(cmd_id, cmd_timeout, cmd_bs_id):
    ba = bytearray()
    ba += cmd_id.to_bytes(2, byteorder='big')
    ba += (cmd_timeout).to_bytes(2, byteorder='big')
    ba += cmd_bs_id.to_bytes(4, byteorder='little')
    ba += (0).to_bytes(12, byteorder='big')
    return ba

async def wake_up_bs(bs_mac_address, loop):
    try:
        async with BleakClient(bs_mac_address, loop=loop) as client:
            cmd = build_bs_ble_cmd(BS_CMD_ID_WAKEUP_DEFAULT_TIMEOUT, 0, BS_DEFAULT_ID)
            logging.debug("WAKE UP CMD : " + str(binascii.hexlify(cmd)))
            await client.write_gatt_char(BS_CMD_BLE_ID, cmd)
    except:
        logging.debug("ERROR DURING BLE : " + str(sys.exc_info()[0]))
        return False
    return True

async def ping_bs(bs_mac_address, bs_unique_id, loop):
    try:
        async with BleakClient(bs_mac_address, loop=loop) as client:
            cmd = build_bs_ble_cmd(BS_CMD_ID_WAKEUP_TIMEOUT, BS_TIMEOUT_IN_SEC, bs_unique_id)
            logging.debug("PING CMD : " + str(binascii.hexlify(cmd)))
            await client.write_gatt_char(BS_CMD_BLE_ID, cmd)
    except:
        logging.debug("ERROR DURING BLE : " + str(sys.exc_info()[0]))
        return False
    return True


def is_pimax_headset_present():
    if not DEBUG_BYPASS_USB:
        if not find_pimax_headset():
            logging.info("Pimax Headset not found.")
            time.sleep(SLEEP_TIME_SEC_USB_FIND)
            return False
    return True

def load_configuration():
    config = configparser.ConfigParser()
    config.read('configuration.ini')
    logging.debug("CONFIG : " + config['BaseStation']['B_MAC_ADDRESS'])
    logging.debug("CONFIG : " + config['BaseStation']['B_UNIQUE_ID'])
    logging.debug("CONFIG : " + config['HeadSet']['USB_VENDOR_ID'])
    global BS_MAC_ADDRESS, BS_UNIQUE_ID, PIMAX_USB_VENDOR_ID
    BS_MAC_ADDRESS = config['BaseStation']['B_MAC_ADDRESS']
    BS_UNIQUE_ID = int(config['BaseStation']['B_UNIQUE_ID'], 0)
    PIMAX_USB_VENDOR_ID = int(config['HeadSet']['USB_VENDOR_ID'], 0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug_ignore_usb", help="Disable the USB search for headset", action="store_true")

    args = parser.parse_args()
    DEBUG_BYPASS_USB = args.debug_ignore_usb

    load_configuration()
    
    while True:
        # Step 1 : find Pimax Headset
        if not is_pimax_headset_present():
            continue
        logging.info("Step 1 : Headset is present.")
        loop = asyncio.get_event_loop()

        # Step 2 : wake up and set default timeout
        if not loop.run_until_complete(wake_up_bs(BS_MAC_ADDRESS, loop)):
            logging.debug("Error in step 2")
            time.sleep(5)
            continue
        logging.info("Step 2 : BS is waking up.... waiting 20 seconds")
        # must wait some time to be fully initialized
        time.sleep(20)

        if not is_pimax_headset_present():
            continue

        logging.info("Step 3 : Enter ping loop.")
        while True:
            if not loop.run_until_complete(ping_bs(BS_MAC_ADDRESS, BS_UNIQUE_ID, loop)):
                logging.debug("Error in step 3")
                break
            time.sleep(BS_TIMEOUT_IN_SEC/2)
            if not is_pimax_headset_present():
                break
        time.sleep(5)