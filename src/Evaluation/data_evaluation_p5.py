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
File Name: data_evaluation_p5.py
## =========================================================================== ## 
"""

# System (Default)
import sys
# Pandas (Data analysis and manipulation) [pip3 install pandas]
import pandas as pd
# Matplotlib (Visualization) [pip3 install matplotlib]
import matplotlib.pyplot as plt
# SciencePlots (Matplotlib styles for scientific plotting) [pip3 install SciencePlots]
import scienceplots
# OS (Operating system interfaces)
import os

def main():
    # Plot Data:
    #   'Experiment_Position'         
    #   'Experiment_Finger_Bends'
    file_name   = 'Experiment_Position'
    # 'P5_Results' or 'P5_Sub_Results'
    folder_name = 'P5_Results'

    # Read Data from the File (P5_Results Folder)
    current_directory_name = os.getcwd()
    p5_glove_data = pd.read_csv(current_directory_name + '\\' + folder_name + '\\' + file_name + '.txt')

    # Assign data to variables
    #   Sequence [-]
    sequence = p5_glove_data[p5_glove_data.columns[0]]
    if file_name == 'Experiment_Position':
        #   Raw Data
        data_actual = [p5_glove_data['X_DATA_RT'], p5_glove_data['Y_DATA_RT'], p5_glove_data['Z_DATA_RT']]
        #   Filtered Data
        data_filtered_1 = [p5_glove_data['X_DATA_F1_RT'], p5_glove_data['Y_DATA_F1_RT'], p5_glove_data['Z_DATA_F1_RT']]
        data_filtered_2 = [p5_glove_data['X_DATA_F2_RT'], p5_glove_data['Y_DATA_F2_RT'], p5_glove_data['Z_DATA_F2_RT']]
        data_filtered_3 = [p5_glove_data['X_DATA_F3_RT'], p5_glove_data['Y_DATA_F3_RT'], p5_glove_data['Z_DATA_F3_RT']]
    elif file_name == 'Experiment_Finger_Bends':
        #   Raw Data
        data_actual = [p5_glove_data['T_DATA_RT'], p5_glove_data['I_DATA_RT'], p5_glove_data['M_DATA_RT'], p5_glove_data['R_DATA_RT'], p5_glove_data['L_DATA_RT']]
        #   Filtered Data
        data_filtered_1 = [p5_glove_data['T_DATA_F1_RT'], p5_glove_data['I_DATA_F1_RT'], p5_glove_data['M_DATA_F1_RT'], p5_glove_data['R_DATA_F1_RT'], p5_glove_data['L_DATA_F1_RT']]
        data_filtered_2 = [p5_glove_data['T_DATA_F2_RT'], p5_glove_data['I_DATA_F2_RT'], p5_glove_data['M_DATA_F2_RT'], p5_glove_data['R_DATA_F2_RT'], p5_glove_data['L_DATA_F2_RT']]
        data_filtered_3 = [p5_glove_data['T_DATA_F3_RT'], p5_glove_data['I_DATA_F3_RT'], p5_glove_data['M_DATA_F3_RT'], p5_glove_data['R_DATA_F3_RT'], p5_glove_data['L_DATA_F3_RT']]

    # Set axis names: Depends on the input file
    if file_name == 'Experiment_Position':
        AXIS_NAME = ['X (cm)', 'Y (cm)', 'Z (cm)']
    elif file_name == 'Experiment_Finger_Bends':
        AXIS_NAME = ['T (-)', 'I (-)', 'M (-)', 'R (-)', 'L (-)']

    ax_vector = [0]*len(data_actual)

    # Set the parameters for the scientific style.
    plt.style.use(['science'])

    # Create figure with multiple subplots
    fig, (ax_vector) = plt.subplots(len(ax_vector), 1)

    for i, ax in enumerate(ax_vector):
        ax.plot(sequence, data_actual[i], '-', linewidth=1.0, color=[0.2,0.4,0.6,0.50], label='Raw Data')
        ax.plot(sequence, data_filtered_1[i], '-', linewidth=1.0, color=[1.0,0.85,0.75,1.0], label='Filtered Data: SMA')
        ax.plot(sequence, data_filtered_2[i], '-', linewidth=1.0, color=[1.0,0.75,0.5,1.0], label='Filtered Data: BLP')
        ax.plot(sequence, data_filtered_3[i], '-', linewidth=1.0, color=[0.8,0.4,0.0,1.0], label='Filtered Data: BLPMA')
        ax.grid(which='major', linewidth = 0.15, linestyle = '--')
        ax.set_xlabel(r'Sequence (-)', fontsize=15, labelpad=10)
        ax.set_ylabel(f'{AXIS_NAME[i]}', fontsize=15, labelpad=10)
        ax.legend()

    # Display the result
    plt.show()

if __name__ == '__main__':
    sys.exit(main())
