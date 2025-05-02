#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --mem=128GB
#SBATCH --time=48:00:00

source /home/baderlab/mzarant/SignatureInference/.venv/bin/activate
export OPENBLAS_NUM_THREADS=30
export GOTO_NUM_THREADS=30
export OMP_NUM_THREADS=30
# Passa tutti i parametri ricevuti a Python
python /home/baderlab/mzarant/SignatureInference/scripts/main.py "$@"