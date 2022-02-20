'''
Created on 13 Feb 2022

@author: rob
'''

import threading
import asyncio
from collections import deque
from bleak import BleakScanner, BleakClient
from bleak.backends.scanner import AdvertisementData
from bleak.backends.device import BLEDevice
from bleak import discover
import platform
from bleak.uuids import uuid16_dict, uuid128_dict

# https://github.com/hbldh/bleak/tree/develop/examples
# run in executor: https://stackoverflow.com/questions/55027940/is-run-in-executor-optimized-for-running-in-a-loop-with-coroutines
# https://github.com/hbldh/bleak/blob/develop/examples/get_services.py
# https://bleak.readthedocs.io/en/latest/scanning.html
# https://github.com/hbldh/bleak/issues/720
# https://stackoverflow.com/questions/69661809/no-name-or-address-cbcentralmanager-no-longer-working-on-macos-12

DEBUG_BLE = False


class BLE_Serial(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        #self.address = ( "E6:8C:5E:4D:AC:99" )   # someone elses random address
        self.address = ( "FE99B89F-C32B-FBAD-A991-54D255F231DE" )   # mac OS uses UUID not hardware address. This is the BLE Nano
        self.make_BLE_Nano()
        
        
        # since we expect only one reader or writer, then deque is thread safe enough
        self.send_queue = deque()
        self.receive_queue = deque()
        self.found_device = None

    def make_Nordic_Uart_Service(self):
        self.UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
        self.UART_TX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e" #Nordic NUS characteristic for TX
        self.UART_RX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e" #Nordic NUS characteristic for RX
        
    def make_BLE_Nano(self):
        # Service = FFE0, Characteristic FFE1
        self.UART_SERVICE_UUID = "FFE0"
        self.UART_TX_UUID = "FFE1"
        self.UART_RX_UUID = "FFE1"
        self.wanted_name = "Ble-Nano"

    def make_HM19(self):
        pass
    
    def make_HM10(self):
        pass
    
    def _notification_handler(self, sender, data):
        """Simple notification handler which prints the data received."""
        print("{0}: {1}".format(sender, data))
        self.receive_queue.append(data)

    def simple_callback(self, device: BLEDevice, advertisement_data: AdvertisementData):
        if DEBUG_BLE: print(f"{device.address} RSSI: {device.rssi}, {advertisement_data}")
        if advertisement_data.local_name == self.wanted_name:
            self.found_device = device
            if DEBUG_BLE: print("Found", self.wanted_name)

    async def scan_for_all(self):
        # broken on MacOSX 12.0, 12.1 ,12.2. Fixed on 12.3, apparently
        print("start")
        devices = await discover()
        for d in devices:
            print(d)
        print("end")
        

    async def _run(self):
        if DEBUG_BLE: print("Running BLE controller")

        
        #device = await BleakScanner.find_device_by_filter(
        #    lambda d, ad: d.name and d.name.lower() == wanted_name.lower()
        #    )
        #print("by device name", device)
        #device = await BleakScanner.find_device_by_address(self.address, timeout=20.0)
        #print("by address", device)
    #===========================================================================
    #     def match_uuid(device: BLEDevice, adv: AdvertisementData):
    #         
    #         print("Local name", adv.local_name, adv.manufacturer_data, adv.platform_data, adv.service_data, adv.service_uuids)
    #         # This assumes that the device includes the UART service UUID in the
    #         # advertising data. This test may need to be adjusted depending on the
    #         # actual advertising data supplied by the device.
    #         if self.UART_SERVICE_UUID.lower() in adv.service_uuids:
    #             return True
    # 
    #         return False
    # 
    #     device = await BleakScanner.find_device_by_filter(match_uuid)
    #     print("Device = ", device)
    #===========================================================================

    
        #  mkoderer commented on 30 Dec 2021 on https://github.com/hbldh/bleak/issues/635
        # https://github.com/hbldh/bleak/blob/develop/examples/detection_callback.py
        service_uuids = [ self.UART_SERVICE_UUID ]
        #service_uuids = []
        #mac_ver = platform.mac_ver()[0].split(".")
        if False: # mac_ver[0] and int(mac_ver[0]) >= 12 and not service_uuids:
            # In macOS 12 Monterey the service_uuids need to be specified. As a
            # workaround for this example program, we scan for all known UUIDs to
            # increse the chance of at least something showing up. However, in a
            # "real" program, only the device-specific advertised UUID should be
            # used. Devices that don't advertize at least one service UUID cannot
            # currently be detected.
            print(
                "Scanning using all known service UUIDs to work around a macOS 12 bug. Some devices may not be detected. Please report this to Apple using the Feedback Assistant app and reference <https://github.com/hbldh/bleak/issues/635>."
            )
            for item in uuid16_dict:
                print(item)
                service_uuids.append("{0:04x}".format(item))
                #print(service_uuids)
            service_uuids.extend(uuid128_dict.keys())
        #print(service_uuids)
        scanner = BleakScanner(service_uuids=service_uuids)
        scanner.register_detection_callback(self.simple_callback)
    
        while self.found_device is None:
            await scanner.start()
            # wait for 5 seconds total
            for _ in range(100):
                await asyncio.sleep(0.05)
                if self.found_device is not None:
                    break
            await scanner.stop()
    
        print("Found", self.wanted_name, "at", self.found_device.address)
            
        # Get services 
        # https://github.com/hbldh/bleak/blob/develop/examples/get_services.py
        async with BleakClient(self.found_device) as client:
 
 
            svcs = await client.get_services()
            print("Services:")
            for service in svcs:
                print(service)

#            return
        
            # wait for BLE client to be connected
            x = client.is_connected
            print("Connected: {0}".format(x))
     
            # wait for data to be sent from client
            await client.start_notify("0000ffe1-0000-1000-8000-00805f9b34fb", self._notification_handler)
         
            while True: 
     
                # give some time to do other tasks, 50ms = 25x a second
                await asyncio.sleep(0.40)
 
                while(len(self.send_queue)):
                    data = self.send_queue.popleft()
                    await client.write_gatt_char(self.UART_TX_UUID, data)
     
                    data = await client.read_gatt_char(self.UART_RX_UUID)
    
    def _asyncio_main(self):
        #loop = asyncio.get_event_loop()
        #loop.run_until_complete(self._run(self.address, loop))
        # Python 3.7+
        # https://stackoverflow.com/questions/55590343/asyncio-run-or-run-until-complete
        asyncio.run(self._run())
    
    def start_task(self):
        self.thread = threading.Thread(target=self._asyncio_main, name="BLE_Serial", daemon=True)
        self.thread.start()
        
    def send_data(self, data):
        self.send_queue.append(data)
    
    def rx_data(self):
        try:
            return self.receive_queue.popleft()
        except IndexError:
            return b""
