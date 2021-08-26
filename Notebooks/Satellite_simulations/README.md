Stage 3 README file for the Satellite_simulations

See Jupyter Notebook: S34_class.ipynb

Note: A PDF will be constructered for further details in this section (Pending)

This section looks at user fitting of the various satellites combined to the observational data. The data is given in a 2D format and with the code we can look at specific windows in the time and frequency domain. The satellite signal is fitted to the observational data in the freqeuncy domain, time is averaged out over a specific window.

When fitting the satellites:
 There are two different parameter types. The first - fits the overall bias choice to the satellite constellation (all <GPS, GLO, etc...> satellites added together. The second - found in the folder <Satellite_Catalogue> is a list of all satellite signals that we could obtain from <Insert text book here and page>. In the second type is a list of Power and Gain (dB) of the individual satellite signals which can be adjusted, the modulation type or function that this signal is transmitted by, the peak frequency and frequency bandwidth of these satellites.

Required files:
- bias_choices.txt: Contains the bias parameters for the satellites when fitting the constellation.
- psd_models_V2.py: The power spectrum density models for the satellites. (The modulation of signal transmission of the satellites).
- gnss_models_V3.py: Constructs the 2D shape of the satellite simulation for all satellites combined. Reads the .csv file in <Satellite_Catalogue>, identifies the modulation type and calculates the satellite signal.

For any questions please contact Brandon Engelbrecht


