## Files in sattelite_RFI:
- "attenuation": File with attenuation functions `tophat_oob` and `gaussian_oob`; rewritten for clarity and celerity. However, all of the mentions to attenuation were removed from the code so this currently is not used.
- "beam_model": File with different telescope beam models, either analytical or from a file; partially rewritten.
- "check_satellite": Old file, not rewritten.
- "data_reduction": Old file, not rewritten.
- "Generating_Calibrated_Data": Old file, not rewritten.
- "psd_models": File with the Power Spectrum Density models for the GNSS satellite signals; partially rewritten.
- "rewrite_tle": Old file, not rewritten.
- "satellite_extract": Old file, not rewritten.
- "simulation": File with the simulation object, which gathers information calculated in the different files; rewritten for clarity and celerity.
- "tle_sat_download": Old file, not rewritten.
- "tools": Old file, not rewritten.
- "wiggleZ_area": Old file, not rewritten.

## Notebooks:
- "N3_fitting": Notebook that fits the simulation to the data, using specific masking parameters.
- "N3_graphs": Notebook that shows the graphs for the data for all of the masks chosen; doesn't show time intervals yet.
- "N4_create_catalogs": Notebook that creates the files 'new_satellite_constellation_catalog.csv' (new catalog that now has the signals of each satellite instead of the signals of each constellation) and 'satellite_angular_positions' (new file that saves the satellite angular positions in a more expedite manner).