NOTEBOOK FOR GENERATING CALIBRATED DATA BACKGROUND MODEL
Contact: 
Author: Brandon Engelbrecht; engelbechtbn@gmail.com
Supervisor: Mario Santos
Co-supervisor: Jingying Wang, Jose Fonseca

Overview:
This notebook looks at re-calibrating and inserting the missing RFI information in the gain and raw visibilitiy maps for the 2019 observation
and found in HI intensity mapping with MeerKAT: Calibration pipeline for multi-dish autocorrelation observations: https://arxiv.org/abs/2011.13789

Required Files:
wiggleZ_area.py - 
- This file outputs the necessary time and frequency information of the survey. Paticularly looking at time dumps for the noise diodes. Here we are only focusing on the nd_S0 (noise diodes during scan period switched off)
- The file is run automatically from the notebook, any questions pertaining to this file should be asked to Brandon Engelbrecht or Dr Jingying Wang

data_reduction.py - 
- A class which extracts various componants of the data
- Requires file name <fname> (see notebook)
    
Notebooks:
Generating_Calibrated_Data_BGM_play.ipynb

The notebook revolves around extracting necessary information for example: Positional, Temporal and Frequency information. The information is cut only from 1000-1500 MHz. 
    
The raw visibilities, gain and background model
Background model:
    Receiver, Elevation, Galactic
    The receiver temperature is missing information and requires a radial bases function fitting in order to fill that in.
    
    Elevation 
    Requires re-running a code of Jingying Wang and filling in that information
    All the information is stored at an open location
    
    Galactic
    Does not require changes
    
Gain calculation:
    A comparison is done between the raw visibility and gain information.
    Gain calculation is done on overlay
    
    
    
To be continued.........
    

