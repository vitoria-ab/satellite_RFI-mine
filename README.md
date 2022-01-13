# satellite_RFI
Updated: 2022/01/13 - Satellite Simulation RFI code for MeerKLASS - Pre-Survey Experiments

- Memo: https://www.overleaf.com/read/myyvyyvdjrkg   (Under construction)

The code setup is divided into three stages found in Notebooks:

Stage 1:
Calibration of the MeerKLASS data [Notebooks/MKAT_recalibration].
[Section dependant on work done by Dr. Jingying Wang, unique to MeerKAT HI IM observations].

Stage 2:
Calculating the positioning of the satellites with respect to the satellite pointing [Notebooks/Satellite_position].

Stage 3:
Simulating satellite signal and fitting to observational data [Notebbooks/Satellite_simulations].

## Requirements to run:
In order to run all 3 stages you need access to the ILIFU cluster.

### setup.py file:
```
1. srun --pty bash
```
```
2. singularity shell /idia/software/containers/hi_im-py3.simg
```
```
3. cd into satellite-RFI
```
```
4. pip install skyfield --user
```
```
5. python3 setup.py install --user
```

###  Set the container:
```
cp -r hi_sats_container ~/.local/share/jupyter/kernels/
```


## Data location
The observational data is stored currently at "/idia/projects/hi_im/satellite_rfi/<specific_folder_names>"


For further questions contact: phD candidate: Brandon Engelbrecht (engelbrechtbn@gmail.com); Supervisor: Prof. Mario Santos (email.add)
