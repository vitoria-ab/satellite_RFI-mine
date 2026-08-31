
''' N3a_fitting: This script creates the simulation object, which gathers all the information, and fits the alphas to the observation given for all of the masking parameters pre-defined. SCRIPT FOR RR. '''


# -------------------------------------------------- #
# ------------------- imports ---------------------- #
# -------------------------------------------------- #

import satellite_RFI.src.simulation as sim
from scipy.optimize import nnls
import sys
sys.path.insert(0, './initialization/')
from imports import *
import parameters as pm
from pathlib import Path


# -------------------------------------------------- #
# -------------- fitting parameters ---------------- #
# -------------------------------------------------- #

# folder in which to save results
Ns = [-2,-1,0,1,2,3,4,5]
folder = f"results/{pm.block}_results/"
folders = []
for N in Ns:
    folders.append(folder + f"RR{N}/")
    Path(folders[-1]).mkdir(exist_ok=True)

# simulation information
path_beam = "{}satbeams_{}_{}_{}-{}.pkl".format(pm.folder, pm.block, pm.beam_model, *pm.freq_range)
path_catalog = f"{pm.folder}catalog_{pm.block}.csv"
path_nearby = f"{pm.folder}nearby_{pm.block}.pkl"

# correct label for satellites in the catalog
if path_catalog==f"{pm.folder}catalogOLD_{pm.block}.csv":  label_sats = "Sat"
else:  label_sats = "NORAD ID"

# cost function options
CFs = ["C1","C2"]

# masking options
masks = {"nomask":[None], 
         "deg":[1,5], 
         "temp":[100,50,25], 
         "pix":[2,5,7]}
time_slices = [(2800,3200), (4200,4700), (5200,5800)]
nearby = pickle.load(open(path_nearby, "rb"))


# -------------------------------------------------- #
# -------------------- fitting --------------------- #
# -------------------------------------------------- #
   
# initializing the simulation
print("Simulating...")
sat = sim.SatelliteSimulation(
    survey_info=[pm.nd_s0, pm.frequency],
    path_catalog=path_catalog,
    path_beam=path_beam,
    freq_range=pm.freq_range,
    freq_slice=pm.freq_slice,
    time_slice=(None,None),
    label_sats=label_sats,
    verbose=False)
sat.use_observations(path_observations=pm.path_observations, verbose=False)

# iterating over mask parameters
for typ in masks:
    for par in masks[typ]:

        # masking
        print(f"Optimizing for {typ} = {par}... ",end="")
        tstart = time.perf_counter()
        if typ=="deg":  sat.use_mask(deg=nearby[par], apply=False, verbose=False)
        elif typ=="nomask":  sat.use_mask(apply=False, verbose=False)
        else:  sat.use_mask(**{typ:par, "apply":False, "verbose":False})

        # iterating over weight choice
        for CF in CFs:

            # doing optimization setup            
            A = np.empty((sat.obs_BGsub.size, len(sat.catalog)))
            for i_sat, start in enumerate(sat.index_sats):
                stop = start + sat.n_signals[i_sat]
                for i in range(start,stop):  
                    A[:,i] = (sat.sat_beam[i_sat] * sat.mask * sat.Tb_factors[i][:,None]).ravel()
            b = (sat.obs_BGsub*sat.mask).ravel()

            # adding weigths and ridge-regularization
            if CF=="C1":  
                weights = 1.0 / sat.obs.ravel()
                A *= weights[:,None]
                b *= weights

            # iterating over each regularization option
            for i,N in enumerate(Ns):
                # creating matrices
                RR = 10**N
                A_RR = np.vstack([A, np.sqrt(RR) * np.eye(A.shape[1])])
                b_RR = np.concatenate([b, np.sqrt(RR) * np.ones(A.shape[1])])
    
                # minimizing
                x,rnorm = nnls(A_RR, b_RR, maxiter=1000)
                alphas_BF = x
                
                # saving information in the file
                if typ=="nomask":  
                    fname = pm.my_name(folder=folders[i], CF=CF)
                    data_info = {"CF":CF, "RR":RR, "freq_slice":pm.freq_slice, "best-fit":alphas_BF}
                else:  
                    fname = pm.my_name(**{"folder":folders[i], "CF":CF, typ:par})
                    data_info = {"CF":CF, "RR":RR, typ:par, "freq_slice":pm.freq_slice, 
                                 "best-fit":alphas_BF}
                with open(fname, "wb") as f:  pickle.dump(data_info,f)

        # printing
        elapsed = time.perf_counter() - tstart
        print(f"took {elapsed/60:.1f} min ({elapsed:.1f} s).")


# -------------------------------------------------- #
# -------------- fitting time_slice ---------------- #
# -------------------------------------------------- #

for time_slice in time_slices:

    # initializing the simulation
    print(f"Optimizing for time_slice = {time_slice}... ",end="")
    tstart = time.perf_counter()
    sat = sim.SatelliteSimulation(
        survey_info=[pm.nd_s0, pm.frequency],
        path_catalog=path_catalog,
        path_beam=path_beam,
        freq_range=pm.freq_range,
        freq_slice=pm.freq_slice,
        time_slice=time_slice, 
        label_sats=label_sats,
        verbose=False)
    sat.use_observations(path_observations=pm.path_observations, verbose=False)
    sat.use_mask(apply=False, verbose=False)

    # iterating over weight choice
    for CF in CFs:

        # doing optimization setup
        A = np.empty((sat.obs_BGsub.size, len(sat.catalog)))
        for i_sat, start in enumerate(sat.index_sats):
            stop = start + sat.n_signals[i_sat]
            for i in range(start,stop):  
                A[:,i] = (sat.sat_beam[i_sat] * sat.Tb_factors[i][:,None]).ravel()
        b = sat.obs_BGsub.ravel()

        # adding weigths
        if CF=="C1":  
            weights = 1.0 / sat.obs.ravel()
            A *= weights[:,None]
            b *= weights

        # iterating over ridge-regularization
        for i,N in enumerate(Ns):
            # creating matrices
            RR = 10**N
            A_RR = np.vstack([A, np.sqrt(RR) * np.eye(A.shape[1])])
            b_RR = np.concatenate([b, np.sqrt(RR) * np.ones(A.shape[1])])

            # minimizing
            x,rnorm = nnls(A_RR, b_RR, maxiter=1000)
            alphas_BF = x
            
            # saving information in the file
            fname = pm.my_name(folder=folders[i], CF=CF, time_slice=time_slice)
            data_info = {"CF":CF, "RR":RR, "time_slice":time_slice, 
                         "freq_slice":pm.freq_slice, "best-fit":alphas_BF}
            with open(fname, "wb") as f:  pickle.dump(data_info,f)
        
    # printing
    elapsed = time.perf_counter() - tstart
    print(f"took {elapsed/60:.1f} min ({elapsed:.1f} s).")


            
            
        




