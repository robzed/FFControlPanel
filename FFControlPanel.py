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
from Remote_End_Analyser.flashforth_interpreter import FlashForth_interpreter

print(platform.python_version())

# Bleak/Asyncio and tkInter
# https://stackoverflow.com/questions/47895765/use-asyncio-and-tkinter-or-another-gui-lib-together-without-freezing-the-gui
# choices are either to run bleak/asyncio in a seperate thread (or process) or 
# call tkinter root.update() repeatedly (instead of calling root.mainloop).
#
# Since we might be using serial ports (or serial ports over classic Bluetooth) 
# with this code, we try to abstract the connection. 


class Main:

    # ==================================================
    # Command system
    # ==================================================
    def __init__(self):
        TERM_ONLY = True        # terminal only
        self.local_commands = {
            # command     function,  term only, description
            b"#help"  :  ( self.help,      TERM_ONLY, "Show help"),
            b"#require": ( self.require,   False,     "upload, ignore if uploaded again via dictionary check"),
            b"#r" :      ( self.require,   TERM_ONLY, "shortcut for #require on terminal"),
            b"#include": ( self.include,   False,     "upload file to target"),
            b"#i" :      ( self.include,   TERM_ONLY, "shortcut for #include on terminal"),
            b"#python" : ( self.do_python, False,     "run the rest of the line in Python"),
            b"#edit" :   ( None,           False,     "edit file (error file or named)"),
            b"#e" :      ( None,           TERM_ONLY, "shortcut for #edit on terminal"),
            b"#ifdef" :  ( None,           False,     "if name (follows command) is found in target, execute rest of line as a terminal line"),
            b"#ifndef" : ( None,           False,     "if name (follows command) is not found in target, execute rest of line as a terminal line"),
            b"#ls" :     ( self.ls,        TERM_ONLY, "list current directory"),
            b"#cd" :     ( self.cd,        TERM_ONLY, "change current directory"),
            }
    # @todo:
    # TAB aborts upload (if in compile mode [ enter)
    # [Backspace] [Left] [Right] [Home] [End] [UP] [Down] [Shift]+[TAB] clears the command line
    # TAB command completion using command history
    #
    # Add 0x17 breaks file send 
    #
    #=============================================================================
    # ff-shell compatability 
    # "#help filter   ": "Print filtered help text",
    # "#warm          ": "Send ctrl-o to FF",
    # "#esc           ": "Make a warm start and disable the turnkey",
    # "#cat file      ": "Show the file contents",
    # "#history filter": "Show the history"
    #=============================================================================
        
        self.current_running_mode = None
    
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

    def disable_input_terminal(self):
        self.term.disable_input_terminal()
    
    def enable_input_terminal(self):
        self.term.enable_input_terminal()
    
    
    def include(self, command, arg):
        self.disable_input_terminal()
        name = arg.strip()
        
        # check if the name is empty
        if len(name) == 0:
            self.include_error = True
            return 
        
        # check if file exists
        try:
            file = open(name, 'r')
        except OSError:
            self.include_error = True
            return

        # Read lines from file.
        # We could use a loop with readline - but I think 
        # the host will have plenty of memory to cache all files.
        lines = file.readlines()
        file.close()

        # run through standard command parser
        for line in lines:
            # @TODO: ignore lines starting with \
            self.term.append(" | %s\n" % os.getcwd())
            if self.known_command(line, False):
                if self.include_error:
                    break
            elif self.connection.connected:
                self.connection.send_data(line)
                #@TODO: Check for errors
                
            # @TODO: We need to defer this processing rather than freeze GUI

    def _include_processing(self):
        pass


    def require(self, command, arg):
        print("No debugged")
        items = arg.split(maxsplit=1)
        word = items[0].strip()
        if len(word) > 0 and self.interpreter.exists_on_target(word):
            self.current_running_mode = self._require_processing
        else:
            self.include_error = True
            
    def _require_processing(self):
        # @TODO: command timeout here
        # or cancel if received reply exists reply
        # or include if didn't receive a reply
        # add a NO-OP word with that filename if no filename exists
        pass
        
    def run_local_command(self, command, payload, tmode = True):
        (func, term_only, _) = self.local_commands[command]
        if func is None: return 
        if not tmode and term_only: return
        func(command, payload)
    
    def known_command(self, data, tmode = True):
        items = data.split(maxsplit=1) 
        if len(items):
            if len(items) >= 2:
                command, payload = items
            else:
                command = items[0]
                payload = ""
            if command in self.local_commands:
                self.run_local_command(command, payload, tmode)
                return True
        return False

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
        self.connection = connection
        connection.open()
        self.interpreter = FlashForth_interpreter(connection)
        
        def send_data_handler(data):
            self.include_error = False
            
            if self.known_command(data):
                # after command is run, make sure input terminal is enabled
                self.enable_input_terminal()
            elif connection.connected:
                #print(">>>>", repr(data))
                connection.send_data(data)

        self.term.set_data_ready_callback(send_data_handler)
    
        def rx_glue():
            data = connection.rx_data()
            while data is not None:
                # @TODO: Consider whether splitlines would be better and interpret lines?
                str_data = data.decode('utf-8').replace('\r\n', '\n')
                self.term.append(str_data)
                self.interpreter.rx_data(data)
                
                if self.current_running_mode is not None:
                    self.current_running_mode()
                data = connection.rx_data()

            self.root.after(50, rx_glue)
            self.term.set_status(connection.status())
        self.root.after(50, rx_glue)
        self.root.mainloop()
            
        print("Finished")
    
if __name__ == '__main__':
    Main().main()
    
    