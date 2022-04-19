'''
A list of imports for the chi2 notebooks.
Note; should be used everywhere
'''

# From satellite_rfi modules
from satellite_RFI.src.satellite_sims import satellite_sim as ss
import satellite_RFI.src.tools as tools

# Parameter list
import param as param

import time
import pickle
import tqdm
import os
from datetime import datetime

import scipy as sp
import numpy as np
import pandas as pd
import astropy.units as u
import scipy.optimize as opt
import matplotlib.pyplot as plt

# Parellization
import multiprocessing as mp
from threading import Thread