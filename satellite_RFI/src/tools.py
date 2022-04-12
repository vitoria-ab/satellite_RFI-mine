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

# --------------------------------------------------------------------------

############################# Timepoint ###################################

# Function that allows the user to return the unix time or datetiime depending
# on which input was given.

def timepoint(fname=None, date=None):
    '''
    Enter the time of observation in unix time and get datetime returned and vice versa
    date - format: yyyy,mm,dd,HH,MM,SS
    fname - unix time
    '''
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

        
    return time_fname

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

def tle_download(tle_load=None, direc_path='TLE/'):
    ''''
    Downloads the TLE information for the current date (today).
    Constructs a folder for that information and places it in a specific path 
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
    
    return path