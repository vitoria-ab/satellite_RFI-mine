'''
List of modules used by the simulations
'''
##---------------------------Python------------------------
import pickle
import sys
import time
from datetime import datetime, timedelta
import pytz
import os
import tqdm as tqdm
##---------------------------Numpy------------------------
import numpy as np

##---------------------------Scipy------------------------
import scipy as sp
import scipy.optimize as opt
from scipy.interpolate import Rbf as Rbf

##---------------------------Panda------------------------
import pandas as pd

##---------------------------Satellite Python Files------------------------
from satellite_RFI.src import check_satellite as cs        
from satellite_RFI.src import beam_model as bm
from satellite_RFI.src import rewrite_tle
from satellite_RFI.src import satellite_extract
from satellite_RFI.src.satellite_sims import satellite_sim as ss
# from satellite_RFI.src import tle_sat_download as tsd
from satellite_RFI.src import psd_models_v2 as psd
from satellite_RFI.src import tools
from satellite_RFI.src import attenuation_function as af

#---------------------------Astropy------------------------
from astropy.time import Time
import astropy.units as u
import astropy.constants as cc
from astropy.stats import SigmaClip
##---------------------------Matplotlib------------------------
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as md
## rc parameter files
small, medium, big = 15, 18, 25
plt.rc('font', size=small)          # controls default text sizes
plt.rc('axes', titlesize=big)     # fontsize of the axes title
plt.rc('axes', labelsize=medium)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=small)    # fontsize of the tick labels
plt.rc('ytick', labelsize=small)    # fontsize of the tick labels
plt.rc('legend', fontsize=medium)    # legend fontsize
plt.rc('figure', titlesize=big)  # fontsize of the figure title
plt.rc('legend', frameon=True) 
##---------------------------Mulitprocessing------------------------
import multiprocessing as mp
from threading import Thread

