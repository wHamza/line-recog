from pymavlink import mavutil
from Vehicleorgi import *
import time

#port='/dev/ttyACM0'
#baud_rate=57600

sub = Vehicle('COM9',_baud=9600)
sub.vehicle.wait_heartbeat()
sub.arm_vehicle()
sub.set_mod_vehicle()


start_time=time.time()
time.sleep(30)



while True:
    if time.time()-start_time<20:
        sub.move_forward()
    elif 20<time.time()-start_time:
        sub.dur()




roll_angle = pitch_angle = 0

for yaw_angel in range(0, 500, 30):
   sub.set_target_attitude(roll_angle, pitch_angle, yaw_angel)
   time.sleep(1)
sub.move_left(2.5)
time.sleep(0.5)
sub.move_forward(2)
time.sleep(0.5)
sub.move_right(2.5)
time.sleep(0.5)
for yaw_angel in range(0, 500, 30):
   sub.set_target_attitude(roll_angle, pitch_angle, yaw_angel)
   time.sleep(1)
sub.move_right(2.5)
time.sleep(0.5)
sub.move_forward(2)
time.sleep(0.5)
sub.move_left(2.5)
time.sleep(0.5)
for yaw_angel in range(0, 500, 30):
   sub.set_target_attitude(roll_angle, pitch_angle, yaw_angel)
   time.sleep(1)
sub.move_down(2)
sub.move_forward(5)
DEPTH_HOLD = 'ALT_HOLD'
DEPTH_HOLD_MODE = master.mode_mapping()[DEPTH_HOLD]
while not master.wait_heartbeat().custom_mode == DEPTH_HOLD_MODE:
   master.set_mode(DEPTH_HOLD)