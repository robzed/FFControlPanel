'''
Created on 20 Feb 2022

@author: Rob Probin
'''

import serial

class BasicSerial(object):
    def __init__(self):
        pass
    
    def open(self):
        pass
    
    def send_data(self, data):
        #self.send_queue.append(data)
        pass
    
    def rx_data(self):
        return b""
        #try:
        #    return self.receive_queue.popleft()
        #except IndexError:
        #    return b""
