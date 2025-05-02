#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --mem=128GB
#SBATCH --time=48:00:00

source /home/baderlab/mzarant/SignatureInference/.venv/bin/activate
# Passa tutti i parametri ricevuti a Python
python /home/baderlab/mzarant/SignatureInference/scripts/main.py --gt_type default --save_evaluations default --save_models default --hyp_type lightgbmxt --time_limit 480
python /home/baderlab/mzarant/SignatureInference/scripts/main.py --gt_type cosmic --save_evaluations cosmic --save_models cosmic --hyp_type lightgbmxt --time_limit 480
python /home/baderlab/mzarant/SignatureInference/scripts/main.py --gt_type reference --save_evaluations reference --save_models reference --hyp_type lightgbmxt --time_limit 480
