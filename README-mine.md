# Structure of the code
### Versions of the code:
- **v0**: Constellation paradigm (uses a matrix for each constellation); results are good.
- **v1**: Satellite paradigm, recovering constellation results (uses a matrix for each satellite, but imposes that alphas of satellites within the same constellations are the same); results are good.
- **v2**: Constellation paradigm (uses a matrix for each constellation), but using `lsq_linear`; results are good.
- **v3**: Satellite paradigm using `nnls`, with new results; results are generally good, but need to be inspected.
- **v4**: Satellite paradigm with a restructured code and some very minor differences; results are practically the same as v3 with some improved peaks.
- **v5**: Satellite paradigm with the updated catalog; results are worse in several aspects which might be due to part 2 of the code having some weird satbeams.
- **v6**: Satellite paradigm with the updated catalog and improved satbeam maps; results are better than v5 but still have several weird aspects (which are now solely due to the catalog lacking necessary signals).
- **v7**: Satellite paradigm with the old catalog and improved satbeam maps, for comparison with v6.

### Files in `sattelite_RFI`:
- **attenuation**: File with attenuation functions `tophat_oob` and `gaussian_oob`; rewritten for clarity and celerity. However, all of the mentions to attenuation were removed from the code so this currently is not used!
- **beam_model**: File with different telescope beam models, either analytical or from a file; rewritten.
- **check_satellite**: Old file, not rewritten.
- **data_reduction**: Old file, not rewritten.
- **Generating_Calibrated_Data**: Old file, not rewritten.
- **psd_models**: File with the Power Spectrum Density models for the GNSS satellite signals; rewritten.
- **simulation_cons**: File with the simulation object, which gathers information calculated in the different files and performs the final calculations for the fitting; completely rewritten for clarity and celerity. Used in v0 and v2.
- **simulation**: Rewrite of simulation_cons but using the paradigm of individual satellites instead of constellations. Used in v1 and v3.
- **simulation_NC**: Rewrite of simulations but using the new catalog.
- **TLE_mapping**: File with functions to map TLEs to angular positions, and also holds the SatBeamCalculator object; rewritten.
- - **tools**: Old file, not rewritten. 
- **wiggleZ_area**: Old file, not rewritten. 

### Files in `Notebooks`:
- **N2_angular_positions**: Calculates the satellite angular positions, dependent on the frequency range, the telescope beam model, and on the satellites present on the TLEs of the given date. Only versions >=v6 use these satbeams, the older versions used the old information pre-calculated (which have some errors, with slightly wrong satbeam maps and regions present that should be cut from the matrices). Needs to be rewritten for clarity and better divided into TLE grabbing and satbeam calculation.
- Notebooks for each version of the code:
    - **{version}_N2a_create_catalogs**: Crosses the total signal list with the existing satellites in the satbeam file, and creates the final signal catalog with only the satellites present.
    - **{version}_N3a_fitting**: Fits the simulation to the data.
    - **{version}_N3b_graphs**: Shows the graphs present in the article.
    - **{version}_N3c_analysis**: Further analysis on the alphas obtained.
- Folders with additional information:
    - **initialization/**: Has the files *parameters.py* (specifies the general observation information) and *imports.py* (general imports).
    - **results/**: Generated results, with subfolders for each version of the code that is created.
    - **previousNBs/**: Notebooks from previous versions (v0,v1 etc) which aren't useful anymore.
    - **simulation_data/**: Folder with necessary catalogs, which includes: *satellites.csv* (list of satellites with operational timeline, ill-working signals, generation); *signals.csv* (list of signals with constellation, generations, and physical properties); *knumbers_{block}.csv* (list of active GLONASS satellites and their respective $k$ numbers); *catalog_{block}.csv* (final signal catalog with only the satellites that are known to appear in the observations); *satbeams_{block}_{beam}_{fs}-{fe}.pkl* (dictionary of beam responses for each satellite that appears in the observation with these specifications); and *nearby_{block}.pkl* (dictionary with the time indexes where satellites were nearer than a given angle).
    - **old_folders**: Old stuff from Brandon.


# Requirements to run
### Setting up the PY3 singularity
Perform these steps in the ILIFU Jupyter Lab terminal in order to set up the singularities HI_IM-PY2 and HI_IM-PY3. The singularities are stored in the */software/astro/containers/* directory, but there doesn't seem to be any recent copy of the PY3 singularity; the way that it worked for me was by creating a copy of the old singularity file into my personal directory and using that new file as the singularity source:
1. Create a temporary folder (need one for the temporary files created during the copy): `mkdir /users/{USER}/tmp`
2. Copy the singularity file into a new file: `TMPDIR=/users/{USER}/tmp SINGULARITY_TMPDIR=/users/{USER}/tmp singularity build /users/{USER}/workspace/hi_im-py3.sif /idia/software/containers/hi_im-py3.simg` (this can take a while, +30 mins).
3. Move to folder `/users/{USER}/.local/share/jupyter/kernels/`.
4. Create a folder for the two singularities: `mkdir /{NAME}/`.
4. In the two folders, create a `kernel.json` and copy the contents from the respective file in `satellite_RFI/kernels`.

### Setting up the two kernels and repository
I'm not sure why it is necessary to perform the initial installations that were described in the initial README; I think nowadays these are already included in the singularities and don't need to be installed. However, I'm including those steps because they do no harm (worst case scenario they just state that the packages are already installed).

These steps need to be performed for both singularities PY2 and PY3 (at the end of the first it might be necessary to command `exit`). First, copy the repository to your personal folder, and then for each singularity do the following:
1. Begin the singularity: `singularity shell {PATH}` (PY2 - */software/astro/containers/hi_im-latest.sif*; PY3 - */users/{USER}/workspace/hi_im-py3.sif*).
2. Change into the repository: `cd satellite_RFI`.
3. Install skyfield: `pip{2/3} install skyfield --user`.
4. Install natsort: `pip{2/3} install natsort`.
5. If you want to use the repository as is: `python{2/3} setup.py install --user`. If you want to have an editable version: `pip{2/3} install -e . --user`.


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
- Continued work on satellite and signal catalog; currently missing just SBAS satellites and signals.
- Rewrote *psd_models.py* file with more accurate signals (added MBOC and lumped CBOC and TMBOC with it, and corrected BOC and BOCcos) and tested it against the old signals - differences are in the order of 1% max in some specific cases and wavelengths but should be fine overall.

### WEEK 15: 18 - 25 of june
(*OBJETIVES: Continuar semana anterior*)
- Finished satellite and signal catalog (up-to-date) and added to directory in the */tables/* folder.
- Created a catalog of $k$ numbers of each GLONASS satellite (relevant for some specific signals for which the central frequency is not equal but has an offset in each satellite given by $k$); this is correct only for the specific date of the observation of February 25, 2019.
- Updated HI_IM-PY2 and HI_IM-PY3 kernels: they needed to be reinstated (probably after ILIFU was up again) and the singularity files have been moved to new directories. For py2 it was just about changing the filename, but for py3 the singularity was seemingly not updated and had an old file format that required me to create a new copy of the singularity file in my own personal directory.
- TO DO (EVENTUALLY): Alter N2 part of the code in order to get information from the correct Celestrak files with all of the satellites (not just "working" satellites), and in general rewrite N2.
- TO DO: Create new (and better) visualizations - try other types of graphs, select by constellation or by signal, select by satellite and check all characteristics of a given satellite (beam response map, signal curve, alpha values, final addition to the 1D and 2D plots).

## WEEK 16: 25 of june - 2 of july
(*OBJETIVE: Implementar código*)
- Corrected setup process and described it in my README (both for general usage or in editable mode).
- Inspected satellite beam response maps and created the specific signal catalog necessary for the observations (N2 part of the code), but now using the new formatting of the signal/satellite lists (and now using NORAD ID instead of the satellite names).
- Found that several satellites have very weird beam responses (unphysical maps that are just quadratic or linear, where it should have the erratic signature of the MeerKAT pointing strategy). One of these was linked to the very big alpha value - makes sense, given that it is a small signal very easily fitted to noise! For now the code is still using these weird satellites, but this should be inspected!
- Organized the information so that the required information (apart from the observations) is stored in the *data/* folder.

### WEEK 17: 2 - 9 of july
(*OBJECTIVE: Implementar código com as novas listas*)
- Altered code extensively in *v4*: changed some variable names, re-organized so that the observations can be given at a later step (instead of being automatically initialized with observations), and re-wrote the code that creates matrix A; checked results and they are almost the same as v3.
- Created *v5* which uses the new signal catalog; results are quite worse than in v4 which might be due to a heavier dependence in some weird maps from satbeam.
- Added time-slice graphs to N4.
- Created *N2_angular_positions.ipynb* which will perform part 2 of the code; currently wrote the first part (TLE download from celestrak and initial formatting), and the beginning of the second (satellite angular positions compared to the telescope). I'm also writing complementary code in *tle_mapping.py* (which will have stuff from *tools.py* and from *check_satellite.py*).

### WEEK 18: 9 - 16 of july
(*OBJECTIVE: Implementar parte 2 do código, escrever abstract para ENAA*)
- Wrote abstract for ENAA.
- Finished *N2_angular_positions.ipynb* and *tle_mapping.py* - the resulting satbeam matrices are slightly different from those obtained previously which is probably due to some incorrect coding, and now the satellites further than 100deg and below the horizon are correctly filtered out of the list.
- Corrected satellite names in the catalog. 
- Created **v6**, which uses the new list + new satbeam maps, and results are slightly better but still worse than with the old list. Specifically, this didn't seem to alter the fact that we have alphas with >50, and it made some peaks more agreeable but is still ill-fitted to data.
- Organized the folders.
- Created **v7**, which uses the old list + new satbeam maps for comparison with v6. The results are almost the same, except it has a small region where GLONASS should emit, and yet its best fits includes no GLONASS satellites! I think the best thing to do now would be to see which specific signals in v4 and v7 are responsible for the better fitting which we can't get in v6, and see if they correspond to some signal which we should have included but don't.