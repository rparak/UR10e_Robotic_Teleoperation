# System (Default)
import sys
# Time (Time access and conversions)
import time
# Threading (Thread-based parallelism)
import threading
# Numpy (Array computing) [pip3 install numpy]
import numpy as np
# Lib.Parameters (Main Control Parameters)
import Lib.Parameters as Parameters
# Lib.Signal.Filter (Filters: SMA, BLP)
import Lib.Signal.Filter as Filter
# RTDE Control interface (Universal Robots) [pip install ur-rtde]
import rtde_control
#   Note: https://sdurobotics.gitlab.io/ur_rtde/guides/guides.html
from Lib.Robotiq.robotiq_gripper_control import RobotiqGripper
# ZeroMQ (Universal messaging library) [pip install zmq]
import zmq

"""
Note:
    UR Polyscope Version:
        CB Series: 3.15.4.106291
        E-Series: 5.11.4.108353
    IP Address:
        Simulation: 192.168.230.132
        Real      : 192.168.10.122
"""

# Initialization of Constants (UR10e):
#   Robot Parameters
CONST_ROBOT_VELOCITY     = 0.05
CONST_ROBOT_ACCELERATION = 0.50
CONST_BLEND = 0.0
#   ServoJ Parameters
CONST_SERVOJ_LOOKAHEAD_TIME = 0.20
CONST_SERVOJ_GAIN           = 100
#   Time step inside robot:
#       UR-cb Version: 125 Hz -> 8 ms 
#       UR-e Version: 500 Hz -> 2 ms
CONST_SEVOJ_DT = 0.002
#   Sensor Factor: Conversion between sensor and robot workspace
CONST_SENSOR_FACTOR = [(Parameters.CONST_UR_WORKSPACE[0] / (np.abs(Parameters.CONST_SENSOR_POS_WORKSPACE[0][0] - Parameters.CONST_SENSOR_POS_WORKSPACE[0][1]))),
                       (Parameters.CONST_UR_WORKSPACE[1] / (np.abs(Parameters.CONST_SENSOR_POS_WORKSPACE[1][0] - Parameters.CONST_SENSOR_POS_WORKSPACE[1][1]))),
                       (Parameters.CONST_UR_WORKSPACE[2] / (np.abs(Parameters.CONST_SENSOR_POS_WORKSPACE[2][0] - Parameters.CONST_SENSOR_POS_WORKSPACE[2][1])))]
#   Sensor Offset: Positive and negative sensor direction
CONST_SENSOR_POS_OFFSET = [np.sum(Parameters.CONST_SENSOR_POS_WORKSPACE[0])/2, 
                           np.sum(Parameters.CONST_SENSOR_POS_WORKSPACE[1])/2, 
                           np.sum(Parameters.CONST_SENSOR_POS_WORKSPACE[2])/2]
#   Direction of movement: 1.0 (Default), -1.0 (Inverse)
CONST_MOVEMENT_DIRECTION = [-1.0, -1.0, 1.0]

def Data_Stream(UR_CTRL, ROBOTIQ_CTRL):
    # Initiation of the process (Subscriber: Client)
    #   Create a zmq Context.
    context = zmq.Context()
    #   Create a Socket associated with this Context.
    socket = context.socket(zmq.SUB)
    #   Set socket options with a unicode object.
    socket.setsockopt_string(zmq.SUBSCRIBE,'')
    #   Connect to a remote socket.
    socket.connect('tcp://127.0.0.1:2224')
    
    BLPMA = []
    # Initialization of filters for each part.
    for _, limit in enumerate(Parameters.CONST_FILTER_POS_LIMIT):
        # Butterworth Low Pass Moving Average (BLPMA)
        BLPMA.append(Filter.Butterworth_Low_Pass_Moving_Average([limit[0], limit[1]], Parameters.CONST_FILTER_POS_NUM_OF_DATA, 20, 1/Parameters.CONST_TIME_STEP, 1.95, 3))

    # Initialization Target (Position, Orientation, Parameters)
    #   Note: Convert data from mm to m.
    Target_Home = [Parameters.CONST_UR_CARTES_POS_HOME[0]/1000, Parameters.CONST_UR_CARTES_POS_HOME[1]/1000, Parameters.CONST_UR_CARTES_POS_HOME[2]/1000, 
                   Parameters.CONST_UR_CARTES_ORIENT_HOME[0], Parameters.CONST_UR_CARTES_ORIENT_HOME[1], Parameters.CONST_UR_CARTES_ORIENT_HOME[2]]

    # Move to position (Linear Interpolation)
    #   Home Target
    UR_CTRL.moveL(Target_Home, CONST_ROBOT_VELOCITY*10, CONST_ROBOT_ACCELERATION)

    # Initialization of the parameters:
    #   Receive message
    pub_msg = [0.0, 0.0, 0.0, False, False, False]
    #   Reset P5 Glove (Sensor) Position
    robot_position  = [0.0] * len(Parameters.CONST_UR_CARTES_POS_HOME)
    sensor_position = [0.0] * len(Parameters.CONST_UR_CARTES_POS_HOME)
    #   Gripper status information: Open / Closed
    gripper_closed = False
    gripper_open   = False
    
    while pub_msg[5] != True:
        # t_{0}: time start
        t_0 = time.time()

        # Receive a Python object as a message using pickle to serialize.
        #   pub_msg: 
        #       Desired robot position:
        #           [0]: X - Position
        #           [1]: Y - Position
        #           [2]: Z - Position
        #       Gripper:
        #           [3]: Gripper State
        #           [4]: Movement State
        #           [5]: Quit State
        pub_msg = socket.recv_pyobj()
        
        # Recalculating the sensor position
        sensor_position = [((BLPMA[0].Compute(pub_msg[0]) + CONST_SENSOR_POS_OFFSET[0]) * CONST_SENSOR_FACTOR[0]),
                           ((BLPMA[2].Compute(pub_msg[2]) + CONST_SENSOR_POS_OFFSET[1]) * CONST_SENSOR_FACTOR[1]),
                           ((BLPMA[1].Compute(pub_msg[1]) + CONST_SENSOR_POS_OFFSET[2]) * CONST_SENSOR_FACTOR[2])]

        # Desired robot position:
        robot_position = [Parameters.CONST_UR_CARTES_POS_HOME[0] + sensor_position[0]*CONST_MOVEMENT_DIRECTION[0],
                          Parameters.CONST_UR_CARTES_POS_HOME[1] + sensor_position[1]*CONST_MOVEMENT_DIRECTION[1], 
                          Parameters.CONST_UR_CARTES_POS_HOME[2] + sensor_position[2]*CONST_MOVEMENT_DIRECTION[2]]

        # Simple condition for gripper control
        if pub_msg[3] == True and gripper_closed == False:
            # Closed Gripper
            if ROBOTIQ_CTRL != None:
                gripper_closed = ROBOTIQ_CTRL.close()
            gripper_open  = False
        elif pub_msg[3] == False and gripper_open == False:
            # Open Gripper
            if ROBOTIQ_CTRL != None:
                gripper_open  = ROBOTIQ_CTRL.open()
            gripper_closed = False

        # Robot moves depending on the input parameters
        if pub_msg[4] == True:
            # Set data to the robot via RTDE
            UR_CTRL.servoL([np.round(robot_position[0]/1000, 6),np.round(robot_position[1]/1000, 6), np.round(robot_position[2]/1000, 6), 
                            Parameters.CONST_UR_CARTES_ORIENT_HOME[0],  Parameters.CONST_UR_CARTES_ORIENT_HOME[1], Parameters.CONST_UR_CARTES_ORIENT_HOME[2]], 
                            CONST_ROBOT_VELOCITY, CONST_ROBOT_ACCELERATION, CONST_SEVOJ_DT, 
                            CONST_SERVOJ_LOOKAHEAD_TIME, CONST_SERVOJ_GAIN)           

        # t_{1}: time stop
        #   t = t_{1} - t_{0}
        t = time.time() - t_0

        # Writing data to the console (Desired robot position)
        print(f'[Time:{t:0.03f}, X: {(np.round(robot_position[0]/1000, 6)):0.4f}, Y: {(np.round(robot_position[1]/1000, 6)):0.4f}, Z: {(np.round(robot_position[2]/1000, 6)):0.4f}, Gripper: {pub_msg[3]}]')

        # Recalculate the time
        if t < CONST_SEVOJ_DT:
            time.sleep(CONST_SEVOJ_DT - t)

    print('[INFO] Disconnect: UR-RTDE')
    time.sleep(1)
    # Stop the ur-rtde.
    UR_CTRL.servoStop()
    UR_CTRL.stopScript()
    print('[INFO] Disconnect: Socket')
    # Note:
    #   netstat -ano | findstr :2012
    #   taskkill /PID {PID} /F
    time.sleep(1)
    # Socket Close
    socket.close()
    # Destroy Context
    context.term()
    context.destroy()
    print(f'[INFO] Closed context state: {context.closed}')
    # Exit from Python.
    sys.exit(1)

def main():
    try: 
        # Initialization and connection to the robot
        #   Note: The robot must be in remote control status.
        UR_RTDE_Ctrl = rtde_control.RTDEControlInterface('192.168.230.132')

        # Activate the gripper and initialize force and speed
        #ROBOTIQ_Gripper = RobotiqGripper(UR_RTDE_Ctrl)
        # Simulation
        ROBOTIQ_Gripper = None

        # Start Control: Thread
        stream_m = threading.Thread(target=Data_Stream, args=(UR_RTDE_Ctrl, ROBOTIQ_Gripper, ), daemon=True)
        stream_m.start()

        while stream_m.is_alive():
            stream_m.join(0.0001)

    except KeyboardInterrupt:
        # Exit from Python.
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())
