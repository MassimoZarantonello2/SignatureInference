for file in ../simulations/ground_truth/random_values_*.csv; do
  filename=$(basename "$file")
  name="${filename%.csv}"
  sbatch --job-name "$name" run_job.slurm \
    --gt_type "$file" \
    --save_evaluations "./results/random/${name}_evaluations.json" \
    --save_models "./models/${name}" \
    --hyp_type lightgbxt \
    --runs 5 \
    --time_limit 240
done
