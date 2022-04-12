 #!/bin/bash

#SBATCH --job-name='full_mask_5'
#SBATCH --cpus-per-task=1
#SBATCH --mem=10GB
#SBATCH --output=/users/bengelbrecht/PhD_Work/Satellite_Code/satellite_RFI-untangle/Notebooks/Testing/data_test/1551055211/data_info/parallel_2022_03_25/5_no_sig_full_output.log
#SBATCH --error=/users/bengelbrecht/PhD_Work/Satellite_Code/satellite_RFI-untangle/Notebooks/Testing/data_test/1551055211/data_info/parallel_2022_03_25/5_no_sig_full_error.log
#SBATCH --time=6:00:00

echo "Submitting Slurm job"
singularity exec /idia/software/containers/hi_im-py3.simg python full_version_code.py