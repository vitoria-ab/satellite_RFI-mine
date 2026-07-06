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
# observational block
block = 1551055211
# folders and files (latest, if other paths are used they are described directly in the notebook)
path_data = f"/idia/projects/hi_im/satellite_rfi/Testing/{block}/"
path_observations = path_data + f"{block}_average_TOD_BG_model.p"
path_beam = f"data/satbeams_{block}_{beam_model}_{freq_range[0]}-{freq_range[1]}.pkl"
path_catalog = f"data/catalog_{block}.csv"


## ----- PARAMETERS : KATDAL INFO ----- ##
f = path_data + f"{block}_katdal_info.p"
if sys.version_info.major == 2:  katdal = pickle.load(open(f,"rb"))
elif sys.version_info.major == 3:  katdal = pickle.load(open(f,"rb"), encoding="latin1")
nd_s0 = katdal["nd_s0"]
nd_s0_coords = katdal["nd_s0_coords"]  # <-- REMOVE
nd_s0_coords2 = katdal["nd_s0_coords2"]  # <-- REMOVE
nd_s0_pos = katdal["nd_s0_pos"]  # <-- REMOVE
frequency = katdal["frequency"]
del katdal


## ---------------------------- ##
## ----- USEFUL FUNCTIONS ----- ##
## ---------------------------- ##

def my_name(folder, CF, deg=None, temp=None, pix=None, t_slice=[None,None]):
    ''' My file name to save alphas. '''

    # chi-sigma
    CF_name = f"_{CF}"

    # masking
    mask_name = ""
    if deg is not None:  mask_name += f"deg{deg[0]}"
    if temp is not None:  mask_name += f"thermal{temp}"
    if pix is not None:  mask_name += f"pix{pix}"
    if (t_slice[0] is not None) or (t_slice[1] is not None):
        mask_name += "interval"
        if t_slice[0] is not None:  mask_name += f"{t_slice[0]}"
        else:  mask_name += f"{nd_s0[0]:.0f}"
        if t_slice[1] is not None:  mask_name += f"-{t_slice[1]}"
        else:  mask_name += f"-{nd_s0[-1]:.0f}"
    if mask_name=="":  mask_name = "nomask"

    # getting final name
    fname = folder + mask_name + CF_name + ".p"
    return fname

## ---------------------------- ##

def brandon_name(folder, CF, deg=None, temp=None, pix=None, t_slice=[None,None]):
    ''' Brandon's file name to save alphas, according to the parameters in the parameters.py file. '''
    
    # frequency range
    freq_name = f"{freq_slice[0]}-{freq_slice[1]}_"

    # time range
    t_name = []
    for i,t in enumerate(t_slice):
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
    if (t_slice[0] is not None) or (t_slice[1] is not None):  mask_name += "temporal_"
    if pix is not None:  mask_name += f"pix_timeline-{pix}_"
    if mask_name=="":  mask_name = "no-mask_"

    # show ideal file name
    fname = (path_data + folder + f"{block}_" + freq_name + time_name + mask_name + 
             CF_name + time_average_name + ".p")
    return fname

## ---------------------------- ##

def show_parameters(CF=None, deg=None, temp=None, pix=None, t_slice=[None,None], plotting=False):
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
    for i,t in enumerate(t_slice):
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
    if (t_slice[0] is not None) or (t_slice[1] is not None):  msg += "Temporal (shown above), "
    if pix is not None:  msg += f"Pixel timeline (Tmax/{pix}), "
    if msg=="Masking: ":  msg += "None, "
    print(msg[:-2])
    return
