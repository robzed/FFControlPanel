'''
Created on 20 Feb 2022

@author: rob
'''

import tkinter as tk


class TerminalWindow():
    '''
    classdocs
    '''


    def __init__(self, window):
        '''
        Constructor
        '''
        self.termWindow = window
        self._callback_function = None

        window.title("FFControlPanel - Terminal")
        

        label_status = tk.Label(window, text = "Terminal")
        label_status.pack(side = tk.TOP)

        self.textw = tk.Text (window, bg='DarkSeaGreen1')
        self.textw.pack(side=tk.TOP, fill=tk.BOTH, expand = True)
        #self.textw.configure(state='disabled')
        self.textw.config(state=tk.DISABLED)

        #buttonExample = tk.Button(window, text = "New Window button")
        #buttonExample.pack()
        
        label2 = tk.Label(window, text = "Enter command and press <return>")
        label2.pack()

        # Colour chart https://i0.wp.com/www.wikipython.com/wp-content/uploads/Color-chart-capture-082321.jpg?w=1904&ssl=1
        self.entry = tk.Entry(window, bg='LemonChiffon2')
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand = True)
        self.entry.bind('<Return>', self._pressed_return)
    
        self.entry.focus_set()
    
    def status(self, status_text):
        self.label_status.config(text="Terminal - " + status_text)

    def set_callback(self, function):
        self._callback_function = function
                
    def _pressed_return(self, _):    # parameter event not used
        text = self.entry.get()
        if self._callback_function is None:
            self.append(text)
        else:
            self._callback_function(text)
            
        self.entry.delete(0, tk.END)
        
    def append(self, text):
        self.textw.config(state=tk.NORMAL)
        self.textw.insert(tk.END, text+'\n')
        self.textw.config(state=tk.DISABLED)
    
    