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
        "--ground_truth_type",
        type=str,
        default='default',
        help="Path del ground truth binarizzato",
    )
    parser.add_argument(
        "--time_limit",
        type=int,
        default=None,
        help="Tempo limite per il training dei modelli",
    )
    parser.add_argument(
        "--num_run", type=int, default=None, help="Numero specifico di run da eseguire"
    )

    args = parser.parse_args()

    if args.ground_truth_type == "default":
        bin_ground_truth_path = "./simulations/ground_truth/bin_exposures.csv"
    else:
        bin_ground_truth_path = "./simulations/ground_truth_" + args.ground_truth_type + "/bin_exposures.csv"
    save_evaluation_path = "./results/" + args.ground_truth_type + "_evaluations.json"
    save_model_path = "./models/" + args.ground_truth_type

    print(f"Ground truth path: {bin_ground_truth_path}")
    print(f"Save path: {save_evaluation_path}")
    print(f"Time limit: {time_limit}")
    print(f"Num run: {num_run}")

    # +------------------------(1)Normal run of models-------------------------
    # |TRAIN                          |  TEST
    # |every sample mutation count    |  if a mutation is present in the sample
    # |Sample_run: Normal             |  GT: Normal
    # +-------------------(2)Tissues as a train feature------------------------
    # |TRAIN                          | TEST
    # |every sample mutation count    |  if a mutation is present in the sample
    # |with the tissues               |  WITHOUT the tissues
    # |Sample_run: With tissues       |  GT: Normal
    # +-------------------(3)Tissues as a test feature--------------------------
    # |TRAIN                          |  TEST
    # |every sample mutation count    |  if a mutation is present in the sample
    # |WITHOUT the tissues            |  with the tissues
    # |Sample_run: Normal             |  GT: Add the tissues -> add tissues label
    # +-------------------------------+---------------------------------------

    er = EvaluationsRunner(          # The labels are the names of the columns of the binarized ground truth df
        ground_truth_path=bin_ground_truth_path,  # Give the binarized ground truth data
        gt_type=args.ground_truth_type,
        runs_path=runs_path,
        data_path=data_path,
        save_evaluation_path=save_evaluation_path,
        sampling_values=sampling_values,
        run_values=run_values,
        num_run=args.num_run,
        train_test_split_value=train_test_split_value,
        time_limit=args.time_limit,
        save_models_path=save_model_path,
    ) 

    er.run_evaluations()