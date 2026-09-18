
# online data retrieval
import os
import requests
from datetime import datetime, timedelta
import csv
import io
from spacetrack import SpaceTrackClient
import spacetrack.operators as op
# satellite handling
from skyfield.api import EarthSatellite,load,wgs84
# data handling
import csv
import pandas as pd
import pickle
# numerical+astrophysical handling
import numpy as np
from astropy import units as u
from astropy.time import Time
# plotting
import matplotlib.pyplot as plt


# -------------------------------------------------- #

def retrieve_sats(params, source=None, sat_names=None):
    '''Retrieves current or historical satellite GP data.'''

    # getting source date
    group = params["group"]
    if source is None:  source = datetime.utcfromtimestamp(params["block"])
    else:  source = datetime.utcfromtimestamp(source)
    days = 4  # <-- window to check for GPs
    
    # -----  CURRENT REQUEST ----- 
    if source.date() >= datetime.now().date():
        # retrieving data from the link
        print("Source is from the present/future, fetching today's GPs!")
        source = datetime.now()
        path = "{}_{:02d}_{:02d}_{:02d}.csv".format(group,source.year,source.month,source.day)
        if os.path.isfile(path):
            print("GPs for '{}' at {:02d}-{:02d}-{:02d} already exist!".format(
                group,source.year,source.month,source.day))
        else:
            print("Retrieving GPs for '{}' at {:02d}-{:02d}-{:02d}...".format(
                group,source.year,source.month,source.day))
            url = "https://celestrak.org/NORAD/elements/gp.php?GROUP={}&FORMAT=csv".format(group)
            data = requests.get(url)
            open(path, "wb").write(data.content)

        # organizing the satellite objects
        ts = load.timescale()
        satellites = {}
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["EPOCH"] = pd.to_datetime(row["EPOCH"]).strftime("%Y-%m-%dT%H:%M:%S.%f")
                sat = EarthSatellite.from_omm(ts,row)
                satellites[row["OBJECT_NAME"]] = sat

    # ----- HISTORICAL REQUEST -----
    else:
        # getting list of satellite NORAD IDs of the group
        path = "{}_SATCAT.csv".format(group)
        if os.path.isfile(path):
            print("SATCAT for '{}' already exist!".format(group))
            satcat = pd.read_csv(path)
        else:
            print("Retrieving SATCAT for group {}...".format(group))
            url = "https://celestrak.org/satcat/records.php?GROUP={}&FORMAT=CSV".format(group)
            data = requests.get(url)
            data.raise_for_status()
            open(path,"wb").write(data.content)
            satcat = pd.read_csv(io.StringIO(data.text))

        # selecting satellites active in the date we want
        satcat["LAUNCH_DATE"] = pd.to_datetime(satcat["LAUNCH_DATE"])
        satcat["DECAY_DATE"] = pd.to_datetime(satcat["DECAY_DATE"])
        active = satcat[(satcat["LAUNCH_DATE"]<=source) & 
            (satcat["DECAY_DATE"].isna()|(satcat["DECAY_DATE"]>=source))]
        if sat_names is not None:  active = active[(active["OBJECT_NAME"].isin(sat_names))]
        norad_ids = active["NORAD_CAT_ID"].astype(int).tolist()
        print("Number of '{}' satellites: {}.".format(group, len(norad_ids)))
        
        # retrieving historical data from space-track and selecting the latest GP in the window
        path = "{}_{:02d}_{:02d}_{:02d}.csv".format(group,source.year,source.month,source.day)
        if sat_names is not None:  path = path[:-4] + "_inc.csv"
        if os.path.isfile(path):
            print("GPs for '{}' at {:02d}-{:02d}-{:02d} already exist!".format(
                group,source.year,source.month,source.day))
            gp = pd.read_csv(path)
        else:
            print("Retrieving GPs for '{}' at {:02d}-{:02d}-{:02d}...".format(
                group,source.year,source.month,source.day))
            st = SpaceTrackClient(identity=params["ST_user"], password=params["ST_password"])
            start = source - timedelta(days=days)
            gp = st.gp_history(norad_cat_id=norad_ids, epoch=op.inclusive_range(start,source), orderby="epoch asc")
            gp = pd.DataFrame(gp)
            gp["EPOCH"] = pd.to_datetime(gp["EPOCH"])
            gp = gp.sort_values("EPOCH").groupby("NORAD_CAT_ID").tail(1)
            gp.to_csv(path, index=False)
        
        # creating Skyfield objects
        gp["EPOCH"] = pd.to_datetime(gp["EPOCH"]).dt.strftime("%Y-%m-%dT%H:%M:%S.%f")
        ts = load.timescale()
        satellites = {}
        for _, row in gp.iterrows():  
            satellites[row["OBJECT_NAME"]] = EarthSatellite.from_omm(ts,row.to_dict())
        
    print("Number of '{}' satellites: {}.".format(group, len(satellites)))
    return satellites


# -------------------------------------------------- #

def check_above_horizon(sats, MK_times, MK_location, params):
    ''' Filters out satellites that are always below the horizon. '''
    
    Nt_check = params["Nt_check"]
    if Nt_check is None:  Nt_check = len(MK_times)
    print("Checking satellites above the horizon...")
    sats2 = {}
    
    # some initial quantities
    time = Time(MK_times[:: len(MK_times) // Nt_check ].value, 
                format="unix", scale="utc")
    time = load.timescale(builtin=True).from_astropy(time)
    N_err = 0
    
    # iterating over the satellites
    for i,(ID,sat) in enumerate(sats.items()):
        topo = (sat - MK_location).at(time)
        alt,az,_ = topo.altaz()
        mask = alt.degrees < 0
        if np.all(mask):  continue
        if np.any(np.isnan(alt.degrees)):  N_err += 1;  continue
        sats2[ID] = sat
    
    print("\tNumber of satellites above horizon: {}".format(len(sats2)))
    print("\tNumber of satellites with obsolete TLEs: {}".format(N_err))
    print("\tNumber of satellites below horizon: {}".format(len(sats)-len(sats2)+N_err))
    return sats2


# -------------------------------------------------- #

def check_within_cutoff(sats, MK_times, MK_az, MK_alt, MK_location, params):
    ''' Filters out satellites that are always outside cutoff angle. '''

    angle_cutoff,Nt_check = params["angle_cutoff"],params["Nt_check"]
    if Nt_check is None:  Nt_check = len(MK_times)
    print("Checking satellites within {} deg of pointing...".format(angle_cutoff))
    sats2 = {}
    
    # initial quantities
    time = Time(MK_times[:: len(MK_times) // Nt_check ].value, 
                format="unix", scale="utc")
    time = load.timescale(builtin=True).from_astropy(time)
    paz = np.deg2rad(MK_az[::len(MK_times) // Nt_check])
    palt = np.deg2rad(MK_alt[::len(MK_times) // Nt_check])
    
    for i,(ID,sat) in enumerate(sats.items()):
        topo = (sat - MK_location).at(time)
        alt, az, _ = topo.altaz()
        cos_angles = np.sin(palt)*np.sin(alt.radians) + np.cos(palt)*np.cos(alt.radians)*np.cos(paz-az.radians)
        angles = np.degrees(np.arccos(np.clip(cos_angles, -1, 1)))
        if np.all(angles >= angle_cutoff):  continue
        sats2[ID] = sat
    
    print("\tNumber of satellites within {} deg: {}".format(angle_cutoff, len(sats2)))
    print("\tNumber of satellites removed: {}".format(len(sats) - len(sats2)))
    return sats2


# -------------------------------------------------- #

def plot_angular_separations(sats, MK_times, MK_az, MK_alt, MK_location, params):
    ''' Plots satellites that go within the cutoff. '''

    # creating figure
    Nt_plot,angle_cutoff,angle_labels = params["Nt_plot"],params["angle_cutoff"],params["angle_labels"]
    fig, ax = plt.subplots(figsize=(16, 8))
    linestyles = ["-", "--", "-.", ":"]

    # defining time and pointing
    if Nt_plot is None:  Nt_plot = len(MK_times)
    time_astropy = Time(MK_times[::len(MK_times)//Nt_plot].value, format="unix", scale="utc")
    time = load.timescale(builtin=True).from_astropy(time_astropy)
    dtime = time_astropy.datetime
    paz = np.deg2rad(MK_az[::len(MK_times)//Nt_plot])
    palt = np.deg2rad(MK_alt[::len(MK_times)//Nt_plot])

    # for each satellite, calculating the curve and plotting
    angles_total = {}
    for i,(ID,sat) in enumerate(sats.items()):
        topo = (sat - MK_location).at(time)
        alt, az, _ = topo.altaz()
        cos_angles = np.sin(palt)*np.sin(alt.radians) + np.cos(palt)*np.cos(alt.radians)*np.cos(paz-az.radians)
        angles = np.degrees(np.arccos(np.clip(cos_angles, -1, 1)))
        mask = (alt.degrees>0) & (angles<angle_cutoff)
        if np.any(angles < angle_labels):
            ax.plot(np.ma.masked_array(time_astropy.unix, mask=~mask), 
                np.ma.masked_array(angles, mask=~mask), 
                linestyle=linestyles[i%4], label=ID)
        else:  
            ax.plot(np.ma.masked_array(time_astropy.unix, mask=~mask), 
                np.ma.masked_array(angles, mask=~mask), 
                linestyle=linestyles[i%4])
        angles_total[ID] = np.ma.masked_array(angles, mask=~mask)

    # showing figure
    ax.axhline(angle_labels, color="black", ls="--")
    ax.axhline(0, color="black", ls="--")
    ax.set_ylabel("Angular separation [deg]")
    idx = np.linspace(0, len(dtime) - 1, 20, dtype=int)
    ax.set_xticks(time_astropy.unix[idx])
    ax.set_xticklabels([t.strftime("%H:%M:%S") for t in dtime[idx]], rotation=45)
    ax.set_xlabel("UTC")
    ax.legend()
    fig.tight_layout()
    plt.show()
    return angles_total


# -------------------------------------------------- #

def plot_different_sources(anglesA, anglesB, MK_times, params):
    ''' Plots the difference between the calculated angles of 2 different sources. '''

    # creating figure
    Nt_plot = params["Nt_plot"]
    fig, ax = plt.subplots(figsize=(16, 8))
    linestyles = ["-", "--", "-.", ":"]

    # making sure that they have the same keys
    anglesA, anglesB = anglesA.copy(), anglesB.copy()
    for sat in list(anglesA):
        if sat not in anglesB:  
            print("Only in angles:", sat)
            del anglesA[sat]
    for sat in list(anglesB):
        if sat not in anglesA:  
            print("Only in angles_older:",sat)
            del anglesB[sat]

    # defining time and pointing
    if Nt_plot is None:  Nt_plot = len(MK_times)
    time_astropy = Time(MK_times[::len(MK_times)//Nt_plot].value, format="unix", scale="utc")
    dtime = time_astropy.datetime

    # for each satellite, calculating the curve and plotting
    angles_diff = {}
    for i,(ID,sat) in enumerate(anglesA.items()):
        angles_diff[ID] = anglesB[ID] - anglesA[ID]
        ax.plot(time_astropy.unix, angles_diff[ID], linestyle=linestyles[i%4])

    # showing figure
    ax.set_ylabel("Difference in angular separation (B-A) [deg]")
    idx = np.linspace(0, len(dtime) - 1, 20, dtype=int)
    ax.set_xticks(time_astropy.unix[idx])
    ax.set_xticklabels([t.strftime("%H:%M:%S") for t in dtime[idx]], rotation=45)
    ax.set_xlabel("UTC")
    fig.tight_layout()
    plt.show()
    return angles_diff


# -------------------------------------------------- #

def plot_different_sources2(anglesA, anglesB, MK_times, params):
    ''' Plots the curves of 5 satellites in 2 different sources.'''

    # creating figure
    Nt_plot = params["Nt_plot"]
    fig, ax = plt.subplots(figsize=(16, 8))
    linestyles = ["-", "--"]
    colors = ["green","yellow","blue","red","black"]

    # making sure that they have the same keys
    anglesA, anglesB = anglesA.copy(), anglesB.copy()
    for sat in list(anglesA):
        if sat not in anglesB:  del anglesA[sat]
    for sat in list(anglesB):
        if sat not in anglesA:  del anglesB[sat]

    # defining time and pointing
    if Nt_plot is None:  Nt_plot = len(MK_times)
    time_astropy = Time(MK_times[::len(MK_times)//Nt_plot].value, format="unix", scale="utc")
    dtime = time_astropy.datetime

    # for each satellite, calculating the curve and plotting
    for i,(ID,sat) in enumerate(anglesA.items()):
        if i==20:  break
        ax.plot(time_astropy.unix, anglesA[ID], linestyle=linestyles[0], color=colors[i%5])
        ax.plot(time_astropy.unix, anglesB[ID], linestyle=linestyles[1], color=colors[i%5])

    # showing figure
    ax.set_title("Angular separations for A(-) and B(--) [deg]")
    ax.set_ylabel("Angular separations [deg]")
    idx = np.linspace(0, len(dtime) - 1, 20, dtype=int)
    ax.set_xticks(time_astropy.unix[idx])
    ax.set_xticklabels([t.strftime("%H:%M:%S") for t in dtime[idx]], rotation=45)
    ax.set_xlabel("UTC")
    fig.tight_layout()
    plt.show()
    return 
    

