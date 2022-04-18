'''
Created on 19 Mar 2022

@author: Rob Probin
'''
#import time

class FlashForth_interpreter(object):
    '''
    classdocs
    '''


    def __init__(self, serial):
        '''
        Constructor
        '''
        self.serial = serial
        self.waiting_reply = False

    def execute(self, command):
        pass
    
    def exists_on_target(self, word):
        command = "' %s drop\n" % word
        if self.serial.connected:
            self.serial.send_data(command)
            self.waiting_reply = True
            #time.sleep(200)
            #reply = self.serial.rx_data()
            #print(reply)
            return True
        else:
            return False

    def rx_data(self, data):
        if self.waiting_reply:
            print(data)
            self.waiting_reply = False
    