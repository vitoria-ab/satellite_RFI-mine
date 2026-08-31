"""
Functions for TLE download and handling, as well as angular position calculations.

Functions
---------
download_TLEs(path_folder=None, verbose=True)
extract_QIs(path, verbose=True)
remove_spaces(path, verbose=True)
get_date(unix=None, date=None, verbose=True)

Classes
-------
SatelliteMap
    __init__(self, path_TLEs, t_start, times, location, pointings, max_angle=None, verbose=True)
    get_nearby_sats(self,angles,verbose=False)
    get_satbeam(self,frequency,beam_model,verbose=False)
    _get_coordinates(self)
    _get_angular_separations(self, max_angle=None)
"""

# -------------------------------------------------- #
## -------------------- IMPORTS ------------------- ##
# -------------------------------------------------- #

# system packages
import glob
import requests
import os
import shutil
# astrophysical packages
from datetime import datetime
from skyfield.api import load, wgs84
from astropy import units as u
from astropy.time import Time
# numerical packages
import numpy as np
import matplotlib.pyplot as plt


# -------------------------------------------------- #
## ------------------- FUNCTIONS ------------------ ##
# -------------------------------------------------- #

class SatelliteMap(object):
    """ (DESCRIPTION)
    
    Attributes (external)
    ----------
    ? : ?
        
    Functions (external)
    ---------
    ? : ?
    """
    
    def __init__(self, path_TLEs, t_start, times, location, pointings, max_angle=100, verbose=False):
        ''' Initializes the calculator with the satellite TLEs and observation time+location. '''

        # getting satellite TLEs
        if verbose:  print("Extracting TLEs...")
        self.cons = ["gps-ops","glo-ops","galileo","beidou","irnss","qzs","sbas"]
        self.sats = []
        for con in self.cons:
            sats_c = {}
            data = load.tle_file(path_TLEs + con + ".txt")
            for sat in data:  sats_c[sat.model.satnum] = sat
            self.sats.append(sats_c)

        # getting time and location
        if verbose:  print("Setting time and location...")
        self.t_start = Time(t_start, format="unix", scale="utc")
        self.times = (times - times[0]) * u.second
        self.location = wgs84.latlon(*location)

        if verbose:  print("Getting coordinates and angular separations...")
        self.pointings = pointings
        self._get_coordinates(verbose)
        self._get_angular_separations(max_angle,verbose)
        if verbose:  
            print("Number of satellites: ",end="")
            for i,con in enumerate(self.cons):  print(f"{len(self.sats[i])} ({con}), ",end="")


    # -------------------------------------------------- #

    def get_nearby_sats(self,angles,verbose=False):
        ''' Determines the time indexes in which any satellite
        crosses below the specified angles and saves the information 
        in the path described (for each angle given).
        
        Parameters
        ----------
        angles : ndarray
            List of angles to consider.
        verbose : bool (default False)
            If True, prints progress.
        '''

        inds_below = {}
        for a in angles:      
            if verbose: print(f"Checking angle {a}...")
            
            # selecting satellites under limit
            inds_a = []
            for i,con in enumerate(self.cons):
                is_under = np.any(self.angseps[i] < a, axis=1)
                for j,ID in enumerate(self.sats[i].keys()):
                    if is_under[j]:  
                        inds_a.append(np.where(self.angseps[i][j] < a)[0])
                        if verbose: 
                            name = self.sats[i][ID].name
                            print(f"\tFound satellite {name} ({ID}) from {con}!")

            # saving index values
            if inds_a:  inds_below[a] = np.unique(np.concatenate(inds_a))
            else:  inds_below[a] = np.array([], dtype=int)
            
        return inds_below

    
    # -------------------------------------------------- #
    
    def get_satbeam(self,frequency,beam_model,verbose=False):
        ''' Calculates satbeam maps (B/r^2) for every satellite.
        
        Parameters
        ----------
        frequency : ndarray
            List of frequencies on which to evaluate.
        beam_model : func
            Beam model function which takes theta and returns
            the beam response of the telescope. 
        verbose : bool (default False)
            If True, prints progress.
        '''

        # looping over each satellite
        self.satbeam = {}
        for i,con in enumerate(self.cons):
            if verbose:  print(f"\tGetting {con}...")
            for j,ID in enumerate(self.sats[i].keys()):
                # calculating
                beam = beam_model(frequency,self.angseps[i][j])
                self.satbeam[ID] = beam / self.dists[i][j]**2

    
    # -------------------------------------------------- #

    def _get_coordinates(self,verbose=False):
        ''' Calculates satellite coordinates from the TLEs, and removes
        those satellites that never cross the horizon. '''
        
        # defining quantities
        new_sats = [];  new_cons = []
        self.coords = []
        self.dists = []
        
        # defining a suitable time array
        t = (self.t_start + self.times).unix
        time_ast = Time(t, format="unix", scale="utc")
        time = load.timescale(builtin=True).from_astropy(time_ast)

        for i,con in enumerate(self.cons):
            # some quantities
            sats_visible = {}
            coords = []
            dists = []

            for ID,sat in self.sats[i].items():
                # get coordinates and mask
                topo = (sat-self.location).at(time)
                alt,az,dist = topo.altaz()
                mask = alt.degrees < 0
                coord = np.stack((az.degrees,alt.degrees), axis=-1)
    
                # save quantities
                if np.all(mask):  
                    continue
                sats_visible[ID] = sat
                coords.append(np.ma.masked_array(coord, mask=np.column_stack((mask, mask))))
                dists.append(dist.m)
    
            # convert and return
            if len(coords)==0:  continue  # <-- if totally masked, skip
            new_sats.append(sats_visible);  new_cons.append(con)
            self.coords.append(np.ma.stack(coords))
            self.dists.append(np.asarray(dists))
        
        self.sats = new_sats
        self.cons = new_cons
        return   

    
    # -------------------------------------------------- #

    def _get_angular_separations(self, max_angle, verbose=False):
        ''' Calculates the angular separations of each satellite, 
        given the satellite pointing throughout the observation. '''

        # getting pointing coordinates
        point_az = np.deg2rad(self.pointings[:, 0])[None, :]
        point_alt = np.deg2rad(self.pointings[:, 1])[None, :]
        self.angseps = []
        new_sats = [];  new_cons = [];  new_dists = []

        for i,con in enumerate(self.cons):
            # getting coordinates
            angseps = []
            dists_visible = []
            sats_visible = {}
            az = np.deg2rad(self.coords[i][:, :, 0])
            alt = np.deg2rad(self.coords[i][:, :, 1])

            # calculating angle
            cos_angles = np.sin(point_alt)*np.sin(alt) + np.cos(point_alt)*np.cos(alt)*np.cos(point_az-az)
            cos_angles = np.clip(cos_angles, -1.0, 1.0)  # <-- to guarantee [-1,1]
            angles = np.rad2deg(np.arccos(cos_angles))
            angles = np.ma.masked_greater_equal(angles,max_angle)

            for j,ID in enumerate(self.sats[i].keys()):
                if np.all(angles[j].mask):  
                    continue  # <-- if totally masked, skip
                sats_visible[ID] = self.sats[i][ID]
                angseps.append(angles[j])
                dists_visible.append(self.dists[i][j])

            # convert and return
            if len(angseps)==0:  continue  # <-- if totally masked, skip
            new_sats.append(sats_visible);  new_cons.append(con)
            self.angseps.append(np.ma.stack(angseps))
            new_dists.append(np.asarray(dists_visible))
            
        self.sats = new_sats
        self.cons = new_cons
        self.dists = new_dists
        return


# -------------------------------------------------- #
## ------------------- FUNCTIONS ------------------ ##
# -------------------------------------------------- #

def download_TLEs(path_folder=None, verbose=False):
    """ Downloads the TLE information for the current date into a folder 
    (that it constructs) in the specific path.
    
    Parameters
    ----------
    path_folder : string
        Path in which to create the folder with TLEs.

    Returns
    -------
    path : string
        Folder path with the new TLEs.
    """

    # getting date
    day = datetime.now()
    path = path_folder + f"{day.year:02d}_{day.month:02d}_{day.day:02d}_tle/"
    check_path = os.path.isdir(path)

    # checking that it hasn't been already extracted
    if os.path.isdir(path):
        print(f"Writing over existing folder")
        shutil.rmtree(path)
        
    os.mkdir(path)
    constellations = ["gps-ops","glo-ops","galileo","beidou","sbas","geo"]  # <-- is geo necessary? 
    if verbose:  print(f"Downloading to {path}: ",end="")
    for cons in constellations:
        if verbose:  print(f"{cons}, ",end="")
        url = f"https://celestrak.org/NORAD/elements/gp.php?GROUP={cons}&FORMAT=tle"
        data = requests.get(url, allow_redirects=True)
        open(f"{path}{cons}.txt","wb").write(data.content)

    return path


# -------------------------------------------------- #

def extract_QIs(path, verbose=False):
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
        if verbose:  print(f"Found {fname} satellites: ",end="")

        # writ fi
        with open(f"{path}{fname}.txt","w") as file:
            for i,line in enumerate(lines):
                if sat in line:
                    if verbose:  print(f"{line[:-1]},",end="")
                    file.write(lines[i])
                    file.write(lines[i+1])
                    file.write(lines[i+2])
        if verbose:  print()
                    
    # removing BEIDOU and QZS satellites from SBAS
    if verbose:  print("Removing QZS and BEIDOU satellites from SBAS...")
    with open(f"{path}sbas.txt","r") as f:  lines = f.readlines()
    with open(f"{path}sbas.txt","w") as file:
        i = 0
        while i < len(lines):
            if ("QZS" not in lines[i]) and ("BEIDOU" not in lines[i]):
                file.write(lines[i])
                i += 1
            else:  i += 3
    return


# -------------------------------------------------- #

def clean_satnames(path, verbose=False):
    ''' Cleans satellite names from the TLEs; removes 
    trailing "-" substitutes spaces by "-".

    Parameters
    ----------
    path : string
        Path to the folder.
    '''

    # open each of the files
    fnames = glob.glob(path + "*.txt")
    for fname in fnames:
        
        # alter lines with satellite names
        with open(fname,"r") as f:  lines = f.readlines()
        for i,line in enumerate(lines):
            if (i%3)==0:  
                name = line.rstrip("\n").replace(" ", "-").rstrip(" -") + "\n"
                name = name.replace("--(", "(").replace("-(","(").replace("(","-(")
                lines[i] = name
                
        # rewrite file
        with open(fname,"w") as f:  
            f.writelines(lines)
    return


# -------------------------------------------------- #

def clean(name):
    ''' Writes the satellite name compatible to the
    way that it is written in the satellites.csv file.
    
    Parameters
    ----------
    name : string
        Satellite name.
        
    Returns
    -------
    name : string
        New satellite name.
    '''

    name = name.rstrip("-")  # <-- hyphens at the end
    name = name.replace("--(", "(").replace("-(","(")  # <-- turns --( or -( into (
    name = name.replace("(","-(")  # <-- turns all ( into -(

    return name
    

# -------------------------------------------------- #

def get_date(unix=None, date=None, verbose=False):
    """ Enter the time of observation in unix time and 
    get date (and vice versa).

    Parameters
    ----------
    unix : int or None
        Date in UNIX time
    date : string or None
        Date in format "YYYY,MM,DD,hh,mm,ss"

    Returns
    -------
    """

    if unix != None:
        date = datetime.fromtimestamp(int(unix))
        
    elif date != None:
        date = [int(x) for x in date.split()]
        date = datetime(*date)
        unix = int((date - datetime(1970,1,1)).total_seconds())

    # converting
    date = date.strftime("%Y-%m-%d %H:%M:%S")
    unix = str(unix)
    if verbose:  print(f"Date of observation: {date}\nFile name: {unix}")
    return unix, date

