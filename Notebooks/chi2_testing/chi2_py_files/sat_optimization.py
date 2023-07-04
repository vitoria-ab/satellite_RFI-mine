## ---------------------------------------------PARAMETES AND IMPORTS
# SYSTEMS IMPORT
import sys
sys.path.insert(0, '../../param_import/')
# -------------------------------------------LIST OF IMPORTS
from imports import *
# -------------------------------------------LIST OF PARAMETERS
# import param as pm
import param as pm
# -------------------------------------------OBSERVATION NAME + DATE 
fname, dtime=tools.timepoint(fname=pm.file, date=None)

## ----------------------------------------------------------FREQUENCY
if pm.fs_slice!=None and pm.fe_slice!=None:
    print ('Frequeny range: '+str(pm.fs_slice)+'-'+str(pm.fe_slice)+' MHz')
elif pm.fs_slice!=None and pm.fe_slice==None:
    print ('Frequeny range: '+str(pm.fs_slice)+' MHz to final value')
elif pm.fs_slice==None and pm.fe_slice!=None:
    print ('Frequeny range: Intial value to '+str(pm.fe_slice)+' MHz')
elif pm.fs_slice==None and pm.fe_slice==None:
    print ('Intial to Final frequency value')
else:
    print ('Error, frequency value choices are incorrect')
    
## ------------------------------------------------------------TIME
if pm.ts_slice!=None and pm.te_slice!=None:
    print ('Time range: '+str(pm.ts_slice)+'-'+str(pm.te_slice)+' sec')
elif pm.ts_slice!=None and pm.te_slice==None:
    print ('Time range: '+str(pm.ts_slice)+' sec to final value')
elif pm.ts_slice==None and pm.te_slice!=None:
    print ('Time range: Intial value to '+str(pm.te_slice)+' sec')
elif pm.ts_slice==None and pm.te_slice==None:
    print ('Intial to Final time value')
else:
    print ('Error, time value choices are incorrect')

## -------------------------------------------------------------MASK
if pm.mask_type==None:
    print ('No mask.')
elif pm.mask_type=='degree':
    print ('Degree masking of '+str(pm.mask_degree)+' degrees.')
elif pm.mask_type=='thermal':
    print ('Thermal masking of '+str(pm.mask_temperature)+' kelvin.')
elif pm.mask_type=='temporal':
    print ('Temporal masking')
else:
    print ('Unknown mask given')
## -----------------------------------------------------TIME AVERAGE
if pm.time_size!=None:
    print ('Time average of '+str(pm.time_size)+' seconds applied.')
else:
    print ('No time average.')
## -----------------------------------------------------DAMPNER
if pm.dampner==None:
    print ('No dampening.')
elif pm.dampner=='goob':
    print ('Gaussian Out of Band dampening given.')
    if pm.dampner_sigma==None:
        print ('Random dampner values given.')
    else:
        print ('Damper values fixed to '+str(pm.dampner_sigma)+' level.')
        
##-----------------------------------------------------CHI-SQUARE-SIGMA
if pm.chi_sigma==True:
    print ('The Chi-Sqaure denominator will be: radiometer equation.')
elif pm.chi_sigma==False:
    print ('The Chi-Sqaure denominator will be: 1.')
else:
    print ('Error in selecting the Chi-Square sigma option,')
    
##-----------------------------------------------FILE SAVING LOCATION
# Location
file_loc = pm.data_save+pm.folder
# File name
name = str(pm.file)+'_'
# Frequency
freq_name = str(pm.fs_slice)+'-'+str(pm.fe_slice)+'_'
# Time
if pm.ts_slice==None and pm.te_slice==None:
    time_name = str(np.round(pm.nd_s0[0],2))+'-'+str(np.round(pm.nd_s0[-1],2))+'_'
elif pm.ts_slice!=None and pm.te_slice==None:
    time_name = str(pm.ts_slice)+'-'+str(np.round(pm.nd_s0[-1],2))+'_'
elif pm.ts_slice==None and pm.te_slice!=None:
    time_name = str(np.round(pm.nd_s0[0],2))+'-'+str(pm.te_slice)+'_'
else:
    time_name = str(pm.ts_slice)+'-'+str(pm.te_slice)+'_'
# Mask   
if pm.mask_type=='degree':
    mask_name = pm.mask_type+'-'+pm.mask_degree+'_'
elif pm.mask_type=='thermal':
    mask_name = pm.mask_type+'-'+str(pm.mask_temperature)+'_'
else:
    mask_name = 'no-mask_'
# Dampening
if pm.dampner=='goob':
    if pm.dampner_sigma!=None:
        dampner_name = pm.dampner+'-'+str(pm.dampner_sigma)+'_'
    else:
        dampner_name = pm.dampner+'-random_'
else:
    dampner_name = 'no-dampening_'
# Time average
if pm.time_size!=None:
    time_size_name = 'time_average_'+str(pm.time_size)+'_'
else:
    time_size_name = ''
# Chi sigma
if pm.chi_sigma==True:
    chi_sig_name = 'fraction_'
else:
    chi_sig_name = 'residual_'
# File save name
file_save = file_loc+name+freq_name+time_name+mask_name+dampner_name+chi_sig_name+time_size_name+pm.save_suffix

print ('File location is: '+file_save)


##-------------------------------------------------------------------------------------------------------------##
##---------------------------------------------------INITIALIZING THE FUNCTION
sat = ss(file_name=fname,          
             sats_only=False, 
             data_loc=pm.data_save, 
             sat_loc=pm.data_save,
             survey_info=[pm.nd_s0, pm.nd_s0_coords, pm.frequency], 
             sat_info=pm.satellite_catalogue,
             plots_loc=pm.data_plot,
             sat_beam=pm.beam_model+'_beam_'+str(pm.fs)+'_'+str(pm.fe)+'MHz', 
             frequency_range=[pm.fs, pm.fe], 
             constellations=pm.constellations_remain,
             nearby_satellites=pm.nearby_constellations,
             verbose=False)

##---------------------------------------------------INTIAL ALPHA DICTIONARY VALUES
# Note- There can be a length issue, the length should be the same as number of signals available, change the alphas to zero and not 1
alpha_dic = np.zeros(pm.no_signals)

##---------------------------------------------------INTIAL SIGMA DICTIONARY VALUES
if pm.dampner!=None:
    # Note- There can be a length issue here, be aware
    if pm.dampner_sigma!=None:
        print ('Dampner will be fixed.')
        sigma_dic = pm.dampner_sigma*np.ones(21)
        # The input values for the Optimization of the Chi-Sqaure fitting
        input_param = alpha_dic
    else:
        print ('Dampner will be random.')
        sigma_dic = np.ones(21)
        input_param = np.concatenate((alpha_dic, sigma_dic))

else:
    sigma_dic = None
    input_param = alpha_dic

##------------------------------------------------------EXCECUTING THE INITIAL FUNCTION
sat.excecute(a_param=alpha_dic,                                                # Should always check this value
                 obs_time_start=pm.ts_slice, obs_time_end=pm.te_slice, 
                 obs_frequency_start=pm.fs_slice, obs_frequency_end=pm.fe_slice, 
                 file_bias_choice=pm.bias, 
                 add_sub=[True, False], 
                 attenuation_func=pm.dampner,
                 attenuation_sigma=sigma_dic, 
                 bandsize=None,
                 verbose=True)

##----------------------------------------------------------CHI SQAURE METHOD
def chisq_func2(params):
    # """
    # Chi2 function which will take in all the parameters for the satellites
    # """
    #------------------------------------------------------ Fitting parameters
    a_param = params[:pm.no_signals]
    if pm.dampner!=None:
        if pm.dampner_sigma==None:
            # If it is random then the sigma will work
            # print ('Random dampening sigma applied.')
            s_param = params[21:]
            # If it is not random then the sigma will fixed
        elif pm.dampner_sigma!=None:
            # print ('Fixed dampening sigma applied.')
            s_param = pm.dampner_sigma*np.ones(21)
        else:
            print ('Error in sigma fitting parameters.')
    else:
        # print ('No dampening function')
        s_param=None

    #------------------------------------------------------------Excucting simulation code
    sat.excecute(a_param=a_param, 
                 obs_time_start=pm.ts_slice, obs_time_end=pm.te_slice, 
                 obs_frequency_start=pm.fs_slice, obs_frequency_end=pm.fe_slice, 
                 file_bias_choice=pm.bias, 
                 add_sub=[True, False], 
                 attenuation_func=pm.dampner,
                 attenuation_sigma=s_param, 
                 bandsize=None,
                 verbose=False)

    # ---------------------------------------------MASKING
    # Thermal 
    if pm.mask_type=='thermal':
        # print ('Running thermal mask for '+str(pm.mask_temperature)+' kelvin.')
        max_k = pm.mask_temperature
        zero_arr = np.zeros(sat.calibration_data_slice.shape)
        mask_idx = np.where(sat.calibration_data_slice > max_k)

        zero_arr[mask_idx]=1
        simulation = np.ma.array(data=sat.simulation_TOD_slice.T, mask=zero_arr.T)    #SIMULATIONS
        data = np.ma.array(data=sat.calibration_data_slice.T, mask=zero_arr.T)  #DATA

    # Degree 
    elif pm.mask_type=='degree':
        # print ('Running degree mask for '+str(pm.mask_degree)+' degrees.')
        simulation = np.ma.array(data=sat.simulation_TOD_slice.T, mask=sat.mask_nearby_satellites_slice)
        data = np.ma.array(data=sat.calibration_data_slice.T, mask=sat.mask_nearby_satellites_slice)

    # No masking
    elif pm.mask_type==None:
        # print ('No mask applied')
        simulation = np.ma.array(data=sat.simulation_TOD_slice.T, mask=None)
        data = np.ma.array(data=sat.calibration_data_slice.T, mask=None)

    # Temporal
    elif pm.mask_type=='temporal':
        # print ('No mask applied')
        simulation = np.ma.array(data=sat.simulation_TOD_slice.T, mask=None)
        data = np.ma.array(data=sat.calibration_data_slice.T, mask=None)

    else:
        print ('Error in masking choice')

    #-------------------------------------------TIME AVERAGING
    # Average over a number of timestamps depending on the size
    if pm.time_size!=None:
        data = tools.waterfall_avg_time(timer=pm.nd_s0[sat.time_idx[0]:sat.time_idx[1]], size=pm.time_size, waterfall=data)
        simulation = tools.waterfall_avg_time(timer=pm.nd_s0[sat.time_idx[0]:sat.time_idx[1]], size=pm.time_size, waterfall=simulation)


   ## ------------------------------------------------------------------CHI SQUARE EQUATION
    # Denominator value
    if pm.chi_sigma==True:
        # print ('Running Chi-sigma=radiometer')
        # sig = tools.radiometer_eq(data=data, n_dish=1)  # Note this is sigma (expected noise level), it must be squared to give the radiometer equation
        sig = data  # Note this is sigma (expected noise level), it must be squared to give the radiometer equation

        # ## An added experiment msking all values below Tsys NOTE!!! Make sure to take off
        # data = np.ma.array(data, mask=data<17)
        # simulation = np.ma.array(simulation, mask=data<17)

    elif pm.chi_sigma==False:
        # print ('Running Chi-sigma=1')
        sig = 1
    
    else:
        print ('Error in sigma value for Chi-Square')
    # Numerator value
    chi_num = simulation - data  
    # Chi-Square
    chi_sq = np.ma.sum(chi_num**2 / sig**2)

    print (chi_sq)
    return chi_sq       # Work on getting that chi_num value out

## -----------------------------------------------------------------PRIOR-BOUNDARY INFORMATION
# Boundary values
bnd_val = (0.0, None)
print ('Boundary values are set at: ', bnd_val)
# Seeting bounds for the Chi-Square
if pm.dampner!=None:
    if pm.dampner_sigma==None:
        bnds = [bnd_val for bnd_i in range(2*sat.alpha_len)]
    elif pm.dampner_sigma!=None:
        bnds = [bnd_val for bnd_i in range(sat.alpha_len)]
    else:
        print ('Error in setting in boundary conditons.')
else:
    bnds = [bnd_val for bnd_i in range(sat.alpha_len)]
    
##-------------------------------------------------------------RUNNING THE OPTIMIZATION PARAMETERS
print ('Running optimization')
signal_PL = opt.minimize(fun=chisq_func2, 
                         x0=input_param,                           # Set to none becuase the number of signals will be determined by the bandsize 
                         method='Powell',
                         bounds=bnds, 
                         tol=1e-6, 
                         options={'maxiter':20})

##---------------------------------------------------BEST FIT VALUES
if pm.dampner!=None:
    # Note- There can be a length issue here, be aware
    if pm.dampner_sigma!=None:
        print ('Dampner will be fixed.')
        sigma_param_bf = pm.dampner_sigma*np.ones(21)
        # The input values for the Optimization of the Chi-Sqaure fitting
        a_param_bf = signal_PL.x
    else:
        print ('Dampner was best fitted.')
        sigma_param_bf = signal_PL.x[21:]
        a_param_bf = signal_PL.x[:21]

else:
    sigma_param_bf = None
    a_param_bf = signal_PL.x

##------------------------------------------------RUNNING SECOND INITIALIZATION
print ('Running 2nd init')
sat2 =  ss(file_name=fname,          
             sats_only=False, 
             data_loc=pm.data_save, 
             sat_loc=pm.data_save,
             survey_info=[pm.nd_s0, pm.nd_s0_coords, pm.frequency], 
             sat_info=pm.satellite_catalogue,
             plots_loc=pm.data_plot,
             sat_beam=pm.beam_model+'_beam_'+str(pm.fs)+'_'+str(pm.fe)+'MHz', 
             frequency_range=[pm.fs,pm.fe], 
             constellations=pm.constellations_remain,
             nearby_satellites=pm.nearby_constellations,
             verbose=False)

sat2.excecute(a_param=a_param_bf,                  
                 obs_time_start=pm.ts_slice, obs_time_end=pm.te_slice, 
                 obs_frequency_start=pm.fs_slice, obs_frequency_end=pm.fe_slice, 
                 file_bias_choice=pm.bias, 
                 add_sub=[True, False], 
                 attenuation_func=pm.dampner,
                 attenuation_sigma=sigma_param_bf, 
                 bandsize=None,
                 verbose=False)




##--------------------------------------------------------------SAVING OUTPUTS TO FILE
data_info = {'initial':input_param,
             'time':[pm.ts_slice, pm.te_slice],
             'frequency_slice':[pm.fs_slice, pm.fe_slice],
             'best-fit':signal_PL.x,
             'chi2_value':signal_PL.fun,
             'chi2_div':signal_PL.fun/sat2.simulation_TOD_slice.size
}

pickle.dump(data_info, open(file_save+'.p', 'wb'))

