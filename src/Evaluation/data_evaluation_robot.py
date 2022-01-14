# System (Default)
import sys
# Pandas (Data analysis and manipulation) [pip3 install pandas]
import pandas as pd
# Matplotlib (Visualization) [pip3 install matplotlib]
import matplotlib.pyplot as plt
# OS (Operating system interfaces)
import os

def main():
    # Plot Data:
    #   Real:
    #       'Universal_Robots_Test_R_1'
    #       'Universal_Robots_Test_R_2'
    file_name   = 'Universal_Robots_Test_R_1'

    # Read Data from the File (P5_Results Folder)
    current_directory_name = os.getcwd()
    p5_glove_data = pd.read_csv(current_directory_name + '\\Robot_Results\\' + file_name + '.txt')

    # Assign data to variables
    #   Sequence [-]
    sequence = p5_glove_data[p5_glove_data.columns[0]]
    #   Desired Position: Sensor Data
    data_desired = [p5_glove_data['X_DATA_SENSOR_RT'], p5_glove_data['Y_DATA_SENSOR_RT'], p5_glove_data['Z_DATA_SENSOR_RT']]
    #   Actual Position: Robota Data
    data_actual = [p5_glove_data['X_DATA_ROBOT_RT'], p5_glove_data['Y_DATA_ROBOT_RT'], p5_glove_data['Z_DATA_ROBOT_RT']]

    # Set axis names: Depends on the input file
    AXIS_NAME = ['X (m)', 'Y (m)', 'Z (m)']

    ax_vector = [0]*len(data_actual)

    # Create figure with multiple subplots
    fig, (ax_vector) = plt.subplots(len(ax_vector), 1)
    fig.suptitle(f'File name: {file_name}.txt', fontsize = 20)

    for i, ax in enumerate(ax_vector):
        ax.plot(sequence, data_desired[i], '-', linewidth=1.0, color=[0.2,0.4,0.6,1.0], label='Desired Position')
        ax.plot(sequence, data_actual[i], '-', linewidth=1.0, color=[0.8,0.4,0.0,1.0], label='Actual Position')
        ax.grid(linewidth = 0.75, linestyle = '--')
        ax.set_xlabel(r'Sequence (-)')
        ax.set_ylabel(f'{AXIS_NAME[i]}')
        ax.legend()

    # Display the result
    plt.show()

if __name__ == '__main__':
    sys.exit(main())