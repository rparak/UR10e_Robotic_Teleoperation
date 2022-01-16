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
File Name: test_data_collection.py
## =========================================================================== ## 
"""

# System (Default)
import sys
# Time (Time access and conversions)
import time
# Threading (Thread-based parallelism)
import threading
# Numpy (Array computing) [pip3 install numpy]
import numpy as np
# Lib.P5.Essential_Reality (Library to control the Essential Reality P5 Glove)
import Lib.P5.Essential_Reality as Essential_Reality
# Lib.Utils (Some useful functions)
import Lib.Utils as Utils

# Initialization of Constants:
#   ABB Robot (IRB 1200)
CONST_ABB_WORKSPACE          = [360.0,360.0,360.0]
CONST_ABB_CARTES_POS_HOME    = [450.0,0.0,500.0]
CONST_ABB_CARTES_ORIENT_HOME = [0.0,0.0,1.0,0.0]
#   Universal Robots (UR10e)
CONST_UR_WORKSPACE          = [350.0, 350.0, 350.0]
CONST_UR_CARTES_POS_HOME    = [-200.0, -600.0, 350.0]
CONST_UR_CARTES_ORIENT_HOME = [0.0, 3.14, 0.0]
# Set Parameters
CONST_ROBOT_WORKSPACE          = CONST_UR_WORKSPACE
CONST_ROBOT_CARTES_POS_HOME    = CONST_UR_CARTES_POS_HOME
CONST_ROBOT_CARTES_ORIENT_HOME = CONST_UR_CARTES_ORIENT_HOME
#   Essential Reality P5 Glove
CONST_SENSOR_POS_WORKSPACE  = Essential_Reality.CONST_FILTER_POS_LIMIT
# ABB: 1,0,2; UR: 0,1,2
CONST_SENSOR_POS_OFFSET     = [np.sum(CONST_SENSOR_POS_WORKSPACE[0])/2, 
                               np.sum(CONST_SENSOR_POS_WORKSPACE[1])/2, 
                               np.sum(CONST_SENSOR_POS_WORKSPACE[2])/2]
CONST_SENSOR_FACTOR = CONST_ROBOT_WORKSPACE[0] / (np.abs(CONST_SENSOR_POS_WORKSPACE[0][0] - CONST_SENSOR_POS_WORKSPACE[0][1]))

def Test_Stream_T1(P5_cls):
    # Absolute Position (Filtered):
    #   [X: {P5_cls.Get_Absolute_Position_ID(0)}, Y: {P5_cls.Get_Absolute_Position_ID(1)}, Z: {P5_cls.Get_Absolute_Position_ID(2)}]
    # Finger Bends (Filtered):
    #   [T: {P5_cls.Get_Fingers_Bend_ID(0)}, I: {P5_cls.Get_Fingers_Bend_ID(1)}, M: {P5_cls.Get_Fingers_Bend_ID(2)}, R: {P5_cls.Get_Fingers_Bend_ID(3)}, L: {P5_cls.Get_Fingers_Bend_ID(4)}]
    # Buttons
    #   [A: {P5_cls.Get_Buttons_Value_ID(0)}, B: {P5_cls.Get_Buttons_Value_ID(1)}, C: {P5_cls.Get_Buttons_Value_ID(2)}, D: {P5_cls.Get_Buttons_Value_ID(3)}]

    while P5_cls.error != True:
        # t_{0}: time start
        t_0 = time.time()

        print(f'[X: {P5_cls.Get_Absolute_Position_ID(0)}, Y: {P5_cls.Get_Absolute_Position_ID(1)}, Z: {P5_cls.Get_Absolute_Position_ID(2)}]')
        
        # t_{1}: time stop
        #   t = t_{1} - t_{0}
        t = time.time() - t_0
        
        # Recalculate the time
        if t < Essential_Reality.CONST_TIME_STEP:
            time.sleep(Essential_Reality.CONST_TIME_STEP - t)

def Test_Stream_T2(P5_cls):
    # Reset P5 Glove (Sensor) Position
    sensor_position = [0.0] * len(CONST_ROBOT_CARTES_POS_HOME)

    # Initialization of the Class (Simple Edge Decetor)
    #   The edge signal depends on the A button (index 0) on the hand.
    SED_Move    = Utils.Simple_Edge_Detector()
    #   The edge signal depends on the opening and closing of the hand
    SED_Gripper = Utils.Simple_Edge_Detector()

    while P5_cls.error != True:
        # t_{0}: time start
        t_0 = time.time()

        if SED_Move.Get_Value(P5_cls.Get_Buttons_Value_ID(0)) == True:
            # Robot moves depending on the input parameters
            # ABB: 2,0,1; UR: 0,2,1
            sensor_position = [(P5_cls.Get_Filtered_Absolute_Position_ID(0) + CONST_SENSOR_POS_OFFSET[0]) * CONST_SENSOR_FACTOR, 
                               (P5_cls.Get_Filtered_Absolute_Position_ID(2) + CONST_SENSOR_POS_OFFSET[1]) * CONST_SENSOR_FACTOR, 
                               (P5_cls.Get_Filtered_Absolute_Position_ID(1) + CONST_SENSOR_POS_OFFSET[2]) * CONST_SENSOR_FACTOR]


        # Writing data to the console (Desired robot position)
        print(f'[X: {(P5_cls.Get_Filtered_Absolute_Position_ID(2) + CONST_SENSOR_POS_OFFSET[0]):0.2f}, Y: {(P5_cls.Get_Filtered_Absolute_Position_ID(0) + CONST_SENSOR_POS_OFFSET[1]):0.2f}, Z: {(P5_cls.Get_Filtered_Absolute_Position_ID(1) + CONST_SENSOR_POS_OFFSET[2]):0.2f}, Gripper: {SED_Gripper.Get_Value(P5_cls.Get_Hand_Gesture())}]]')
        
        # t_{1}: time stop
        #   t = t_{1} - t_{0}
        t = time.time() - t_0
        
        # Recalculate the time
        if t < Essential_Reality.CONST_TIME_STEP:
            time.sleep(Essential_Reality.CONST_TIME_STEP - t)

def main():
    try: 
        # Initialization of the Class (Essential Reality P5 Glove)
        #   'P5DLL.dll' - must be in the same folder
        P5_G = Essential_Reality.P5_Glove('P5DLL.dll')
        
        # Thread initialization:
        #   Writing data to the console
        #       target=Test_Stream_T1, args=(P5_G,)
        #       target=Test_Stream_T2, args=(P5_G,)
        #   Saving data to a file:
        #       target=Utils.Data_Collection_Position, args=(P5_G, 'Experiment_Position', 1000)
        #       target=Utils.Data_Collection_Finger_Bends, args=(P5_G, 'Experiment_Finger_Bends', 1000)

        # Start Control: Thread
        ctrl_m = threading.Thread(target=Utils.Data_Collection_Position, args=(P5_G, 'Experiment_Position_1', 1000), daemon=True)
        ctrl_m.start()

        # Connection to the Essential Reality P5 glove
        P5_G.Connect()

        while ctrl_m.is_alive():
            ctrl_m.join(0.0001)

    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())
