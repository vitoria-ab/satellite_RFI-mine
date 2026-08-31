#!/bin/bash

#SBATCH --job-name='RR'
#SBATCH --cpus-per-task=1
#SBATCH --mem=20GB
#SBATCH --time=08:00:00
#SBATCH --output=job_submissions/RR-%j-stdout.log
#SBATCH --error=job_submissions/RR-%j-stderr.log

echo "Submitting Slurm job"
cd /users/bvitoria/workspace/satellite_RFI-mine/Notebooks
singularity exec /users/bvitoria/workspace/hi_im-py3.sif python -u job_submissions/RR.py