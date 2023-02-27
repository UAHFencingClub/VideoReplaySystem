from Focuser import Focuser
from gpiozero import Servo

class CameraController:
    def __init__(self):
        i2c_bus = 1
        self.focuser = Focuser(i2c_bus)

        servo_step = 0.025

        servo_x = Servo(16)
        servo_y = Servo(20)

        self.motor_elements = {
            "motor_x" : {
                "MIN_VALUE" : -1,
                "MAX_VALUE" : 1,
                "DEF_VALUE" : 0,
                "STEP"      : servo_step,
                "SERVO"     : servo_x
            },
            "motor_y" : {
                "MIN_VALUE" : -1,
                "MAX_VALUE" : 1,
                "DEF_VALUE" : 0,
                "STEP"      : servo_step,
                "SERVO"     : servo_y
            }
        }

        self.focuser.opts.update(self.motor_elements)
        self.control_elements = self.focuser.opts

    def set(self, element, value):
        if element in self.motor_elements.keys():
            self.motor_elements[element]["SERVO"].value = value
        else:
            self.focuser.set(element, value)
        return True

    def get(self,element):
        if element in self.motor_elements.keys():
            return self.motor_elements[element]["SERVO"].value
        else:
            return self.focuser.get(element)
            

        