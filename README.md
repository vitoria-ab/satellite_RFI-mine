# Structure of the code
## Versions of the code:
- **v0**: Constellation paradigm (uses a matrix for each constellation); results are good.
- **v1**: Satellite paradigm, recovering constellation results (uses a matrix for each satellite, but imposes that alphas of satellites within the same constellations are the same); results are good.
- **v2**: Constellation paradigm (uses a matrix for each constellation), but using `lsq_linear`; results are good.
- **v3**: Satellite paradigm using `nnls`, with new results; results are generally good, but need to be inspected.
- **v4**: Satellite paradigm with a restructured code and some very minor differences; results are practically the same as v3 with some improved peaks.
- **v5**: Satellite paradigm with the updated catalog; results are worse in several aspects which might be due to part 2 of the code having some weird satbeams.
- **v6**: Satellite paradigm with the updated catalog and improved satbeam maps; results are better than v5 but still have several weird aspects (which are now solely due to the catalog lacking necessary signals).
- **v7**: Satellite paradigm with the old catalog and improved satbeam maps, for comparison with v6.
- **v8**: Satellite paradigm with new catalog and new satbeam maps, with ridge-regularization. 

## Files in `sattelite_RFI`:
- **attenuation**: File with attenuation functions `tophat_oob` and `gaussian_oob`; rewritten for clarity and celerity. However, all of the mentions to attenuation were removed from the code so this currently is not used!
- **beam_model**: File with different telescope beam models, either analytical or from a file; rewritten.
- **check_satellite**: Old file, not rewritten.
- **data_reduction**: Old file, not rewritten.
- **Generating_Calibrated_Data**: Old file, not rewritten.
- **psd_models**: File with the Power Spectrum Density models for the GNSS satellite signals; rewritten.
- **simulation_cons**: File with the simulation object, which gathers information calculated in the different files and performs the final calculations for the fitting; completely rewritten for clarity and celerity. Used in v0 and v2.
- **simulation**: Rewrite of simulation_cons but using the paradigm of individual satellites instead of constellations. Used in v1 and v3.
- **simulation_NC**: Rewrite of simulations but using the new catalog.
- **tle_mapping**: File with functions to map TLEs to angular positions, and also holds the SatelliteMap object; rewritten.
- - **tools**: Old file, not rewritten. 
- **wiggleZ_area**: Old file, not rewritten. 

## Files in `Notebooks`:
- **final_notebooks/**: Folder with the final notebooks; whenever necessary, copy them into the parent directory and change them. They use the final satbeam maps and nearby sats and new catalog.
- **initialization/**: Folder with the imports and the parameters (block, beam model, frequency range, etc).
- **job_submissions/**: Folder with the files to submit the fit as a job to the batch.
- **previous_NBs/**: Folder with various notebooks with previous versions of the code and their results.
- **results/**: Folder of results (divided by observation blocks).
- **simulation_data/**: Folder with the necessary simulation data (the generated satbeam + nearby_sats + catalog for each observation, and signal + satellite list which stay the same).

## Best values for ridge-regularization:
For each of the observation blocks, several values for lambda_RR were tried in order to regularize the alphas obtained; this gave much more agreeable lambda_RR results but the exact value depends on the mask, observation and CF.

#### 1551055211
- For C1: can go up to RR=1e-2 (time-slice), 1e-1 (thermal), 1e0 (degree,pixel) and 1e1 (no mask) before recovering worse fit, and the alphas get much more agreeable. 
- For C2: can go up to RR=1e1 (time-slice), 1e2 (thermal25K), 1e3 (thermal50K100K,pixel), 1e4 (no mask,degree) before recovering worse fit, and the alphas get much more agreeable.
- Overall C2 needs a much harder regularization constant to achieve any differences in alphas (makes sense, its CF showing in graphs is several orders of magnitude bigger than in C1) - only shows any difference in alphas 1e1 and bigger, while C1 shows difference for values 1e-2!

#### 1553966342
- For C1: can go up to RR=1e0 (time-slice 1800-2200), RR=1e1 (nomask, angular, thermal, pix, time-slice 4400-4800s) before having a worse fit.
- For C2: can go up to RR1e3 (time-slice 1800-2200), RR=1e4 (nomask, angular, thermal, pix, time-slice 4400-4800s) before having a worse fit.


# Requirements to run
## Setting up the PY3 singularity
Perform these steps in the ILIFU Jupyter Lab terminal in order to set up the singularities HI_IM-PY2 and HI_IM-PY3. The singularities are stored in the */software/astro/containers/* directory, but there doesn't seem to be any recent copy of the PY3 singularity; the way that it worked for me was by creating a copy of the old singularity file into my personal directory and using that new file as the singularity source:
1. Create a temporary folder (need one for the temporary files created during the copy): `mkdir /users/{USER}/tmp`
2. Copy the singularity file into a new file: `TMPDIR=/users/{USER}/tmp SINGULARITY_TMPDIR=/users/{USER}/tmp singularity build /users/{USER}/workspace/hi_im-py3.sif /idia/software/containers/hi_im-py3.simg` (this can take a while, +30 mins).
3. Move to folder `/users/{USER}/.local/share/jupyter/kernels/`.
4. Create a folder for the two singularities: `mkdir /{NAME}/`.
4. In the two folders, create a `kernel.json` and copy the contents from the respective file in `satellite_RFI/kernels`.

## Setting up the two kernels and repository
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

### WEEK 19: 16 - 23 of july
(*OBJECTIVES: Tentar ver o que está errado com o código, escrever relatório para a extensão da bolsa, fazer apresentação para mostrar dia 24 ao josé fonseca.*)
- Finishing writing v4 in a way that is compatible with the final codes, and created the final notebooks N3a, N3b and N3c (which can be run with any versions of the simulation data, and so can be just used as default from now on). 
- Found a coding error in N2 which made the satbeam maps slightly wrong; now they are corrected. Redid v6 and v7, and results are the same with only a slightly better final minimized value for CF. 
- Wrote files for job submission of N3a on slurm instead of running interactively on the notebook. 
- Overall, different masks equal different best-case scenarios for the fitting (old catalog vs. new catalog) using the new satbeams (and this is the correct one, so it doesn't make sense to compare with the old satbeams).
- Wrote scholarship report. 

### WEEK 20: 23 - 30 of july
(*OBJETIVES: Fazer apresentação, fazer cenas que forem faladas.*) 
- Made presentation for MeerKLASS. 
- Retrieved missing GLONASS satellites from Space-Track.org, in order to include them on the TLEs. Re-ran the code and fitting doesn't need to be repeated, since they are always below the horizon during observations. 
- Wrote **v8** which adds various degrees of ridge-regularization (in order to penalize large alphas - doesn't do anything to make the simulation itself better). Created the simulation with varying RR, and found that the best value depends both on the cost function (C1 or C2) and on the mask used. 
- Results for **v8** are the same, and we achieve better alphas for the same simulated signal which is good, but with various degrees of sucess (higher RR means harder regularization).
- Created satbeam files for 1553966342; added 2 missing GLONASS satellites (ended up not mattering for the fit), and correcting beidou names (only M1,M2 appeared). It won't be necessary to do an angular 5deg, since there is a satellite that is always below that value and so we wouldn't get almost anything.

### WEEK 21: 30 of july - 6 of august
(*OBJECTIVES: Fazer fit com as outras observações, melhorar a visualização dos alphas, ver se a calibração pode ser corrida para outras antenas.*)
- Fitted some further observations (that were already calibrated): 1553966342, 1554156377, 1556138397 (stopped midway because the observations are weird).
- Currently performing fit on all observational blocks for which we have the calibration (stated in the paper); check if what we are fitting is per antenae or if it is a mean of all antennae responses. 

### WEEK 22: 6 - 13 of august
(*OBJETIVES: Try to use other observations besides Brandon's, check calibration notebook, visualize more clearly results*)
- Gave a look at the calibration notebook, and most of the quantities I can recover except specifically the calibrated visibility maps of each antenna! However, the calibrated visibility needs to be done from scratch, and so I'm waiting for access to the necessary folders.
- Began to generate the table with all results together in a single DataFrame.

### WEEK 23: 13 - 20 of august
(*OBJECTIVES: Finish calibration notebook, finish visualization of all results*)
- Generated the table of all results obtained and saved them in the `results/{block}_results.csv` files.
- Chose the best RR values for each block + mask + CF and saved them in the `results/bestRRs.csv` file.
- Debugged code - sat.simulate() was working incorrectly (using some extra empty satellites when it should skip them) and so the cost function values were a bit different than supposed to; I think the plots were mostly correct, and the optimization wasn't affected since it was performed with the matrix A and not the simulate() function.

### WEEK 24: 21 - 27 of august
(*OBJECTIVES: Ler bibliografia para a tese, ver se os alphas de satélites longe contribuem alguma coisa significativa, ver como adicionar barras de erro, ver calibração por completo!*)
- Finished rewriting calibration, but without any debugging since I don't have yet access to the data.
- Started reading thesis bibliography.

## WEEK 25: 28 of august - 3 of september
(*OBJECTIVES: Igual a semana passada*)
- Gained access to the calibration data, started debugging the calibration code.
- Finished calibration of the background temperatures except for the constant additive value (however, only debugged for the first antenna so far due to ILIFU's problems).
- Finished calibration of the bandpass: several problems were arising but were since solutioned, and managed to retrieve exactly the same calibration plots as Brandon for the m000 antenna. 
- Continued reading thesis bibliography. 