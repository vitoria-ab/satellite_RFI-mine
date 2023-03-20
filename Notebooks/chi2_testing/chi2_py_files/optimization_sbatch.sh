#!/bin/bash
#SBATCH --job-name=T2-chi-f
#SBATCH --cpus-per-task=1
#SBATCH --mem=5GB
#SBATCH --output=1100-1350_temporal_T2_avg10_chi-f_output.log
#SBATCH --error=1100-1350_temporal_T2_avg10_chi-f_error.log
#SBATCH --time=8:00:00

echo "Submitting Slurm job"
# sed -i '99s/.*/save_suffix="'$1'"/' /users/bengelbrecht/PhD_Work/Satellite_Code/satellite_RFI-untangle/Notebooks/param.py
# sed -i '105s/.*/    degree="'$2'"/' /users/bengelbrecht/PhD_Work/Satellite_Code/satellite_RFI-untangle/Notebooks/param.py
# sed -i '102s/.*/mask='$3'/' /users/bengelbrecht/PhD_Work/Satellite_Code/satellite_RFI-untangle/Notebooks/param.py

singularity exec /idia/software/containers/hi_im-py3.simg python sat_optimization.py
