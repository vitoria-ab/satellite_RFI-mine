Stage 1 README file for the reCalibration_Data code 

See Jupyter Notebook: Generating_Calibrated_Data_BGM.ipynb

Note: A PDF will be constructed for further details in this section (Pending)

Essentially this section looks at the work done by Dr. Jingying Wang for the MeerKLASS pilot pilot survey. The outputs from this work becomes our input. This section looks at a pseudo re-calibration process of the data in order to maintain the RFI zones around 1000-1500 MHz which is masked out in the original data.

The code mianly requires the katdal software which is inside the HI_IM PY2 containter to run succesfully on ILIFU.
OR
Data is stored here: /idia/projects/hi_im/brandon

All data is on ILIFU for the inputs and therefore all paths are focused on the data. 
NOTE that data requires user access. If so speak to Prof. Mario Santos 

Required Files:
wiggleZ_area.py - 
    This file outputs the necessary time and frequency information of the survey.     
    Paticularly looking at time dumps for the noise diodes. 
    Here we are only focusing on the nd_S0 (noise diodes during scan period switched off)

data_reduction.py - 
    A class which extracts various componants of the data
    
Information is commented into the files and folder.
The notebook "Generating_Calibrated_Data_BGM.ipynb" should be run.