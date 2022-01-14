# System (Default)
import sys
# RTDE Control interface (Universal Robots) [pip install ur-rtde]
import rtde_control
#   Note: https://sdurobotics.gitlab.io/ur_rtde/guides/guides.html
from Lib.Robotiq.robotiq_gripper_control import RobotiqGripper

"""
Note:
    UR Polyscope Version:
        CB Series: 3.15.4.106291
        E-Series: 5.11.4.108353
    IP Address:
        Simulation: 192.168.230.132
        Real      : 192.168.10.122
"""

def main():
    try: 
        # Initialization and connection to the robot
        #   Note: The robot must be in remote control status.
        UR_RTDE_Ctrl = rtde_control.RTDEControlInterface('192.168.10.122')

        # Initialization and connection to the robotiq gripper
        ROBOTIQ_Gripper = RobotiqGripper(UR_RTDE_Ctrl)
        #   Activate:
        #ROBOTIQ_Gripper.activate()
        #   Set force and speed:
        #       From 0% to 100%
        ROBOTIQ_Gripper.set_force(100)
        ROBOTIQ_Gripper.set_speed(100)

        # Control of the Gripper.
        #   Method 1: Position
        #ROBOTIQ_Gripper.move(50)
        #   Method 2: Force
        ROBOTIQ_Gripper.open()
        ROBOTIQ_Gripper.close()

    except KeyboardInterrupt:
        # Stop the ur-rtde.
        UR_RTDE_Ctrl.stopScript()
        # Exit from Python.
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())