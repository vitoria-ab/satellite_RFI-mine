#!/bin/bash
#SBATCH --job-name=Chi2
#SBATCH --cpus-per-task=1
#SBATCH --mem=5GB
#SBATCH --output=<Filename>
#SBATCH --error=<Filename>
#SBATCH --time=8:00:00

echo "Submitting Slurm job"

singularity exec /idia/software/containers/hi_im-py3.simg python sat_optimization.py
