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


## ----- PARAMETERS : FILES ----- ##
# observational block
block = 1551055211
# folders and files
path_data = "/idia/projects/hi_im/satellite_rfi/Testing/"+str(block)+"/"


## ----- PARAMETERS : FITTING ----- ##
# (the rest of the parameters that we are varying are within the notebooks themselves)
# frequency window for the alpha fitting
fs_slice, fe_slice = 1100, 1350
# total frequency window
fs, fe = 1000, 1500
# temporal averaging [seconds] (options: 10,20,etc or None)
time_average = None  # <-- NÃO ESTÁ NO CÓDIGO


## ----- PARAMETERS : SATELLITE MODEL ----- ##
# beam model (options: "emss", "cosine" or "eidos")
beam_model = "emss"
# constellations to include (options: "gps-ops","glo-ops","galileo","beidou","irnss","sbas","qzs")
include_cons = ['gps-ops', 'glo-ops', 'galileo', 'beidou', 'irnss', 'sbas']


## ----- PARAMETERS : KATDAL INFO ----- ##
f = path_data + str(block) + "_katdal_info.p"
if sys.version_info.major == 2:  katdal = pickle.load(open(f,"rb"))
elif sys.version_info.major == 3:  katdal = pickle.load(open(f,"rb"), encoding="latin1")
nd_s0 = katdal["nd_s0"]
nd_s0_coords = katdal["nd_s0_coords"]
nd_s0_coords2 = katdal["nd_s0_coords2"]
nd_s0_pos = katdal["nd_s0_pos"]
frequency = katdal["frequency"]
del katdal


## ---------------------------- ##
## ----- USEFUL FUNCTIONS ----- ##
## ---------------------------- ##

def my_name(folder, CF, deg=None, temp=None, pix=None, t_slice=[None,None]):
    ''' My file name to save alphas. '''

    # chi-sigma
    CF_name = "_" + CF

    # masking
    mask_name = ""
    if deg is not None:  mask_name += "deg{}".format(deg[0])
    if temp is not None:  mask_name += "thermal{}".format(temp)
    if pix is not None:  mask_name += "pix{}".format(pix)
    if (t_slice[0] is not None) or (t_slice[1] is not None):
        mask_name += "interval"
        if t_slice[0] is not None:  mask_name += "{}".format(t_slice[0])
        else:  mask_name += "{:.0f}".format(nd_s0[0])
        if t_slice[1] is not None:  mask_name += "-{}".format(t_slice[1])
        else:  mask_name += "-{:.0f}".format(nd_s0[-1])
    if mask_name=="":  mask_name = "nomask"

    # getting final name
    fname = folder + mask_name + CF_name + ".p"
    return fname

## ---------------------------- ##

def brandon_name(folder, CF, deg=None, temp=None, pix=None, t_slice=[None,None]):
    ''' Brandon's file name to save alphas, according to the parameters in the parameters.py file. '''
    
    # frequency range
    freq_name = str(fs_slice) + "-" + str(fe_slice) + "_"

    # time range
    t_name = []
    for i,t in enumerate(t_slice):
        if t is None:  t_name.append(str(np.round(nd_s0[-i], 2)))
        else:  t_name.append(str(t))
    time_name = t_name[0]+"-"+t_name[1]+"_"

    # time averaging
    if time_average is not None:  time_average_name = "time_average_{}_".format(time_average)
    else:  time_average_name = ""

    # chi-sigma
    if CF == "C1":  CF_name = "residual_"
    elif CF == "C2":  CF_name = "fractional_"

    # masking
    mask_name = ""
    if deg is not None:  mask_name += "degree-{}_".format(deg)
    if temp is not None:  mask_name += "thermal-{}_".format(temp)
    if (t_slice[0] is not None) or (t_slice[1] is not None):  mask_name += "temporal_"
    if pix is not None:  mask_name += "pix_timeline-{}_".format(pix)
    if mask_name=="":  mask_name = "no-mask_"

    # show ideal file name
    fname = (path_data + folder + "{}_".format(block) + freq_name + time_name + mask_name + 
             CF_name + time_average_name + ".p")
    return fname

## ---------------------------- ##

def show_parameters(CF=None, deg=None, temp=None, pix=None, t_slice=[None,None], plotting=False):
    ''' Show parameters in the parameters.py file, formatted correctly. '''
    
    # block
    print("Block: {}".format(block))

    # frequency range
    f_write = []
    for f in [fs_slice,fe_slice]:
        if f is None:  f_write.append("inf")
        else:  f_write.append(str(f))
    print("Frequency range: {} - {} MHz".format(*f_write))

    # stop here if i'm plotting all the results i got so far
    if plotting: return

    # time range
    t_write = []
    for i,t in enumerate(t_slice):
        if t is None:  t_write.append("inf")
        else:  t_write.append(str(t))
    print("Time range: {} - {} seconds".format(*t_write))

    # chi-sigma
    print("The cost function denominator will be:",end=" ")
    if CF=="C1":  print("radiometer equation (C1).")
    elif CF=="C2":  print("unweighted (C2).")

    # masking
    msg = "Masking: "
    if deg is not None:  msg += "Angular ({} deg), ".format(deg)
    if temp is not None:  msg += "Thermal ({} K), ".format(temp)
    if (t_slice[0] is not None) or (t_slice[1] is not None):  msg += "Temporal (shown above), "
    if pix is not None:  msg += "Pixel timeline, "
    if msg=="Masking: ":  msg += "None, "
    print(msg[:-2])
    return
