#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --mem=128GB
#SBATCH --time=60:00:00

source /home/baderlab/mzarant/SignatureInference/.venv/bin/activate
export OPENBLAS_NUM_THREADS=10
export GOTO_NUM_THREADS=10
export OMP_NUM_THREADS=10
# Passa tutti i parametri ricevuti a Python
python /home/baderlab/mzarant/SignatureInference/scripts/sequential/sequential.py "$@"


# sbatch --job-name default scripts/sequential/sequential_run_job.slurm --gt_path ground_truth/bin_exposures --save_evaluations sm_default --save_models default
# sbatch --job-name cosmic scripts/sequential/sequential_run_job.slurm --gt_path ground_truth_cosmic/bin_exposures --save_evaluations sm_cosmic --save_models cosmic
#   