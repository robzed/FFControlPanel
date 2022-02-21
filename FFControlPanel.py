'''
Created on 13 Feb 2022

@author: Rob Probin

LICENSE: MIT license
'''

from CP_Lib.BLE_Serial_interface import BLE_Serial
from CP_Lib.terminal_window import TerminalWindow

import time
import tkinter as tk
import platform
print(platform.python_version())

# Bleak/Asyncio and tkInter
# https://stackoverflow.com/questions/47895765/use-asyncio-and-tkinter-or-another-gui-lib-together-without-freezing-the-gui
# choices are either to run bleak/asyncio in a seperate thread (or process) or 
# call tkinter root.update() repeatedly (instead of calling root.mainloop).
#
# Since we might be using serial ports (or serial ports over classic Bluetooth) 
# with this code, I figured running the 


#def create_terminal_window():
#    global term
#    global root
#    term = TerminalWindow(tk.Toplevel(root))

    
def main():
    global root
    root = tk.Tk()
    term = TerminalWindow(root)
    root.eval('tk::PlaceWindow . center')
    
    #start_button = tk.Button(root, 
    #              text="Start Connection",
    #              command=create_terminal_window)
    #start_button.pack(pady = 5, padx = 5)
    #root.geometry("400x100")
    #root.title("FFControlPanel - Select Connection")
    
    connection = BLE_Serial()
    connection.open()
    term.set_data_ready_callback(connection.send_data)

    def rx_glue():
        data = connection.rx_data()
        if data is not None:
            term.append(data.decode('utf-8').replace('\r\n', '\n'))
        root.after(50, rx_glue)
        
    root.after(50, rx_glue)
    root.mainloop()
        
    print("Finished")
    
if __name__ == '__main__':
    main()
    
    