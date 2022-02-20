'''
Created on 13 Feb 2022

@author: Rob Probin
'''

from CP_Lib.BLE_Serial_interface import BLE_Serial
import time

# Bleak/Asyncio and tkInter
# https://stackoverflow.com/questions/47895765/use-asyncio-and-tkinter-or-another-gui-lib-together-without-freezing-the-gui
# choices are either to run bleak/asyncio in a seperate thread (or process) or 
# call tkinter root.update() repeatedly (instead of calling root.mainloop).
#
# Since we might be using serial ports (or serial ports over classic Bluetooth) 
# with this code, I figured running the 

def main():
    connection = BLE_Serial()
    connection.start_task()
    
    print("Waiting for thread")
    time.sleep(30)
    print("Finished")
    
if __name__ == '__main__':
    main()
    
    