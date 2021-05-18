# satellite_RFI
2021/05/04 - Satellite RFI code for MeerKLASS

The code setup is divided into three stages:

Stage 1:
Calibration of the MeerKLASS data [reCalibration_Data].

Stage 2:
Calculating the positioning of the satellites with respect to the MeerKAT pointing [GNSS_position].

Stage 3:
Simulation construction of satellites and fitting to observational data [Satellite_simulations].

Requirements to run:
1. In order to run all 3 stages you need access to the ILIFU cluster.
2. The "HI_IM PY2" container should be used to run.
3. The observational data is stored currently at "/idia/projects/hi_im/brandon/<specific_folder_names>"

Each folder has a unique README file with more details.

For further questions contact Brandon Engelbrecht (engelbrechtbn@gmail.com) 
