from imports import *

## Filename
file = 1551055211

## Location of saved files and images
data_save = "/idia/projects/hi_im/satellite_rfi/Testing/"+str(file)+'/'
data_plot = "/idia/projects/hi_im/satellite_rfi/Testing/"+str(file)+'/'
filename = "/users/bvitoria/workspace/brandon_NEW_nomask_C1"

## Frequency box size
fs = 1000  # Starting
fe = 1500  # Ending

## Two-Line-Element (TLE) location
tle_location = "TLE/2019_02_21_tle/"
## TLE cleaning
## Initiates a cleaning process on data, used when downloading fresh TLE data (unproccessed)
tle_data_sort = False

## Position of telescope [Degrees]
telescope_Lon = 21.0 + 26.0 / 60.0 + 38.00 / 3600.0
telescope_Lat = -(30.0 + 42.0 / 60.0 + 47.41 / 3600.0)

## Constellations of interest
## Can remove and focus on less constellations
satellite_type = ["gps-ops", "glo-ops", "galileo", "beidou", "irnss", "sbas", "qzs"]

## Beam model
## Options available: 'emss', 'cosine', etc.....
## Check python file beam_models.py in src folder
beam_model = "emss"  # <-- USED

## Satellite catalogue
path_catalog = ("/Satellite_Catalogue/satellite_constellation_catalog.csv")  # <-- USED

## Chi Square output folder
folder = "sat_12" + "/"
## Chi Square suffix
save_suffix = "iara"

## Sub Frequency Slice
## If fs and fe is set to None, will return the edges of the frequency range
## If fs or/and fe is not set to None, will return indices closest to the given values.
fs_slice = 1100
fe_slice = 1350

## Different masks
## Angular mask [Degrees], eg: "1F", "1", "5", "5F" or however applicable
mask_degree = None
## Thermal mask [Kelvin], eg: 10, 25, 100 or however applicable
mask_temperature = None
## Temporal mask [Seconds], eg: 1000, 1200 or however applicable
mask_temporal = None, None
##Threshold pixel mask
mask_pixel_timeline = None
## Temporal averaging [Seconds], eg: 10, 20 or however applicable
time_average = None

## Chi Sqaure Sigma
## True==Radiometer equation (see tools.py), False==1
chi_sigma = True

## Dampening fucntion
## Set to None or "gaussian" (gaussian out-of-band, see )
dampner = None
# If dampner is not None,
# Dampner_sigma can None which results in a random Chi-sigma values
# Dampner-sigma can an integer which results in a fixed damppening value
dampner_sigma = None


##====================================================================================================================================##
## Different Notebooks Work Throughs
##====================================================================================================================================##
"""
=================================================RE-CALIBRATION OF MEERKAT DATA=================================================
"""

## OBSERVATION FOLDERS
folder_2018 = "SCI-20180330-MS-01"
folder_2019 = "SCI-20190418-MS-01"
folder_2021 = "SCI-20210212-MS-01"

## VARIOUS OBSERVATIONS
observation_2018 = ["1551037708", "1551055211", "1553966342", "1554156377"]

observation_2019 = [
    "1555775533",
    "1555793534",
    "1555861810",
    "1556034219",
    "1556052116",
    "1556120503",
    "1556138397",
    "1555879611",
    "1561650779",
    "1562857793",
]

observation_2021 = [
    "1631379874",
    "1631387336",
    "1631552188",
    "1631559762",
    "1631659886",
    "1631667564",
    "1631724508",
    "1631732038",
    "1631810671",
    "1631818149",
    "1634835083",
]

## CREATING FILE FOLDER PATHS
if os.path.exists(data_save)==False:
    print ("Data Path does not exist, creating")
    os.mkdir(data_save)
    os.mkdir(data_plot)

else:
    print ("Data Path exists")
    


## TEMPORAL AND FREQUENCY INFORMATION STORED FROM KATDAL
if os.path.isfile(data_save + str(file) + "_katdal_info.p") == True:
    if sys.version_info.major == 2:
        katdal_info = pickle.load(
            open(data_save + str(file) + "_katdal_info.p", "rb")
        )  # , encoding='latin1')

    elif sys.version_info.major == 3:
        katdal_info = pickle.load(
            open(data_save + str(file) + "_katdal_info.p", "rb"), encoding="latin1"
        )

    info = [katdal_info[i] for i in katdal_info.keys()]
    nd_s0 = katdal_info["nd_s0"]  # <-- USED
    nd_s0_coords = katdal_info["nd_s0_coords"]
    nd_s0_coords2 = katdal_info["nd_s0_coords2"]
    nd_s0_pos = katdal_info["nd_s0_pos"]
    frequency = katdal_info["frequency"]  # <-- USED

else:
    print("Katdal information does not exist, manual implementation required")

## MASK LEVEL ANALYTSIS
mask_level = "4"

"""
=================================================SATELLITE POSITION AND BEAM MODEL=================================================
"""
## Sorts TLE infromation into the favourable working method
tle_data_sort = False
if tle_data_sort is True:
    print("Extracting IRNSS and QZs")
    satellite_extract.sat_extract(folder=tle_location)
    print("Extract complete ")
    print("Re-writing data")
    rewrite_tle.rewrite_sat_cat(file_path=tle_location)
    print("Re-write completed")

"""
=====================================================CHI SQUARE FITTING=====================================================
"""

print("Importing masking parameters...")

# putting together all parameters
masks = np.array([mask_degree,mask_temperature,mask_temporal[0],mask_temporal[1],mask_pixel_timeline])
indexes = np.where(masks!=None)[0]

# some things that can be defined beforehand
ts_slice, te_slice = mask_temporal
if mask_degree==None:  nearby_constellations = None
else:  nearby_constellations = data_save + "nearby_satellites/nearby_satellite_close_angle_" + mask_degree + ".p"

# -- no mask
if indexes.size==0:  
    mask_name = "no-mask_"
    mask_type = "Masking: None."

# -- angular
elif np.array_equal(indexes,[0]):  
    mask_name = "degree-" + str(masks[0]) + "_"
    mask_type = "Masking: Angular."

# -- thermal
elif np.array_equal(indexes,[1]):   
    mask_name = "thermal-" + str(masks[1]) + "_"
    mask_type = "Masking: Thermal."

# -- temporal
elif np.array_equal(indexes,[2,3]) or np.array_equal(indexes,[2]) or np.array_equal(indexes,[3]):  
    mask_name = "temporal_"
    mask_type = "Masking: Temporal."

# -- timeline pixel
elif np.array_equal(indexes,[4]):  
    mask_name = "pix_timeline_" + str(masks[4]) + "_"
    mask_type = "Masking: Pixel timeline."

# -- angular and thermal
elif np.array_equal(indexes,[0,1]):  
    mask_name = "degree-" + str(masks[0]) + "_thermal-" + str(masks[1]) + "_"
    mask_type = "Masking: Angular and Thermal."

# -- angular and temporal
elif np.array_equal(indexes,[0,2,3]):  
    mask_name = "degree-" + str(masks[0]) + "_temporal_"
    mask_type = "Masking: Angular and Temporal."

# -- thermal and temporal
elif np.array_equal(indexes,[1,2,3]):  
    mask_name = "thermal-" + str(masks[1]) + "_temporal_"
    mask_type = "Masking: Thermal and Temporal."

# angular, thermal and temporal
elif np.array_equal(indexes,[0,1,2,3]):  
    mask_name = "degree-" + str(masks[0]) + "_thermal-" + str(masks[1]) + "_temporal_"
    mask_type= "Masking: Angular, Thermal and Temporal."
    
else:  
    mask_type = "Masking: Permutation not available!"


## Number of constellations that remain after the removal
constellations_remain = ['gps-ops', 'glo-ops', 'galileo', 'beidou', 'irnss', 'sbas']  # <-- USED

## Active Frequecny signals
## Amount of active signals that relate to number of alpha parameters [Must make this automatic]
no_signals = 21

## Constellation bias factor
## Changes the general amplitude of constellation power [Obsolete]
bias = np.ones(len(constellations_remain))  # <-- USED
