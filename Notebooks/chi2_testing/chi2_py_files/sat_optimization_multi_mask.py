##====================================================================================================================================##
## PARAMETERS AND IMPORTS
import sys
from imports import *
import param_multi_mask as pm

##====================================================================================================================================##
## OBSERVATION NAME + DATE
fname, dtime = tools.timepoint(fname=pm.file, date=None)

##====================================================================================================================================##
## FILE SAVE
## File path
file_loc = pm.data_save + pm.folder
## Filename
name = str(pm.file) + "_"

##====================================================================================================================================##
## FREQUENCY
if pm.fs_slice is not None and pm.fe_slice is not None:
    print("Frequeny range: " + str(pm.fs_slice) + "-" + str(pm.fe_slice) + " MHz")
elif pm.fs_slice is not None and pm.fe_slice is None:
    print("Frequeny range: " + str(pm.fs_slice) + " MHz to final value")
elif pm.fs_slice is None and pm.fe_slice is not None:
    print("Frequeny range: Intial value to " + str(pm.fe_slice) + " MHz")
elif pm.fs_slice is None and pm.fe_slice is None:
    print("Intial to Final frequency value")
else:
    print("Error, frequency value choices are incorrect")

freq_name = str(pm.fs_slice) + "-" + str(pm.fe_slice) + "_"

##====================================================================================================================================##
## MASK TYPE
## No mask
if (
    pm.mask_degree is None
    and pm.mask_temperature is None
    and pm.mask_temporal[0] is None
    and pm.mask_temporal[1] is None
    and pm.mask_pixel_timeline is None
):
    mask_name = "no-mask_"
    print(pm.mask_type)
    
    
## Angular mask
elif (
    pm.mask_degree is not None
    and pm.mask_temperature is None
    and pm.mask_temporal[0] is None
    and pm.mask_temporal[1] is None
    and pm.mask_pixel_timeline is None
):
    mask_name = "degree-" + pm.mask_degree + "_"
    print(pm.mask_type)
    
    
## Temperature mask
elif (
    pm.mask_temperature is not None
    and pm.mask_degree is None
    and pm.mask_temporal[0] is None
    and pm.mask_temporal[1] is None
    and pm.mask_pixel_timeline is None
):
    mask_name = "thermal-" + str(pm.mask_temperature) + "_"
    print(pm.mask_type)
    
    
## Temporal mask
elif (
    pm.mask_degree is None
    and pm.mask_temperature is None
    and (pm.mask_temporal[0] is not None or pm.mask_temporal[1] is not None)
    and pm.mask_pixel_timeline is None
):
    mask_name = "temporal_"
    print(pm.mask_type)
    
    
## Timeline Pixel mask
elif (
    pm.mask_degree is None
    and pm.mask_temperature is None
    and pm.mask_temporal[0] is None
    and pm.mask_temporal[1] is None
    and pm.mask_pixel_timeline is not None
):
    mask_name = "pix_timeline_"+str(pm.mask_pixel_timeline) + "_"
    print(pm.mask_type)

    
## Angular+Thermal mask
elif (
    pm.mask_degree is not None
    and pm.mask_temperature is not None
    and pm.mask_temporal[0] is None
    and pm.mask_temporal[1] is None
    and pm.mask_pixel_timeline is None
):
    mask_name = (
        "degree-" + pm.mask_degree + "_thermal-" + str(pm.mask_temperature) + "_"
    )
    print(pm.mask_type)
    
    
## Angular+Temporal mask
elif (
    pm.mask_degree is not None
    and pm.mask_temperature is None
    and (pm.mask_temporal[0] is not None or pm.mask_temporal[1] is not None)
    and pm.mask_pixel_timeline is None
):
    mask_name = "degree-" + pm.mask_degree + "_temporal_"
    print(pm.mask_type)
    
    
## Thermal+Temporal mask
elif (
    pm.mask_degree is None
    and pm.mask_temperature is not None
    and (pm.mask_temporal[0] is not None or pm.mask_temporal[1] is not None)
    and pm.mask_pixel_timeline is None
):
    mask_name = "thermal-" + str(pm.mask_temperature) + "_temporal_"
    print(pm.mask_type)
    
    
## Angular+Thermal+Temporal
elif (
    pm.mask_degree is not None
    and pm.mask_temperature is not None
    and pm.mask_temporal[0] is not None
    and pm.mask_temporal[1] is not None
    and pm.mask_pixel_timeline is None
):
    mask_name = (
        "degree-"
        + pm.mask_degree
        + "_thermal-"
        + str(pm.mask_temperature)
        + "_temporal_"
    )
    print(pm.mask_type)
else:
    print(pm.mask_type)

    
## Temporal mask
if pm.ts_slice is not None and pm.te_slice is not None:
    print(
        "Time range: "
        + str(pm.ts_slice)
        + " seconds to "
        + str(pm.te_slice)
        + " seconds."
    )
    time_name = str(pm.ts_slice) + "-" + str(pm.te_slice) + "_"
elif pm.ts_slice is not None and pm.te_slice is None:
    print("Time range: " + str(pm.ts_slice) + " seconds to final time.")
    time_name = str(pm.ts_slice) + "-" + str(np.round(pm.nd_s0[-1], 2)) + "_"
elif pm.ts_slice is None and pm.te_slice is not None:
    print("Time range: initial time to " + str(pm.te_slice) + " seconds.")
    time_name = str(np.round(pm.nd_s0[0], 2)) + "-" + str(pm.te_slice) + "_"
elif pm.ts_slice is None and pm.te_slice is None:
    print("Time range: inital to final time.")
    time_name = (
        str(np.round(pm.nd_s0[0], 2)) + "-" + str(np.round(pm.nd_s0[-1], 2)) + "_"
    )
else:
    print("Error, time range choices are incorrect.")

## Time average
if pm.time_average is not None:
    time_average_name = "time_average_" + str(pm.time_average) + "_"
else:
    time_average_name = ""

##====================================================================================================================================##
## DAMPNER
if pm.dampner is None:
    print("No dampening.")
    dampner_name = "no-dampening_"
elif pm.dampner == "goob":
    print("Gaussian Out of Band dampening given.")
    if pm.dampner_sigma is None:
        print("Random dampner values given.")
        dampner_name = pm.dampner + "-random_"
    else:
        print("Damper values fixed to " + str(pm.dampner_sigma) + " level.")
        dampner_name = pm.dampner + "-" + str(pm.dampner_sigma) + "_"

##====================================================================================================================================##
## CHI SQUARE SIGMA
if pm.chi_sigma == True:
    print("The Chi-Sqaure denominator will be: radiometer equation.")
    chi_sig_name = "fraction_"
elif pm.chi_sigma == False:
    print("The Chi-Sqaure denominator will be: 1.")
    chi_sig_name = "residual_"
else:
    print("Error in selecting the Chi-Square sigma option.")

##====================================================================================================================================##
file_save = (
    file_loc
    + name
    + freq_name
    + time_name
    + mask_name
    + dampner_name
    + chi_sig_name
    + time_average_name
    + pm.save_suffix
)
print("File location is: " + file_save)

##====================================================================================================================================##
# Saving parameter file
parameter_save = {
    "Angular mask": pm.mask_degree,
    "Thermal mask": pm.mask_temperature,
    "Temporal mask": pm.mask_temporal,
    "Time average": pm.time_average,
    "Chi Square Sigma": pm.chi_sigma,
    "Dampner": pm.dampner,
}

pickle.dump(parameter_save, open(file_save + "_parameter.p", "wb"))

##====================================================================================================================================##
## INITIALIZING THE FUNCTION
sat = ss(
    file_name=fname,
    sats_only=False,
    data_loc=pm.data_save,
    sat_loc=pm.data_save,
    survey_info=[pm.nd_s0, pm.nd_s0_coords, pm.frequency],
    sat_info=pm.satellite_catalogue,
    plots_loc=pm.data_plot,
    sat_beam=pm.beam_model + "_beam_" + str(pm.fs) + "_" + str(pm.fe) + "MHz",
    frequency_range=[pm.fs, pm.fe],
    constellations=pm.constellations_remain,
    nearby_satellites=pm.nearby_constellations,
    verbose=False,
)

## INTIAL ALPHA DICTIONARY VALUES
## NOTE - There can be a length issue, the length should be the same as number of signals available
alpha_dic = np.zeros(pm.no_signals)

## INTIAL SIGMA DICTIONARY VALUES
if pm.dampner is not None:
    # Note- There can be a length issue here, be aware
    if pm.dampner_sigma is not None:
        print("Dampner will be fixed.")
        sigma_dic = pm.dampner_sigma * np.ones(21)
        # The input values for the Optimization of the Chi-Sqaure fitting
        input_param = alpha_dic
    else:
        print("Dampner will be random.")
        sigma_dic = np.ones(21)
        input_param = np.concatenate((alpha_dic, sigma_dic))

else:
    sigma_dic = None
    input_param = alpha_dic

##====================================================================================================================================##
## EXCECUTING THE INITIAL FUNCTION
sat.excecute(
    a_param=alpha_dic,  # Should always check this value
    obs_time_start=pm.ts_slice,
    obs_time_end=pm.te_slice,
    obs_frequency_start=pm.fs_slice,
    obs_frequency_end=pm.fe_slice,
    file_bias_choice=pm.bias,
    add_sub=[True, False],
    attenuation_func=pm.dampner,
    attenuation_sigma=sigma_dic,
    bandsize=None,
    verbose=True,
)

##====================================================================================================================================##
## CHI SQAURE METHOD
def chisq_func2(params):
    ## FITTING PARAMETERS
    a_param = params[: pm.no_signals]
    if pm.dampner is not None:
        if pm.dampner_sigma is one:
            # If it is random then the sigma will work
            s_param = params[21:]
            # If it is not random then the sigma will fixed
        elif pm.dampner_sigma is not None:
            s_param = pm.dampner_sigma * np.ones(21)
        else:
            print("Error in sigma fitting parameters.")
    else:
        s_param = None

    ## EXCECUTION
    sat.excecute(
        a_param=a_param,
        obs_time_start=pm.ts_slice,
        obs_time_end=pm.te_slice,
        obs_frequency_start=pm.fs_slice,
        obs_frequency_end=pm.fe_slice,
        file_bias_choice=pm.bias,
        add_sub=[True, False],
        attenuation_func=pm.dampner,
        attenuation_sigma=s_param,
        bandsize=None,
        verbose=False,
    )

    ##====================================================================================================================================##
    ## MASK TYPE
    ## No mask
    if (
        pm.mask_degree is None
        and pm.mask_temperature is None
        and pm.mask_temporal[0] is None
        and pm.mask_temporal[1] is None
        and pm.mask_pixel_timeline is None
    ):
        simulation = np.ma.array(data=sat.simulation_TOD_slice.T, mask=None)
        data = np.ma.array(data=sat.calibration_data_slice.T, mask=None)

    ## Angular mask
    elif (
        pm.mask_degree is not None
        and pm.mask_temperature is None
        and pm.mask_temporal[0] is None
        and pm.mask_temporal[1] is None
        and pm.mask_pixel_timeline is None
    ):
        simulation = np.ma.array(
            data=sat.simulation_TOD_slice.T, mask=sat.mask_nearby_satellites_slice
        )
        data = np.ma.array(
            data=sat.calibration_data_slice.T, mask=sat.mask_nearby_satellites_slice
        )

    ## Temperature mask
    elif (
        pm.mask_temperature is not None
        and pm.mask_degree is None
        and pm.mask_temporal[0] is None
        and pm.mask_temporal[1] is None
        and pm.mask_pixel_timeline is None
    ):
        max_k = pm.mask_temperature
        zero_arr = np.zeros(sat.calibration_data_slice.shape)
        mask_idx = np.where(sat.calibration_data_slice > max_k)
        zero_arr[mask_idx] = 1
        simulation = np.ma.array(data=sat.simulation_TOD_slice.T, mask=zero_arr.T)
        data = np.ma.array(data=sat.calibration_data_slice.T, mask=zero_arr.T)

    ## Temporal mask
    elif (
        pm.mask_degree is None
        and pm.mask_temperature is None
        and (pm.mask_temporal[0] is not None or pm.mask_temporal[1] is not None)
        and pm.mask_pixel_timeline is None
    ):
        simulation = np.ma.array(data=sat.simulation_TOD_slice.T, mask=None)
        data = np.ma.array(data=sat.calibration_data_slice.T, mask=None)
        
    ## Pixel timeline mask
    elif (
            pm.mask_degree is None
            and pm.mask_temperature is None
            and pm.mask_temporal[0] is None
            and pm.mask_temporal[1] is None
            and pm.mask_pixel_timeline is not None
        ):
        masker_tod = tools.time_line_masker(data_in = sat.calibration_data_slice.T, t_value = pm.mask_pixel_timeline)
        simulation = np.ma.array(data=sat.simulation_TOD_slice.T, mask=masker_tod)
        data = np.ma.array(data=sat.calibration_data_slice.T, mask=masker_tod)


    ## Angular+Thermal mask
    elif (
        pm.mask_degree is not None
        and pm.mask_temperature is not None
        and pm.mask_temporal[0] is None
        and pm.mask_temporal[1] is None
        and pm.mask_pixel_timeline is None
    ):
        max_k = pm.mask_temperature
        zero_arr = np.zeros(sat.calibration_data_slice.shape)
        mask_idx = np.where(sat.calibration_data_slice > max_k)
        zero_arr[mask_idx] = 1
        sim = np.ma.array(data=sat.simulation_TOD_slice.T, mask=zero_arr.T)
        dat = np.ma.array(data=sat.calibration_data_slice.T, mask=zero_arr.T)
        simulation = np.ma.array(data=sim, mask=sat.mask_nearby_satellites_slice)
        data = np.ma.array(data=dat, mask=sat.mask_nearby_satellites_slice)

    ## Angular+Temporal mask
    elif (
        pm.mask_degree is not None
        and pm.mask_temperature is None
        and (pm.mask_temporal[0] is not None or pm.mask_temporal[1] is not None)
        and pm.mask_pixel_timeline is None
    ):
        simulation = np.ma.array(
            data=sat.simulation_TOD_slice.T, mask=sat.mask_nearby_satellites_slice
        )
        data = np.ma.array(
            data=sat.calibration_data_slice.T, mask=sat.mask_nearby_satellites_slice
        )

    ## Thermal+Temporal mask
    elif (
        pm.mask_degree is None
        and pm.mask_temperature is not None
        and (pm.mask_temporal[0] is not None or pm.mask_temporal[1] is not None)
        and pm.mask_pixel_timeline is None
    ):
        max_k = pm.mask_temperature
        zero_arr = np.zeros(sat.calibration_data_slice.shape)
        mask_idx = np.where(sat.calibration_data_slice > max_k)
        zero_arr[mask_idx] = 1
        simulation = np.ma.array(data=sat.simulation_TOD_slice.T, mask=zero_arr.T)
        data = np.ma.array(data=sat.calibration_data_slice.T, mask=zero_arr.T)

    ## Angular+Thermal+Temporal
    elif (
        pm.mask_degree is not None
        and pm.mask_temperature is not None
        and pm.mask_temporal[0] is not None
        and pm.mask_temporal[1] is not None
        and pm.mask_pixel_timeline is None
    ):
        max_k = pm.mask_temperature
        zero_arr = np.zeros(sat.calibration_data_slice.shape)
        mask_idx = np.where(sat.calibration_data_slice > max_k)
        zero_arr[mask_idx] = 1
        sim = np.ma.array(data=sat.simulation_TOD_slice.T, mask=zero_arr.T)
        dat = np.ma.array(data=sat.calibration_data_slice.T, mask=zero_arr.T)
        simulation = np.ma.array(data=sim, mask=sat.mask_nearby_satellites_slice)
        data = np.ma.array(data=dat, mask=sat.mask_nearby_satellites_slice)

    else:
        print("Error in masking choice")

    ##====================================================================================================================================##

    ## TIME AVERAGING
    if pm.time_average is not None:
        data = tools.waterfall_avg_time(
            timer=pm.nd_s0[sat.time_idx[0] : sat.time_idx[1]],
            size=pm.time_average,
            waterfall=data,
        )
        simulation = tools.waterfall_avg_time(
            timer=pm.nd_s0[sat.time_idx[0] : sat.time_idx[1]],
            size=pm.time_average,
            waterfall=simulation,
        )

    ##====================================================================================================================================##

    ## CHI SQUARE EQUATION
    ## Denominator value
    if pm.chi_sigma == True:
        sig = data
    elif pm.chi_sigma == False:
        sig = 1
    else:
        print("Error in sigma value for Chi-Square")
    ## Numerator value
    chi_num = simulation - data
    ## Chi-Square
    chi_sq = np.ma.sum(chi_num ** 2 / sig ** 2)

    ##====================================================================================================================================##
    print(chi_sq)
    return chi_sq


##====================================================================================================================================##
## PRIOR-BOUNDARY INFORMATION
## Boundary values
bnd_val = (0.0, None)
print("Boundary values are set at: ", bnd_val)
## Seeting bounds for the Chi-Square
if pm.dampner is not None:
    if pm.dampner_sigma is None:
        bnds = [bnd_val for bnd_i in range(2 * sat.alpha_len)]
    elif pm.dampner_sigma is not None:
        bnds = [bnd_val for bnd_i in range(sat.alpha_len)]
    else:
        print("Error in setting in boundary conditons.")
else:
    bnds = [bnd_val for bnd_i in range(sat.alpha_len)]

##====================================================================================================================================##
## RUNNING THE OPTIMIZATION PARAMETERS
print("Running optimization")
signal_PL = opt.minimize(
    fun=chisq_func2,
    x0=input_param,  # Set to none becuase the number of signals will be determined by the bandsize
    method="Powell",
    bounds=bnds,
    tol=1e-6,
    options={"maxiter": 20},
)

##====================================================================================================================================##
## BEST FIT VALUES
if pm.dampner is not None:
    # Note- There can be a length issue here, be aware
    if pm.dampner_sigma is not None:
        print("Dampner will be fixed.")
        sigma_param_bf = pm.dampner_sigma * np.ones(21)
        # The input values for the Optimization of the Chi-Sqaure fitting
        a_param_bf = signal_PL.x
    else:
        print("Dampner was best fitted.")
        sigma_param_bf = signal_PL.x[21:]
        a_param_bf = signal_PL.x[:21]

else:
    sigma_param_bf = None
    a_param_bf = signal_PL.x

##====================================================================================================================================##
## RUNNING SECOND INITIALIZATION
print("Running 2nd init")
sat2 = ss(
    file_name=fname,
    sats_only=False,
    data_loc=pm.data_save,
    sat_loc=pm.data_save,
    survey_info=[pm.nd_s0, pm.nd_s0_coords, pm.frequency],
    sat_info=pm.satellite_catalogue,
    plots_loc=pm.data_plot,
    sat_beam=pm.beam_model + "_beam_" + str(pm.fs) + "_" + str(pm.fe) + "MHz",
    frequency_range=[pm.fs, pm.fe],
    constellations=pm.constellations_remain,
    nearby_satellites=pm.nearby_constellations,
    verbose=False,
)

sat2.excecute(
    a_param=a_param_bf,
    obs_time_start=pm.ts_slice,
    obs_time_end=pm.te_slice,
    obs_frequency_start=pm.fs_slice,
    obs_frequency_end=pm.fe_slice,
    file_bias_choice=pm.bias,
    add_sub=[True, False],
    attenuation_func=pm.dampner,
    attenuation_sigma=sigma_param_bf,
    bandsize=None,
    verbose=False,
)

##====================================================================================================================================##
## SAVING DATA INFORMATION
data_info = {
    "initial": input_param,
    "time": [pm.ts_slice, pm.te_slice],
    "frequency_slice": [pm.fs_slice, pm.fe_slice],
    "best-fit": signal_PL.x,
    "chi2_value": signal_PL.fun,
    "chi2_div": signal_PL.fun / sat2.simulation_TOD_slice.size,
}

pickle.dump(data_info, open(file_save + ".p", "wb"))
