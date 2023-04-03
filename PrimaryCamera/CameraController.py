from Focuser import Focuser
from gpiozero import Servo

class CameraController:
    def __init__(self):
        i2c_bus = 1
        self.focuser = Focuser(i2c_bus)

        servo_step = 0.01

        servo_x = Servo(16,min_pulse_width=0.0005,max_pulse_width=0.0025)
        servo_y = Servo(20,min_pulse_width=0.0005,max_pulse_width=0.0025)

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
                "DEF_VALUE" : -.8,
                "STEP"      : servo_step,
                "SERVO"     : servo_y
            }
        }

        servo_x.value = self.motor_elements["motor_x"]["DEF_VALUE"]
        servo_y.value = self.motor_elements["motor_y"]["DEF_VALUE"]

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
            

        