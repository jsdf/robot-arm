# Simple demo of of the PCA9685 PWM servo/LED controller library.
# This will move channel 0 from min to max position repeatedly.
# Author: Tony DiCola
# License: Public Domain
from __future__ import division
import time
import re

import json


# Import the PCA9685 module.
import Adafruit_PCA9685




# Uncomment to enable debug output.
# import logging
# logging.basicConfig(level=logging.DEBUG)

import os
script_dir = os.path.dirname(os.path.realpath(__file__))
initial_positions_file = os.path.join(script_dir, 'initialpositions.jsonc')
runtime_positions_file = os.path.join(script_dir, 'positions.json')


# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# Configure min and max servo pulse lengths
# servo_min = 150  # Min pulse length out of 4096
# servo_max = 600  # Max pulse length out of 4096
servo_min = 200  # Min pulse length out of 4096
servo_max = 530  # Max pulse length out of 4096
servo_mid = int(servo_min + (servo_max - servo_min) / 2)


# Helper function to make setting a servo pulse width simpler.
def set_servo_pulse(channel, pulse):
    pulse_length = 1000000    # 1,000,000 us per second
    pulse_length //= 50       # 50 Hz
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096     # 12 bits of resolution
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)

# Set frequency to 50hz, good for servos.
pwm.set_pwm_freq(50)

pin_names_pins = {
  "15": 15,
  "14": 14,
  "13": 13,
  "11": 11,
  "10": 10,
  "8": 8,
  "7": 7,
  "6": 6,
}


pin_names_max_speed = {
  "7":1, # rotate base (mid=300)
  "8":1, # arm bottom joint  (mid=300)
  "10":1, # arm middle joint (mid=320)
  "11":1, # tilt claw (min=150, mid=300, max=500)
  "13":5, # rotate claw (mid=300)
  "15":5  # close claw (mid=300)
}

"""
default positions: 
  "7": 300,
  "8": 300,
  "10": 320,
  "11": 300,
  "13": 300,
  "15": 300
"""

# reset_pos_at_init = runtime_positions_file
reset_pos_at_init = initial_positions_file

def read_positions(source_file):
    with open(source_file, 'r') as content_file:
        content = content_file.read()
    return json.loads(re.sub(r'\/\/.*\n','',content))

current_positions = read_positions(reset_pos_at_init)


for pin_name in current_positions:
    current_pos = current_positions[pin_name]
    to_pos = current_positions[pin_name]
    pin = pin_names_pins[pin_name]
    print('moving {0} from {1} to {2}'.format(pin, current_pos, to_pos))
    current_pos = to_pos
    pwm.set_pwm(pin, 0, current_pos)
    current_positions[pin_name] = current_pos

print('Moving servo on channel 0, press Ctrl-C to quit...')
while True:
    # Move servo on channel 15 between extremes.
    # pwm.set_pwm(15, 0, input("go to val (min=150, max=600): "))
    # time.sleep(2)
    try:
        to_positions = read_positions(runtime_positions_file)
    except:
        continue

    print('moving',to_positions)

    

    needs_move = True
    while needs_move:
        needs_move = False
        for pin_name, to_pos in to_positions.items():
            if current_positions[pin_name] != to_pos:
                needs_move = True
        if needs_move:
            for pin_name in to_positions:
                current_pos = current_positions[pin_name]
                to_pos = to_positions[pin_name]
                pin = pin_names_pins[pin_name]
                print('moving {0} from {1} to {2}'.format(pin, current_pos, to_pos))
                if current_pos != to_pos:
                    to_move = min( pin_names_max_speed[pin_name], abs(to_pos - current_pos))
                    if current_pos < to_pos:
                        current_pos += to_move
                    else:
                        current_pos -= to_move
                    pwm.set_pwm(pin, 0, current_pos)
                    current_positions[pin_name] = current_pos

        time.sleep(0.001)

    print('done moving')

    time.sleep(1)
    # continue
    # pwm.set_pwm(15, 0, servo_min)
    # time.sleep(1)
    # pwm.set_pwm(15, 0, servo_max)
    # time.sleep(1)
