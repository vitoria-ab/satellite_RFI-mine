#!/bin/bash

echo "Running mixed test"
## ============================================================================================##
## PARAMETERS
filename=1551055211
folder_name="sat_12"
degrees=
thermals=
time_starts=
time_ends=
pixel_timeline=
chi_sigma=True
time_average_main=
parampath=param_multi_mask.py
sbashpath=optimization_sbatch.sh

## SLEEP TIME PER RUN
sleeptime=45
## FILENAME LENGTH
file_len=${#filename[@]}
## ============================================================================================##

for (( fidx=0; fidx<=$file_len-1; fidx++ ))
    do
        ## FILE NAME
        echo ${filename[$fidx]}
        sed -i '8s/.*/file = '${filename[$fidx]}'/' $parampath
        ## FOLDER NAME
        echo ${folder_name[$fidx]}
        sed -i '43s/.*/folder = "'${folder_name[$fidx]}'"/' $parampath

        ## ============================================================================================##

        ## CHI SIGMA BOOLEAN
        for csigma in "${chi_sigma[@]}"
            do
                echo "Runnning Chi Sqaure Sigma: $csigma"
                sed -i '68s/.*/chi_sigma = '$csigma'/' $parampath

                ## TIME AVERAGING
                if [ -z "$time_average_main" ]
                then
                    sed -i '64s/.*/time_average = None/' $parampath
                else
                    sed -i '64s/.*/time_average = '$time_average_main'/' $parampath
                fi
                
                
                ## NO MASKING
                if [[ -z "$degrees" && -z "$thermals" && -z "$time_starts" && -z "$time_ends" && -z "$pixel_timeline" ]]
                then
                    echo "No mask"
                    sed -i '56s/.*/mask_degree = None/' $parampath
                    sed -i '58s/.*/mask_temperature = None/' $parampath
                    sed -i '60s/.*/mask_temporal = None, None/' $parampath
                    sed -i '62s/.*/mask_pixel_timeline = None/' $parampath

                    mtype="no-mask"
                    if [ -z "$time_average_main" ]
                    then
                        echo "Time averaging: No"
                        sed -i '5s/.*/#SBATCH --output='${filename[$fidx]}'_'$mtype'_'$csigma'_output.log/' $sbashpath
                        sed -i '6s/.*/#SBATCH --error='${filename[$fidx]}'_'$mtype'_'$csigma'_error.log/' $sbashpath  
                    else
                        echo "Time averaging: Yes-$time_average_main seconds"
                        sed -i '5s/.*/#SBATCH --output='${filename[$fidx]}'_'$mtype'_'$csigma'_time_average_'$time_average_main'_output.log/' $sbashpath
                        sed -i '6s/.*/#SBATCH --error='${filename[$fidx]}'_'$mtype'_'$csigma'_time_average_'$time_average_main'_error.log/' $sbashpath  
                    fi
                
                else     
                    ## ANGULAR MASKING
                    if [ -z "$degrees" ]
                    then
                        echo "Angular masking is empty"
                    else
                        echo "Angular masking running"
                        for var in "${degrees[@]}"
                            do
                                sed -i '56s/.*/mask_degree = "'$var'"/' $parampath
                                sed -i '58s/.*/mask_temperature = None/' $parampath
                                sed -i '60s/.*/mask_temporal = None, None/' $parampath
                                sed -i '62s/.*/mask_pixel_timeline = None/' $parampath

                                mtype="degree"

                                if [ -z "$time_average_main" ]
                                then
                                    echo "Time averaging: No"
                                    sed -i '5s/.*/#SBATCH --output='${filename[$fidx]}'_'$mtype'_'$var'_'$csigma'_output.log/' $sbashpath
                                    sed -i '6s/.*/#SBATCH --error='${filename[$fidx]}'_'$mtype'_'$var'_'$csigma'_error.log/' $sbashpath  
                                else
                                    echo "Time averaging: Yes-$time_average_main seconds"
                                    sed -i '5s/.*/#SBATCH --output='${filename[$fidx]}'_'$mtype'_'$var'_'$csigma'_time_average_'$time_average_main'_output.log/' $sbashpath
                                    sed -i '6s/.*/#SBATCH --error='${filename[$fidx]}'_'$mtype'_'$var'_'$csigma'_time_average_'$time_average_main'_error.log/' $sbashpath  
                                fi
                                sbatch $sbashpath
                                sleep $sleeptime
                            done
                    fi


                    ## THERMAL MASKING
                    if [ -z "$thermals" ]
                    then
                        echo "Themal masking is empty"
                    else
                        echo "Thermal masking running"
                        for var in "${thermals[@]}"
                            do
                                sed -i '56s/.*/mask_degree = None/' $parampath
                                sed -i '58s/.*/mask_temperature = '$var'/' $parampath
                                sed -i '60s/.*/mask_temporal = None, None/' $parampath
                                sed -i '62s/.*/mask_pixel_timeline = None/' $parampath
                                mtype="thermal"

                                if [ -z "$time_average_main" ]
                                then
                                    echo "Time averaging: No"
                                    sed -i '5s/.*/#SBATCH --output='${filename[$fidx]}'_'$mtype'_'$var'_'$csigma'_output.log/' $sbashpath
                                    sed -i '6s/.*/#SBATCH --error='${filename[$fidx]}'_'$mtype'_'$var'_'$csigma'_error.log/' $sbashpath      
                                else
                                    echo "Time averaging: Yes-$time_average_main seconds"
                                    sed -i '5s/.*/#SBATCH --output='${filename[$fidx]}'_'$mtype'_'$var'_'$csigma'_time_average_'$time_average_main'_output.log/' $sbashpath
                                    sed -i '6s/.*/#SBATCH --error='${filename[$fidx]}'_'$mtype'_'$var'_'$csigma'_time_average_'$time_average_main'_error.log/' $sbashpath  
                                fi
                                sbatch $sbashpath
                                sleep $sleeptime
                            done
                    fi


                    ## TEMPORAL MASKING
                    if [[ -z "$time_starts" && -z "$time_ends" ]]
                    then
                        echo "Temporal masking is empty"
                    else
                        echo "Temporal masking running"
                        time_len=${#time_starts[@]}
                        for (( tidx=0; tidx<=$time_len-1; tidx++ ))
                            do
                                sed -i '56s/.*/mask_degree = None/' $parampath
                                sed -i '58s/.*/mask_temperature = None/' $parampath
                                sed -i '60s/.*/mask_temporal = '"${time_starts[$tidx]}"', '"${time_ends[$tidx]}"'/' $parampath
                                sed -i '62s/.*/mask_pixel_timeline = None/' $parampath
                                mtype="temporal"

                                if [ -z "$time_average_main" ]
                                then
                                    echo "Time averaging: No"
                                    sed -i '5s/.*/#SBATCH --output='${filename[$fidx]}'_'$mtype'_'${time_starts[$tidx]}'-'${time_ends[$tidx]}'_'$csigma'_time_output.log/' $sbashpath
                                    sed -i '6s/.*/#SBATCH --error='${filename[$fidx]}'_'$mtype'_'${time_starts[$tidx]}'-'${time_ends[$tidx]}'_'$csigma'_time_error.log/' $sbashpath     
                                else
                                    echo "Time averaging: Yes-$time_average_main seconds"
                                    sed -i '5s/.*/#SBATCH --output='${filename[$fidx]}'_'$mtype'_'${time_starts[$tidx]}'-'${time_ends[$tidx]}'_'
                                    $csigma'_time_average_'$time_average_main'_output.log/' $sbashpath

                                    sed -i '6s/.*/#SBATCH --error='${filename[$fidx]}'_'$mtype'_'${time_starts[$tidx]}'-'${time_ends[$tidx]}'_'
                                    $csigma'_time_average_'$time_average_main'_error.log/' $sbashpath          
                                fi
                                sbatch $sbashpath
                                sleep $sleeptime
                            done
                    fi


                    ## PIXEL TIMEILINE MASKING
                    if [ -z "$pixel_timeline" ]
                    then
                        echo "Pixel timeline masking is empty"
                    else
                        echo "Pixel timeline masking running:"
                        for var in "${pixel_timeline[@]}"
                            do
                                echo $var
                                sed -i '56s/.*/mask_degree = None/' $parampath
                                sed -i '58s/.*/mask_temperature = None/' $parampath
                                sed -i '60s/.*/mask_temporal = None, None/' $parampath
                                sed -i '62s/.*/mask_pixel_timeline = '$var'/' $parampath
                                mtype="pixel_timeline"


                                if [ -z "$time_average_main" ]
                                then
                                    echo "Time averaging: No"
                                    sed -i '5s/.*/#SBATCH --output='${filename[$fidx]}'_'$mtype'_'$var'_'$csigma'_output.log/' $sbashpath
                                    sed -i '6s/.*/#SBATCH --error='${filename[$fidx]}'_'$mtype'_'$var'_'$csigma'_error.log/' $sbashpath         
                                else
                                    echo "Time averaging: Yes-$time_average_main seconds"
                                    sed -i '5s/.*/#SBATCH --output='${filename[$fidx]}'_'$mtype'_'$var'_'$csigma'_time_average_'$time_average_main'_output.log/' $sbashpath
                                    sed -i '6s/.*/#SBATCH --error='${filename[$fidx]}'_'$mtype'_'$var'_'$csigma'_time_average_'$time_average_main'_error.log/' $sbashpath    
                                fi
                                sbatch $sbashpath
                                sleep $sleeptime
                            done
                    fi
                fi
            done
    done
