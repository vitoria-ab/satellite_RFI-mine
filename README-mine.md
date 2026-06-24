# Structure of the code
### Versions of the code:
- **v0**: Constellation paradigm (uses a matrix for each constellation); results are good.
- **v1**: Satellite paradigm, recovering constellation results (uses a matrix for each satellite, but imposes that alphas of satellites within the same constellations are the same); results are good.
- **v2**: Constellation paradigm (uses a matrix for each constellation), but using `lsq_linear`; results are good.
- **v3**: Satellite paradigm using `nnls`, with new results; results are generally good, they need to be inspected.

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
- **simulation_cons**: File with the simulation object, which gathers information calculated in the different files and performs the final calculations for the fitting; completely rewritten for clarity and celerity. Used in v0 and v2.
- **simulation**: Rewrite of simulation_cons but using the paradigm of individual satellites instead of constellations. Used in v1 and v3.
- **tle_sat_download**: Old file, not rewritten.
- **tools**: Old file, not rewritten. 
- **wiggleZ_area**: Old file, not rewritten. 

### Notebooks:
(*These are the notebooks that i created, based on the existing notebooks, which i didn't touch.*)
- **N2a_create_catalogs**: Notebook that creates files with individual satellite information, instead of the current files with general information of each constellation. Creates files *new_satellite_constellation_catalog.csv* (new catalog that now has the signals of each satellite instead of the signals of each constellation) and *satellite_angular_positions* (new file that saves the satellite angular positions in a more expedite manner). 
- **N3_fitting**: Notebook that fits the simulation to the data, using specific masking parameters.
- **N4_graphs**: Notebook that shows the graphs for the data for all of the masks chosen; doesn't show time intervals yet!
- **\param_import**: Folder with the files *parameters.py* which specify the parameters used in notebooks N3 (fitting) and N4 (graphs).
- **\results**: Folder with generated results, with subfolders for each version of the code that is created.
- **\PreviousNBs**: Notebooks from previous versions (v0,v1 etc) which have been completed and don't need to be touched anymore.


# Logs
### WEEK 5: 9 - 16 of april
(*OBJECTIVES: Getting graphs, getting information from the individual satellites, performing fitting with alphas from each satellite instead of each constellation.*) 
- Visualized what the current files of satellite information contain; 
- Retrieved necessary info from file "individual_satellite_angular_positions" (it has the individual satellites instead of the constellations' beam response) and saved it in a new file "satellite_angular_positions" (much quicker to open); 
- Created a new csv catalog that now has the signals that each satellite has; not the best way to perform this (could be done directly on the simulation) but for now it's the easier way to use the existing code, altering it in the least. 
- Rewrote N4 and simulations in order to have a simulation not defined by the mask; that way we only have to initialize once for each dataset and every new mask does not require a new initialization (which is the part that takes the longest). Still missing time interval! 
- Began simulation with individual satellites. Created a new file `simulation` that modifies the file `simulationv0` but with individual satellites. For now, managed to rewrite `_get_beam_response` (to get the new file with individual satellites) and managed to get the new catalog. 

### WEEK 6: 16 - 23 of april
(*OBJECTIVES: repeat procedure with equal alphas for satellites of the same constellation.*)
- Finished correcting the initialization function; I didn't alter anything in the `execute` function because it's not necessary.
- Altered the cost function in order to use only the 21 alphas (same situation as the constellations).
- Running the simulation - found some errors, currently debugging.

### WEEK 7: 23 - 30 of april
(*OBJECTIVES: repeat procedure with equal alphas for satellites of the same constellation.*)
- Rewrote catalog retrieval, now the signals should have the same order as the previous catalog (makes comparing easier).
- Debugged: the final value of the cost function was incorrect, so I was checking to see if everything is the same between the two codes. Some corrections in the ordering were done in the calculations, and then in the ordering of the alphas in order to match, and it was solved.
- Generated values for all masks using the new code, retrieved the results from the paper but now treating each satellite individually in the code (and just considering the alpha values to be the same for satellites within the same constellation). The graphs are the same.
- Ran complete simulation; took to long, stopped midway, needs to be paralelized! 

### WEEK 8: 30 of april - 7 of may
(*OBJECTIVES: quantify difference between values obtained in v0 and v1, run the complete code, see if paralelization is possible or if there are other faster methods, such as ones which use jacobian and hessian.*)
- Rewrite the matrices that i have right now into a 2d matrix instead of 3d by collapsing the time x frequency dimensions into a single dimension of pixels, so that the final simulations factors are pixels x alphas and observations are just pixels (1d array, much more memory efficient)!

### WEEK 9: 7 - 14 of may
(*OBJECTIVES: Since this problem is essentially minimizing a system of equations A.alpha - b, it seems to be possible to use least squares directly (instead of through optimization algorithms). It might save a lot of time, so I'm going to rewrite the problem for the constellations using this paradigm and check if they recover the same alphas.*)
- Altered the plotting notebooks so they show the absolute errors of the new alpha values vs. the paper values.
- Wrote *v2*, which uses the constellation paradigm from *v0* but with a new optimization - lsq_linear; as such should be faster and more reliable while still recovering the same results.
- Recovered results in *v2*, they are all consistent with the graphs from the paper.

### WEEK 10: 14 - 21 of may
(*OBJETIVES: Run optimization with all of the satellites, and try to find what's happening with the paper's results.*)
- TO DO: Check if the files I'm using for reference recover the same results as the paper; check the pdfs of graphs! 
- Cleaned the optimizing code; now the parameters that are constantly changing are in the beginning of the notebook (instead of in *parameters.py*) so I don't need to change that file all the time, and the optimizing functions are described within the notebook (makes sense, since they are a separate object from the simulation). 
- Changed `lsq_linear` to `nnls` since that is the boundary condition that we want and it uses a more specialized code; the results in *v2* remained the same. 
- Wrote *v3*, which uses this new optimization with all of the satellites; using `nnls` the code went from 30mins to 3mins. Generated all of the results. 

### WEEK 11+12: 21 - 4 of june
(*OBJECTIVES: Break to complete some Uni work*)

### WEEK 13: 4 - 11 of june
(*OBJECTIVES: Confirmar cenas da Iara em que alguns sinais são zero; ver se com as priors da Iara fica bem na mesma; tentar ver a correspondência com os satélites de cada constelação. Matriz de Fisher para estimar os erros? - não fazer agora.*)  
- Created a catalog of satellites and generations in each constellation - complete guide (includes satellites that have been decommisioned since), with several IDs, and whether they are present in Brandon and Iara's work. Currently incomplete.
- Created a catalog of constellation signals - complete guide, with modulation, rate, and central frequency, and whether they match Brandon's specification. Currently incomplete.

### WEEK 14: 11 - 18 of june
(*OBJETIVES: Continuar semana anterior*)
- Corrected PSD models in file *psd_models*; several of them were incomplete or used approximate formulas (but within the chosen frequency range all remains approximately the same).
- Continued work on satellite and signal catalog; currently missing just SBAS satellites and signals.
- Rewrote *psd_models.py* file with more accurate signals (added MBOC and lumped CBOC and TMBOC with it, and corrected BOC and BOCcos) and tested it against the old signals - differences are in the order of 1% max in some specific cases and wavelengths but should be fine overall.
- TO DO: Create new (and better) visualizations - try other types of graphs, select by constellation or by signal, select by satellite and check all characteristics of a given satellite (beam response map, signal curve, alpha values, final addition to the 1D and 2D plots).

### WEEK 15: 18 - 25 of june
- Finished satellite and signal catalog (up-to-date) and added to directory in the */tables/* folder.
- Created a catalog of *k* numbers of each GLONASS satellite (relevant for some specific signals for which the central frequency is not equal but has an offset in each satellite given by *k*); this is correct only for the specific date of the observation of February 25, 2019.
- Updated HI_IM-PY2 and HI_IM-PY3 kernels: they needed to be reinstated (probably after ILIFU was up again) and the singularity files have been moved to new directories. For py2 it was just about changing the filename, but for py3 the singularity was seemingly not updated and had an old file format that required me to create a new copy of the singularity file in my own personal directory.
- Corrected the whole setup process, which I'll later put in a new README file for the directory.
- QUESTION: With this way to compute that garantees a global minimum, isn't it better to keep the amplitudes completely neutral in order to understand if the alpha values make sense physically?
- QUESTION: Is HI_IM-PY2 and 3 working for everyone but me??
- TO DO: I don't know which of the BeiDou-3 1M (S?) satellite was the one crossing the sky. Maybe can see its TLE directly and don't need to re-do the whole step of creating the angular maps of each satellite!
- TO DO (EVENTUALLY): Alter N2 part of the code in order to get information from the correct Celestrak files with all of the satellites (not just "working" satellites), and in general rewrite N2.