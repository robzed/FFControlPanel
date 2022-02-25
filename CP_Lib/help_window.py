'''
Created on 25 Feb 2022

@author: rob
'''
import tkinter as tk

class HelpWindow(object):
    '''
    Display a help window
    '''


    def __init__(self, root, commands):
        '''
        Constructor
        '''
        self.window = tk.Toplevel(root)
        help_list = []
        for command in commands:
            func, termonly, helptext = commands[command]
            auxtext = "(Terminal only)" if termonly else ""
            auxtext2 = "[NOT IMPLEMENTED YET]" if func is None else ""
            help_list.append(command.decode('utf8') + "\t" + helptext + " " + auxtext + " " + auxtext2)
        
        label_text = "\n".join(help_list)
        label= tk.Label(self.window, text= label_text, font= ('Aerial', 17), justify=tk.LEFT)
        label.pack(pady=20)
        self.window.deiconify()
        self.window.title("FFControlPanel Help")