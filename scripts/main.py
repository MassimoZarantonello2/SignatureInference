from EvaluationsRunner import EvaluationsRunner
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Esecuzione del modello di valutazione con parametri opzionali"
    )
    bin_ground_truth_path = "./simulations/ground_truth/bin_exposures.csv"
    runs_path = "./simulations/data/run_"
    data_path = "/trinucleotides_counts_sampling_"
    save_evaluation_path = "./results/locked_models_evaluations.json"
    tissues_path = "./simulations/ground_truth/tumor_site.csv"
    sampling_values = [
        "1",
        "0.9",
        "0.8",
        "0.7",
        "0.6",
        "0.5",
        "0.4",
        "0.3",
        "0.2",
        "0.15",
        "0.1",
        "0.05",
        "0.04",
        "0.03",
        "0.02",
        "0.01",
    ]
    run_values = [str(i) for i in range(1, 101)]
    train_test_split_value = 0.8
    time_limit = None
    num_run = None
    
    parser.add_argument(
        "--gt_type",
        type=str,
        default="default",
        help="Path del ground truth binarizzato",
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
        "--runs", type=int, default=None, help="Numero specifico di run da eseguire"
    )

    args = parser.parse_args()

    if args.gt_type == "default":
        bin_ground_truth_path = "./simulations/ground_truth/bin_exposures.csv"
    else:
        bin_ground_truth_path = "./simulations/ground_truth_" + args.gt_type + "/bin_exposures.csv"
        
    if args.save_evaluations is None:
        save_evaluation_path = "./results/" + args.gt_type + "_evaluations.json"
    else:
        save_evaluation_path = "./results/" + args.save_evaluations + "_evaluations.json"
   
    if args.save_models is None:
        save_model_path = "./models/" + args.gt_type
    else:
        save_model_path = "./models/" + args.save_models + "/"
        

    print(f"Taking the ground truth from: {bin_ground_truth_path}")
    print(f"Saving the evaluation in: {save_evaluation_path}")
    print(f"Saving the models in: {save_model_path}")
    print(f"Using quality of: {args.quality}")
    print(f"Taking the hyperparameters from: {args.hyp_type}")
    print(f"Time limit: {args.time_limit}")
    print(f"Num run: {num_run}")

    er = EvaluationsRunner(          # The labels are the names of the columns of the binarized ground truth df
        ground_truth_path=bin_ground_truth_path,  # Give the binarized ground truth data
        gt_type=args.gt_type,
        runs_path=runs_path,
        data_path=data_path,
        fit_quality=args.quality,
        hyperparameters_type= args.hyp_type,
        save_evaluation_path=save_evaluation_path,
        sampling_values=sampling_values,
        run_values=run_values,
        num_run=args.runs,
        train_test_split_value=train_test_split_value,
        time_limit=args.time_limit,
        save_models_path=save_model_path,
    ) 

    er.run_evaluations()