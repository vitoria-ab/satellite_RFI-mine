# satellite_RFI
Updated: 2023/07/01 - Satellite Simulation RFI code for MeerKLASS - Pre-Survey Experiments

- Memo: https://www.overleaf.com/read/myyvyyvdjrkg   (Under construction)

The code setup is divided into three stages found in Notebooks:

Stage 1:
Calibration of the MeerKLASS data [Notebooks/MKAT_recalibration].
[Section dependant on work done by Dr Jingying Wang, unique to MeerKAT HI IM observations].

Stage 2:
Calculating the positioning of the satellites with respect to the satellite pointing [Notebooks/Satellite_position].

Stage 3:
We are simulating satellite signals and fitting them to observational data [Notebbooks/Satellite_simulations].

### Note
Currently, the code runs a Py2 [Stage 1&2] / Py3 [Stage 3] hybrid. 
Work on making it Py3 is still under construction for now.

## Requirements to run:
In order to run all 3 stages you need access to the ILIFU cluster.

### setup.py file
Note: If you are using a terminal, do step 1. If you are running via the JupyterLab terminal you can skip the step
```
1. srun --pty bash
```
Next, activate a singularity shell. These steps must be for both Py2.7 and Py3
```
2.1 singularity shell /idia/software/containers/hi_im-python2.7.simg
2.2 singularity shell /idia/software/containers/hi_im-py3.simg
```
If already no within the git repo folder change directory to there
```
3. cd satellite_RFI
```
```
4.1 pip2 install skyfield --user
4.2 pip3 install skyfield --user
```
Note: There may be a permission issue with PY2, this can be seen on loading the package in the notebooks
Solution 1 (Calm): ```pip2 install --no-deps skyfield```
Solution 2 (Crazy): ```pip2 install --force skyfield```
If this problem arises in PY3 redo it appropriately.
```
5.1 python2 setup.py install --user
5.2 python3 setup.py install --user
```
Repeat the process for Python 3 version as well

###  Set the container:
If the container is not already in place on your home screen
```
cp -r hi_sats_container ~/.local/share/jupyter/kernels/
```


## Data location
The observational data is stored currently at "/idia/projects/hi_im/users/brandon/meerkat_gain_cali/<specific_folder_names>"


For further questions contact: phD candidate: Brandon Engelbrecht (engelbrechtbn@gmail.com)
