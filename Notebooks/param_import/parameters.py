"""
File with parameter information.

Functions
---------
show_ideal_name : prints the ideal saving file name.
show_parameters : prints the parameter information.
"""

## ----- IMPORTS ----- ##
from imports import *


## ----- PARAMETERS : FILES ----- ##
# observational block
block = 1551055211
# folders and files
path_data = "/idia/projects/hi_im/satellite_rfi/Testing/"+str(block)+"/"
path_catalog  = "Satellite_Catalogue/satellite_constellation_catalog.csv"
# final results
folder_results = "sat_12/"
suffix_results = "vitoria"


## ----- PARAMETERS : FITTING ----- ##
# cost function from eq. 11 (options: True=radiometer(C1), False=1(C2))
CF_case = "C2"
# frequency window for the alpha fitting
fs_slice, fe_slice = 1100, 1350
# total frequency window
fs, fe = 1000, 1500
# angular mask [degrees] (options: "1F","5F" or None)
mask_degree = None
if mask_degree==None:  path_nearby = None
else:  path_nearby = (path_data+"nearby_satellites/nearby_satellite_close_angle_"+mask_degree+".p")
# thermal mask [kelvin] (options: 100,50,25 or None)
mask_temperature = None
# temporal mask [seconds] (options: 1000,1200,etc or None)
ts_slice, te_slice = 5500,6200
# threshold pixel mask (options: 2,5,7 or None)
mask_pix = None
# temporal averaging [seconds] (options: 10,20,etc or None)
time_average = None  # <-- NÃO ESTÁ NO CÓDIGO


## ----- PARAMETERS : SATELLITE MODEL ----- ##
# beam model (options: "emss", "cosine" or "eidos")
beam_model = "emss"
# constellations to include (options: "gps-ops","glo-ops","galileo","beidou","irnss","sbas","qzs"
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


## ---------------------------- ##
## ----- USEFUL FUNCTIONS ----- ##
## ---------------------------- ##

def my_name():
    ''' My file name to save alphas. '''

    # chi-sigma
    if CF_case=="C1":  CF_name = "_C1"
    elif CF_case=="C2":  CF_name = "_C2"

    # masking
    mask_name = ""
    if mask_degree is not None:  mask_name += "_deg{}".format(mask_degree[0])
    if mask_temperature is not None:  mask_name += "_thermal{}".format(mask_temperature)
    if mask_pix is not None:  mask_name += "_pix{}".format(mask_pix)
    if (ts_slice is not None) or (te_slice is not None):
        mask_name += "_interval"
        if ts_slice is not None:  mask_name += "{}".format(ts_slice)
        else:  mask_name += "{:.0f}".format(nd_s0[0])
        if te_slice is not None:  mask_name += "-{}".format(te_slice)
        else:  mask_name += "-{:.0f}".format(nd_s0[-1])
    if mask_name=="":  mask_name = "_nomask"

    # getting final name
    fname = ("results/vi" + mask_name + CF_name + ".p")
    return fname
    

def brandon_name():
    ''' Brandon's file name to save alphas, according to the parameters in the parameters.py file. '''

    # frequency range
    freq_name = str(fs_slice) + "-" + str(fe_slice) + "_"

    # time range
    t_name = []
    for i,t in enumerate([ts_slice,te_slice]):
        if t is None:  t_name.append(str(np.round(nd_s0[-i], 2)))
        else:  t_name.append(str(t))
    time_name = t_name[0]+"-"+t_name[1]+"_"

    # time averaging
    if time_average is not None:  time_average_name = "time_average_{}_".format(time_average)
    else:  time_average_name = ""

    # chi-sigma
    if CF_case == "C1":  CF_name = "residual_"
    elif CF_case == "C2":  CF_name = "fractional_"

    # masking
    mask_name = ""
    if mask_degree is not None:  mask_name += "degree-{}_".format(mask_degree)
    if mask_temperature is not None:  mask_name += "thermal-{}_".format(mask_temperature)
    if (ts_slice is not None) or (te_slice is not None):  mask_name += "temporal_"
    if mask_pix is not None:  mask_name += "pix_timeline-{}_".format(mask_pix)
    if mask_name=="":  mask_name = "no-mask_"

    # show ideal file name
    fname = (path_data + folder_results + "{}_".format(block) + freq_name + time_name + mask_name + 
             CF_name + time_average_name + suffix_results + ".p")
    return fname


def show_parameters():
    ''' Show parameters in the parameters.py file, formatted correctly. '''

    # block
    print("Block: {}".format(block))

    # frequency range
    f_write = []
    for f in [fs_slice,fe_slice]:
        if f is None:  f_write.append("inf")
        else:  f_write.append(str(f))
    print("Frequency range: {} - {} MHz".format(*f_write))

    # time range
    t_write = []
    for i,t in enumerate([ts_slice,te_slice]):
        if t is None:  t_write.append("inf")
        else:  t_write.append(str(t))
    print("Time range: {} - {} seconds".format(*t_write))

    # chi-sigma
    print("The cost function denominator will be:",end=" ")
    if CF_case == "C1":  print("radiometer equation (C1).")
    elif CF_case == "C2":  print("unweighted (C2).")

    # masking
    msg = "Masking: "
    if mask_degree is not None:  msg += "Angular ({} deg), ".format(mask_degree)
    if mask_temperature is not None:  msg += "Thermal ({} K), ".format(mask_temperature)
    if (ts_slice is not None) or (te_slice is not None):  msg += "Temporal (shown above), "
    if mask_pix is not None:  msg += "Pixel timeline, "
    if msg=="Masking: ":  msg += "None., "
    print(msg[:-2])
    return
