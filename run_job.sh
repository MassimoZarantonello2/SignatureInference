#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --mem=128GB
#SBATCH --time=60:00:00

source .venv/bin/activate
export OPENBLAS_NUM_THREADS=10
export GOTO_NUM_THREADS=10
export OMP_NUM_THREADS=10
# Passa tutti i parametri ricevuti a Python
python ./scripts/main.py "$@"


# sbatch --job-name cosmic run_job.slurm --gt_type cosmic --save_evaluation cosmic --save_models cosmic --hyp_type lightgbmxt
# sbatch --job-name reference run_job.slurm --gt_type reference --save_evaluation reference --save_models reference --hyp_type lightgbmxt
