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
File Name: sub_data_collection.py
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
# Lib.Parameters (Main Control Parameters)
import Lib.Parameters as Parameters
# Lib.Signal.Filter (Filters: SMA, BLP)
import Lib.Signal.Filter as Filter
# ZeroMQ (Universal messaging library) [pip install zmq]
import zmq

def Data_Stream(SAVE_FILE):
    # Initiation of the process (Subscriber: Client)
    #   Create a zmq Context.
    context = zmq.Context()
    #   Create a Socket associated with this Context.
    socket = context.socket(zmq.SUB)
    #   Set socket options with a unicode object.
    socket.setsockopt_string(zmq.SUBSCRIBE,'')
    #   Connect to a remote socket.
    socket.connect('epgm://127.0.0.1:2224')

    SMA = []; BLP = []; BLPMA = []
    # Initialization of filters for each part.
    for _, limit in enumerate(Parameters.CONST_FILTER_POS_LIMIT):
        # Simple Moving Average (SMA)
        SMA.append(Filter.Simple_Moving_Average([limit[0], limit[1]], Parameters.CONST_FILTER_POS_NUM_OF_DATA))
        # Butterworth Low Pass (BLP)
        BLP.append(Filter.Butterworth_Low_Pass([limit[0], limit[1]], Parameters.CONST_FILTER_POS_NUM_OF_DATA, 1/Parameters.CONST_TIME_STEP, 2.5, 3))
        # Butterworth Low Pass Moving Average (BLPMA)
        BLPMA.append(Filter.Butterworth_Low_Pass_Moving_Average([limit[0], limit[1]], Parameters.CONST_FILTER_POS_NUM_OF_DATA, 50, 1/Parameters.CONST_TIME_STEP, 2.5, 3))
    
    # Initialization of the parameters:
    #   Receive message
    pub_msg = [0.0, 0.0, 0.0, False, False, False]
    #   File: Raw Data, Filter Data (1, 2, 3)
    x_data_rt = []; x_data_f1_rt = []; x_data_f2_rt = []; x_data_f3_rt = []
    y_data_rt = []; y_data_f1_rt = []; y_data_f2_rt = []; y_data_f3_rt = []
    z_data_rt = []; z_data_f1_rt = []; z_data_f2_rt = []; z_data_f3_rt = []

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

        # Actual Data (Raw)
        x_data_rt.append(pub_msg[0])
        y_data_rt.append(pub_msg[1])
        z_data_rt.append(pub_msg[2])
        # Filtered Data
        #   SMA
        x_data_f1_rt.append(SMA[0].Compute(pub_msg[0]))
        y_data_f1_rt.append(SMA[1].Compute(pub_msg[1]))
        z_data_f1_rt.append(SMA[2].Compute(pub_msg[2]))
        #   BLP
        x_data_f2_rt.append(BLP[0].Compute(pub_msg[0]))
        y_data_f2_rt.append(BLP[1].Compute(pub_msg[1]))
        z_data_f2_rt.append(BLP[2].Compute(pub_msg[2]))
        #   BLPMA
        x_data_f3_rt.append(BLPMA[0].Compute(pub_msg[0]))
        y_data_f3_rt.append(BLPMA[1].Compute(pub_msg[1]))
        z_data_f3_rt.append(BLPMA[2].Compute(pub_msg[2]))         
        # t_{1}: time stop
        #   t = t_{1} - t_{0}
        t = time.time() - t_0

        # Writing data to the console (Desired robot position)
        print(f'[Time:{t:0.03f}]')

        # Recalculate the time
        if t < 0.002:
            time.sleep(0.002 - t)

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
    if SAVE_FILE == True:
        data_collection = pd.DataFrame(data = {'X_DATA_RT': x_data_rt, 'X_DATA_F1_RT': x_data_f1_rt, 'X_DATA_F2_RT': x_data_f2_rt, 'X_DATA_F3_RT': x_data_f3_rt,
                                               'Y_DATA_RT': y_data_rt, 'Y_DATA_F1_RT': y_data_f1_rt, 'Y_DATA_F2_RT': y_data_f2_rt, 'Y_DATA_F3_RT': y_data_f3_rt,
                                               'Z_DATA_RT': z_data_rt, 'Z_DATA_F1_RT': z_data_f1_rt, 'Z_DATA_F2_RT': z_data_f2_rt, 'Z_DATA_F3_RT': z_data_f3_rt})
        current_directory_name = os.getcwd()
        data_collection.to_csv(current_directory_name + '\\Evaluation\\P5_Sub_Results\\' + 'Experiment_Position' + '.txt')
        print('[INFO] The data has been successfully saved.')
    time.sleep(1)
    # Exit from Python.
    sys.exit(1)

def main():
    try: 
        # Start Control: Thread
        stream_m = threading.Thread(target=Data_Stream, args=(False, ), daemon=True)
        stream_m.start()

        while stream_m.is_alive():
            stream_m.join(0.0001)

    except KeyboardInterrupt:
        # Exit from Python.
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())
