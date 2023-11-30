# Robotic Teleoperation Based on the P5 Essential Reality Robotic Gloves

<p align="center">
<img src=https://github.com/rparak/UR10e_Robotic_Teleoperation/blob/main/images/Background.png width="800" height="450">
</p>

## Requirements

**Programming Language**

```bash
Python (32 bit. and 64 bit.)
```

**Import Libraries**
```bash
More information can be found in the individual scripts (.py).
```

**Supported on the following operating systems**
```bash
Windows
```

## Project Description

A human-robot interaction system for robotic teleoperation based on the P5 Essential Reality robotic glove to control the UR10e collaborative robot. The project was created primarily for Children's University as an explanation of how humans can work with robots without boundaries. The project included data analysis, signal processing, robot control, etc.

The project architecture was created based on publisher/subscriber communication between two Python programs. One of the programs was based on the 32-bit version, and the other one on the 64-bit version. The main reason for this solution was that the '*.dll' file was created based on the 32-bit version, and the universal robot control library can only be installed on a 64-bit version of Python. Communication between Python programs is realized through the ZMQ library.

**Warning!**

It is necessary to copy and paste the P5DLL.dll file into the 'C:\Windows\SysWOW64' directory.

<p align="center">
<img src=https://github.com/rparak/UR10e_Robotic_Teleoperation/blob/main/images/scheme.png width="800" height="450">
</p>

The solution can be used to control a real robot or to simulate one (using VMware <-> UR Polyscope on Windows).

**Essential Reality P5 Glove:**
 - The P5 virtual reality gloves are data gloves suitable for gaming and 3D virtual environments. 
 - The gloves contain two infrared sensors. They detect the visible LEDs on the glove (there are eight in total) and convert them to the position (x, y, z) and orientation in terms of pitch, yaw and roll. The glove also has bend sensors in the fingers and four buttons on the top. 
 - Communication between the gloves and the application on the computer is via USB port.

More information about signal processing filters, such as SMA (Simple Moving Average), BLP (Butterworth Low Pass), and BLPMA (Butterworth Low Pass Moving Average), can be found in the repository below:
[/rparak/Simple_Signal_Processing](https://github.com/rparak/Simple_Signal_Processing)

The project was realized at the Institute of Robotics, Johannes Kepler University in Linz as part of an Erasmus+ research internship.

## Project Hierarchy

**../DLL/**

A dynamic-link library (DLL) designed by the company that created the 'P5 Essential Reality' robotic glove to collect data using various programming languages.

**../src/Lib/**

The main part of the project, which includes the library to collect the data from the robotic gloves, a library for signal processing, and other useful utilities.

**../src/Evaluation/**

Programs to evaluate the collected data from the robotic gloves as well as from the collaborative robot

**../src/UR/**

A simple program to evaluate the safe area of the robot workspace.

**../src/**

Main programs (scripts) for data collection and robot control.

## Data Evaluation

The figure below shows the collection of position data (x, y, z) from the gloves and the use of different types of designed filters to filter the raw data.

<p align="center">
<img src=https://github.com/rparak/UR10e_Robotic_Teleoperation/blob/main/images/Data_Evaluation/Figure_1_P5_Position.svg width="800" height="450">
</p>

The figure below shows the collection of finger bends data (T, I, M, R, L) from the gloves and the use of different types of designed filters to filter the raw data.

<p align="center">
<img src=https://github.com/rparak/UR10e_Robotic_Teleoperation/blob/main/images/Data_Evaluation/Figure_1_P5_Finger_Bends.svg width="800" height="450">
</p>

The figure below illustrates the position control of the collaborative robot, depending on the filtered data from the robotic gloves.

<p align="center">
<img src=https://github.com/rparak/UR10e_Robotic_Teleoperation/blob/main/images/Data_Evaluation/Figure_1_Robot.svg width="800" height="450">
</p>

## Simulation

<p align="center">
 <img src=https://github.com/rparak/UR10e_Robotic_Teleoperation/blob/main/images/Simulation/Simulation_UR.png width="800" height="450">
</p>

## Real-World Application

<p align="center">
 <img src=https://github.com/rparak/UR10e_Robotic_Teleoperation/blob/main/images/Real_World/Setup.JPG width="575" height="400">
 <img src=https://github.com/rparak/UR10e_Robotic_Teleoperation/blob/main/images/Real_World/Env_1.JPG width="575" height="400">
</p>

## Children's University

<p align="center">
 <img src=https://github.com/rparak/UR10e_Robotic_Teleoperation/blob/main/images/DOD/DOD_1.JPG width="575" height="400">
 <img src=https://github.com/rparak/UR10e_Robotic_Teleoperation/blob/main/images/DOD/DOD_2.JPG width="575" height="400">
</p>

## YouTube

<p align="center">
  <a href="https://www.youtube.com/watch?v=FrP-bRYXE3I">
    <img src=https://github.com/rparak/UR10e_Robotic_Teleoperation/blob/main/images/YouTube.png width="275" height="200">
  </a>
</p>

## Contact Info
Roman.Parak@outlook.com

## Citation (BibTex)
```bash
@misc{RomanParak_UR10e_Robotic_Teleoperation,
  author = {Roman Parak},
  title = {Human-robot interaction system for robotic teleoperation},
  year = {2021},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://https://github.com/rparak/UR10e_Robotic_Teleoperation
}}
}
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
