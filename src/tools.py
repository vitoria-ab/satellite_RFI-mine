'''
Python file which holds definitions that can be useful.
'''

# Packages ---------------------------------------------------------------

import pickle
import sys
import time
from datetime import datetime
import pytz
import tempfile
import glob
import requests
import os
import numpy as np

# --------------------------------------------------------------------------

'''------------------FUNCTIONS IN SATELLITE POSTION AND BEAM MODEL-------------------------------------------------------'''

############################# Timepoint ###################################

# Function that allows the user to return the unix time or datetiime depending
# on which input was given.

def timepoint(fname=None, date=None):
    '''
    Enter the time of observation in unix time and get datetime returned and vice versa
    date - format: yyyy,mm,dd,HH,MM,SS
    fname - unix time
    '''
    if type(fname)==str:
        fname=int(fname)
        
    if fname==None and date!=None:
        time_date=[int(x) for x in date.split()]
        time_date = datetime(time_date[0], time_date[1], time_date[2], time_date[3], time_date[4], time_date[5])
        time_fname = int((time_date - datetime(1970, 1, 1)).total_seconds())
        time_date = time_date.strftime('%Y-%m-%d %H:%M:%S')
        print ('Date of observation: '+time_date+'\nFname: '+str(time_fname))

        
    elif fname!=None and date==None:
        time_fname=fname
        time_date = datetime.fromtimestamp(time_fname)
        time_date = time_date.strftime('%Y-%m-%d %H:%M:%S')
        print ('Date of observation: '+time_date+'\nFname: '+str(time_fname))
        
    elif fname==None and date==None:
        time_fname=fname
        time_date=date
        print ('Fname and Date have no entry')

    if type(fname)!=str:
        fname=str(fname)
    
    return time_fname, time_date

# --------------------------------------------------------------------------

############################# Rewrite TLE ###################################

# Functions that adjusts the TLE information packets and makes it readable for the code.

def tle_satellite_cat(filename):
    '''
    Removes the spaces from the names of the catalogues and 
    replaces with - dashes.
    '''
    #Create temporary file read/write
    temp = tempfile.NamedTemporaryFile(mode="r+")

    #Open input file read-only
    file = open(filename, 'r')

    # #Copy input file to temporary file, modifying as we go
    count = 0                 # Satellite file name is always on the 3rd option 0,4,
    for i in file:
        if count%3==0:
            temp.write(i.replace(" ", "-"))
        else:
            temp.write(i)

        count+=1

    file.close()
    temp.seek(0)
    file_n = open(filename, "w")    # Reopen input file writable
    for line in temp:
        file_n.write(line)

    temp.close()
    file_n.close()
    
def rewrite_sat_cat(file_path):
    '''
    Rewrites all txt files in the given path to not include spaces
    file_path - directory path
    '''
    files=glob.glob(file_path+'*.txt')
    for sat_cat in files:
        tle_satellite_cat(filename=sat_cat)
        
        
# --------------------------------------------------------------------------

############################# Satellite Extract ###################################

# Function that extracts the IRNSS and QZS constellations from the GEO file

def sat_extract(folder):
    """
    A function in order to extract the IRNSS and QZS satellites from the 
    geo.txt (Geo-Satellites) and create there own file for their TLE info
    
    Requirements:
        folder - path to where the geo.txt file exits
    """
    file = 'geo.txt'
    
    sat_name = [
        ('QZS', 'qzs'), ('IRNSS', 'irnss')
    ]
    
    with open(folder+file) as f:
        sat_file = f.readlines()
        
    for sat in sat_name:
        sat_write = open(folder+sat[1]+'.txt', 'w')
        
        
        for i, line in enumerate(sat_file):
            if sat[0] in line:
#                 print sat_file[i]
                sat_write.write(sat_file[i])
                sat_write.write(sat_file[i+1])
                sat_write.write(sat_file[i+2])

        sat_write.close()
        
# --------------------------------------------------------------------------

############################# TLE Satellite Download ###################################

# Function: Download the TLE satellite from the Celestak website for today and makes a folder.

def tle_download(tle_load=None, direc_path=None):
    ''''
    Downloads the TLE information for the current date (today).
    Constructs a folder for that information and places it in a specific path 
    
    *Parameters:
    tle_load: if 'None' will downlad else will return the path given
    direc_path: path of parent directory
    '''
    if tle_load==None:
        day = datetime.now()
        directory = "{0:02d}".format(day.year)+"_"+"{0:02d}".format(day.month)+"_"+"{0:02d}".format(day.day)+"_tle/"

        parent_path = direc_path
        path = os.path.join(parent_path, directory)
        check_path = os.path.isdir(path)
        try:

            if not check_path:

                os.mkdir(path)

                constellations = ['gps-ops', 'glo-ops', 'galileo', 'beidou', 'sbas', 'geo']

                for i in constellations:  
                    url = 'https://celestrak.com/NORAD/elements/'+i+'.txt'
                    r = requests.get(url, allow_redirects=True)

                    open(path+i+'.txt', 'wb').write(r.content)

            else:
                print ("Path alredy exists: "+path)

        except FileNotFoundError:
            print ("Parent directory does NOT exist: "+parent_path)
            
    else:
        path=tle_load
        
    print ("Two Line Element location: "+path) 
    
    return path


# --------------------------------------------------------------------------

############################# Path exsiting ###################################

# Function: Given a path, will check if it exists, if not, will create.

def path_exists(path):
    '''
    Function to check if the path exists
    '''
    if not os.path.exists(path):
        print ('Path does not exist, making....')
        os.makedirs(path)
    else:
        print ('Path exists :)')
    
    return 

# --------------------------------------------------------------------------

############################# Radiometer equation ###################################

# Function: Returns the radiometer solution for meerkat

def radiometer_eq(data):
    '''
    Radiometer euquation for determining the error on the data
    '''
    d_nu = 0.2 * 10**6 # Hz
    d_t = 2 # s
    n_pol = 2 
    n_dish = 58
    sig2 = data**2 / (n_pol*d_nu*d_t*n_dish)
    sig = np.ma.sqrt(sig2)
    
    return sig

# --------------------------------------------------------------------------

############################# Waterfall time average ###################################

def waterfall_avg_time(timer, size, waterfall):
    '''
    Function that can average waterfall plots in the time domain for some time period
    time - array of temporal points
    size - time box to average over
    waterfall - Can we 2d or 1d 
                waterfall data, must have the 0 axis size same as length of time
    
    
    If waterfall=None, then the averaged time will be returned instead
    '''
    a = timer[0]
    b = timer[-1]
    
    
    try:
        if waterfall.all()!=None:
            if waterfall.ndim==2:
                intervals = int(round((b-a)/size,0))
                new_waterfall = np.zeros((intervals, waterfall.shape[1]))
                for i in range(intervals):
                    a1 = timer[0] + i*size
                    a2 = timer[0] + i*size+size
                    idx_i = np.where((timer >= a1) & (timer < a2))[0]
                    new_waterfall[i, :] = np.ma.mean(waterfall[idx_i, :], axis=0)  
                    new_waterfall = np.ma.array(data=new_waterfall, mask=new_waterfall==0)
            elif waterfall.ndim==1:
                intervals = int(round((b-a)/size,0))
                new_waterfall = np.zeros(intervals)
                for i in range(intervals):
                    a1 = timer[0] + i*size
                    a2 = timer[0] + i*size+size
                    idx_i = np.where((timer >= a1) & (timer < a2))[0]
                    new_waterfall[i] = np.ma.mean(waterfall[idx_i], axis=0)  
                

    except AttributeError:
        # Catching the error so that we can time be averaged
        new_waterfall = np.arange(a,b, size)
    
    return new_waterfall


# --------------------------------------------------------------------------

############################# Waterfall time average ###################################

def timeline(f_choice, f_list, waterfall):
    '''
    Function that given a frequency value will select and plot the timeline of that value
    f_choice - frequency value of choice
    f_list - list of frequency values corresponding with the waterfall image
    waterfall - 2d image of the data [time x frequency]
    '''
    
    fidx = np.where(f_list>=f_choice)[0][0]
    t_wfall = waterfall[:, fidx]
    
    return t_wfall

# --------------------------------------------------------------------------

############################# Index finder ###################################

def find_idx(data_array, data_variable):
    """
    Function to obtain the index position in the array of given points
    data_array - array of data points
    data_variable - the element within the array that indices we wish to obtain
    Returns:
        The idx -1 to get the previous data point
    """
    
    idx = np.where(data_array > data_variable)[0][0] - 1
    
    return idx


############################# Converting RA/DEC ----> Az/Alt ###################################

# import numpy as np
# from astropy.time import Time
# import astropy as ap

# def gmst(date, verbose=False):
#     '''
#     Calculating the Greenwhich Meridian Sidereal Time at time of observer
#     Format: date = YYYY-MM-DD hh:mm:sec as a str
#     Link: https://lweb.cfa.harvard.edu/~jzhao/times.html#:~:text=Local%20Mean%20Sidereal%20time%20is,on%20an%20observatory's%20sidereal%20clock.
#     Link: https://squarewidget.com/astronomical-calculations-sidereal-time/
    
#     Returns Greenwhich Mean 
#     '''
#     t = Time(date, format=None, scale='utc')
#     # Date in Julian time subtracted by the Julian time in seconds of 1 January 2000 or J2000
#     d = t.jd - 2451545.0
#     # Getting the value in centuries
#     tc = d / 36525.
#     # Greenwich Mean Sidereal Time
#     # GMST = lambda T: 24110.54841 + 8640184.812866 * T + 0.093104 * T**2 - 0.0000062 * T**3
#     GMST = 18.697374558 + 24.06570982441908*(d)

#     # GMST = lambda T: 280.46061837 + 360.98564736629 * (d) + (0.000387933 * T * T) - (T * T * T / 38710000.0)
    
#     'Link: https://github.com/jhaupt/Sidereal-Time-Calculator/blob/master/SiderealTimeCalculator.py    [Making use of this]'
#     gmst_ = GMST % 24                        # use modulo operator to convert to 24 hours
#     gmst_mm = (gmst_ - int(gmst_))*60          #convert fraction hours to minutes
#     gmst_ss = (gmst_mm - int(gmst_mm))*60      #convert fractional minutes to seconds
#     gmst_hh = int(gmst_)
#     gmst_mm = int(gmst_mm)
#     gmst_ss = int(gmst_ss)
    
#     if verbose==True:
#         print ('\nGreenwhich Mean Sidereal Time: %s:%s:%s' %(gmst_hh, gmst_mm, gmst_ss))
    
#     return gmst_

# ###########################################################################################

# def lst(date, longitude, direction, verbose=False):
#     '''
#     Calculating Local Sideral Time at time of observer
#     Format: date = YYYY-MM-DD hh:mm:sec as a str
#     Longitude = degrees
#     Direction = E or W 
#     Link: https://github.com/jhaupt/Sidereal-Time-Calculator/blob/master/SiderealTimeCalculator.py    [Making use of this]
#     Link: https://squarewidget.com/astronomical-calculations-sidereal-time/
#     Link: https://sceweb.sce.uhcl.edu/helm/WEB-Positional%20Astronomy/Tutorial/Sidereal%20Time/Sidereal%20Time.html#:~:text=LST%20%3D%20GST%20%2D%20longitude%20west.,Time%20%2D%20RA%20of%20the%20star.
    
#     returns Local sideral time in hour time
#     '''
    
#     if direction=='W':
#         longitude=longitude*-1
        
#     # Converting degrees to hours
#     longitude = longitude/15.
#     # Local sidereal time
#     lst_ = gmst(date=date2) + Long
#     if lst_<0:
#         lst_+=24
        
#     lst_mm = (lst_ - int(lst_))*60          #convert fraction hours to minutes
#     lst_ss = (lst_mm - int(lst_mm))*60      #convert fractional minutes to seconds
#     lst_hh = int(lst_)
#     lst_mm = int(lst_mm)
#     lst_ss = int(lst_ss)
    
#     if verbose==True:
#         print ('\nLocal Sidereal Time: %s:%s:%s' %(lst_hh, lst_mm, lst_ss))

#     return lst_

# ###########################################################################################

# def convert_RA_deg_time(degree=None, time=None, verbose=False):
#     '''
#     Converts the RA from Degree to Time
#     Converts the RA from Time to Degree [Still in process]
    
#     Format: degree = degrees
#             time = HH:MM:SS
#     '''
#     if degree!=None:
#         hour_time = degree/15.
#         time_m = (hour_time-int(hour_time))*60
#         time_s = (time_m - int(time_m))*60
        
#         time_h = int(hour_time)
#         time_m = int(time_m)
#         time_s = int(time_s)
        
#         if verbose==True:
#             print ('\nConverted RA from degrees to hours: %s:%s:%s' %(time_h, time_m, time_s))
        
#     if time!=None:
#         time_obj = datetime.strptime(times, '%H:%M:%S').time()
#         time_hour = time_obj.hour
#         time_min = time_obj.minute/60.
#         time_sec = time_obj.second/60./60.
        
#         hour_time = time_hour+time_min+time_sec
        
        
#     return hour_time
 
# ###########################################################################################
     
# def lha(date, longitude, direction, RA, verbose=False):
#     '''
#     Local Hour Angle at observer
#     Format: date = YYYY-MM-DD hh:mm:sec as a str
#     Longitude = degrees
#     Direction = E or W 
#     RA = degrees
#     '''
#     lst_ = lst(date=date, longitude=longitude, direction=direction)   # returns hour time
#     ra_deg_ = convert_RA_deg_time(degree=RA)                         # returns hour time
    
#     lha_ = lst_ - ra_deg_
#     if lha_<0:
#         lha_+=24
#     if verbose==True:
#         print ('Hour angle is '+str(lha_))
        
#     return lha_


# def atan2_conversion(ha, latitude, decliation):
#     '''
#     Convert the RA and Declination to Azimuth and Elevation
#     format: ha [hour angle] in degrees
#             laitude - in degrees
#             declination - degrees
#     Link: https://astrogreg.com/convert_ra_dec_to_alt_az.html
#     '''
#     # ha, latitude, decliation = ha*np.pi/180, latitude*np.pi/180, decliation*np.pi/180
    
#     az_tan = np.sin(ha) / ((np.cos(ha)*np.sin(latitude)) - np.tan(decliation)*np.cos(latitude))
#     az = np.arctan(az_tan)
    
#     al_sin = np.sin(latitude)*np.sin(decliation) + np.cos(latitude)*np.cos(decliation)*np.cos(ha)
#     al = np.arcsin(al_sin)
    
#     return az, al