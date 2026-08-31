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


## ----- PARAMETERS : FITTING ----- ##
# (the rest of the parameters that we are varying are within the notebooks themselves)
# frequency window for the alpha fitting
freq_slice = [1100, 1350]
# total frequency window
freq_range = [1000, 1500]
# temporal averaging [seconds] (options: 10,20,etc or None)
time_average = None


## ----- PARAMETERS : SATELLITE MODEL ----- ##
# beam model (options: "emss", "cosine" or "eidos")
beam_model = "emss"


## ----- PARAMETERS : FILES ----- ##
# observation data (options: 1551055211 (original), 1553966342, 1554156377, 1556138397, 1562857793)
block = 1551055211
path_data = "/idia/projects/hi_im/satellite_rfi/Testing/{}/".format(block)
path_observations = path_data + "{}_average_TOD_BG_model.p".format(block)
# simulation data
folder = "simulation_data/"
# calibration paths
path_cali = "results_calibration/{}/".format(block)


## ----- PARAMETERS : KATDAL INFO ----- ##
f = path_cali + "katdal_info.p"
katdal = pickle.load(open(f,"rb"), encoding="latin1")
nd_s0 = katdal["nd_s0"]
nd_s0_coords = katdal["nd_s0_coords"]
nd_s0_coords2 = katdal["nd_s0_coords2"]
nd_s0_pos = katdal["nd_s0_pos"]
frequency = katdal["frequency"]
del katdal


## ----- PARAMETERS : OBSERVATION ----- ##
TL_longitude = 21.0 + 26.0 / 60.0 + 38.00 / 3600.0
TL_latitude = -(30.0 + 42.0 / 60.0 + 47.41 / 3600.0)


## ---------------------------- ##
## ----- USEFUL FUNCTIONS ----- ##
## ---------------------------- ##

def my_name(folder, CF, deg=None, temp=None, pix=None, time_slice=(None,None)):
    ''' My file name to save alphas. '''

    # chi-sigma
    CF_name = "_" + CF

    # masking
    mask_name = ""
    if deg is not None:  
        if type(deg) is int:  mask_name += "deg" + deg
        else:  mask_name += "deg" + deg[0]
    if temp is not None:  mask_name += "thermal" + temp
    if pix is not None:  mask_name += "pix" + pix
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

def brandon_name(folder, CF, deg=None, temp=None, pix=None, time_slice=[None,None]):
    ''' Brandon's file name to save alphas, according to the parameters in the parameters.py file. '''
    
    # frequency range
    freq_name = f"{freq_slice[0]}-{freq_slice[1]}_"

    # time range
    t_name = []
    for i,t in enumerate(time_slice):
        if t is None:  t_name.append(str(np.round(nd_s0[-i], 2)))
        else:  t_name.append(str(t))
    time_name = f"{t_name[0]}-{t_name[1]}_"

    # time averaging
    if time_average is not None:  time_average_name = f"time_average_{time_average}_"
    else:  time_average_name = ""

    # chi-sigma
    if CF == "C1":  CF_name = "residual_"
    elif CF == "C2":  CF_name = "fractional_"

    # masking
    mask_name = ""
    if deg is not None:  mask_name += f"degree-{deg}_"
    if temp is not None:  mask_name += f"thermal-{temp}_"
    if (time_slice[0] is not None) or (time_slice[1] is not None):  mask_name += "temporal_"
    if pix is not None:  mask_name += f"pix_timeline-{pix}_"
    if mask_name=="":  mask_name = "no-mask_"

    # show ideal file name
    fname = (path_data + folder + f"{block}_" + freq_name + time_name + mask_name + 
             CF_name + time_average_name + ".p")
    return fname

## ---------------------------- ##

def show_parameters(CF=None, deg=None, temp=None, pix=None, time_slice=[None,None], plotting=False):
    ''' Show parameters in the parameters.py file, formatted correctly. '''
    
    # block
    print(f"Block: {block}")

    # frequency range
    f_write = []
    for f in freq_slice:
        if f is None:  f_write.append("inf")
        else:  f_write.append(str(f))
    print(f"Frequency range: {f_write[0]} - {f_write[1]} MHz")

    # stop here if i'm plotting all the results i got so far
    if plotting: return

    # time range
    t_write = []
    for i,t in enumerate(time_slice):
        if t is None:  t_write.append("inf")
        else:  t_write.append(str(t))
    print(f"Time range: {t_write[0]} - {t_write[1]} seconds")

    # chi-sigma
    print("The cost function denominator will be:",end=" ")
    #print("The cost function denominator will be:")
    if CF=="C1":  print("radiometer equation (C1).")
    elif CF=="C2":  print("unweighted (C2).")

    # masking
    msg = "Masking: "
    if deg is not None:  msg += f"Angular ({deg} deg), "
    if temp is not None:  msg += f"Thermal ({temp} K), "
    if (time_slice[0] is not None) or (time_slice[1] is not None):  msg += "Temporal (shown above), "
    if pix is not None:  msg += f"Pixel timeline (Tmax/{pix}), "
    if msg=="Masking: ":  msg += "None, "
    print(msg[:-2])
    return
