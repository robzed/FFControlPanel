'''
Created on 13 Feb 2022

@author: Rob Probin

LICENSE: MIT license
'''

from CP_Lib.BLE_Serial_interface import BLE_Serial
from CP_Lib.terminal_window import TerminalWindow
import tkinter as tk
import platform
from CP_Lib.help_window import HelpWindow
import os

print(platform.python_version())

# Bleak/Asyncio and tkInter
# https://stackoverflow.com/questions/47895765/use-asyncio-and-tkinter-or-another-gui-lib-together-without-freezing-the-gui
# choices are either to run bleak/asyncio in a seperate thread (or process) or 
# call tkinter root.update() repeatedly (instead of calling root.mainloop).
#
# Since we might be using serial ports (or serial ports over classic Bluetooth) 
# with this code, I figured running the 

class Main:

    # ==================================================
    # Command system
    # ==================================================
    def __init__(self):
        TERM_ONLY = True        # terminal only
        self.local_commands = {
            # command     function,  term only, description
            b"#help"  :  ( self.help,      TERM_ONLY, "Show help"),
            b"#require": ( None,           False,     "upload, ignore if uploaded again via dictionary check"),
            b"#r" :      ( None,           TERM_ONLY, "shortcut for #require on terminal"),
            b"#include": ( None,           False,     "upload file to target"),
            b"#i" :      ( None,           TERM_ONLY, "shortcut for #include on terminal"),
            b"#python" : ( self.do_python, False,     "run the rest of the line in Python"),
            b"#edit" :   ( None,           False,     "edit file (error file or named)"),
            b"#e" :      ( None,           TERM_ONLY, "shortcut for #edit on terminal"),
            b"#ifdef" :  ( None,           False,     "if name (follows command) is found in target, execute rest of line as a terminal line"),
            b"#ifndef" : ( None,           False,     "if name (follows command) is not found in target, execute rest of line as a terminal line"),
            b"#ls" :     ( self.ls,        TERM_ONLY, "list current directory"),
            b"#cd" :     ( self.cd,        TERM_ONLY, "change current directory"),
            }
    # todo:
    # TAB aborts upload (if in compile mode [ enter)
    # [Backspace] [Left] [Right] [Home] [End] [UP] [Down] [Shift]+[TAB] clears the command line
    # TAB command completion using command history
    
    def do_python(self, _, command):
        try:
            expr = eval(command)
            if expr is not None:
                self.term.append(repr(expr))
        except SyntaxError:
            self.term.append("#python: Syntax Error\n")

    def cd(self, _, path):
        if path.strip() == "":
            self.term.append("#cd: %s \n" % os.getcwd())
            return
        try:
            os.chdir(path.rstrip())
            self.term.append("#cd: %s\n" % os.getcwd())
        except FileNotFoundError:
            self.term.append("#cd: Folder not found\n")
            
    def ls(self, cmd, arg):
        self.term.append("#ls: %s\n" % os.getcwd())
        dir_list = os.listdir(".")
        for dtext in dir_list:
            self.term.append('  | '+dtext+'\n')

    def help(self, command, _):
        self.help_window = HelpWindow(self.root, self.local_commands)


    def run_local_command(self, command, payload, tmode = True):
        (func, term_only, _) = self.local_commands[command]
        if func is None: return 
        if not tmode and term_only: return
        func(command, payload)
    
    # ==================================================
    # Main function
    # ==================================================

    def main(self):
        self.root = tk.Tk()
        self.term = TerminalWindow(self.root)
        self.root.eval('tk::PlaceWindow . center')
        
        #start_button = tk.Button(self.root, 
        #              text="Start Connection",
        #              command=create_terminal_window)
        #start_button.pack(pady = 5, padx = 5)
        #self.root.geometry("400x100")
        #self.root.title("FFControlPanel - Select Connection")
        
        connection = BLE_Serial()
        connection.open()
    
        def send_data_handler(data):
            items = data.split(maxsplit=1) 
            if len(items):
                if len(items) >= 2:
                    command, payload = items
                else:
                    command = items[0]
                    payload = ""
                if command in self.local_commands:
                    self.run_local_command(command, payload)
                    return
            if connection.connected:
                connection.send_data(data)
            
        self.term.set_data_ready_callback(send_data_handler)
    
        def rx_glue():
            data = connection.rx_data()
            if data is not None:
                self.term.append(data.decode('utf-8').replace('\r\n', '\n'))
            self.root.after(50, rx_glue)
            self.term.set_status(connection.status())
            
        self.root.after(50, rx_glue)
        self.root.mainloop()
            
        print("Finished")
    
if __name__ == '__main__':
    Main().main()
    
    