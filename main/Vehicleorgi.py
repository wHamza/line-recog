import time
from pymavlink import mavutil



class Vehicle:
    def __init__(self, _port, _baud):
        self.vehicle = None
        self.debug_vehicle = True
        self.boot_time = time.time()
        self.connection(_port, _baud)

    def connection(self, _port, _baud):
        """
        This function provides connection pixhawk 
        """
        self.vehicle = mavutil.mavlink_connection(_port, baud=_baud,autoreconnect=True)
        self.vehicle.wait_heartbeat()
        if self.debug_vehicle:
            print("[INFO] Vehicle Connected.")

    def arm_vehicle(self):
        """
        This function provides change into disarm to arm
        """
        self.vehicle.mav.command_long_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            1,0,0,0,0,0,0
        )
        print("Waiting for the vehicle to arm")
        self.vehicle.motors_armed_wait()

        if self.debug_vehicle:
            print("[INFO] Armed")

    def set_mod_vehicle(self, parameter='MANUAL'):
        """
        This method provides changing the flight(drive) mode.Modes are Manual and stabilize
        """
        mode =parameter
        #mode = 'STABILIZE'
        if mode not in self.vehicle.mode_mapping() and self.debug_vehicle:
            print('Unknown mode : {}'.format(mode))
            print('Try:', list(self.vehicle.mode_mapping().keys()))
            exit()

        mode_id = self.vehicle.mode_mapping()[mode]

        self.vehicle.mav.set_mode_send(
            self.vehicle.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id
        )


    def move_right(self, duration):
        """
        Move the vehicle to the right for the specified duration.
        """
        end_time = time.time() + duration
        while time.time() < end_time:
            self.vehicle.mav.manual_control_send(
                self.vehicle.target_system,
                0,  # x-axis (forward/backward)
                500,  # y-axis (left/right)
                0,  # z-axis (up/down)
                0,  # r-axis (rotation)
                0   # buttons (not used)
            )
        self.stop_thruster()

    def move_left(self, duration):
        """
        Move the vehicle to the left for the specified duration.
        """
        end_time = time.time() + duration
        while time.time() < end_time:
            self.vehicle.mav.manual_control_send(
                self.vehicle.target_system,
                0,  # x-axis (forward/backward)
                0,  # y-axis (left/right)
                0,  # z-axis (up/down)
                0,  # r-axis (rotation)
                0   # buttons (not used)
            )
        self.stop_thruster()

    def move_forward(self, duration):
        """
        Move the vehicle forward for the specified duration.
        """
        end_time = time.time() + duration
        while time.time() < end_time:
            self.vehicle.mav.manual_control_send(
                self.vehicle.target_system,
                1000,  # x-axis (forward/backward)
                0,  # y-axis (left/right)
                1500,  # z-axis (up/down)
                0,  # r-axis (rotation)
                0   # buttons (not used)
            )
        self.stop_thruster()

    def move_back(self, duration):
        """
        Move the vehicle backward for the specified duration.
        """
        end_time = time.time() + duration
        while time.time() < end_time:
            self.vehicle.mav.manual_control_send(
                self.vehicle.target_system,
                0,  # x-axis (forward/backward)
                800,  # y-axis (left/right)
                1000,  # z-axis (up/down)
                0,  # r-axis (rotation)
                0   # buttons (not used)
            )
        self.stop_thruster()

    def move_up(self, duration):
        """
        Move the vehicle upward for the specified duration.
        """
        end_time = time.time() + duration
        while time.time() < end_time:
            self.vehicle.mav.manual_control_send(
                self.vehicle.target_system,
                0,  # x-axis (forward/backward)
                0,  # y-axis (left/right)
                500,  # z-axis (up/down)
                0,  # r-axis (rotation)
                0   # buttons (not used)
            )
        self.stop_thruster()

    def move_down(self, duration):
        """
        Move the vehicle downward for the specified duration.
        """
        end_time = time.time() + duration
        while time.time() < end_time:
            self.vehicle.mav.manual_control_send(
                self.vehicle.target_system,
                0,  # x-axis (forward/backward)
                0,  # y-axis (left/right)
                -500,  # z-axis (up/down)
                0,  # r-axis (rotation)
                0   # buttons (not used)
            )
        self.stop_thruster()

    def stop_thruster(self):
        """
        Stops all thrusters.
        """
        self.vehicle.mav.manual_control_send(
            self.vehicle.target_system,
            0,  # x-axis (forward/backward)
            0,  # y-axis (left/right)
            0,  # z-axis (up/down)
            0,  # r-axis (rotation)
            0   # buttons (not used)
        )
    def dur(self):
           """
           This function provides change into disarm to arm
           """
           self.vehicle.mav.command_long_send(
               self.vehicle.target_system,
               self.vehicle.target_component,
               mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
               0,
               0,0,0,0,0,0,0
           )



if __name__ == "__main__":
    arac = Vehicle("COM9", 9600)

    arac.arm_vehicle()
    arac.set_mod_vehicle("MANUAL")
    arac.move_back(120)

