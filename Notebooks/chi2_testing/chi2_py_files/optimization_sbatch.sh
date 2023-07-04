#!/bin/bash
#SBATCH --job-name=Chi2
#SBATCH --cpus-per-task=1
#SBATCH --mem=5GB
#SBATCH --output=1551037708_temporal_3543-4623.55_False_time_avg_output.log
#SBATCH --error=1551037708_temporal_3543-4623.55_False_time_avg_error.log
#SBATCH --time=8:00:00

echo "Submitting Slurm job"

singularity exec /idia/software/containers/hi_im-py3.simg python sat_optimization.py
