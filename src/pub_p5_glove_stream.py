# System (Default)
import sys
# Time (Time access and conversions)
import time
# Threading (Thread-based parallelism)
import threading
# Lib.P5.Essential_Reality (Library to control the Essential Reality P5 Glove)
import Lib.P5.Essential_Reality as Essential_Reality
# Lib.Utils (Some useful functions)
import Lib.Utils as Utils
# Lib.Parameters (Main Control Parameters)
import Lib.Parameters as Parameters
# ZeroMQ (Universal messaging library) [pip install zmq]
import zmq 
# Keyboard (Simulate keyboard events) [pip install keyboard]
import keyboard 

def Main_Control(P5_cls):
    # Initiation of the process (Publisher: Server)
    #   Create a zmq Context.
    context = zmq.Context()
    #   Create a Socket associated with this Context.
    socket = context.socket(zmq.PUB)
    socket.linger = 0

    # Initialization of the parameters:
    # Reset P5 Glove (Sensor) Position {X, Y, Z} -> 3
    sensor_position = [0.0] * 3

    # Bind the socket to an address.
    socket.bind('tcp://*:2224')

    # Initialization of the Class (Simple Edge Decetor)
    #   The edge signal depends on the A button (index 0) on the hand.
    SED_Move    = Utils.Simple_Edge_Detector()
    #   The edge signal depends on the opening and closing of the hand
    SED_Gripper = Utils.Simple_Edge_Detector()

    # Wait for the glove to run
    time.sleep(2)
    
    print('[INFO] Press the (q) button to exit.')

    while P5_cls.error != True:
        # t_{0}: time start
        t_0 = time.time()

        enable_movement = SED_Move.Get_Value(P5_cls.Get_Buttons_Value_ID(0))
        # Robot moves depending on the input parameters
        if enable_movement == True:
            sensor_position = [P5_cls.Get_Absolute_Position_ID(0), P5_cls.Get_Absolute_Position_ID(1), P5_cls.Get_Absolute_Position_ID(2)]

        # Send a Python object as a message using pickle to serialize.
        #   pub_msg: 
        #       Desired robot position:
        #           [0]: X - Position
        #           [1]: Y - Position
        #           [2]: Z - Position
        #       Gripper:
        #           [3]: Gripper State
        #           [4]: Movement State
        #           [5]: Quit State
        socket.send_pyobj([sensor_position[0], sensor_position[1], sensor_position[2], 
                           SED_Gripper.Get_Value(P5_cls.Get_Hand_Gesture()), enable_movement, 
                           False])
        
        if keyboard.is_pressed('q'):
            socket.send_pyobj([sensor_position[0], sensor_position[1], sensor_position[2], 
                               False, False,
                               True])
            break

        # t_{1}: time stop
        #   t = t_{1} - t_{0}
        t = time.time() - t_0
        
        # Recalculate the time
        if t < Essential_Reality.CONST_TIME_STEP:
            time.sleep(Essential_Reality.CONST_TIME_STEP - t)

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
    time.sleep(1)
    P5_cls.Disconnect()
    print('[INFO] Disconnect: Essential P5 Glove')
    print('[INFO] Press the keyboard shortcut Ctrl+c.')
    # Exit from Python.
    sys.exit(1)

def main():
    try: 
        # Initialization of the Class (Essential Reality P5 Glove)
        #   'P5DLL.dll' - must be in the same folder
        P5_G = Essential_Reality.P5_Glove('P5DLL.dll')

        # Thread initialization:
        #   Main Control:
        #       target=Main_Control, args=(ABB_EGM_Ctrl, P5_G, )
        
        # Start Control: Thread
        ctrl_m = threading.Thread(target=Main_Control, args=(P5_G, ), daemon=True)
        ctrl_m.start()

        # Connection to the Essential Reality P5 glove
        P5_G.Connect()

        while ctrl_m.is_alive():
            ctrl_m.join(0.0001)

    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())