NOTEBOOK FOR SATELLITE POSITION
Contact: 
Author: Brandon Engelbrecht; engelbechtbn@gmail.com
Supervisor: Mario Santos
Co-supervisor: Yi-Chao Li, Jose Fonseca

Overivew:

This notebook works to plot the trajectory information of the GNSS (not limited to) satellites with respect to a point on Earth for instance 
the MeerKAT telescope (not limited to). It utilizes the two-line-element information located in the <TLE/> folder. These should be as close to date of obsevation as possible and can start deteriating after a few weeks in accuracy.

Notebooks:

Satellite_position.ipynb (Main)

Requires information such as time, position and beam type as well.
obs_time: User enters the date and time of observation with respect to UTC time format: YYYY MM DD hh mm ss
nd_s: the scanning timestamps (can leave empty)
nd_s: a list of the scan in seconds should be given here, this is added to the fname/obs_time and can be the scanning zone, in seconds or timestamp seconds
frequency: a list of the frequency for the observation (f0, f1, f2....., fn) [Units MHz]
fs,fe: The starting and ending point of the frequency [Units MHz]\n
If None, will use the entire frequency band
timestamps: can leave empty
telescopeLon/Lat The longitude and latitude of the telescope position
nd_s0_coords: a tuple of (AZ_list, ALT_list), these should be of equal size and equal to the length of nd_s0
data_save: location to save the data
tle_location: location of the TLE satellite inforamtion for the observation
sats_type: the different satellite constellations for the satellites: name variable should correspond to the file name xxx.txt
tle_data_sort: Given the format of the TLE from the website, the data needs to be processed first. None to do nothing

Auxilary Notebooks:
Satellite_downloader.ipynb (redundant)
Notebook exists to download current TLE information for the day and then process it into useful information

Satellite_info.ipynb
Notebook exists to create manual information for observation, such as time, position and so on.

tle_satellite_cat.ipynb (redundant)
Notebook exists to process the TLE information for the future users


To be continued....


