'''
A list of parameters that are run in the chi2 notebooks.
Note; this should be untilized everywhere
'''
from imports import *


'''
-------------------------------------------GENERAL PARAMATERS
'''
## FILE NAME
file=1551055211

## LOCATION OF SAVED FILES
data_save=str(file)+'/'
data_plot=str(file)+'/figure/'

## FREQUENCY BOX SIZE
fs=1000    # Starting
fe=1500    # Ending

'''
------------------------------------------GENERATING MEERKAT DATA
'''

## OBSERVATION FOLDERS
folder_2018 = 'SCI-20180330-MS-01'
folder_2019 = 'SCI-20190418-MS-01'
folder_2021 = 'SCI-20210212-MS-01'

## VARIOUS OBSERVATIONS
observation_2018 = ['1551037708', '1551055211', '1553966342', '1554156377']

observation_2019 = ['1555775533','1555793534', '1555861810', '1556034219',
               '1556052116', '1556120503', '1556138397', '1555879611', '1561650779', '1562857793']

observation_2021 = ['1631379874', '1631387336', '1631552188', '1631559762', '1631659886', 
 '1631667564', '1631724508', '1631732038', '1631810671', '1631818149', '1634835083']


## TEMPORAL AND FREQUENCY INFORMATION STORED FROM KATDAL
if os.path.isfile(data_save+str(file)+'_katdal_info.p')==True:
    if sys.version_info.major==2:
        katdal_info = pickle.load(open(data_save+str(file)+'_katdal_info.p', 'rb'))#, encoding='latin1')

    elif sys.version_info.major==3:
        katdal_info = pickle.load(open(data_save+str(file)+'_katdal_info.p', 'rb'), encoding='latin1')

    info = [katdal_info[i] for i in katdal_info.keys()]
    nd_s0=katdal_info['nd_s0']
    nd_s0_coords=katdal_info['nd_s0_coords']
    nd_s0_coords2=katdal_info['nd_s0_coords2']
    nd_s0_pos=katdal_info['nd_s0_pos']
    frequency=katdal_info['frequency']

else:
    print ('Katdal information does not exist, manual implementation required')

## MASK LEVEL ANALYTSIS
mask_level='6'



'''
-----------------------------SATELLITE POSITION AND BEAM MODEL
'''

## -------------------------------------------------------LOCATION OF TLE INFORMATION
tle_location='TLE/2019_02_21_tle/'

## ------------------------------------------------------SORTING OF TLE INFORMATION
# Sorts TLE infromation into the favourable working method
tle_data_sort=False
if tle_data_sort is True: 
    print ('Extracting IRNSS and QZs')
    satellite_extract.sat_extract(folder=tle_location)
    print ('Extract complete ')
    print ('Re-writing data')
    rewrite_tle.rewrite_sat_cat(file_path=tle_location)
    print ('Re-write completed')


## -----------------------------------------------------OBSERVATION TIME
# Set to None if the file name is given
observation_time=None

## -----------------------------------------------------TELESCOPE LATITUDE AND LONGITUDE
telescope_Lon =  (21. + 26./60. + 38.00/3600.) 
telescope_Lat = -(30. + 42./60. + 47.41/3600.) 

## -----------------------------------------------CONSTELLATION TYPES
# The constellations that we are interested in
# Note user intervention is required.
# Note number of constellations can be less
satellite_type = ['gps-ops', 'glo-ops', 'galileo', 'beidou', 'irnss', 'sbas','qzs'] # Can be all or one REMOVED SBAS
# satellite_type = ['geo'] # Can be all or one
# satellite_type = ['gps-ops', 'glo-ops', 'galileo', 'beidou', 'irnss', 'qzs', 'sbas', 'geo'] # Can be all or one


## -------------------------------------------------BEAM MODEL
# Choice of beam model for current simulation can be set to 'emss' or 'cosine'
# Note, the angular evaluations for the constellations should be available on these beam models
beam_model = 'emss'

'''
--------------------------------------------------CHI^2 FITTING
'''
## ----------------------------------------------CHI-SQAURE OUTPUT FOLDER
folder = 'sat_4/'
## ----------------------------------------------CHI-SQAURE SUFFIX
save_suffix="v1"

## ----------------------------------------------MASKING INFORMATION
# Mask-none
mask_type="temporal"
# print (mask_type)
if mask_type==None:
    nearby_constellations=None
# Mask-degree
if mask_type=='degree':
    mask_degree="5F"
    # Constellation files with 
    nearby_constellations = data_save+'nearby_satellites/nearby_satellite_close_angle_'+mask_degree+'.p'
# Mask-thermal
if mask_type=='thermal':
    nearby_constellations=None
    mask_temperature=100
# Mask-temporal
## -------------------------------------------------------SUB TIME SLICE
# If ts and te is set to None, will return the edges of the frequency range
# If ts and te is not set to None, will return indices closest to the given values.
# Note ts can be None and te does not have to be (vice-versa)
if mask_type=='temporal':
    ts_slice=5500
    te_slice=6200

    nearby_constellations=None
else:
    ts_slice, te_slice=None, None
    
## -------------------------------------------CHIS-SQUARE SIGMA
## If True chi_sigma will become the radiometer equation, if False chis_sigma=1

chi_sigma=False
# chi_sigma=False

## -----------------------------------------------SATELLITE CATALOGUE
# Path to satellite catalogue, currently displaying the full catalogue
satellite_catalogue = '/users/bengelbrecht/PhD_Work/Satellite_Code/satellite_RFI-untangle/Notebooks/Satellite_Catalogue/table3B_satellite_v3-1_reduced_2_bw.csv'

## -----------------------------------------------CONSTELLATIONS OF INTEREST
# The constellations that we are interested in
# Note user intervention is required.
# Note number of constellations can be less
constellations_remain = [ 'GPS', 'GLO', 'GAL', 'BDS', 'SBAS', 'IRNSS']

## -----------------------------------------------NUMBER OF SIGNALS [ALPAH, SIGMA]
# The number of satellite signals available in the current freqeucny range of choice.
# For now, not in use
no_signals=21

## -----------------------------------------------CONSTELATION BIAS FACTOR
# Fixed constellation bias which multpiles the amplitude for an entire constellation. 
# Left to be zero
bias = np.ones(len(constellations_remain))


## ------------------------------------------------------SUB FREQUENCY SLICE
# If fs and fe is set to None, will return the edges of the frequency range
# If fs and fe is not set to None, will return indices closest to the given values.
# Note fs can be None and fe does not have to be (vice-versa)
fs_slice=1100
fe_slice=1350


## ---------------------------------------Time Averaging
# Controlling the time average.
# If set to 'None' then will ignore
# time_size=None   # sec
time_size=10   # sec

## ---------------------------------------------------DAMPENIG FUNCTION
# Dampening function set to None will switch off function
# Dampening function set to 'goob' will switch on the Gaussian Out-of-Band function
dampner=None
# If dampner is not None, 
# Dampner_sigma can None which results in a random Chi-sigma values
# Dampner-sigma can an integer which results in a fixed damppening value
dampner_sigma=None
