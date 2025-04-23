#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=160
#SBATCH --mem=128GB
#SBATCH --time=23:59:00

source /home/baderlab/mzarant/SignatureInference/.venv/bin/activate

# Passa tutti i parametri ricevuti a Python
python /home/baderlab/mzarant/SignatureInference/scripts/prova.py "$@"
