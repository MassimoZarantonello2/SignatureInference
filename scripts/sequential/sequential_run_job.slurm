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


# sbatch --job_name default --gt_path ground_truth/bin_exposures --save_evaluations default --save_models default
# sbatch --job_name default --gt_path ground_truth_cosmic/bin_exposures --save_evaluations cosmic --save_models cosmic
# sbatch --job_name default --gt_path ground_truth_reference/bin_exposures --save_evaluations reference --save_models reference