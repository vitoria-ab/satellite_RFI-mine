# satellite_RFI
2021/05/04 - Satellite RFI code for MeerKLASS

- Memo: https://www.overleaf.com/read/myyvyyvdjrkg   (Under construction)

The code setup is divided into three stages:

Stage 1:
Calibration of the MeerKLASS data [reCalibration_Data].

Stage 2:
Calculating the positioning of the satellites with respect to the MeerKAT pointing [GNSS_position].

Stage 3:
Simulation construction of satellites and fitting to observational data [Satellite_simulations].

## Requirements to run:
In order to run all 3 stages you need access to the ILIFU cluster.
###  Set the container:
```
cp -r hi_sats_container ~/.local/share/jupyter/kernels/
```

```
cd ~/.local/share/jupyter/kernels/hi_sats_container
```


## Data location
The observational data is stored currently at "/idia/projects/hi_im/brandon/<specific_folder_names>"


For further questions contact Brandon Engelbrecht (engelbrechtbn@gmail.com) 
