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

##---------------------------Astropy------------------------
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

