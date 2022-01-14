# System (Default)
import sys
# RTDE Control interface (Universal Robots) [pip install ur-rtde]
import rtde_control
# Numpy (Array computing) [pip3 install numpy]
import numpy as np

"""
Note:
    UR Polyscope Version:
        CB Series: 3.15.4.106291
        E-Series: 5.11.4.108353
    IP Address:
        Simulation: 192.168.230.132
        Real      : 192.168.10.122
"""

# Initialization Cuboid Data
#   Center Position
#CENTER_POSITION = [0.0, -600.0, 500.0]
CENTER_POSITION = [0.0, -700.0, 515.0]
#   Size
#CUBOID_SIZE = [800.0, 400.0, 300.0]
CUBOID_SIZE = [760.0, 400.0, 200.0]
#   Vertices
CUBOID_VERTICES = [[(CENTER_POSITION[0] - CUBOID_SIZE[0]/2) + CUBOID_SIZE[0], (CENTER_POSITION[1] - CUBOID_SIZE[1]/2)                 , (CENTER_POSITION[2] - CUBOID_SIZE[2]/2)],
                   [(CENTER_POSITION[0] - CUBOID_SIZE[0]/2) + CUBOID_SIZE[0], (CENTER_POSITION[1] - CUBOID_SIZE[1]/2) + CUBOID_SIZE[1], (CENTER_POSITION[2] - CUBOID_SIZE[2]/2)],
                   [(CENTER_POSITION[0] - CUBOID_SIZE[0]/2)                 , (CENTER_POSITION[1] - CUBOID_SIZE[1]/2) + CUBOID_SIZE[1], (CENTER_POSITION[2] - CUBOID_SIZE[2]/2)],
                   [(CENTER_POSITION[0] - CUBOID_SIZE[0]/2)                 , (CENTER_POSITION[1] - CUBOID_SIZE[1]/2)                 , (CENTER_POSITION[2] - CUBOID_SIZE[2]/2)],
                   [(CENTER_POSITION[0] - CUBOID_SIZE[0]/2) + CUBOID_SIZE[0], (CENTER_POSITION[1] - CUBOID_SIZE[1]/2)                 , (CENTER_POSITION[2] - CUBOID_SIZE[2]/2) + CUBOID_SIZE[2]],
                   [(CENTER_POSITION[0] - CUBOID_SIZE[0]/2) + CUBOID_SIZE[0], (CENTER_POSITION[1] - CUBOID_SIZE[1]/2) + CUBOID_SIZE[1], (CENTER_POSITION[2] - CUBOID_SIZE[2]/2) + CUBOID_SIZE[2]],
                   [(CENTER_POSITION[0] - CUBOID_SIZE[0]/2)                 , (CENTER_POSITION[1] - CUBOID_SIZE[1]/2) + CUBOID_SIZE[1], (CENTER_POSITION[2] - CUBOID_SIZE[2]/2) + CUBOID_SIZE[2]],
                   [(CENTER_POSITION[0] - CUBOID_SIZE[0]/2)                 , (CENTER_POSITION[1] - CUBOID_SIZE[1]/2)                 , (CENTER_POSITION[2] - CUBOID_SIZE[2]/2) + CUBOID_SIZE[2]]]

# Initialization Robot Parameters
VELOCITY     = 0.5
ACCELERATION = 0.5
BLEND = 0.0
#   Orientation
ORIENTATION = [0.0, 3.142, 0.0]

def main():
    # Initialization and connection to the robot
    #   Note: The robot must be in remote control status.
    UR_RTDE_Ctrl = rtde_control.RTDEControlInterface('192.168.230.132')

    # Initialization Target (Position, Orientation, Parameters)
    #   Note: Convert data from mm to m.
    Target_Home = [CENTER_POSITION[0]/1000, CENTER_POSITION[1]/1000, CENTER_POSITION[2]/1000, 
                   ORIENTATION[0], ORIENTATION[1], ORIENTATION[2]]

    # Move to position (Linear Interpolation)
    #   Home Target
    UR_RTDE_Ctrl.moveL(Target_Home, VELOCITY, ACCELERATION)

    cuboid_path = []
    # Testing the workspace of the robot from the created cube
    for _, vertices in enumerate(CUBOID_VERTICES):
        cuboid_path.append([np.round(vertices[0]/1000,5), np.round(vertices[1]/1000,5), np.round(vertices[2]/1000,5), 
                            ORIENTATION[0], ORIENTATION[1], ORIENTATION[2], VELOCITY,ACCELERATION,BLEND])

    # Move to each pose specified in a path.
    #   cuboid_path: Poses that includes acceleration, speed and blend for each position.
    UR_RTDE_Ctrl.moveL(cuboid_path)

    # Move to position (Linear Interpolation)
    #   Home Target
    UR_RTDE_Ctrl.moveL(Target_Home, VELOCITY, ACCELERATION)

    # Stops the script in the controller.
    UR_RTDE_Ctrl.stopScript()

if __name__ == '__main__':
    sys.exit(main())