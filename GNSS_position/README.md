Stage 2 README file for the GNSS position and angular seperation of satellites

See Jupyter Notebook: Satellite_position.ipynb

Note: A PDF will be constructed for further details in this section (Pending)

This notebook looks at the positioning of all GNSS satellites that was given (GPS (USA), GLONASS (RUS), etc....) as parameters. You can restrict
the amount of satellites you wish to test. The Two-Line-Element (TLE) which contains the positioning of the satellites can be found at <https://www.celestrak.com/norad/elements/>. However this gives only the most recent snapshot, for observations done in the past we look here <https://web.archive.org/web/2019*/https://www.celestrak.com/NORAD/elements/geo.txt>. Simply change <geo> with the other satellite names (this can be seen on CelesTrack) and you will find all snapshots taken. We took the nearest snapshots to observation day also saw it does not matter if you take before or after observation day (Closest snapshot is prefered). 

These snapshots can be found in TLE folder

Required files:
- beam_model.py: Contains different beam choices, or different beams can be added to this file based on user preference. Default: Co-sine beam model 
- check_satellite.py: Based on the satellites of choice and the positioning of MeerKAT pointings, this file outputs the 2D angular seperation maps.
- satellite_extract.py: Since not all GNSS satellites are given, some fall under <geo.txt> such as IRNSS and QBZ therefor we extract these satellites. All that is required is the folder location containing the geo.txt TLE data.

For any questions pertaining to these 3 files or notebook, please contact Brandon Engelbrecht of Dr Yi-Chao Li.

