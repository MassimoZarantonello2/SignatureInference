#!/bin/bash
#SBATCH --job-name=multi_job
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8GB
#SBATCH --time=23:59:00

source /home/baderlab/mzarant/SignatureInference/.venv/bin/activate

export OPENBLAS_NUM_THREADS=1
export GOTO_NUM_THREADS=1
export OMP_NUM_THREADS=1

# Passa tutti i parametri ricevuti a Python
python /home/baderlab/mzarant/SignatureInference/scripts/EvaluationsRunner.py "$@"

