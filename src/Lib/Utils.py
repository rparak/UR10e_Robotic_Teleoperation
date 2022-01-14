# Pandas (Data analysis and manipulation) [pip3 install pandas]
import pandas as pd
# Time (Time access and conversions)
import time
# OS (Operating system interfaces)
import os
# Lib.P5.Essential_Reality (Library to control the Essential Reality P5 Glove)
import Lib.P5.Essential_Reality as Essential_Reality
# Lib.Signal.Filter (Filters: SMA, BLP)
import Lib.Signal.Filter as Filter
# Lib.Parameters (Main Control Parameters)
import Lib.Parameters as Parameters

# Initialization of Constants:
#   Control State: SET, NULL (Inverting the individual value using the edge signal)
CONST_STATE_SET  = True
CONST_STATE_NULL = False

class Simple_Edge_Detector:
    """
    Description:
        A simple class for detecting {False} to {True} transitions from an external value.

    Example:
        Initialization:
            Cls = Simple_Edge_Detector()

        Calculation:
            Cls.Get_Value(True)  -> result True
            Cls.Get_Value(False) -> result True
            Cls.Get_Value(True)  -> result False
            Cls.Get_Value(False)  -> result False
            ....
    """

    def __init__(self):
        # << PRIVATE >> #
        # Result value
        self.__result  = False
        # Actual state
        self.__state = False

    def Get_Value(self, value):
        """
        Description:
            Function to get the resulting value from a simple edge detector. (SMA).

        Args:
            (1) value [Bool]: Input value.
        
        Returns:
            (1) parameter [Bool]: Result value.
        """

        if value == True and self.__state == CONST_STATE_NULL:
            self.__state = CONST_STATE_SET
            # Inverse Value
            self.__result = not self.__result

        if value == False and self.__state == CONST_STATE_SET:
            self.__state = CONST_STATE_NULL

        return self.__result

def Data_Collection_Position(P5_cls, file_name, num_of_data_collections):
    """
    Description:
        A simple function to collect position data from the sensor and write it to a text file.

    Args:
        (1) P5_cls [P5_Glove Class]: Essential Reality P5 Glove class for sensor data collection.
        (2) file_name [String]: Output file name.
        (3) num_of_data_collections [INT]: Number of data collections.
    """

    x_data_rt = []; x_data_f1_rt = []; x_data_f2_rt = []; x_data_f3_rt = []
    y_data_rt = []; y_data_f1_rt = []; y_data_f2_rt = []; y_data_f3_rt = []
    z_data_rt = []; z_data_f1_rt = []; z_data_f2_rt = []; z_data_f3_rt = []

    SMA = []; BLP = []; BLPMA = []
    # Initialization of filters for each part.
    for _, limit in enumerate(Parameters.CONST_FILTER_POS_LIMIT):
        # Simple Moving Average (SMA)
        SMA.append(Filter.Simple_Moving_Average([limit[0], limit[1]], Parameters.CONST_FILTER_POS_NUM_OF_DATA))
        # Butterworth Low Pass (BLP)
        BLP.append(Filter.Butterworth_Low_Pass([limit[0], limit[1]], Parameters.CONST_FILTER_POS_NUM_OF_DATA, 1/Essential_Reality.CONST_TIME_STEP, 2.5, 3))
        # Butterworth Low Pass Moving Average (BLPMA)
        BLPMA.append(Filter.Butterworth_Low_Pass_Moving_Average([limit[0], limit[1]], Parameters.CONST_FILTER_POS_NUM_OF_DATA, 50, 1/Essential_Reality.CONST_TIME_STEP, 2.5, 3))

    while P5_cls.error != True and len(x_data_rt) <= num_of_data_collections:
        # t_{0}: time start
        t_0 = time.time()

        # Actual Data (Raw)
        x_data_rt.append(P5_cls.Get_Absolute_Position_ID(0))
        y_data_rt.append(P5_cls.Get_Absolute_Position_ID(1))
        z_data_rt.append(P5_cls.Get_Absolute_Position_ID(2))
        # Filtered Data
        #   SMA
        x_data_f1_rt.append(SMA[0].Compute(P5_cls.Get_Absolute_Position_ID(0)))
        y_data_f1_rt.append(SMA[1].Compute(P5_cls.Get_Absolute_Position_ID(1)))
        z_data_f1_rt.append(SMA[2].Compute(P5_cls.Get_Absolute_Position_ID(2)))
        #   BLP
        x_data_f2_rt.append(BLP[0].Compute(P5_cls.Get_Absolute_Position_ID(0)))
        y_data_f2_rt.append(BLP[1].Compute(P5_cls.Get_Absolute_Position_ID(1)))
        z_data_f2_rt.append(BLP[2].Compute(P5_cls.Get_Absolute_Position_ID(2)))
        #   BLPMA
        x_data_f3_rt.append(BLPMA[0].Compute(P5_cls.Get_Absolute_Position_ID(0)))
        y_data_f3_rt.append(BLPMA[1].Compute(P5_cls.Get_Absolute_Position_ID(1)))
        z_data_f3_rt.append(BLPMA[2].Compute(P5_cls.Get_Absolute_Position_ID(2)))

        # t_{1}: time stop
        #   t = t_{1} - t_{0}
        t = time.time() - t_0
        
        # Recalculate the time
        if t < Essential_Reality.CONST_TIME_STEP:
            time.sleep(Essential_Reality.CONST_TIME_STEP - t)

    if P5_cls.error != True:
        data_collection = pd.DataFrame(data = {'X_DATA_RT': x_data_rt, 'X_DATA_F1_RT': x_data_f1_rt, 'X_DATA_F2_RT': x_data_f2_rt, 'X_DATA_F3_RT': x_data_f3_rt,
                                               'Y_DATA_RT': y_data_rt, 'Y_DATA_F1_RT': y_data_f1_rt, 'Y_DATA_F2_RT': y_data_f2_rt, 'Y_DATA_F3_RT': y_data_f3_rt,
                                               'Z_DATA_RT': z_data_rt, 'Z_DATA_F1_RT': z_data_f1_rt, 'Z_DATA_F2_RT': z_data_f2_rt, 'Z_DATA_F3_RT': z_data_f3_rt})
        current_directory_name = os.getcwd()
        data_collection.to_csv(current_directory_name + '\\Evaluation\\P5_Results\\' + file_name + '.txt')
        print('[INFO] The data has been successfully saved.')

def Data_Collection_Finger_Bends(P5_cls, file_name, num_of_data_collections):
    """
    Description:
        A simple function to collect finger bend data from the sensor and write it to a text file.
        
    Args:
        (1) P5_cls [P5_Glove Class]: Essential Reality P5 Glove class for sensor data collection.
        (2) file_name [String]: Output file name.
        (3) num_of_data_collections [INT]: Number of data collections.
    """

    t_data_rt = []; t_data_f1_rt = []; t_data_f2_rt = []; t_data_f3_rt = []
    i_data_rt = []; i_data_f1_rt = []; i_data_f2_rt = []; i_data_f3_rt = []
    m_data_rt = []; m_data_f1_rt = []; m_data_f2_rt = []; m_data_f3_rt = []
    r_data_rt = []; r_data_f1_rt = []; r_data_f2_rt = []; r_data_f3_rt = []
    l_data_rt = []; l_data_f1_rt = []; l_data_f2_rt = []; l_data_f3_rt = []

    SMA = []; BLP = []; BLPMA = []
    # Initialization of filters for each part.
    for _, limit in enumerate(Parameters.CONST_FILTER_FINGERS_BEND_LIMIT):
        # Simple Moving Average (SMA)
        SMA.append(Filter.Simple_Moving_Average([limit[0], limit[1]], Parameters.CONST_FILTER_POS_NUM_OF_DATA))
        # Butterworth Low Pass (BLP)
        BLP.append(Filter.Butterworth_Low_Pass([limit[0], limit[1]], Parameters.CONST_FILTER_POS_NUM_OF_DATA, 1/Essential_Reality.CONST_TIME_STEP, 2.5, 3))
        # Butterworth Low Pass Moving Average (BLPMA)
        BLPMA.append(Filter.Butterworth_Low_Pass_Moving_Average([limit[0], limit[1]], Parameters.CONST_FILTER_POS_NUM_OF_DATA, 50, 1/Essential_Reality.CONST_TIME_STEP, 2.5, 3))

    while P5_cls.error != True and len(t_data_rt) <= num_of_data_collections:
         # t_{0}: time start
        t_0 = time.time()

        # Actual Data (Raw)
        t_data_rt.append(P5_cls.Get_Fingers_Bend_ID(0))
        i_data_rt.append(P5_cls.Get_Fingers_Bend_ID(1))
        m_data_rt.append(P5_cls.Get_Fingers_Bend_ID(2))
        r_data_rt.append(P5_cls.Get_Fingers_Bend_ID(3))
        l_data_rt.append(P5_cls.Get_Fingers_Bend_ID(4))
        # Filtered Data
        #   SMA
        t_data_f1_rt.append(SMA[0].Compute(P5_cls.Get_Fingers_Bend_ID(0)))
        i_data_f1_rt.append(SMA[1].Compute(P5_cls.Get_Fingers_Bend_ID(1)))
        m_data_f1_rt.append(SMA[2].Compute(P5_cls.Get_Fingers_Bend_ID(2)))
        r_data_f1_rt.append(SMA[3].Compute(P5_cls.Get_Fingers_Bend_ID(3)))
        l_data_f1_rt.append(SMA[4].Compute(P5_cls.Get_Fingers_Bend_ID(4)))
        #   BLP
        t_data_f2_rt.append(BLP[0].Compute(P5_cls.Get_Fingers_Bend_ID(0)))
        i_data_f2_rt.append(BLP[1].Compute(P5_cls.Get_Fingers_Bend_ID(1)))
        m_data_f2_rt.append(BLP[2].Compute(P5_cls.Get_Fingers_Bend_ID(2)))
        r_data_f2_rt.append(BLP[3].Compute(P5_cls.Get_Fingers_Bend_ID(3)))
        l_data_f2_rt.append(BLP[4].Compute(P5_cls.Get_Fingers_Bend_ID(4)))
        #   BLPMA
        t_data_f3_rt.append(BLPMA[0].Compute(P5_cls.Get_Fingers_Bend_ID(0)))
        i_data_f3_rt.append(BLPMA[1].Compute(P5_cls.Get_Fingers_Bend_ID(1)))
        m_data_f3_rt.append(BLPMA[2].Compute(P5_cls.Get_Fingers_Bend_ID(2)))
        r_data_f3_rt.append(BLPMA[3].Compute(P5_cls.Get_Fingers_Bend_ID(3)))
        l_data_f3_rt.append(BLPMA[4].Compute(P5_cls.Get_Fingers_Bend_ID(4)))

        # t_{1}: time stop
        #   t = t_{1} - t_{0}
        t = time.time() - t_0
        
        # Recalculate the time
        if t < Essential_Reality.CONST_TIME_STEP:
            time.sleep(Essential_Reality.CONST_TIME_STEP - t)

    if P5_cls.error != True:
        data_collection = pd.DataFrame(data = {'T_DATA_RT': t_data_rt, 'T_DATA_F1_RT': t_data_f1_rt, 'T_DATA_F2_RT': t_data_f2_rt, 'T_DATA_F3_RT': t_data_f3_rt, 
                                               'I_DATA_RT': i_data_rt, 'I_DATA_F1_RT': i_data_f1_rt, 'I_DATA_F2_RT': i_data_f2_rt, 'I_DATA_F3_RT': i_data_f3_rt,
                                               'M_DATA_RT': m_data_rt, 'M_DATA_F1_RT': m_data_f1_rt, 'M_DATA_F2_RT': m_data_f2_rt, 'M_DATA_F3_RT': m_data_f3_rt,
                                               'R_DATA_RT': r_data_rt, 'R_DATA_F1_RT': r_data_f1_rt, 'R_DATA_F2_RT': r_data_f2_rt, 'R_DATA_F3_RT': r_data_f3_rt,
                                               'L_DATA_RT': l_data_rt, 'L_DATA_F1_RT': l_data_f1_rt, 'L_DATA_F2_RT': l_data_f2_rt, 'L_DATA_F3_RT': l_data_f3_rt})
        current_directory_name = os.getcwd()
        data_collection.to_csv(current_directory_name + '\\Evaluation\\P5_Results\\' + file_name + '.txt')
        print('[INFO] The data has been successfully saved.')
