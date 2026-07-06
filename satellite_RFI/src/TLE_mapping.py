"""
Functions for TLE download and handling.

Functions
---------
- (...)
"""

# ----------------------------------------------- #
## ------------------- IMPORTS ----------------- ##
# ----------------------------------------------- #

from datetime import datetime
import glob
import requests
import os


# ----------------------------------------------- #
## ------------------ FUNCTIONS ---------------- ##
# ----------------------------------------------- #

def download_TLEs(path_folder=None):
    """ Downloads the TLE information for the current date into a folder (that it
    constructs) in the specific path.
    
    Parameters
    ----------
    path_folder : string
        Path in which to create the folder with TLEs.
    """

    # getting date
    day = datetime.now()
    path = path_folder + f"{day.year:02d}_{day.month:02d}_{day.day:02d}_tle/"
    check_path = os.path.isdir(path)

    # checking that it hasn't been already extracted
    if os.path.isdir(path):
        print(f"Error: Date is already in use!")
    # extracting 
    else:
        os.mkdir(path)
        constellations = ["gps-ops","glo-ops","galileo","beidou","sbas","geo"]  # <-- is geo necessary? 
        for cons in constellations:
            print(f"Downloading {cons}...")
            url = f"https://celestrak.org/NORAD/elements/gp.php?GROUP={cons}&FORMAT=tle"
            data = requests.get(url, allow_redirects=True)
            open(f"{path}{cons}.txt","wb").write(data.content)

    print(f"TLE folder: {path}")
    return


# ----------------------------------------------- #

def extract_QIs(path):
    """ Extracts IRNSS and QZS satellites from geo.txt and remove 
    from sbas.txt (some repeated QZS and BEIDOU satellites).

    Parameters
    ----------
    path : string
        Path to the folder.
    """

    # defining quantities
    search = [("QZS","qzs"), ("IRNSS","irnss")]
    with open(f"{path}geo.txt","r") as f:  lines = f.readlines()

    # creating files
    for sat,fname in search:
        print(f"Creating {fname} file...")

        # writ fi
        with open(f"{path}{fname}.txt","w") as file:
            for i,line in enumerate(lines):
                if sat in line:
                    print(" - " + line,end="")
                    file.write(lines[i])
                    file.write(lines[i+1])
                    file.write(lines[i+2])
                    
    # removing BEIDOU and QZS satellites from SBAS
    print("Removing QZS and BEIDOU satellites from SBAS...")
    with open(f"{path}sbas.txt","r") as f:  lines = f.readlines()
    with open(f"{path}sbas.txt","w") as file:
        i = 0
        while i < len(lines):
            if ("QZS" not in lines[i]) and ("BEIDOU" not in lines[i]):
                file.write(lines[i])
                i += 1
            else:
                print(" - " + lines[i],end="")
                i += 3
    return


# ----------------------------------------------- #

def remove_spaces(path):
    ''' Removes spaces from satellite names, replaces with "-".

    Parameters
    ----------
    path : string
        Path to the folder.
    '''

    # open each of the files
    fnames = glob.glob(path + "*.txt")
    for fname in fnames:
        print(f"Editing {fname}...")
        # alter lines with satellite names
        with open(fname,"r") as f:  lines = f.readlines()
        for i,line in enumerate(lines):
            if (i%3)==0:  lines[i] = line.replace(" ","-")

        # rewrite file
        with open(fname,"w") as f:  
            f.writelines(lines)
    return


# ----------------------------------------------- #

