"""
## =========================================================================== ## 
MIT License
Copyright (c) 2021 Roman Parak
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
## =========================================================================== ## 
Author   : Roman Parak
Email    : Roman.Parak@outlook.com
Github   : https://github.com/rparak
File Name: test_robotiq_gripper.py
## =========================================================================== ## 
"""

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
