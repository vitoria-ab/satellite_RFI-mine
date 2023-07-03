#!/bin/bash

echo "Running test"

filename=1551037708
folder_name="sat_3"
# Values or inputs
# mask_type=(None "degree" "temporal" "thermal")
mask_type=("temporal")
degrees=("1F" "5F")
thermals=(25 50 100)
time_starts=(851 3543)
time_ends=(1757 4623.55)
chi_sigma=(True False)

time_average_main=10

time_len=${#time_starts[@]}
# File path for param.py
parampath=../../param_import/param.py
sbashpath=optimization_sbatch.sh
# File name
sed -i '12s/.*/file='$filename'/' $parampath
# Folder name
sed -i '109s/.*/folder="'$folder_name'"/' $parampath

# Controlling the pause in between runs
sleeptime=45
# Running through the chi_sigma boolean
for csigma in "${chi_sigma[@]}"
    do
        # echo $csigma
        # Changing the chi_sigma values in the param.py file
        sed -i '144s/.*/chi_sigma='$csigma'/' $parampath
        # Changing the msk_type values in the param.py file
        for mtype in "${mask_type[@]}"
            do
                # Seperating the None and string components from the mask_typpe
                if [ $mtype = None ]
                then
                    # echo $mtype
                    sed -i '115s/.*/mask_type='$mtype'/' $parampath
                    time_average=None
                    sed -i '179s/.*/time_size='${time_average}'/' $parampath

                    sed -i '5s/.*/#SBATCH --output='$filename'_'$mtype'_'$csigma'_output.log/' $sbashpath
                    sed -i '6s/.*/#SBATCH --error='$filename'_'$mtype'_'$csigma'_error.log/' $sbashpath
                    
                    sbatch $sbashpath
                    sleep $sleeptime
                else
                    # echo $mtype
                    sed -i '115s/.*/mask_type="'$mtype'"/' $parampath
                    # Running through each mask type
                    # DEGREE
                    if [ $mtype = "degree" ]
                    then
                        # echo $mtype
                        for dmask in "${degrees[@]}"
                            do
                                sed -i '121s/.*/    mask_degree="'$dmask'"/' $parampath
                                time_average=None
                                sed -i '179s/.*/time_size='${time_average}'/' $parampath

                                sed -i '5s/.*/#SBATCH --output='$filename'_'$mtype'_'$dmask'_'$csigma'_output.log/' $sbashpath
                                sed -i '6s/.*/#SBATCH --error='$filename'_'$mtype'_'$dmask'_'$csigma'_error.log/' $sbashpath
                                
                                sbatch $sbashpath
                                sleep $sleeptime
                            done
                    # THERMAL
                    elif [ $mtype = "thermal" ]
                    then
                        # echo $mtype
                        for tmask in "${thermals[@]}"
                            do
                                sed -i '127s/.*/    mask_temperature='$tmask'/' $parampath
                                time_average=None
                                sed -i '179s/.*/time_size='${time_average}'/' $parampath

                                sed -i '5s/.*/#SBATCH --output='$filename'_'$mtype'_'$tmask'_'$csigma'_output.log/' $sbashpath
                                sed -i '6s/.*/#SBATCH --error='$filename'_'$mtype'_'$tmask'_'$csigma'_error.log/' $sbashpath
                                
                                sbatch $sbashpath
                                sleep $sleeptime
                            done
                    # TEMPORAL
                    elif [ $mtype = "temporal" ]
                    then
                        echo $mtype
                        # for Running the number of time points available
                        for (( tidx=0; tidx<=$time_len-1; tidx++ ))
                            do
                                # echo $tidx
                                sed -i '134s/.*/    ts_slice='"${time_starts[$tidx]}"'/' $parampath
                                sed -i '135s/.*/    te_slice='"${time_ends[$tidx]}"'/' $parampath
                                time_average=None
                                sed -i '179s/.*/time_size='${time_average}'/' $parampath

                                sed -i '5s/.*/#SBATCH --output='$filename'_'$mtype'_'${time_starts[$tidx]}'-'${time_ends[$tidx]}'_'$csigma'_time_output.log/' $sbashpath
                                sed -i '6s/.*/#SBATCH --error='$filename'_'$mtype'_'${time_starts[$tidx]}'-'${time_ends[$tidx]}'_'$csigma'_time_error.log/' $sbashpath
                                
                                sbatch $sbashpath
                                sleep $sleeptime
                                
                                # Running for the time average
                                if [ -z "$time_average_main" ]
                                then
                                    echo "Null time average"
                                else
                                    echo "not Null"
                                
                                    sed -i '179s/.*/time_size='${time_average_main}'/' $parampath

                                    sed -i '5s/.*/#SBATCH --output='$filename'_'$mtype'_'${time_starts[$tidx]}'-'${time_ends[$tidx]}'_'$csigma'_time_avg_output.log/' $sbashpath
                                    sed -i '6s/.*/#SBATCH --error='$filename'_'$mtype'_'${time_starts[$tidx]}'-'${time_ends[$tidx]}'_'$csigma'_time_avg_error.log/' $sbashpath
                                    
                                    sbatch $sbashpath
                                    sleep $sleeptime
                                fi          
                            done
                    else
                        echo "INCORRECT !!!! MASK"
                    fi                  
                fi
                sleep $sleeptime     
            done
        sleep $sleeptime
    done 