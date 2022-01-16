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
File Name: Filter.py
## =========================================================================== ## 
"""

# Numpy (Array computing) [pip3 install numpy]
import numpy as np
# Scipy (Mathematics, science, etc.) [pip install scipy]
import scipy.signal
# Random (Generate pseudo-random numbers)
import random

def Check_Limit(value, limit, data_stack):
    """
    Description:
        Input data limit check.

    Args:
        (1) value [Float]: Raw value from the sensor.
        (2) limit [Float Vector]: Limit (Boundaries [low(-),high(+)]).
        (3) data_stack [Float Vector]: Data stack of values.
        
    Returns:
        (1) parameter [Float]: New value after limit check.

    """

    if limit[0] <= value <= limit[1]:
        # Return input value (everything is fine).
        return value #if data_stack and value != data_stack[-1] else value + offset
    else:
        # If the value is out of range, set a random offset and add it to the previous value.
        offset = random.choice([-1, 1]) * 0.01
        
        # Return the modified value.
        return data_stack[-1] + offset if data_stack else offset

class Butterworth_Low_Pass_Moving_Average(object):
    """
    Description:
        The Butterworth Low Pass Moving Average filter is a type of signal processing filter
        that combines (extends) the default Butterworth filter with a moving average.

    Initialization of the Class:
        Args:
            (1) limit [Float Vector]: Limit (Boundaries: [Lower Value{-}, Upper Value{+}]).
            (2) num_of_data_blp [INT]: Number of total periods (BLP).
            (3) num_of_data_avg [INT]: Number of total periods (SMA).
            (4) frq_s [INT]: Sample frequency in Hz.
            (5) frq_c [Float]: Cut-off frequency in Hz.
            (6) order [INT]: Order of the butterworth filter.

        Example:
            Initialization:
                Cls = Butterworth_Low_Pass_Moving_Average(limit = [-25.0, 25.0], num_of_data_blp = 100, num_of_data_avg = 10, frq_s = 100, frq_c = 1.0, order = 2)

            Calculation:
                Cls.Compute(value{0})
                ...
                Cls.Compute(value{n})
    """

    def __init__(self, limit = [-25.0, 25.0], num_of_data_blp = 100, num_of_data_avg = 10, frq_s = 100, frq_c = 1.0, order = 2):
        # << PRIVATE >> #
        # Simple moving average (SMA): More information below
        self.__SMA = Simple_Moving_Average(limit, num_of_data_avg)
        # Number of total periods
        self.__num_of_data = num_of_data_blp
        # The normalized value of a frequency variable: f_c/f_s
        #   Note: Nyquist frequency f_s/2
        self.__w_c_normalized = frq_c / (frq_s/2)
        # Order of the butterworth filter
        self.__order = order
        # New value after limit check
        self.__new_value = 0
        # Data stack of values
        self.__data_stack  = []
    
    def Compute(self, value):
        """
        Description:
            Main function to calculate the Butterworth low-pass moving average (BLPMA).

        Args:
            (1) value [Float]: Raw value from the sensor.
        
        Returns:
            (1) parameter [Float]: The new value of the BLP model.
        """

        # Calculate the simple moving average (SMA) from the input raw variable.
        self.__new_value = self.__SMA.Compute(value)

        # Add new data to the stack
        self.__data_stack.append(self.__new_value)

        if len(self.__data_stack) > self.__num_of_data:
            # Remove of the first element of the stack
            self.__data_stack.pop(0)
        
        """
        Note:
            b, a = scipy.signal.butter() -> Transfer function coefficients of the filter.
        """
        return scipy.signal.lfilter(*scipy.signal.butter(self.__order, self.__w_c_normalized, btype='lowpass', analog=False), 
                                    self.__data_stack)[-1]


class Butterworth_Low_Pass(object):
    """
    Description:
        The Butterworth filter is a type of signal processing filter designed to have a frequency response 
        that is as flat as possible in the passband. 

    Initialization of the Class:
        Args:
            (1) limit [Float Vector]: Limit (Boundaries: [Lower Value{-}, Upper Value{+}]).
            (2) num_of_data [INT]: Number of total periods.
            (3) frq_s [INT]: Sample frequency in Hz.
            (4) frq_c [Float]: Cut-off frequency in Hz.
            (5) order [INT]: Order of the butterworth filter.

        Example:
            Initialization:
                Cls = Butterworth_Low_Pass(limit = [-25.0, 25.0], num_of_data = 100, frq_s = 100, frq_c = 1.0, order = 2)

            Calculation:
                Cls.Compute(value{0})
                ...
                Cls.Compute(value{n})
    """

    def __init__(self, limit = [-25.0, 25.0], num_of_data = 100, frq_s = 100, frq_c = 1.0, order = 2):
        # << PRIVATE >> #
        # Limit (Boundaries [low(-),high(+)])
        self.__limit = limit
        # Number of total periods
        self.__num_of_data = num_of_data
        # The normalized value of a frequency variable: f_c/f_s
        #   Note: Nyquist frequency f_s/2
        self.__w_c_normalized = frq_c / (frq_s/2)
        # Order of the butterworth filter
        self.__order = order
        # New value after limit check
        self.__new_value = 0
        # Data stack of values
        self.__data_stack  = []

    def Compute(self, value):
        """
        Description:
            Main function to calculate the Butterworth low-pass filter (BLP).

        Args:
            (1) value [Float]: Raw value from the sensor.
        
        Returns:
            (1) parameter [Float]: The new value of the BLP model.
        """

        # Input data limit check
        self.__new_value = Check_Limit(value, self.__limit, self.__data_stack)

        # Add new data to the stack
        self.__data_stack.append(self.__new_value)

        if len(self.__data_stack) > self.__num_of_data:
            # Remove of the first element of the stack
            self.__data_stack.pop(0)
        
        """
        Note:
            b, a = scipy.signal.butter() -> Transfer function coefficients of the filter.
        """
        return scipy.signal.lfilter(*scipy.signal.butter(self.__order, self.__w_c_normalized, btype='lowpass', analog=False), 
                                    self.__data_stack)[-1]

class Simple_Moving_Average(object):
    """
    Description:
        The simplest form of moving average, known as the simple moving average (SMA), 
        is calculated by arithmetically averaging a given set of values over a period of 
        time. In other words, a set of numbers is added together and then divided by the number 
        of values  in the set. 

        SMA = (A_1 + A2 + ... + A_n) / n

        where {A_n} is the value of the asset in period {n} and {n} is the number of all periods.

    Initialization of the Class:
        Args:
            (1) limit [Float Vector]: Limit (Boundaries: [Lower Value{-}, Upper Value{+}]).
            (2) num_of_data [INT]: Number of total periods.

        Example:
            Initialization:
                Cls = Simple_Moving_Average(limit = [-25.0, 25.0], num_of_data = 100)

            Calculation:
                Cls.Compute(value{0})
                ...
                Cls.Compute(value{n})
    """

    def __init__(self, limit = [-25.0, 25.0], num_of_data = 100):
        # << PRIVATE >> #
        # Limit (Boundaries [low(-),high(+)])
        self.__limit = limit
        # Number of total periods
        self.__num_of_data = num_of_data
        # New value after limit check
        self.__new_value = 0
        # Sum of all values
        self.__sum = 0
        # Data stack of values
        self.__data_stack  = []

    def Compute(self, value):
        """
        Description:
            Main function to calculate the Simple moving average (SMA).

        Args:
            (1) value [Float]: Raw value from the sensor.
        
        Returns:
            (1) parameter [Float]: The new value of the SMA model.
        """

        # Input data limit check
        self.__new_value = Check_Limit(value, self.__limit, self.__data_stack)

        # Add new data to the stack
        self.__data_stack.append(self.__new_value)
        # Calculation of the sum of the current data
        self.__sum += self.__new_value 

        if len(self.__data_stack) > self.__num_of_data:
            # Remove of the first element and recalculate the sum of the new stack
            self.__sum -= self.__data_stack.pop(0)  

        return np.float64(self.__sum) / len(self.__data_stack)
