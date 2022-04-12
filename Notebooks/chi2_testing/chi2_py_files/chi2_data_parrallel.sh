#!/bin/bash

#SBATCH --job-name='mask_5_fill'
#SBATCH --cpus-per-task=23
#SBATCH --mem=40GB
#SBATCH --output=/users/bengelbrecht/PhD_Work/Satellite_Code/satellite_RFI-untangle/Notebooks/Testing/data_test/1551055211/data_info/parallel_2022_03_20/5_fill_no_sig_output.log
#SBATCH --error=/users/bengelbrecht/PhD_Work/Satellite_Code/satellite_RFI-untangle/Notebooks/Testing/data_test/1551055211/data_info/parallel_2022_03_20/5_fill_no_sig_error.log
#SBATCH --time=6:00:00

echo "Submitting Slurm job"
singularity exec /idia/software/containers/hi_im-py3.simg python parallel_code.py