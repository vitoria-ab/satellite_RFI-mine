"""
Author: Brandon Engelbrecht
Date: 30/09/2021
Function: Download the TLE satellite from the Celestak website for today and makes a folder.
"""

import requests
import datetime
import os


def tle_download(direc_path):
    """'
    Downloads the TLE information for the current date (today).
    Constructs a folder for that information and places it in a specific path 
    direc_path: path of parent directory
    """
    day = datetime.datetime.now()
    directory = (
        "{0:02d}".format(day.year)
        + "_"
        + "{0:02d}".format(day.month)
        + "_"
        + "{0:02d}".format(day.day)
        + "_tle/"
    )

    parent_path = direc_path
    path = os.path.join(parent_path, directory)
    check_path = os.path.isdir(path)
    try:

        if not check_path:

            os.mkdir(path)

            constellations = ["gps-ops", "glo-ops", "galileo", "beidou", "sbas", "geo"]

            for i in constellations:
                url = "https://celestrak.com/NORAD/elements/" + i + ".txt"
                r = requests.get(url, allow_redirects=True)

                open(path + i + ".txt", "wb").write(r.content)

        else:
            print("Path alredy exists: " + path)

    except FileNotFoundError:
        print("Parent directory does NOT exist: " + parent_path)

    return path
