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
File Name: sub_ur_stream.py
## =========================================================================== ## 
"""

# System (Default)
import sys
# Time (Time access and conversions)
import time
# Pandas (Data analysis and manipulation) [pip3 install pandas]
import pandas as pd
# OS (Operating system interfaces)
import os
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
import rtde_receive 
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

def Data_Stream(UR_CTRL, UR_STREAM):
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

    # Initialization of the Robot Cartesian positions vector
    x_rob_cartesian_position_rt = []; y_rob_cartesian_position_rt = []; z_rob_cartesian_position_rt = []
    # Initialization of the Sensor positions vector
    x_sensor_position_rt = []; y_sensor_position_rt = []; z_sensor_position_rt = []

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

        # Get data fromt the robot via RTDE
        stream_cartesian_position = UR_STREAM.getActualTCPPose()

        # Get Robot Cartesian position (X, Y, Z): 
        #   Actual Position of the robot
        x_rob_cartesian_position_rt.append(stream_cartesian_position[0])
        y_rob_cartesian_position_rt.append(stream_cartesian_position[1])
        z_rob_cartesian_position_rt.append(stream_cartesian_position[2])
        # Get Sensor position (X, Y, Z): 
        #   Desired Position of the robot
        x_sensor_position_rt.append(np.round(robot_position[0]/1000, 6))
        y_sensor_position_rt.append(np.round(robot_position[1]/1000, 6))
        z_sensor_position_rt.append(np.round(robot_position[2]/1000, 6))

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
    data_collection = pd.DataFrame(data = {'X_DATA_SENSOR_RT': x_sensor_position_rt, 'X_DATA_ROBOT_RT': x_rob_cartesian_position_rt,
                                           'Y_DATA_SENSOR_RT': y_sensor_position_rt, 'Y_DATA_ROBOT_RT': y_rob_cartesian_position_rt,
                                           'Z_DATA_SENSOR_RT': z_sensor_position_rt, 'Z_DATA_ROBOT_RT': z_rob_cartesian_position_rt})
    current_directory_name = os.getcwd()
    data_collection.to_csv(current_directory_name + '\\Evaluation\\Robot_Results\\' + 'Universal_Robots_Test_S_2' + '.txt')
    print('[INFO] The data has been successfully saved.')
    time.sleep(1)
    # Exit from Python.
    sys.exit(1)

def main():
    try: 
        # Initialization and connection to the robot
        #   Note: The robot must be in remote control status.
        UR_RTDE_Ctrl   = rtde_control.RTDEControlInterface('192.168.10.122')
        UR_RTDE_Stream = rtde_receive.RTDEReceiveInterface('192.168.10.122')

        # Start Control: Thread
        stream_m = threading.Thread(target=Data_Stream, args=(UR_RTDE_Ctrl, UR_RTDE_Stream, ), daemon=True)
        stream_m.start()

        while stream_m.is_alive():
            stream_m.join(0.0001)

    except KeyboardInterrupt:
        # Exit from Python.
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())
