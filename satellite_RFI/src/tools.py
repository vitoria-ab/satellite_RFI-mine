'''
Python file which holds definitions that can be useful.
'''

# Packages ---------------------------------------------------------------

import pickle
import sys
import time
from datetime import datetime
import pytz

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
        obs_time = datetime(date[0], date[1], date[2], date[3], date[4], date[5])
        time = int((obs_time - datetime(1970, 1, 1)).total_seconds())
        
    elif fname!=None and date==None:
        time = datetime.fromtimestamp(fname)
        
    return time