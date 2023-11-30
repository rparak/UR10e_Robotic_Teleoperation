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
File Name: Parameters.py
## =========================================================================== ## 
"""

# Filter Paramteres: Limit (Boundaries [-,+]), Number of total periods
#   Position
CONST_FILTER_POS_LIMIT = [[-22.5, 22.5], [0.0, 45.0], [-45.0, 0.0]]
CONST_FILTER_POS_NUM_OF_DATA = 100
#   Fingers Bend
CONST_FILTER_FINGERS_BEND_LIMIT = [[5.0, 65.0], [5.0, 65.0], [5.0, 65.0], [5.0, 65.0], [5.0, 65.0]]
CONST_FILTER_FINGERS_BEND_NUM_OF_DATA = 25

# Time step inside threads (Essential Reality P5)
CONST_TIME_STEP  = 0.004

# Initialization of Constants:-+
#   Universal Robots (UR10e)
#       Workspace
CONST_UR_WORKSPACE          = [760.0, 400.0, 200.0]
#       Position and Orientation
CONST_UR_CARTES_POS_HOME    = [0.0, -700.0, 515.0]
CONST_UR_CARTES_ORIENT_HOME = [0.0, 3.142, 0.0]
#   Essential Reality P5 Glove
CONST_SENSOR_POS_WORKSPACE  = CONST_FILTER_POS_LIMIT
