# Structure of the code
### Files in sattelite_RFI:
(*These are the files from satellite_RFI; tried to keep the same files and structure and just rewrite for clarity and for faster code.*)
- **attenuation**: File with attenuation functions `tophat_oob` and `gaussian_oob`; rewritten for clarity and celerity. However, all of the mentions to attenuation were removed from the code so this currently is not used!
- **beam_model**: File with different telescope beam models, either analytical or from a file; partially rewritten for clarity.
- **check_satellite**: Old file, not rewritten.
- **data_reduction**: Old file, not rewritten.
- **Generating_Calibrated_Data**: Old file, not rewritten.
- **psd_models**: File with the Power Spectrum Density models for the GNSS satellite signals; partially rewritten for clarity.
- **rewrite_tle**: Old file, not rewritten.
- **satellite_extract**: Old file, not rewritten.
- **simulation**: File with the simulation object, which gathers information calculated in the different files; completely rewritten for clarity and celerity.
- **simulation_MOD**: Same as simulation but using individual satellites instead of constellations.
- **tle_sat_download**: Old file, not rewritten.
- **tools**: Old file, not rewritten.
- **wiggleZ_area**: Old file, not rewritten. 

### Notebooks:
(*These are the notebooks that i created, based on the existing notebooks, which i didn't touch.*)
- **N2a_create_catalogs**: Notebook that creates files with individual satellite information, instead of the current files with general information of each constellation. Creates files *new_satellite_constellation_catalog.csv* (new catalog that now has the signals of each satellite instead of the signals of each constellation) and *satellite_angular_positions* (new file that saves the satellite angular positions in a more expedite manner). 
- **N3_fitting**: Notebook that fits the simulation to the data, using specific masking parameters.
- **N3_MOD_fitting**: Same as N3 but using individual satellites instead of constellations; for now considers alphas to be the same for satellites within the same constellation.
- **N4_graphs**: Notebook that shows the graphs for the data for all of the masks chosen; doesn't show time intervals yet!
- **N4_MOD_graphs**: Same as N4 but using individual satellites instead of constellations; doesn't show time intervals yet, and for now considers alphas to be the same for satellites within the same constellation.
- **\param_import**: Folder with the files *parameters.py* and *parameters_graphs.py* which specify the parameters used in notebooks N3 (fitting) and N4 (graphs) respectively.
- **\results**: Folder with generated results; for now includes folder *\paper* (generated from the rewritten original code, same as paper), and *\individual_sats0* (generated from the individual satellites code reproducing the results from the paper).


# Logs
### WEEK 5: 9 - 16 of april
(*OBJECTIVES: Getting graphs, getting information from the individual satellites, performing fitting with alphas from each satellite instead of each constellation.*) 
- Visualized what the current files of satellite information contain; 
- Retrieved necessary info from file "individual_satellite_angular_positions" (it has the individual satellites instead of the constellations' beam response) and saved it in a new file "satellite_angular_positions" (much quicker to open); 
- Created a new csv catalog that now has the signals that each satellite has; not the best way to perform this (could be done directly on the simulation) but for now it's the easier way to use the existing code, altering it in the least. 
- Rewrote N4 and simulations in order to have a simulation not defined by the mask; that way we only have to initialize once for each dataset and every new mask does not require a new initialization (which is the part that takes the longest). Still missing time interval! 
- Began simulation with individual satellites. Created a new file `simulation_MOD` that modifies the file `simulation` but with individual satellites. For now, managed to rewrite `_get_beam_response` (to get the new file with individual satellites) and managed to get the new catalog. 

### WEEK 6: 16 - 23 of april
(*OBJECTIVES: repetir procedimento com alphas iguais para satélites de cada constelação, ver busy week.*)
- Finished correcting the initialization function; I didn't alter anything in the `execute` function because it's not necessary.
- Altered the cost function in order to use only the 21 alphas (same situation as the constellations).
- Running the simulation - found some errors, currently debugging.

### WEEK 7: 23 - 30 of april
(*OBJECTIVES: repetir procedimento com alphas iguais para satélites de cada constelação.*)
- Rewrote catalog retrieval, now the signals should have the same order as the previous catalog (makes comparing easier).
- Debugged: the final value of the cost function was incorrect, so I was checking to see if everything is the same between the two codes. Some corrections in the ordering were done in the calculations, and then in the ordering of the alphas in order to match, and it was solved.
- Generated values for all masks using the new code, retrieved the results from the paper but now treating each satellite individually in the code (and just considering the alpha values to be the same for satellites within the same constellation).
- 