### Files in sattelite_RFI:
- *(these are the files from satellite_RFI; tried to keep the same files and structure and just rewrite for clarity and for faster code.)*
- **attenuation**: File with attenuation functions `tophat_oob` and `gaussian_oob`; rewritten for clarity and celerity. However, all of the mentions to attenuation were removed from the code so this currently is not used!
- **beam_model**: File with different telescope beam models, either analytical or from a file; partially rewritten for clarity.
- **check_satellite**: Old file, not rewritten.
- **data_reduction**: Old file, not rewritten.
- **Generating_Calibrated_Data**: Old file, not rewritten.
- **psd_models**: File with the Power Spectrum Density models for the GNSS satellite signals; partially rewritten for clarity.
- **rewrite_tle**: Old file, not rewritten.
- **satellite_extract**: Old file, not rewritten.
- **simulation**: File with the simulation object, which gathers information calculated in the different files; completely rewritten for clarity and celerity.
- **tle_sat_download**: Old file, not rewritten.
- **tools**: Old file, not rewritten.
- **wiggleZ_area**: Old file, not rewritten. 

### Notebooks:
- *(these are the notebooks that i created, based on the existing notebooks, which i didn't touch.)*
- **N3_fitting**: Notebook that fits the simulation to the data, using specific masking parameters.
- **N3_MOD_fitting**: Same as N3 but using individual satellites instead of constellations; incomplete.
- **N4_graphs**: Notebook that shows the graphs for the data for all of the masks chosen; doesn't show time intervals yet!
- **N2a_create_catalogs**: Notebook that creates files with individual satellite information, instead of the current files with general information of each constellation. Creates files 'new_satellite_constellation_catalog.csv' (new catalog that now has the signals of each satellite instead of the signals of each constellation) and 'satellite_angular_positions' (new file that saves the satellite angular positions in a more expedite manner). 

### Logs:
**WEEK 5: 9 - 16 of april**
- (*OBJECTIVES: Getting graphs, getting information from the individual satellites, performing fitting with alphas from each satellite instead of each constellation.*) 
- Visualized what the current files of satellite information contain; 
- Retrieved necessary info from file "individual_satellite_angular_positions" (it has the individual satellites instead of the constellations' beam response) and saved it in a new file "satellite_angular_positions" (much quicker to open);
- Created a new csv catalog that now has the signals that each satellite has; not the best way to perform this (could be done directly on the simulation) but for now it's the easier way to use the existing code, altering it in the least.
- Rewrote N4 and simulations in order to have a simulation not defined by the mask; that way we only have to initialize once for each dataset and every new mask does not require a new initialization (which is the part that takes the longest). Still missing time interval! 
- Began simulation with individual satellites. Created a new file `simulation_MOD` that modifies the file `simulation` but with individual satellites. For now, managed to rewrite `_get_beam_response` (to get the new file with individual satellites) and managed to get the new catalog. 

**WEEK 6: 16 - 23 of april** 
- (*OBJECTIVES: repetir procedimento com alphas iguais para satélites de cada constelação, ver busy week.*)
- Finished correcting the initialization function; I didn't alter anything in the `execute` function because it's not necessary.
- Altered the cost function in order to use only the 21 alphas (same situation as the constellations).
- Running the simulation - found some errors, currently debugging.