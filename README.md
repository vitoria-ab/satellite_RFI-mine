# satellite_RFI
Updated: 2023/07/01 - Satellite Simulation RFI code for MeerKLASS - Pre-Survey Experiments

- Memo: https://www.overleaf.com/read/myyvyyvdjrkg   (Under construction)

The code setup is divided into three stages found in Notebooks:

Stage 1:
Calibration of the MeerKLASS data [Notebooks/MKAT_recalibration].
[Section dependant on work done by Dr. Jingying Wang, unique to MeerKAT HI IM observations].

Stage 2:
Calculating the positioning of the satellites with respect to the satellite pointing [Notebooks/Satellite_position].

Stage 3:
Simulating satellite signal and fitting to observational data [Notebbooks/Satellite_simulations].

### Note
Currently, the code runs a Py2 [Stage 1&2] / Py3 [Stage 3] hybrid. 
Work on making it Py3 is still under construction for now.

## Requirements to run:
In order to run all 3 stages you need access to the ILIFU cluster.

### setup.py file
```
1. srun --pty bash
```
Note: If you are using a terminal, do the above. If you are running via JupyterLab you can skip the step
```
2.1 singularity shell /idia/software/containers/hi_im-python2.7.simg
2.2 singularity shell /idia/software/containers/hi_im-py3.simg
```
```
3. cd satellite_RFI
```
```
4. pip install skyfield --user
```
```
5.1 python2 setup.py install --user
5.2 python3 setup.py install --user
```

###  Set the container:
```
cp -r hi_sats_container ~/.local/share/jupyter/kernels/
```


## Data location
The observational data is stored currently at "hi_im/brandon/meerkat_gain_cali/<specific_folder_names>"


For further questions contact: phD candidate: Brandon Engelbrecht (engelbrechtbn@gmail.com)
