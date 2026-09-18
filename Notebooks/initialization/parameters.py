"""
File with parameter information. If the parameters are constantly changed, the ones shown here are just dummy parameters and they are altered within the notebook whenever necessary.

Functions
---------
my_name : prints the current filename used.
brandon_name: prints Brandon's filename.
show_parameters : prints the parameter information.
"""

## ----- IMPORTS ----- ##
from imports import *



## ----- PARAMETERS : TELESCOPE MODEL ----- ##
# observation information
block = 1551055211
antenna = "m000"
# beam model (options: "emss", "cosine" or "eidos")
beam_model = "emss"


## ----- PARAMETERS : FILES ----- ##
# calibration paths
path_old = "/idia/projects/hi_im/satellite_rfi/Testing/{}/".format(block)
path_old = "results_calibration_brandon/"  # <-- personal computer
path_source = "katcali_data/{}/".format(block)
path_calibration = "results_calibration/{}/".format(block)
path_simulating = "simulating_data/"
# TLE data (specific date of TLE's to use; maybe retrieve the correct TLEs if none are given) 
path_TLEs = {1551055211: "2019_02_21_tle/",
             1553966342: "2019_03_25_tle/", 
             1554156377: "2019_03_25_tle/",
             1556138397: "2019_04_22_tle/",
             1562857793: "2019_07_09_tle/"}



## ----- PARAMETERS : FITTING ----- ##
# (the rest of the parameters that we are varying are within the notebooks themselves)
# frequency window for the alpha fitting
freq_slice = [1100, 1350]
# total frequency window
freq_range = [1000, 1500]
# temporal averaging [seconds] (options: 10,20,etc or None)
time_average = None



## ----- PARAMETERS : KATDAL INFO ----- ##
f = path_calibration + "katdal_info.p"
katdal = pickle.load(open(f,"rb"), encoding="latin1")
nd_s0 = katdal["nd_s0"]
nd_s0_coords = katdal["nd_s0_coords"]
nd_s0_coords2 = katdal["nd_s0_coords2"]
nd_s0_pos = katdal["nd_s0_pos"]
frequency = katdal["frequency"]
del katdal



## ---------------------------- ##
## ----- USEFUL FUNCTIONS ----- ##
## ---------------------------- ##

def my_name(folder, CF, deg=None, temp=None, pix=None, time_slice=(None,None)):
    ''' My file name to save alphas. '''

    # chi-sigma
    CF_name = "_" + str(CF)

    # masking
    mask_name = ""
    if deg is not None:  
        if type(deg) is int:  mask_name += "deg" + str(deg)
        else:  mask_name += "deg" + deg[0]
    if temp is not None:  mask_name += "thermal" + str(temp)
    if pix is not None:  mask_name += "pix" + str(pix)
    if (time_slice[0] is not None) or (time_slice[1] is not None):
        mask_name += "interval"
        if time_slice[0] is not None:  mask_name += str(time_slice[0])
        else:  mask_name += "{:.0f}".format(nd_s0[0])
        if time_slice[1] is not None:  mask_name += "-" + str(time_slice[1])
        else:  mask_name += "-" + "{:.0f}".format(nd_s0[-1])
    if mask_name=="":  mask_name = "nomask"

    # getting final name
    fname = folder + mask_name + CF_name + ".p"
    return fname

## ---------------------------- ##

def show_parameters(CF=None, deg=None, temp=None, pix=None, time_slice=[None,None], plotting=False):
    ''' Show parameters in the parameters.py file, formatted correctly. '''
    
    # block
    print("Block: {}".format(block))
    print("Antenna: {}".format(antenna))

    # frequency range
    f_write = []
    for f in freq_slice:
        if f is None:  f_write.append("inf")
        else:  f_write.append(str(f))
    print("Frequency range: {} - {} MHz".format(*f_write))

    # stop here if i'm plotting all the results i got so far
    if plotting: return

    # time range
    t_write = []
    for i,t in enumerate(time_slice):
        if t is None:  t_write.append("inf")
        else:  t_write.append(str(t))
    print("Time range: {} - {} seconds".format(*t_write))

    # chi-sigma
    print("The cost function denominator will be:",end=" ")
    #print("The cost function denominator will be:")
    if CF=="C1":  print("radiometer equation (C1).")
    elif CF=="C2":  print("unweighted (C2).")

    # masking
    msg = "Masking: "
    if deg is not None:  msg += "Angular ({} deg), ".format(deg)
    if temp is not None:  msg += "Thermal ({} K), ".format(temp)
    if (time_slice[0] is not None) or (time_slice[1] is not None):  msg += "Temporal (shown above), "
    if pix is not None:  msg += "Pixel timeline (Tmax/{}), ".format(pix)
    if msg=="Masking: ":  msg += "None, "
    print(msg[:-2])
    return
