'''
    Arducam programable zoom-lens controller.
    Copyright (c) 2019-4 Arducam <http://www.arducam.com>.
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
    DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
    OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
    OR OTHER DEALINGS IN THE SOFTWARE.
'''

import sys
import time
import os



class Focuser:
    bus = None
    CHIP_I2C_ADDR = 0x0C
    BUSY_REG_ADDR = 0x04
    def __init__(self, bus):
        print("Mock Init")
        
    def read(self,chip_addr,reg_addr):
        return 8
# return self.focus_value

    def write(self,chip_addr,reg_addr,value):
        return 0

    OPT_FOCUS   = "focus"
    OPT_ZOOM    = "zoom"
    OPT_MOTOR_X = "motor_x"
    OPT_MOTOR_Y = "motor_y"
    OPT_IRCUT   = "ircut"

    opts = {
        # OPT_FOCUS : {
        OPT_ZOOM  : {
            "REG_ADDR" : 0x01,
            "MIN_VALUE": 0,
            "MAX_VALUE": 20000,
            "DEF_VALUE": 0,
            "RESET_ADDR": 0x01 + 0x0A,
        },
        # OPT_ZOOM  : {
        OPT_FOCUS : {    
            "REG_ADDR" : 0x00,
            "MIN_VALUE" : 0,
            "MAX_VALUE": 20000,
            "DEF_VALUE": 0,
            "RESET_ADDR": 0x00 + 0x0A,
        },
        OPT_MOTOR_X : {
            "REG_ADDR" : 0x05,
            "MIN_VALUE" : 0,
            "MAX_VALUE": 180,
            "RESET_ADDR": None,
        },
        OPT_MOTOR_Y : {
            "REG_ADDR" : 0x06,
            "MIN_VALUE" : 0,
            "MAX_VALUE": 180,
            "RESET_ADDR": None,
        },
        OPT_IRCUT : {
            "REG_ADDR" : 0x0C, 
            "MIN_VALUE" : 0,
            "MAX_VALUE": 0x01,   
            "RESET_ADDR": None,
        }
    }

    def isBusy(self):
        return False

    def waitingForFree(self):
        print("Mock Waiting")

    def reset(self,opt,flag = 1):
        print("Mock Reset")

    def get(self,opt,flag = 0):
            return self.opts[opt]["REG_ADDR"]

    def set(self,opt,value,flag = 1):
        if not opt in self.opts:
            return False
        print("Mock Set",value)
        return True

pass 

def test():
    focuser = Focuser(7)
    focuser.set(Focuser.OPT_FOCUS, 0)
    time.sleep(3)
    focuser.set(Focuser.OPT_FOCUS, 0)
    time.sleep(3)
    focuser.reset(Focuser.OPT_FOCUS)

if __name__ == "__main__":
    test()