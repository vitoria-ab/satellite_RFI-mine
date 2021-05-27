import pandas as pd
import numpy as np
import scipy as sp
import astropy.constants as cc
import psd_models_v2 as psd
from fractions import Fraction
#-------------------------------------------------------------_#

def floaty(x):
    '''
    In case the ratio becomes a pickle to deal with
    '''
    try:
        a = float(x)
    except ValueError:
        a = float(Fraction(x))

    return a

#-------------------------------------------------------------_#

def gnss_satellites(name_gnss, frequency_gnss):
    '''Returns the Spectral Energy Density of the GNSS and the Data file that we used as an input'''
    # Distances to the satellite constellations, taken from Springer Handbook pg 1234 

    if name_gnss=='gps-ops':
        name = 'GPS'
        r = 20180 * 1000 # Distance in metres

    elif name_gnss=='glo-ops':
        name = 'GLO'
        r = 19130 * 1000 # Distance in meters

    elif name_gnss=='galileo':
        name = 'GAL'
        r = 23220 * 1000 # Distance in metres

    elif name_gnss=='beidou':
        name = 'BDS'
        r = 21530 * 1000 # Distance in meters

    elif name_gnss=='irnss':
        name = 'IRNSS'
        r = 35790 * 1000  # Distance in meters

    elif name_gnss=='qzs':
        name = 'QZS'
        r = 35790 * 1000  # Distance in meters

    elif name_gnss=='sbas':
        name = 'SBAS'
        r = 35790 * 1000  # Distance in meters

    else:
        print ('Oops, make the sure name is written as GPS or Galileo or GLONASS')
        return -1

    
    data = pd.read_csv('../../Notebooks/Satellite_simulations/Satellite_Catalogue/table3B_satellite_v3.csv', header=0, engine='python')   # Excel data file with all the GNSS and models Table 2

    # Re-ordering by frequency
#         data = data.sort_values(by = 'Frequency[MHz]')
#-----# Looking at all frequency below 1500 MHz
    data = data[data['Frequency[MHz]']< 1500]
#------# Changing the rate values
#         data.loc[data['Rate(MHz)'] != 1.023, 'Rate(MHz)'] = 1.023



    # Extracting smaller data table
    data_sub = data[data[data.columns[0]].str.contains(name)]

    # Making the Spectral Energy density list
    sed = []

    # Looping through all the sub-data index
    for i in data_sub.index:
        power = 10**(data_sub['P_t (dBW)'][i]/10) * 10**(data_sub['G_t (dBi)'][i]/10) / (4*np.pi*r**2) 

        if 'BPSK(' in data_sub['Modulation'][i]:
            s = data_sub['Modulation'][i]
            T_c = float(s[s.find("(")+1:s.find(")")])   # Getting the chip interval value
            model = psd.BPSK(f=frequency_gnss - data_sub['Frequency[MHz]'][i], n_c=T_c,
                             f0=data_sub['Rate(MHz)'][i] / T_c)

#                 print T_c, data_sub['Rate(MHz)'][i] / T_c

        elif 'BOC(' in data_sub['Modulation'][i]:
            try:
                s = data_sub['Modulation'][i]
                # Getting the values between parenthesis and converting to float
                T_s, T_c = [float(x) for x in s[s.find("(")+1:s.find(")")].split(',')]
                model = psd.BOC(f=frequency_gnss - data_sub['Frequency[MHz]'][i], n_c=T_c,
                                 n_s=T_s, f0=data_sub['Rate(MHz)'][i] / T_c)
            # Bad method of by-passing TMBOC values

#                     print T_s, T_c, data_sub['Rate(MHz)'][i] / T_c

            except ValueError, UnboundLocalError:
                pass


        elif 'BOCcos(' in data_sub['Modulation'][i]:
            s = data_sub['Modulation'][i]
            # Getting the values between parenthesis and converting tp float
            T_s, T_c = [float(x) for x in s[s.find("(")+1:s.find(")")].split(',')]
            model = psd.BOCc(f=frequency_gnss - data_sub['Frequency[MHz]'][i], n_c=T_c,
                             n_s=T_s, f0=data_sub['Rate(MHz)'][i] / T_c)

#                 print T_s, T_c, data_sub['Rate(MHz)'][i] / T_c

        elif 'AltBOC(' in data_sub['Modulation'][i]:
            # Going to also catch TD-AltBOC
            s = data_sub['Modulation'][i]
            # Getting the values between parenthesis and converting to float
            T_s, T_c = [float(x) for x in s[s.find("(")+1:s.find(")")].split(',')]
            model = psd.altBOC(f=frequency_gnss - data_sub['Frequency[MHz]'][i], m=T_s,
                               n=T_c, f0=data_sub['Rate(MHz)'][i] / T_c)

#                 print T_s, T_c, data_sub['Rate(MHz)'][i] / T_c

        elif 'TMBOC(' in data_sub['Modulation'][i]:
            s = data_sub['Modulation'][i]
            # Getting the values between parenthesis and converting to float
            T_s, T_c, rt = [floaty(x) for x in s[s.find("(")+1:s.find(")")].split(',')]
            model = psd.TMBOC(f=frequency_gnss - data_sub['Frequency[MHz]'][i], n_c=T_c,
                             n_s=T_s, f0=data_sub['Rate(MHz)'][i] / T_c, ratio=rt)

#                 print T_s, T_c, data_sub['Rate(MHz)'][i] / T_c

        elif 'CBOC(' in data_sub['Modulation'][i]:
            s = data_sub['Modulation'][i]
            # Getting the values between parenthesis and converting to float
            T_s, T_c, rt = [floaty(x) for x in s[s.find("(")+1:s.find(")")].split(',')]
            model = psd.CBOC(f=frequency_gnss - data_sub['Frequency[MHz]'][i], n_c=T_c,
                             n_s=T_s, f0=data_sub['Rate(MHz)'][i] / T_c, ratio=rt)

#                 print T_s, T_c, data_sub['Rate(MHz)'][i] / T_c

        # Checking for NaN values in model and swapping with zeros.
        model = np.array([0 if np.isnan(x) else x for x in model])

        sed.append(power * model * 1e26 / 1e6)  # In Jansky

    sed = np.array(sed)


    # Returning the SED values and the data of the input for the user
    return sed

 
    
    
    
## Function that returns the TOD values

def TOD_sats(name_tod, fname, frequency_tod, beam_model):
    '''
    Returns the sat_temp in units of mK
    name - a str;
    frequency - range of frequencies in MHz;
    beam_model - coming from Yi-Chaos angular seperation code, if 2d then should be transposed
    plot - option to plot 'yes', 'y', '1' then plot
    '''
    
    sats_model = gnss_satellites(name_gnss=name_tod, frequency_gnss=frequency_tod)   # Calling another fucntion
    sats_model_t = np.sum(sats_model, axis=0)       # Adding all the satellites togther
    
    # Multiplied with the gains
    sats_model_tc = sats_model_t * cc.c.value**2 / cc.k_B.value / 4 / np.pi / (frequency_tod*1e6)**2 / 1e26  # Multiplying the constants, look at the page to see the units
    
    sats_model_tc = sats_model_tc * 1e4  # The gain being multiplied as well, see Harper
    
    # Cheking if the beam model is 1d or 2d
    if beam_model.ndim == 1:
        temp_sats = sats_model_tc[:, None] * beam_model[None, :]     # Multiplying the beam and the satellite data
    
    elif beam_model.ndim == 2:
        temp_sats = beam_model * sats_model_tc[:, None]     # Multiplying the beam and the satellite data

    temp_sats = temp_sats  ## Units in Kelvin                
                              
    return temp_sats, sats_model_tc, sats_model_t, frequency_tod    # Kelvin