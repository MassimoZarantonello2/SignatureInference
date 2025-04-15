#!/bin/bash
#SBATCH --job-name=multi_job
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64GB
#SBATCH --time=23:59:00

# Carica moduli, ambienti, ecc. se necessario
source /home/baderlab/mzarant/SignatureInference/.venv/bin/activate
# Il tuo comando
bash /home/baderlab/mzarant/SignatureInference/multithread_run.sh --save_path toronto_cluster --num_run 10
