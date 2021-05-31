# satellite_RFI
2021/05/04 - Satellite RFI code for MeerKLASS

- Memo: https://www.overleaf.com/read/myyvyyvdjrkg   (Under construction)

The code setup is divided into three stages found in Notebooks:

Stage 1:
Calibration of the MeerKLASS data [s1_reCalibration_Data].

Stage 2:
Calculating the positioning of the satellites with respect to the MeerKAT pointing [s2_GNSS_position].

Stage 3:
Simulation construction of satellites and fitting to observational data [s3_Satellite_simulations].

## Requirements to run:
In order to run all 3 stages you need access to the ILIFU cluster.

### setup.py file:
```
srun --pty bash
```
```
singularity shell /idia/software/containers/hi_im-python2.7.simg
```
```
python2 setup.py install --user
```

###  Set the container:
```
cp -r hi_sats_container ~/.local/share/jupyter/kernels/
```


## Data location
The observational data is stored currently at "/idia/projects/hi_im/brandon/<specific_folder_names>"


For further questions contact Brandon Engelbrecht (engelbrechtbn@gmail.com) 
