# LOGS

## SEPTEMBER

### Log 1: 14 - 20 of september (Busy Week)

#### Work:
Continue work on `satellite_RFI` (need EMSS beam to continue!):
1. *Finished calibration:* completed with several alterations (now only needs to have minvis curve manually calibrated, constant BG factor is done for each polarization, for good pixels used original gain instead of interpolated), and deleted the satellite_RFI files that were unnecessary. 
2. *Tried the pipeline in m000,m001,m002; found that calibration gives weirder results:* The results were a bit weird; overall it's the same, but it seems like the continuum is now a bit lower in the 1100-1300 window, which makes the fit worse. Doesn't make any sense because the bandpass was now sitting lower = higher final temperature, not lower!
3. *Added location information for each antenna:* Corrected location for each antenna, I think it didn't matter in m000 because in rsat^2 it's negligible and in the angular separations the differences are in the order of 0-10as.
5. *(To Do) Check other things:* Other telescope beam, if 20/40º isn't enough, air distortion, exact TLEs.
6. *(To Do) Alter satellite trajectories in order to use CSV instead of TLEs.*
7. *(To Do) Create a .py file dedicated to meerkat-only processes.*

Read thesis bibliography: 
1. *Try to read as much as possible:* will skip DESI articles and read more deeply the angular power spectrum articles.  

Complete `CheckSatellites` notebook: 
1. *Completed skeleton:* Satellites from a specific group ("active","gnss","starlink") are retrieved from today, filtered based on being above the horizon and under X angle, and it's used to propagate up to the block and pointings that it's given.
2. *(To Do) Add information on GP precision for the specific group.* 
3. *(To Do) Check frequency bands of each satellite type.*
4. *(To Do) Check what kind of information they want from the notebook.*

#### Questions:
- Has the calibration changed since Brandon presented his work? Because the file has more null columns than the one that the presents as the raw file, and the level 4 mask as well. Maybe ask Jingying. 
- Is EMSS the most useful beam, or the one that's being currently used in observations? Maybe try gaussian beam(!). 
- Need EMSS beam in order to continue working on satellite_RFI! 
- Isn't it useful to add information on the air distortion, as stated in that comment from Ricardo Gafeira in ENAA?
