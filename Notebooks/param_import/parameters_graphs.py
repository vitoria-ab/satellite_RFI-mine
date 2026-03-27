"""
File with parameter information for graphs.

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
# frequency window for the alpha fitting
fs_slice, fe_slice = 1100, 1350
# total frequency window
fs, fe = 1000, 1500


## ----- PARAMETERS : SATELLITE MODEL ----- ##
# beam model (options: "emss", "cosine" or "eidos")
beam_model = "emss"
# constellations to include (options: "gps-ops","glo-ops","galileo","beidou","irnss","sbas","qzs"
include_cons = ['gps-ops', 'glo-ops', 'galileo', 'beidou', 'irnss', 'sbas']


## ----- PARAMETERS : KATDAL INFO ----- ##
f = path_data + str(block) + "_katdal_info.p"
if os.path.isfile(f) == True:
    if sys.version_info.major == 2:  katdal = pickle.load(open(f,"rb"))
    elif sys.version_info.major == 3:  katdal = pickle.load(open(f,"rb"), encoding="latin1")
    nd_s0 = katdal["nd_s0"]
    nd_s0_coords = katdal["nd_s0_coords"]
    nd_s0_coords2 = katdal["nd_s0_coords2"]
    nd_s0_pos = katdal["nd_s0_pos"]
    frequency = katdal["frequency"]
else:
    print("Katdal information does not exist, manual implementation required")


## ---------------------------- ##
## ----- USEFUL FUNCTIONS ----- ##
## ---------------------------- ##

def my_name(CF_case, degree=None, temperature=None, pix=None, time_slice=None):
    ''' My file name to save alphas. '''

    # chi-sigma
    if CF_case=="C1":  CF_name = "_C1"
    elif CF_case=="C2":  CF_name = "_C2"

    # masking
    mask_name = ""
    if degree is not None:  mask_name += "_deg{}".format(degree[0])
    if temperature is not None:  mask_name += "_thermal{}".format(temperature)
    if pix is not None:  mask_name += "_pix{}".format(pix)
    if time_slice is not None:
        mask_name += "_interval"
        if time_slice[0] is not None:  mask_name += "{}".format(time_slice[0])
        else:  mask_name += "{:.0f}".format(pm.nd_s0[0])
        if time_slice[1] is not None:  mask_name += "-{}".format(time_slice[1])
        else:  mask_name += "-{:.0f}".format(pm.nd_s0[-1])
    if mask_name=="":  mask_name = "_nomask"

    # getting final name
    fname = ("results/vi" + mask_name + CF_name + ".p")
    return fname

# -------------------------------

def show_parameters():
    ''' Show parameters in the parameters_graphs.py file, formatted correctly. '''

    # block
    print("Block: {}".format(block))

    # frequency range
    f_write = []
    for f in [fs_slice,fe_slice]:
        if f is None:  f_write.append("inf")
        else:  f_write.append(str(f))
    print("Frequency range: {} - {} MHz".format(*f_write))
    return
