'''
Created on 20 Feb 2022

@author: rob
'''

import tkinter as tk


class TerminalWindow():
    '''
    classdocs
    '''


    def __init__(self, window, EOL='\n\r'):
        '''
        Constructor
        '''
        self.termWindow = window
        self._callback_function = None
        self.EOL = EOL
        
        window.title("FFControlPanel - Terminal")
        

        self.label_status = tk.Label(window, text = "Terminal")
        self.label_status.pack(side = tk.TOP)

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
        self.old_status = None

    def disable_input_terminal(self):
        self.entry.config(state='disabled') # OR entry['state'] = 'disabled'
    
    def enable_input_terminal(self):
        self.entry.config(state='normal')
    
    def set_status(self, status_text):
        if self.old_status != status_text:
            self.label_status.config(text="Terminal - " + status_text)

    def set_data_ready_callback(self, function):
        self._callback_function = function
    
    def _pressed_return(self, _):    # parameter event not used
        texts = self.entry.get().splitlines()
        for text in texts:
            text += self.EOL
            if self._callback_function is None:
                self.append(text)
            else:
                self._callback_function(text.encode('utf-8'))
            
        self.entry.delete(0, tk.END)
        
    def append(self, text):
        # @TODO: Make control characters visibie (e.g. 0-31 except NL, LF)
        self.textw.config(state=tk.NORMAL)
        self.textw.insert(tk.END, text)
        self.textw.see(tk.END)
        self.textw.config(state=tk.DISABLED)
    
    