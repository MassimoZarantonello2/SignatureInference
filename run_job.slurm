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
python /home/baderlab/mzarant/SignatureInference/scripts/main.py "$@"

# sbatch --job-name default run_job.slurm --gt_path ground_truth/bin_exposure --save_evaluations default --save_models default
# sbatch --job-name cosmic run_job.slurm --gt_path ground_truth_cosmic/bin_exposure --save_evaluations cosmic --save_models cosmic
# sbatch --job-name reference run_job.slurm --gt_path ground_truth_reference/bin_exposure --save_evaluations reference --save_models reference
