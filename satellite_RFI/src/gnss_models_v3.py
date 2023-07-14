import pandas as pd
import numpy as np
import scipy as sp
import astropy.constants as cc
from satellite_RFI.src import psd_models_v2 as psd
from fractions import Fraction
from satellite_RFI.src import attenuation_function as af
#-------------------------------------------------------------_#

def floaty(x):
    '''
    In case the ratio becomes a pickle to deal with
    '''
    try:
        a = float(x)
    except (ValueError):
        a = float(Fraction(x))

    return a

def signal_cosntant(x):
    '''
    A function to return the alpha values
    '''
    return np.ones(len(x))

#-------------------------------------------------------------_#

def gnss_satellites(name_sat, frequency_gnss, attenuation, sat_cat_data):

    '''Returns the Spectral Energy Density of the GNSS and the Data file that we used as an input
    name_sat - Satellite name
    frequency_gnss - Frequency list of satellites [MHz]
    excel_sat_info - The satellite excel cataloguen name in the s3 Notebook folder
    attenuation- the bandwidth and level of the drop
    
    '''
    # Distances to the satellite constellations, taken from Springer Handbook pg 1234 

    # Extracting smaller data table for each name
    data_sub = sat_cat_data[sat_cat_data['Sys'].str.contains(name_sat)]
 
    # Making the Spectral Energy density list
    sed = []
    flux_density = []

    # Looping through all the sub-data index
    for i in data_sub.index:

        if data_sub['P_t (dBW)'][i]==0 or data_sub['G_t (dBi)'][i]==0:
            power = 0
        else:
            power = 10**(data_sub['P_t (dBW)'][i]/10) * 10**(data_sub['G_t (dBi)'][i]/10) * data_sub['Alpha'][i] / (4*np.pi)# Edit *r**2) 
        

        if 'BPSK(' in data_sub['Modulation'][i]:
            s = data_sub['Modulation'][i]
            T_c = float(s[s.find("(")+1:s.find(")")])   # Getting the chip interval value
            model = psd.BPSK(f=frequency_gnss - data_sub['Frequency[MHz]'][i], n_c=T_c,
                             f0=data_sub['Rate(MHz)'][i] / T_c)


        if 'BOC(' in data_sub['Modulation'][i]:
            try:
                s = data_sub['Modulation'][i]
                # Getting the values between parenthesis and converting to float
                T_s, T_c = [float(x) for x in s[s.find("(")+1:s.find(")")].split(',')]
                model = psd.BOC(f=frequency_gnss - data_sub['Frequency[MHz]'][i], n_c=T_c,
                                 n_s=T_s, f0=data_sub['Rate(MHz)'][i] / T_c)
            # Bad method of by-passing TMBOC values


            except (ValueError, UnboundLocalError):
                pass


        if 'BOCcos(' in data_sub['Modulation'][i]:
            s = data_sub['Modulation'][i]
            # Getting the values between parenthesis and converting tp float
            T_s, T_c = [float(x) for x in s[s.find("(")+1:s.find(")")].split(',')]
            model = psd.BOCc(f=frequency_gnss - data_sub['Frequency[MHz]'][i], n_c=T_c,
                             n_s=T_s, f0=data_sub['Rate(MHz)'][i] / T_c)


        if 'AltBOC(' in data_sub['Modulation'][i]:
            # Going to also catch TD-AltBOC
            s = data_sub['Modulation'][i]
            # Getting the values between parenthesis and converting to float
            T_s, T_c = [float(x) for x in s[s.find("(")+1:s.find(")")].split(',')]
            model = psd.altBOC(f=frequency_gnss - data_sub['Frequency[MHz]'][i], n_s=T_s,
                               n_c=T_c, f0=data_sub['Rate(MHz)'][i] / T_c)


        if 'TMBOC' in data_sub['Modulation'][i]:
            s = data_sub['Modulation'][i]
            # Getting the values between parenthesis and converting to float
            T_s, T_c, rt = [floaty(x) for x in s[s.find("(")+1:s.find(")")].split(',')]
            model = psd.TMBOC(f=frequency_gnss - data_sub['Frequency[MHz]'][i], n_c=T_c,
                             n_s=T_s, f0=data_sub['Rate(MHz)'][i] / T_c, ratio=rt)


        if 'CBOC' in data_sub['Modulation'][i]:
            s = data_sub['Modulation'][i]
            # Getting the values between parenthesis and converting to float
            T_s, T_c, rt = [floaty(x) for x in s[s.find("(")+1:s.find(")")].split(',')]
            model = psd.CBOC(f=frequency_gnss - data_sub['Frequency[MHz]'][i], n_c=T_c,
                             n_s=T_s, f0=data_sub['Rate(MHz)'][i] / T_c, ratio=rt)


        model = np.array([0 if np.isnan(x) else x for x in model])
               
        # Attenuation section
        if attenuation[0]==None:
            model2 = model
            
        elif attenuation[0]=='tophat':
        # Adding Top-Hat
            model2 = model * af.tophat_rect(f=frequency_gnss, fi=data_sub['Frequency[MHz]'][i], 
                                            band=attenuation[0], level=attenuation[1][i], values=np.ones(len(model)))
            
        elif attenuation[0]=='goob':
        # Adding Gaussian Out-of-Band
            model2 = model * af.gaussian_oob(f=frequency_gnss, fi=data_sub['Frequency[MHz]'][i], 
                                             band=data_sub['Bandwidth'][i], sigma=data_sub['Sigma'][i], values=np.ones(len(model)))
        else:
            break
 

        ##  Converting the SED into SI units of Jansky
        # sed.append(power * model2 * 1e26 / 1e6)
        sed.append(power * model2)
        flux_density.append(power)

    sed = np.array(sed)
    # return sed
    
    flux_density = np.array(flux_density)
    return sed, flux_density

    
## Function that returns the TOD values

def TOD_sats(name_tod, fname, frequency_tod, beam_model, attenuation, sat_cat_data):

    '''
    Returns the sat_temp in units of mK
    name - a str;
    frequency - range of frequencies in MHz;
    beam_model - coming from Yi-Chaos angular seperation code, if 2d then should be transposed
    excel_sat - the satellite catalogue name
    excel_cat_loc - the location of the mask, if !None, you set the location, else location is the same
    '''
    
    # Calling the GNSS function above in order to obtain the PSD's for the constellation with the power from the satellites
    sats_model, flux_density = gnss_satellites(name_sat=name_tod, frequency_gnss=frequency_tod, attenuation=attenuation, sat_cat_data=sat_cat_data)   
    
    # Comninging all the satellites that belong to a specific constellation together
    sats_model_t = np.sum(sats_model, axis=0)  
    
    # Channel width
    delta_nu = 0.2*1e6   # Hz
    # delta_nu = 1*1e6   # Hz
    # Multiplying the SED with the conversion constants, include converting out of Jansky
    sats_model_tc = sats_model_t * cc.c.value**2 / cc.k_B.value / 4 / np.pi / (frequency_tod*1e6)**2 / delta_nu  
    
    # sats_model_tc = sats_model_t * cc.c.value**2 / cc.k_B.value / 4 / np.pi / (frequency_tod*1e6)**2 / 1e26  # Multiplying the constants, look at the page to see the units

    
    # A gain factor is multplied to the SED, see Harpar paper. NOTE!!! this is of concern because unsure of where it came from
    sats_model_tc = sats_model_tc * 1e4  
    
    # Multplying the SED by the beam model.
    # Checking to see if the beam model is 1D or 2D
    if beam_model.ndim == 1:
        temp_sats = sats_model_tc[:, None] * beam_model[None, :]     
    
    elif beam_model.ndim == 2:
        temp_sats = beam_model * sats_model_tc[:, None]     

    # Satellite temperature brightness in units of Kelvin
    temp_sats = temp_sats
    
    # Returns 
    # Temperarture brightness of satellites;
    # The SED of the model multplied by a unit factor and conversion factors
    # The SED of the signal
    # Frequecny timestamps of the observation
    return temp_sats, sats_model_tc, sats_model_t, frequency_tod   