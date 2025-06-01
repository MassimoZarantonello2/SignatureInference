from EvaluationsRunner import EvaluationsRunner
import argparse
from utils.Log import LogClass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Esecuzione del modello di valutazione con parametri opzionali"
    )
    time_limit = None
    num_run = None
    
    parser.add_argument(
        "--gt_type",
        type=str,
        default="default",
        help="Path del ground truth binarizzato",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0,
        help="Threshold value for considering a segnature active in a sample"
    )
    parser.add_argument(
        "--save_evaluations",
        type=str,
        default=None,
        help="Path per salvare le valutazioni",
    )
    parser.add_argument(        # Folder in which to save the models
        "--save_models",
        type=str,
        default=None,
        help="Path per salvare i modelli",
    )
    parser.add_argument(
        "--quality",
        type=str,
        default="medium_quality",
    )
    parser.add_argument(
        "--hyp_type",
        type=str,
        default="default",
        help="Tipo di hyperparametri da utilizzare",
    )
    parser.add_argument(
        "--time_limit",
        type=int,
        default=None,
        help="Tempo limite per il training dei modelli",
    )
    parser.add_argument(
        "--label_correlation",
        type=bool,
        default=True,
        help="Correlation between target labels"
    )
    parser.add_argument(
        "--runs", type=int, default=None, help="Numero specifico di run da eseguire"
    )

    args = parser.parse_args()

    if args.gt_type == "default":
        bin_ground_truth_path = "./simulations/ground_truth/exposures_"+args.threshold+".csv"
    else:
        bin_ground_truth_path = "./simulations/ground_truth_" + args.gt_type + "/exposures_"+args.threshold+".csv"
        
    if args.save_evaluations is None:
        save_evaluation_path = "./results/" + args.gt_type + "_evaluations.json"
    else:
        save_evaluation_path = "./results/" + args.save_evaluations + "_evaluations.json"
   
    if args.save_models is not None:
        save_model_path = "./models/" + args.save_models + "/"        

    print(f"Taking the ground truth from: {bin_ground_truth_path}")
    print(f"Saving the evaluation in: {save_evaluation_path}")
    print(f"Saving the models in: {save_model_path}")
    print(f"Using quality of: {args.quality}")
    print(f"Taking the hyperparameters from: {args.hyp_type}")
    print(f"Time limit: {args.time_limit}")
    print(f"Using label correlation: {args.label_correlation}")
    print(f"Num run: {args.runs}")

    er = EvaluationsRunner(          # The labels are the names of the columns of the binarized ground truth df
        ground_truth_path=bin_ground_truth_path,  # Give the binarized ground truth data
        gt_type=args.gt_type,
        fit_quality=args.quality,
        hyperparameters_type= args.hyp_type,
        save_evaluation_path=save_evaluation_path,
        save_evaluation_name=args.save_evaluations,
        num_run=args.runs,
        time_limit=args.time_limit,
        label_correlation = args.label_correlation,
        save_models_path=save_model_path,
    ) 

    er.run_evaluations()
    
# sbatch --job-name default run_job.slurm --gt_type default --save_evaluation default --save_models default --hyp_type lightgbmxt
# sbatch --job-name cosmic run_job.slurm --gt_type cosmic --save_evaluation cosmic --save_models cosmic --hyp_type lightgbmxt
# sbatch --job-name reference run_job.slurm --gt_type reference --save_evaluation reference --save_models reference --hyp_type lightgbmxt

# sbatch --job-name th n run_job.slurm --gt_type default --threshold n --save_evaluation default_n --save_models default_n --hyp_type lightgbxt