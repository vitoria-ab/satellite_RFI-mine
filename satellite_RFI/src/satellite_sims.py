from satellite_RFI.src import gnss_models_v3 as gm
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.gridspec as gridspec
from tqdm.notebook import tqdm


# ----------------------------------------FUNCTIONS---------------------------------------
def specific_cons(constellation=None, satellite_list=None, angle_list=None):
    '''
    Function returns specific constellations based on the user needs
    constellations: list of constellations which user wants: GPS, GLO, GAL, BDS, QZS, IRNSS, SBAS.
    if constellations==None then will use all sat_types in satellite_list
    satellite_list: the names of the different satellites in the list
    angle_list: corresponding anglular seperation maps of the different sat_types
    '''
    if constellation==None:
        name, angle = satellite_list, angle_list
        
    else:
        angle, name = [],[]
        for i in constellation:
            if i=='BDS':
                i='beidou'
            match = [s for s in satellite_list if i.lower() in s][0]  # string match
            pos = satellite_list.index(match)  # index position

            name.append(match)
            angle.append(angle_list[pos])

        angle=np.array(angle)
    
    return name, angle


# ------------------------------------------------------------------------------------------------------------------

class satellite_sim:
    """
    An object which calculates the comparison between the Observational TOD and the simulated TOD.
    The TOD can be sliced in both time and frequency for the users preferance.
    
    Requirements:
        file_name - file name 
        sats_only - Include or exclude observational data set to !=None
        data_loc - Location of the re-calibration data and angualr seperation maps of the satellite
        sat_loc - Location of the satelite TOD
        sat_beam - The beam choice applied for the data eg: [emss_beam]
        bias_choice_loc - Location of the bias choice parameters for the satellites
        constellations - list of constellations which user wants: GPS, GLO, GAL, BDS, QZS, IRNSS, SBAS. If constellations==None then will use all sat_types in satellite_list
    """
    def __init__(self, 
                 file_name=None, 
                 sats_only=None,
                 data_loc=None, 
                 sat_loc=None,
                 survey_info=None,
                 sat_info=None,
                 plots_loc=None,
                 sat_beam=None,
                 frequency_range=None,
                 constellations=None,
                 bias_choice_loc=''):
        
        self.file_name=file_name
        self.sats_only=sats_only
        self.data_loc=data_loc
        self.sat_loc=sat_loc
        # Getting the outputs of katdal info:
        self.nd_s0, self.nd_s0_coords, self.frequency=survey_info[0], survey_info[1], survey_info[2]
        self.sat_data = pd.read_csv(sat_info, header=0, engine='python')   # Get the chi2 here
        self.plots_loc=plots_loc
        self.sat_beam = sat_beam
        self.frequency_choice=frequency_range
        self.bias_choice_loc=bias_choice_loc
        self.cons=constellations
                
        
        #------------------------------------------------------
        
        '''
        nd_s - noise diode scan in period
        nd_s0 - noise diode off scan in period
        frequency - frequency range or band
        nd_s0_pos - index of noise diode off in scan perid
        timestamps - time flow od the data
        nd_s0_coords - azimuth and elevation of the data
        '''
        
        # Satellite positioning
        self.satellite_type, self.satellite_angle = self.get_satellite_angle_seperation()
        self.satellite_type, self.satellite_angle = specific_cons(constellation=self.cons, satellite_list=self.satellite_type, angle_list=self.satellite_angle)
        print ('Number of constellations: ',len(self.satellite_type))
        #------------------------------------------------------
        
        # Subsetting the data with the constellations of choice
        self.sat_data=self.sat_data[self.sat_data['Sys'].str.contains('|'.join(self.cons))]
        self.alpha_len=len(self.sat_data)
        print ('Length of the satellite catalogue: ',self.alpha_len)
        #-------------------------------------------------------

        
## RUNNING CODE-START ##

    def excecute(self, a_param, obs_time_start=None, obs_time_end=None, 
                 obs_frequency_start=None, obs_frequency_end=None, frequency_idx=None,
                 file_bias_choice=None, add_sub=[None, None], band_lvl=[None, None]):
        '''
        A function which excutes all the function currently available to us. 
        A means to avoid initializing them.
    
        obs_time_start/end - the time slice of the data and simulation
        obs_frequency_start/end - the frequency start and end for the data and simulations
        file_bias_choice - 1. is a str: file name, should be placed in the correct folder
                           2. is a list: the list should have the same number as constellations plus noise parameter
                           3. is None: user will then put amplitude choices for the constellation
        frequency_idx - The minimum and maximum idx for the frequency band (user defined)
        add_sub - a list. First None: add the BG model to the satellite data if !=None
                          Second None: subtracts the BG model from observation data if ==None
        band_lvl - the bandwidth of the signal and the level of attenuation, default=[None,None]
        '''
        
        
                
#         self.sat_data['Alpha'] = self.sat_data['Alpha'].mul(a_param, axis=0)   # Changing/Updating the alpha values


        # Testing single paramter change -----------------------------------
        self.sat_data.loc[:, 'Alpha']=a_param
#         print (self.sat_data.head(14))
        # ----------------------------------
    
        # Sets the frequency band
        self.frequency_band = self.get_frequency_information() 
        
        # Bandwith and level of difference for attenuation
        self.band_lvl = band_lvl
                
        # Satellite TOD
        self.satellite_TOD, self.satellite_SED = self.get_gnss_simulation()
        
        # BG Noise: subtract the observational data; add to the simulations
        self.add_BG,  self.sub_BG = add_sub
       
        
        # Slice idx in the frequency and the time
        self.time_idx, self.frequency_idx = self.get_slice_idx(start_time=obs_time_start, 
                                                                    end_time=obs_time_end, 
                                                                    start_frequency=obs_frequency_start, 
                                                                    end_frequency=obs_frequency_end)


        if self.sats_only==None:
            # Observational data
            self.calibration_data, self.calibration_data_original, self.calibration_data_noise = self.get_calibration_data()
            
            # Calibration data slice
            self.calibration_data_slice, self.calibration_noise_slice = self.get_data_slice()

        
        # Satellite simulation slice
        self.simulation_slice, self.simulation_TOD_slice, self.bias_choice, self.satellite_TOD_slice = self.get_simulation_slice(file_bias_choice=file_bias_choice)
        
        
        

        
## RUNNING CODE-END ##
       
        
        
     
        
## PLOTTING SECTION-START##
        
    def plotting(self, individual=None, logger=None, axis_limit=None,
                 tod_limit=None, save_file=None, file_type=None):
        """
        Plotting various plots: 
        1. The 1D Simulation model vs the Observational data 
        2. The Time-Ordered-Data for the obsevational data
        3. The Time-Ordered-Data for the simualtion data
        
        Parameters:
        individual - If "None" will plot the combined model vs observation data. If "not None" will show the indivdiual satellite componants
        logger - If "None" plots will be in linear scale. If "not None" plots will be in log scale
        axis_limit - If "None" will be the whole limit. If "not None" plots will limited [x1, x2, y1, y2]
        tod_limit - The vmin and vmax for both TOD maps
        sats_only - If you want to show the satellites alone
        save_file - If "not None" file will be saved for all plots. Plots name will include both time and freqeuncy positions.
        suffix - If "not None" plot name will contain user input suffix
        
              
        """
        
        self.file_type = file_type
        
        self.slice_plot_frequency = self._get_slice_plot_(ALL=individual, save_file=save_file, 
                                                          log_scale=logger, limit=axis_limit)

        
        self.sat_sim_map = self._get_TOD_sim_maps_(log_values=logger, vlimits=tod_limit, save_file=save_file)
       
        if self.sats_only == None:
            
            self.TOD_map = self._get_TOD_maps_(log_values=logger, vlimits=tod_limit, save_file=save_file) 
            
            self.get_slice_plot_diff = self._get_slice_plot_diff_(ALL=individual, save_file=save_file, 
                                                              log_scale=logger, limit=axis_limit)
            
            self.TOD_residual = self._get_TOD_resid_maps_(log_values=logger, vlimits=tod_limit, save_file=save_file)
  

 
            
## PLOTTING SECTION-END##



        
    def get_frequency_information(self):
        '''
        Function for the frequency start and end postion
        !!! Should add some extra stuff here regarding the printing of the freqeuncy bands.
        For not fixed
        '''
        f_start_idx = (np.where(self.frequency > self.frequency_choice[0])[0][0])
        f_end_idx = (np.where(self.frequency > self.frequency_choice[1])[0][0])
#         f_start_idx = 600
#         f_end_idx = 2482
        f_band = self.frequency[f_start_idx-1:f_end_idx+1]
        
        return f_band
        
               
        
    def get_calibration_data(self):
        '''
        Obtain the calibrated TOD for the temperature and the noise
        '''
        
        try:
            fname = self.file_name
            data = pickle.load(open(self.data_loc+fname+'_average_TOD_BG_model.p', 'rb'),encoding='latin1')
            
            Temp_tod = data['TOD Avg'].T
            Temp_noise = data['BG Model'].T
            
            if self.sub_BG==None:
                Temp_res = Temp_tod - Temp_noise     # Getting the BG model to be added to the simualtions instead
            else:
                Temp_res = Temp_tod
                
            return Temp_res, Temp_tod, Temp_noise

        except Exception as e:
            print (fname+'-Calibration Information not found :(')
       
        
           
    def get_satellite_angle_seperation(self):
        '''
        Obtain the angular seperation results for the various satellites
        This takes 9sec to read in
        '''
        
        try:
            fname = self.file_name
            beam_choice = self.sat_beam
            data = pickle.load(open(self.sat_loc+str(fname)+'_satellite_angular_position_'+beam_choice+".p", "rb"), encoding='latin1')
            
            Satellite_type = data["sat_name"]     # Contains the names of the constellations
            Satellite_angle = data["angular"]     # Contains the angular seperation maps
            
            return Satellite_type, Satellite_angle
        
        except Exception as e:
            print (fname+'-Satellite angular seperation not found :(')
            
            return 
                        
        
    def get_gnss_simulation(self):
        '''
        Get the TOD maps of the satellites and our data.
        For all the different types of satellites
        '''
        
        satellite_TOD = np.array([gm.TOD_sats(name_tod=satellite_name, 
                                     fname=self.file_name, 
                                     frequency_tod=self.frequency_band, 
                                     beam_model=self.satellite_angle[i], band_lvl=self.band_lvl, 
                                     sat_cat_data=self.sat_data)[0] for i, satellite_name in enumerate(self.satellite_type)])

        
        satellite_SED = np.array([gm.TOD_sats(name_tod=satellite_name, 
                                     fname=self.file_name, 
                                     frequency_tod=self.frequency_band, 
                                     beam_model=self.satellite_angle[i], band_lvl=self.band_lvl, 
                                     sat_cat_data=self.sat_data)[1] for i, satellite_name in enumerate(self.satellite_type)])
        
        return satellite_TOD, satellite_SED
    
    
    
    #-------------------------------------------S4-----------------------------------------------------------------
    #                                         SECTION 4
    #-------------------------------------------S4-----------------------------------------------------------------

    def get_slice_idx(self, start_time=None, end_time=None, start_frequency=None, end_frequency=None):
        '''emss_b.calibration_data_slice
        A function that provides the idx that you wish to slice from
        start_time - the beginning of the scan period - 774 seconds
        end_time - the end of the scan period - 6474 seconds
        start_frequency - beginning of the freqeuncy band usually 981 MHz
        end_frequency - end of the frequency band usually 1499.9
        '''   
        
        # Slicing in the time domain:
        if start_time==None and end_time==None:
            st_pos, et_pos = 0,-1
        else:
            st_pos = (np.where(self.nd_s0 > start_time)[0][0])
            et_pos = (np.where(self.nd_s0 > end_time)[0][0])
#             print 'Time between: '+str(self.nd_s0[st_pos])+' and '+str(self.nd_s0[et_pos])+' in seconds\n'
            
            
        # Slicing in the frequency domain:
        if start_frequency==None and end_frequency==None:
            sf_pos, ef_pos = 0,-1
        else:
            sf_pos = (np.where(self.frequency_band > start_frequency)[0][0])
            ef_pos = (np.where(self.frequency_band > end_frequency)[0][0])
#             print 'Frequency between: '+str(self.frequency_band[sf_pos-1])+' and '+str(self.frequency_band[ef_pos+1])+' in MHz\n'
            
        return (st_pos, et_pos), (sf_pos-1, ef_pos+1)
    
    
    def get_data_slice(self):
        """
        A function that slices the observational data based on the users input of frequency and time points
        """
        calibration_data_slice = self.calibration_data[self.frequency_idx[0]:self.frequency_idx[1], self.time_idx[0]:self.time_idx[1]]
        calibration_noise_slice = self.calibration_data_noise[self.frequency_idx[0]:self.frequency_idx[1], self.time_idx[0]:self.time_idx[1]]
        
        return calibration_data_slice, calibration_noise_slice
      
    
    
    def _average_over_time_(self, x):
        '''
        Function to return the averaged time response
        from a 2d shape, time should be in the first axis
        '''
        return np.mean(x, axis=0)

    
    
    def _average_over_frequency_(self, x):
        '''
        Function to return the averaged frequency response
        from a 2d shape
        '''
        return np.mean(x, axis=1)
    
    
    
    
    def get_simulation_slice(self, file_bias_choice=None):
        '''
        Slicing the simualted satellite data with the index values obtained from the 'get_data_sliced'
        
        '''
#       This is needs to spliced with the above slice
        satellite_TOD_slice = self.satellite_TOD[:, self.frequency_idx[0]:self.frequency_idx[1], self.time_idx[0]:self.time_idx[1]]    
           
        if type(file_bias_choice)==str:
            bias_choice = np.loadtxt(fname=self.bias_choice_loc+(file_bias_choice)+'.txt', delimiter=' ')
        
        elif type(file_bias_choice)==list:
            bias_choice = file_bias_choice
    
        elif type(file_bias_choice)==np.ndarray:
            bias_choice = file_bias_choice
  
        else:
            print  ('Enter the '+str(len(self.satellite_type))+' bias choices and 1 noise bias for the following: ')
            bias_choices_input = input('Enter elements of a list separated by space ')
            try:
                bias_choice = [int(i) for i in bias_choices_input.split()]
            except ValueError:
                print ('Seperate by SPACES')
                bias_choice = [int(i) for i in bias_choices_input.split()]
        
        
        gnss_bias_model = np.nansum([satellite_TOD_slice[i]*bias_choice[i] for i in range(len(satellite_TOD_slice))], 0) #+ bias_choice[-1] Don't require this amplitude
        
        
        #Threshold ---------------------------------------
        threshold_k = 400   # K   : Since there is evidence that MeerKAT has a limit function
#         gnss_bias_model_m = np.ma.masked_where(gnss_bias_model >=threshold_k, gnss_bias_model)     # Old method of masking the values, 
                                                                                                     # NOTE have to change the the variable name to have 'xxx_m'
        gnss_bias_model[gnss_bias_model >= threshold_k] = threshold_k                              # Adding a new threshold method 
#         satellite_TOD_slice[satellite_TOD_slice >= threshold_k] = threshold_k                        # Setting the threshold before bias choice
        # ----------------------------------------------
        
        if self.add_BG==None:
            gnss_bias_model_m = gnss_bias_model 
        else:
            gnss_bias_model_m = gnss_bias_model + self.calibration_noise_slice
               
       
        gnss_bias_model_frequency = self._average_over_frequency_(gnss_bias_model_m)

        
        
        return gnss_bias_model_frequency, gnss_bias_model_m, bias_choice, satellite_TOD_slice

    
    
 
    # ------------------------------------PLOTS--------------------------------------
# **********************************************************************************************************
    # ------------------------------------PLOTS--------------------------------------

    def _get_slice_plot_(self, ALL=None, save_file=None, log_scale=None, limit=None):
        '''
        Function for plotting the Simulation outputs
        '''        

        plt.figure(figsize=(14, 4))
        plt.title(self.file_name+': Time-['+str(np.round(self.nd_s0[self.time_idx[0]], 2))+'-'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'] seconds')
        
        simulation = self.simulation_slice
        plt.plot(self.frequency_band[self.frequency_idx[0]:self.frequency_idx[1]], simulation, color='cyan', label='Model')      
        
        if self.sats_only==None:
            observation = self._average_over_frequency_(self.calibration_data_slice)
            plt.plot(self.frequency_band[self.frequency_idx[0]:self.frequency_idx[1]], observation, '-', color='black', label='Data')   
        else:
            observation=[]
        
        if self.add_BG==None:
            bg_noise = 0 
        else:
            bg_noise = self._average_over_frequency_(self.calibration_noise_slice)
        
        plt.xlabel('Frequency [MHz]')
        plt.ylabel('Temperature [K]')
        if ALL!=None:
            for i in range(len(self.satellite_type)):
                plt.plot(self.frequency_band[self.frequency_idx[0]:self.frequency_idx[1]], 
                         self._average_over_frequency_(self.satellite_TOD_slice[i]) * self.bias_choice[i] + bg_noise, 
                         label=self.satellite_type[i]+'  x'+str(np.round(self.bias_choice[i],3)))
            plt.ylim(bottom=1e-2)

        
        if log_scale==None:
            plt.yscale('log')
            plt.ylabel(r'log$_{10}$(Temperature [K])')
            
        if limit!=None:
            x1, x2, y1, y2 = limit
            plt.xlim(x1, x2)
            plt.ylim(y1, y2)
        
        
        plt.legend()
        plt.tight_layout()
        if save_file !=None:
            plt.savefig(self.plots_loc+self.file_name+'_'+str(np.round(self.nd_s0[self.time_idx[0]], 2))
                        +'_'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'_'+self.sat_beam+'_'+save_file+'.'+self.file_type)
            
            
            data_dump = {'frequency':self.frequency_band[self.frequency_idx[0]:self.frequency_idx[1]],
                         'simulation':simulation,
                         'observation':observation}
            
#             # Saving the data to file
#             pickle.dump(data_dump, open(self.data_loc+self.file_name+'_data_slice_nu_'+str(np.round(self.nd_s0[self.time_idx[0]], 2))+
#                             '_'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'_'+self.sat_beam+'_'+save_file+'_tod.p', 'wb'))
            
        else:
            plt.show()
            
    def _get_slice_plot_diff_(self, ALL=None, save_file=None, log_scale=None, limit=None):
        '''
        Function for plotting the Simulation outputs
        '''        

        plt.figure(figsize=(14, 4))
        plt.title(self.file_name+'-Resulatant Plot: Time-['+str(np.round(self.nd_s0[self.time_idx[0]], 2))+'-'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'] seconds')
        
        observation = self._average_over_frequency_(self.calibration_data_slice)

        
        plt.plot(self.frequency_band[self.frequency_idx[0]:self.frequency_idx[1]], observation - self.simulation_slice, color='black', label='Data-Model')      
        plt.axhline(0, color='r', linestyle='--')
        
        plt.xlabel('Frequency [MHz]')
        plt.ylabel('Temperature [K]')

            
        if limit!=None:
            x1, x2, y1, y2 = limit
            plt.xlim(x1, x2)
#             plt.ylim(y1, y2)
        
        
        plt.legend()
        plt.tight_layout()
        if save_file !=None:
            plt.savefig(self.plots_loc+self.file_name+'_'+str(np.round(self.nd_s0[self.time_idx[0]], 2))
                        +'_'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'_'+self.sat_beam+'_resultant_'+save_file+'.'+self.file_type)            

        else:
            plt.show()
        
        
   # Work in progress
    def _get_TOD_maps_(self, log_values=None, vlimits=None, save_file=None):
        '''
        Obtiaing the TOD maps for the different values for the OBSERVATION DATA
        '''
        

        extent = [self.frequency_band[self.frequency_idx[0]], self.frequency_band[self.frequency_idx[1]],\
                    self.nd_s0[self.time_idx[1]], self.nd_s0[self.time_idx[0]]]

        plt.figure()
        plt.title(self.file_name+'-Observation Data: Time-['+str(np.round(self.nd_s0[self.time_idx[0]], 2))+'-'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'] seconds')
        plt.ylabel('Time [s]')
        plt.xlabel('Frequency [MHz]')
        
        data_slice = self.calibration_data[self.frequency_idx[0]:self.frequency_idx[1], self.time_idx[0]:self.time_idx[1]]
        

        
        if log_values==None:
            if vlimits==None:
                hb=plt.imshow(np.log10(data_slice.T), extent=extent, aspect='auto')
            else:
                hb=plt.imshow(np.log10(data_slice.T), extent=extent, aspect='auto', vmin=vlimits[0], vmax=vlimits[1])
            
            cbar = plt.colorbar(hb)
            cbar.set_label(r'log$_{10}$(T) [K]', rotation=270, labelpad=20, y=0.45)

        else:
            if vlimits==None:
                hb=plt.imshow((data_slice.T), extent=extent, aspect='auto')
            else:
                hb=plt.imshow((data_slice.T), extent=extent, aspect='auto', vmin=vlimits[0], vmax=vlimits[1])
       
            cbar = plt.colorbar(hb)
            cbar.set_label(r'T [K]', rotation=270, labelpad=20, y=0.45)

        plt.tight_layout()
        if save_file !=None:
            plt.savefig(self.plots_loc+self.file_name+'_obs_data_'+str(np.round(self.nd_s0[self.time_idx[0]], 2))+
                        '_'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'_'+self.sat_beam+'_'+save_file+'.'+self.file_type)
            
            # Saving the data to file
            pickle.dump(data_slice, open(self.data_loc+self.file_name+'_obs_data_'+str(np.round(self.nd_s0[self.time_idx[0]], 2))+
                            '_'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'_'+self.sat_beam+'_'+save_file+'_tod.p', 'wb'))
            
        else:
            plt.show()
            
            
   # Work in progress
    def _get_TOD_sim_maps_(self, log_values=None, vlimits=None, save_file=None):
        '''
        Obtiaing the TOD maps for the different values for the SIMULATION DATA
        log_values - 
        '''


        extent = [self.frequency_band[self.frequency_idx[0]], self.frequency_band[self.frequency_idx[1]],\
                    self.nd_s0[self.time_idx[1]], self.nd_s0[self.time_idx[0]]]

        plt.figure()
        plt.title(self.file_name+'-Simulation Data: Time-['+str(np.round(self.nd_s0[self.time_idx[0]], 2))+'-'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'] seconds')
        plt.ylabel('Time [s]')
        plt.xlabel('Frequency [MHz]')
        
        data_slice = self.simulation_TOD_slice
        

        
        if log_values==None:
            if vlimits==None:
                hb=plt.imshow(np.log10(data_slice.T), extent=extent, aspect='auto')
            else:
                hb=plt.imshow(np.log10(data_slice.T), extent=extent, aspect='auto', vmin=vlimits[0], vmax=vlimits[1])
            
            cbar = plt.colorbar(hb)
            cbar.set_label(r'log$_{10}$(T) [K]', rotation=270, labelpad=20, y=0.45)

        else:
            if vlimits==None:
                hb=plt.imshow((data_slice.T), extent=extent, aspect='auto')
            else:
                hb=plt.imshow((data_slice.T), extent=extent, aspect='auto', vmin=vlimits[0], vmax=vlimits[1])
       
            cbar = plt.colorbar(hb)
            cbar.set_label(r'T [K]', rotation=270, labelpad=20, y=0.45)

        plt.tight_layout()
        if save_file !=None:
            plt.savefig(self.plots_loc+self.file_name+'_sim_data_'+str(np.round(self.nd_s0[self.time_idx[0]], 2))+
                        '_'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'_'+self.sat_beam+'_'+save_file+'.'+self.file_type)
            
#             # Saving the file
#             pickle.dump(data_slice, open(self.data_loc+self.file_name+'_sim_data_'+str(np.round(self.nd_s0[self.time_idx[0]], 2))+
#                             '_'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'_'+self.sat_beam+'_'+save_file+'_tod.p', 'wb'))
        else:
            plt.show()
            
            
    def _get_TOD_resid_maps_(self, log_values=None, vlimits=None, save_file=None):
        
        
        extent = [self.frequency_band[self.frequency_idx[0]], self.frequency_band[self.frequency_idx[1]],\
                    self.nd_s0[self.time_idx[1]], self.nd_s0[self.time_idx[0]]]

        plt.figure()
        plt.title(self.file_name+'-Residual: Time-['+str(np.round(self.nd_s0[self.time_idx[0]], 2))+'-'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'] seconds')
        plt.ylabel('Time [s]')
        plt.xlabel('Frequency [MHz]')
        
        data_slice = self.calibration_data[self.frequency_idx[0]:self.frequency_idx[1], self.time_idx[0]:self.time_idx[1]]
        sim_slice = self.simulation_TOD_slice

        residual_slice = data_slice - sim_slice
        
        if log_values==None:
            if vlimits==None:
                hb=plt.imshow(np.log10(residual_slice.T), extent=extent, aspect='auto')
            else:
                hb=plt.imshow(np.log10(residual_slice.T), extent=extent, aspect='auto', vmin=vlimits[0], vmax=vlimits[1])
            
            cbar = plt.colorbar(hb)
            cbar.set_label(r'log$_{10}$(T) [K]', rotation=270, labelpad=20, y=0.45)

        else:
            if vlimits==None:
                hb=plt.imshow((residual_slice.T), extent=extent, aspect='auto')
            else:
                hb=plt.imshow((residual_slice.T), extent=extent, aspect='auto', vmin=vlimits[0], vmax=vlimits[1])
       
            cbar = plt.colorbar(hb)
            cbar.set_label(r'T [K]', rotation=270, labelpad=20, y=0.45)

        plt.tight_layout()
        if save_file !=None:
            plt.savefig(self.plots_loc+self.file_name+'_obs_data_'+str(np.round(self.nd_s0[self.time_idx[0]], 2))+
                        '_'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'_'+self.sat_beam+'_'+save_file+'.'+self.file_type)
            
            # Saving the data to file
            pickle.dump(data_slice, open(self.data_loc+self.file_name+'_residual_'+str(np.round(self.nd_s0[self.time_idx[0]], 2))+
                            '_'+str(np.round(self.nd_s0[self.time_idx[1]], 2))+'_'+self.sat_beam+'_'+save_file+'_tod.p', 'wb'))
            
        else:
            plt.show()

 

        
        
        
    