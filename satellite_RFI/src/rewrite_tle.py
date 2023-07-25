"""
August 9 2021 

Used to change the naming of satellites in the TLE files

"""

import tempfile
import sys
import glob

##


def tle_satellite_cat(filename):
    """
    Removes the spaces from the names of the catalogues and 
    replaces with - dashes.
    """
    # Create temporary file read/write
    temp = tempfile.NamedTemporaryFile(mode="r+")

    # Open input file read-only
    file = open(filename, "r")

    # #Copy input file to temporary file, modifying as we go
    count = 0  # Satellite file name is always on the 3rd option 0,4,
    for i in file:
        if count % 3 == 0:
            temp.write(i.replace(" ", "-"))
        else:
            temp.write(i)

        count += 1

    file.close()
    temp.seek(0)
    file_n = open(filename, "w")  # Reopen input file writable
    for line in temp:
        file_n.write(line)

    temp.close()
    file_n.close()


###


def rewrite_sat_cat(file_path):
    """
    Rewrites all txt files in the given path to not include spaces
    file_path - directory path
    """
    files = glob.glob(file_path + "*.txt")
    for sat_cat in files:
        tle_satellite_cat(filename=sat_cat)
