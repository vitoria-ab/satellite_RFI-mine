'''
A list of parameters that are run in the chi2 notebooks.
Note; this should be untilized everywhere
'''

# File name [The unix time of observation]
file_name='1551055211'
file_name_ext=''

# The yyyy MM DD hh mm ss of the observation ['2021 9 30 20 06 36']
observation_time=None

# KATDAL path
telescope_info_path='/idia/projects/hi_im/satellite_rfi/Observations/'+file_name+file_name_ext+'/'+file_name+'_katdal_info.p'

# Frequency start and end
fs, fe=1000,1500

# Path to save the simulation file
sat_sim_save_data='/idia/projects/hi_im/satellite_rfi/Results/Data/'+file_name+file_name_ext+'/pickle_info/'

# MeerKAT observation maps and results
meerkat_data='/idia/projects/hi_im/satellite_rfi/Observations/Untangle/'+file_name+file_name_ext+'/'

# Nearby constellation times
    # Degree value
deg='2'    #[Can be '#_fill' or '#']
    # Full path
nearby_constellation_fpath = '/idia/projects/hi_im/satellite_rfi/Observations/'+file_name+'/nearby_satellite_mask/nearby_satellite_close_angle_'+deg+'.p'
    # Suffix needed
nearby_constellation_path = '/idia/projects/hi_im/satellite_rfi/Observations/'+file_name+'/nearby_satellite_mask/'

# Work folder to save results
work_folder='parallel_2022_03_20'

# Path to save chi_2 best-fit values
chi2_save_data='/idia/projects/hi_im/satellite_rfi/Results/Data/'+file_name+file_name_ext+'/data_info/'+work_folder+'/'

# Satellite catalogue path 
satellite_catalogue='../../Satellite_simulations/Satellite_Catalogue/table3B_satellite_v3-1_reduced_2.csv'

# Plot location
save_plots='/idia/projects/hi_im/satellite_rfi/Results/Plots/'+file_name+file_name_ext+'/'+work_folder+'/'

# Beam model
beam_model='emss_beam_r'

# Constellation choice
constellations=['GPS', 'SBAS', 'GAL', 'BDS', 'GLO', 'IRNSS']