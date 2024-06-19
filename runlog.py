# virtualenv nurselog_venv
# source nurselog_venv/bin/activate
# pip3 install Phidget22

from Phidget22.Phidget import *
from Phidget22.Devices.DigitalOutput import *
import time
import signal
import sys
import math
import secrets

# How many LEDs are we using (from 0)
LED_COUNT = 52

# What resolution are we attempting to change the brightness at?
TIME_STEP = 0.05

# How long to go from 0 to max brightness and back?
CYCLE_LENGTH = 3

# After a cycle, what's the max time in seconds to randomly delay one light for?
MAX_DELAY = 20

F_HZ = 1/(2*CYCLE_LENGTH)
MAX_STEP = int(CYCLE_LENGTH / TIME_STEP)
MAX_DELAY_STEP = int(MAX_DELAY / TIME_STEP)


outputs = [None] * LED_COUNT
current_steps = [0] * LED_COUNT

the_wave = [0.0] * MAX_STEP

def precalculate_wave():
    global the_wave
    for i in range(0,MAX_STEP):
        the_wave[i] = math.sin(2*math.pi*F_HZ*i*TIME_STEP)

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    global outputs
    for output in outputs:
        output.close()
    sys.exit(0)

def loop():
    global current_steps
    global outputs
    for i in range(0, LED_COUNT):
        # sin(2*Pi*F*t)
        # F is frequency in Hz of a complete wave, but we use only half
        #print(current_steps)
        if current_steps[i] < 0:
            # Then we're off, just iterate.
            current_steps[i] += 1
        elif current_steps[i] >= MAX_STEP:
            outputs[i].setDutyCycle(0) #Turn it off
            # Then it's time to choose a new random delay
            current_steps[i] = -1 * secrets.randbelow(MAX_DELAY_STEP)
            print(f"Delay [{i}] for {-1 * current_steps[i]*TIME_STEP}s")
        else:
            outputs[i].setDutyCycle(the_wave[current_steps[i]])
            #print(b)
            current_steps[i] += 1
        

def initialize():
    global outputs
    for i in range(0, LED_COUNT):
        outputs[i] = DigitalOutput()
        outputs[i].setChannel(i)
        outputs[i].openWaitForAttachment(5000)
    

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    initialize()
    precalculate_wave()
    print("Beginning.")
    while True:
        loop()
        time.sleep(TIME_STEP)
