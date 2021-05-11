import numpy as np
import os as os
import sys as sys
##

name = [str(sys.argv[0])]

##

def satellite_tle_extraction(key):
    '''
    Extracts the TLE information from the geo.txt file in the current directory and 
    looks for the TLE information and writes that to file named after the key
    '''
    if os.path.exists(key[0].lower()+'.txt'):
        os.remove(key[0].lower()+'.txt')


    new_f = open(key[0].lower()+'.txt', 'a')

    with open('geo.txt', 'r') as file:
        for i, line in enumerate(file):
            for k in key:
                if k in line:
                    txt = line, file.next(), file.next()
                    for t in txt:
                        new_f.write(' '.join(str(s) for s in t))


    new_f.close()
    
##
#DONE
##