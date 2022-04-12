'''
A list of imports for the chi2 notebooks.
Note; should be used everywhere
'''


from satellite_RFI.src.satellite_sims import satellite_sim as ss
import satellite_RFI.src.tools as tools

import param as param

import time
import pickle
import astropy.units as u
from datetime import datetime
import tqdm
import os


import scipy as sp
import numpy as np
import pandas as pd
import scipy.optimize as opt
import matplotlib.pyplot as plt