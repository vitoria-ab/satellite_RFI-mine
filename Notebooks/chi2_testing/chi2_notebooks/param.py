'''
A list of parameters that are run in the chi2 notebooks.
Note; this should be untilized everywhere
'''

# File name [The unix time of observation]
file_name='1551055211'

# The yyyy MM DD hh mm ss of the observation ['2021 9 30 20 06 36']
observation_time=None

# KATDAL path
telescope_info_path='/idia/projects/hi_im/brandon/'+file_name+'/'+file_name+'_katdal_info.p'

# Frequency start and end
fs, fe=1000,1500

# Path to save the simulation file
save_data='../data_test/'+file_name+'/pickle_info/'

# MeerKAT observation maps and results
meerkat_data='../../../../Observation_results/Untangle/'+file_name+'/'

# Nearby constellation times
deg='2'    #[Can be '#_fill' or '#']
nearby_constellation_path = '../nearby_satellite_mask/nearby_satellite_close_angle_'+deg+'.p'

# Work folder to save results
work_folder='2022_03_20'

# Satellite catalogue path 
satellite_catalogue='../../Satellite_simulations/Satellite_Catalogue/table3B_satellite_v3-1_reduced_2.csv'

# Plot location
save_plots='data_test_plots/'+file_name+'/'+work_folder+'/'

# Beam model
beam_model='emss_beam_r'

# Constellation choice
constellations=['GPS', 'SBAS', 'GAL', 'BDS', 'GLO', 'IRNSS']