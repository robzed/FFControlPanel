'''
Created on 13 Feb 2022

@author: Rob Probin
'''

import threading
import asyncio
from collections import deque
from bleak import BleakScanner, BleakClient
from bleak.backends.scanner import AdvertisementData
from bleak.backends.device import BLEDevice

# https://github.com/hbldh/bleak/tree/develop/examples
# run in executor: https://stackoverflow.com/questions/55027940/is-run-in-executor-optimized-for-running-in-a-loop-with-coroutines
# https://github.com/hbldh/bleak/blob/develop/examples/get_services.py
# https://bleak.readthedocs.io/en/latest/scanning.html
# https://github.com/hbldh/bleak/issues/720
# https://stackoverflow.com/questions/69661809/no-name-or-address-cbcentralmanager-no-longer-working-on-macos-12

DEBUG_BLE = False
DEBUG_SHOW_DATA = False

class BLE_Serial(object):
    '''
    A BLE interface that acts as a serial port for BLE devices.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
        
        # Make these into parameters to the function
        self.wanted_name = "Ble-Nano"
        #self.wanted_address = ( "E6:8C:5E:4D:AC:99" )   # someone elses random address, used on Linux and Windows 
        self.wanted_address = "FE99B89F-C32B-FBAD-A991-54D255F231DE"   # mac OS uses UUID not hardware address. This is the BLE Nano

        
        # a parameter should select the type device (and therefore characteristics).
        self.make_BLE_Nano()
        
        # since we expect only one reader or writer, then deque is thread safe enough
        self.send_queue = deque()
        self.receive_queue = deque()
        self.found_device = None
        self.connected = False
        self.terminate = False
        self.data_send = False

    def make_Nordic_Uart_Service(self):
        self.UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
        self.UART_TX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e" #Nordic NUS characteristic for TX
        self.UART_RX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e" #Nordic NUS characteristic for RX

    def make_BLE_Nano(self):
        # Service = FFE0, Characteristic FFE1
        self.UART_SERVICE_UUID = "FFE0"
        self.UART_TX_UUID = "FFE1"
        self.UART_RX_UUID = "FFE1"
        self.UART_RX_UUID_128 = "0000ffe1-0000-1000-8000-00805f9b34fb"
        self.UART_TX_UUID_128 = "0000ffe1-0000-1000-8000-00805f9b34fb"

    def make_HM19(self):
        pass
    
    def make_HM10(self):
        pass
    
    def _notification_handler(self, sender, data):
        """Simple notification handler which prints the data received."""
        if DEBUG_SHOW_DATA: print("RX {0}: {1}".format(sender, data))
        self.receive_queue.append(data)

    def _device_discovered(self, device: BLEDevice, advertisement_data: AdvertisementData):
        if DEBUG_BLE: print(f"{device.address} RSSI: {device.rssi}, {advertisement_data}")
        if advertisement_data.local_name == self.wanted_name and device.address == self.wanted_address:
            self.found_device = device
            if DEBUG_BLE: print("Found", self.wanted_name)

    async def _run(self):
        if DEBUG_BLE: print("Running BLE controller")
    
        #  mkoderer commented on 30 Dec 2021 on https://github.com/hbldh/bleak/issues/635
        # https://github.com/hbldh/bleak/blob/develop/examples/detection_callback.py
        service_uuids = [ self.UART_SERVICE_UUID ]
        scanner = BleakScanner(service_uuids=service_uuids)
        scanner.register_detection_callback(self._device_discovered)
    
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
    
            # wait for data to be sent from client
            await client.start_notify(self.UART_RX_UUID_128, self._notification_handler)
         
            self.connected = True
            while self.terminate == False: 
     
                # give some time to do other tasks, 50ms = 25x a second
                await asyncio.sleep(0.40)
                while(len(self.send_queue)):
                    data = self.send_queue.popleft()
                    if DEBUG_SHOW_DATA: print("TX:", data)
                    await client.write_gatt_char(self.UART_TX_UUID_128, data, True)

                    #data = await client.read_gatt_char(self.UART_RX_UUID)
                self.data_send = True
                
    def _asyncio_main(self):
        # Python 3.7+
        # https://stackoverflow.com/questions/55590343/asyncio-run-or-run-until-complete
        asyncio.run(self._run())
    
    def open(self):
        self.thread = threading.Thread(target=self._asyncio_main, name="BLE_Serial", daemon=True)
        self.thread.start()
        
    def send_data(self, data):
        if len(data):
            self.data_send = False
            self.send_queue.append(data)

    def rx_data(self):
        try:
            return self.receive_queue.popleft()
        except IndexError:
            return None
