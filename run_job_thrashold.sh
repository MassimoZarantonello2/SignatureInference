#!/bin/bash
for n in {0..9}; do
  sbatch --job-name th$n run_job.slurm --gt_type default --threshold $n --save_evaluation default_$n --save_models default_$n --hyp_type lightgbxt
done
