# System (Default)
import sys
# Time (Time access and conversions)
import time
# Threading (Thread-based parallelism)
import threading
# CTypes (C compatible data types, and allows calling functions in DLLs)
import ctypes as ct
# Lib.Signal.Filter (Filters: SMA, BLP)
import Lib.Signal.Filter as Filter
# Lib.Parameters (Main Control Parameters)
import Lib.Parameters as Parameters

"""
Essential Reality P5 Glove Notes: 
      - The P5 virtual reality gloves are data gloves suitable for gaming and 3D virtual environments. 
      - The gloves contain two infrared sensors. They detect the visible LEDs on the glove (there are eight in total) 
        and convert them to the position (x, y, z) and orientation in terms of pitch, yaw and roll. The glove also has 
        bend sensors in the fingers and four buttons on the top. 
      - Communication between the gloves and the application on the computer is via USB port.

Warning: It is necessary to use the 32-bit version of Python!
"""

# Initialization of Constants:
# Sensor Units
CONST_P5_CM      = ct.c_float((2.54/51.2))
# Time step inside threads
CONST_TIME_STEP  = Parameters.CONST_TIME_STEP
# Fingers Bend
CONST_FINGERS_BEND_LIMIT = [[5.0, 65.0], [5.0, 65.0], [5.0, 65.0], [5.0, 65.0], [5.0, 65.0]]
# Offset for gesture recognition
CONST_FINGERS_BEND_OFFSET = 10.0
# Gesture recognition: Hand (open or closed)
CONST_HAND_STATE_OPEN   = False
CONST_HAND_STATE_CLOSED = True
# Other auxiliary constants
CONST_NULL = 0
CONST_NUM_OF_FINGERS = 5

class P5_Glove(object):
    """
    Description:
        A class for controlling and collecting data from the Essential reality glove.

    Initialization of the Class:
        Args:
            (1) lib_name [string]: DLL name.
        
        Example:
            Initialization:
                Cls = Essential_Reality.P5_Glove('P5DLL.dll')

            Connection:
                Cls.Connect()

            Returns:
                Cls.Get_{name}(ID)          # Cls.Get_Absolute_Position_ID(0): Raw X-Position
    """
    def __init__(self, lib_name = 'P5DLL.dll'):
        # << PUBLIC >> #
        self.error = False

        # << PRIVATE >> #
        # Load the library (.dll) to communicate with the P5 Glove
        try:
            self.__dll_lib = ct.cdll.LoadLibrary(lib_name)
        except FileNotFoundError as error:
            self.__dll_lib = CONST_NULL
            self.error = True 
            print('[ERROR] Could not find module ' + lib_name + '. Try using the full path with constructor syntax.')

        # P5 Glove Data:
        #   Identificational number
        self.__id = ct.c_int(CONST_NULL - 1)
        #   Position Raw (X, Y, Z)
        self.__pos_rt = [ct.c_float(0.0), ct.c_float(0.0), ct.c_float(0.0)] 
        #   Fingers Bend Raw (Thumb, Index, Middle, Ring, Little)
        self.__fingers_bend_rt = [ct.c_float(0.0), ct.c_float(0.0), ct.c_float(0.0), ct.c_float(0.0), ct.c_float(0.0)]; 
        #   Buttons (A, B, C, D)
        self.__buttons_rt = [ct.c_float(0.0), ct.c_float(0.0), ct.c_float(0.0), ct.c_float(0.0)]

    def Connect(self):
        """
        Description:
            Function to connect and initialize the P5 glove. The function also triggers multi-threaded 
            processing for data collection.
        """

        # Initialization and start the glove driver
        self.__dll_lib.P5_Init()

        if self.__dll_lib.P5_GetCount() > CONST_NULL:
            # Get the number of gloves
            self.__id = ct.c_int(self.__dll_lib.P5_GetCount() - 1)
            # Set Parameters (Units)
            self.__dll_lib.P5_SetUnits(CONST_P5_CM)
            # Disable mouse control on the desktop
            self.__dll_lib.P5_SetMouseState(self.__dll_lib.P5_GetCount() - 1, ct.c_bool(False))

            print('[INFO] The USB device is recognized.')
            
            # Start multi-threaded processing for data collection
            self.__Data_Collection()
        else:
            self.__id  = ct.c_int(CONST_NULL - 1)
            self.error = True 
            print('[ERROR] The USB device is not recognized. Try connecting the device again.')

    def __Get_Absolute_Position(self):
        """
        Description:
            Function (thread) to collect position data from gloves.
        """

        while True:
            # t_{0}: time start
            t_0 = time.time()

            # Get the raw data from the sensor
            self.__dll_lib.P5_GetAbsolutePos(self.__id, 
                                             ct.byref(self.__pos_rt[0]), 
                                             ct.byref(self.__pos_rt[1]), 
                                             ct.byref(self.__pos_rt[2]))

            # t_{1}: time stop
            #   t = t_{1} - t_{0}
            t = time.time() - t_0

            # Recalculate the time
            if t < CONST_TIME_STEP:
                time.sleep(CONST_TIME_STEP - t)

    def __Get_Fingers_Bend(self):
        """
        Description:
            Function (thread) to collect fingers bend data from gloves.
        """

        while True:
            # t_{0}: time start
            t_0 = time.time()

            # Get the raw data from the sensor
            self.__dll_lib.P5_GetFingerBends(self.__id, 
                                             ct.byref(self.__fingers_bend_rt[0]), 
                                             ct.byref(self.__fingers_bend_rt[1]), 
                                             ct.byref(self.__fingers_bend_rt[2]),
                                             ct.byref(self.__fingers_bend_rt[3]),
                                             ct.byref(self.__fingers_bend_rt[4]))

            # t_{1}: time stop
            #   t = t_{1} - t_{0}
            t = time.time() - t_0

            # Recalculate the time
            if t < CONST_TIME_STEP:
                time.sleep(CONST_TIME_STEP - t)

    def __Get_Buttons_Value(self):
        while True:
            # t_{0}: time start
            t_0 = time.time()

            # Get the raw data from the sensor
            self.__dll_lib.P5_GetButtons(self.__id, 
                                         ct.byref(self.__buttons_rt[0]),
                                         ct.byref(self.__buttons_rt[1]),
                                         ct.byref(self.__buttons_rt[2]),
                                         ct.byref(self.__buttons_rt[3]))

            # t_{1}: time stop
            #   t = t_{1} - t_{0}
            t = time.time() - t_0

            # Recalculate the time
            if t < CONST_TIME_STEP:
                time.sleep(CONST_TIME_STEP - t)

    def __Data_Collection(self):
        try:
            # Start Stream: Thread (Position: X, Y, Z)
            self.__t_position_rt = threading.Thread(target = self.__Get_Absolute_Position, daemon = True)
            self.__t_position_rt.start()

            # Start Stream: Thread (Fingers Bend: T, I, M, R, L)
            self.__t_fingers_bend_rt = threading.Thread(target = self.__Get_Fingers_Bend, daemon = True)
            self.__t_fingers_bend_rt.start()

            # Start Stream: Thread {Buttons: A, B, C, D}
            self.__t_buttons_rt = threading.Thread(target = self.__Get_Buttons_Value, daemon = True)
            self.__t_buttons_rt.start()

            while self.__t_position_rt.is_alive() and self.__t_fingers_bend_rt.is_alive() and self.__t_buttons_rt.is_alive():
                self.__t_position_rt.join(0.0001)
                self.__t_fingers_bend_rt.join(0.0001)
                self.__t_buttons_rt.join(0.0001)

        except KeyboardInterrupt:
            self.Disconnect()
            sys.exit(1)

    def Get_Absolute_Position_ID(self, id):
        """
        Description:
            Function to get the raw position value from the sensor.
        
        Input:
            (1) id [INT]: The identification value of the vector.
                          (ID{0}: X,ID{1}: Y,ID{2}: Z)
        
        Returns:
            (1) parameter [Float]: Raw position value.
        """
        try:
            assert id < len(self.__pos_rt)
            return self.__pos_rt[id].value
        except AssertionError as error:
            print('[ERROR] The identification number is out of range.')


    def Get_Fingers_Bend_ID(self, id):
        """
        Description:
            Function to get the raw value of the fingers bend from the sensor.
        
        Input:
            (1) id [INT]: The identification value of the vector.
                          (ID{0}: T,ID{1}: I,ID{2}: M, ID{3}: R, ID{4}: L)

        Returns:
            (1) parameter [Float]: Raw fingers bend value.
        """
        try:
            assert id < len(self.__fingers_bend_rt)
            return self.__fingers_bend_rt[id].value
        except AssertionError as error:
            print('[ERROR] The identification number is out of range.')

    def Get_Buttons_Value_ID(self, id):
        """
        Description:
            Function to get the raw value of the buttons from the sensor.
        
        Input:
            (1) id [INT]: The identification value of the vector.
                          (ID{0}: A,ID{1}: B,ID{2}: C, ID{3}: D)

        Returns:
            (1) parameter [Bool]: Converted raw button value (0.0/1.0) to bool (false/true).
        """
        try:
            assert id < len(self.__buttons_rt)
            return bool(self.__buttons_rt[id].value)
        except AssertionError as error:
            print('[ERROR] The identification number is out of range.')

    def Get_Hand_Gesture(self):
        """
        Description:
            Function to hand gesture recognition (closed or open).
        """

        SMA = []
        # Initialization of filters for each part.
        for _, limit in enumerate(Parameters.CONST_FILTER_FINGERS_BEND_LIMIT):
            # Simple Moving Average (SMA)
            SMA.append(Filter.Simple_Moving_Average([limit[0], limit[1]], Parameters.CONST_FILTER_FINGERS_BEND_NUM_OF_DATA))

        counter = 0
        for i, f_b in enumerate(self.__fingers_bend_rt):
            counter = counter + 1 if CONST_FINGERS_BEND_LIMIT[0][1] - CONST_FINGERS_BEND_OFFSET <= SMA[i].Compute(f_b.value) <= CONST_FINGERS_BEND_LIMIT[0][1] else counter

            if i != counter - 1:
                return CONST_HAND_STATE_OPEN

        return CONST_HAND_STATE_CLOSED
            
    def Disconnect(self):
        """
        Description:
            Function to disconnect (close) the P5 glove.
        """
        self.__dll_lib.P5_Close()
        time.sleep(2)