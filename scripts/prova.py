from RayEvaluation import EvaluationSettings, MultiLabelEvaluator
import argparse
import os
import pandas as pd
import json
from utils.EvaluationsHelper import create_empty_json_file
from utils.HyperparametersModels import get_hyperparameters
from utils.Log import LogClass
import shutil
import ray

def multhithread_framework(run, sample, es, lc, ground_truth_df):       # Here the evaluation for a single sample are done and the output_dic is filled
    """
    ### Input
    - run: The run number
    - sample: The sampling value
    - output_dict: The dictionary where the evaluation metrics will be saved
    ### Output
    - None
    """
    run_sample_df = pd.read_csv(
        "./simulations/data/run_" + run + "/trinucleotides_counts_sampling_" + sample + ".csv"
    )  # Create the evaluation dataframe
    evaluation_df = pd.merge(
        run_sample_df, 
        ground_truth_df, 
        on="Unnamed: 0")
    
    evaluation_df.drop(columns=["Unnamed: 0"], inplace=True)
    
    mle = MultiLabelEvaluator(sample, evaluation_df=evaluation_df, lc=lc, evaluation_settings=es)  # Create the evaluator
    signature_model_info = mle.train_and_evaluate_framework(evaluation_df, sample, lc)     # Eva

    lc.log(f"Run {run} and sample {sample} evaluation done")
    lc.log("-----------------------------------")
    return signature_model_info


@ray.remote
def ray_multhithread_framework(run, sample, gt_type, es, ground_truth_df):
    lc = LogClass(f"logs/{gt_type}", sample)
    lc.log(f"Starting run {run} and sample {sample}")
    output = multhithread_framework(run, sample, es, lc, ground_truth_df)  # Modifica multhithread_framework per restituire il dizionario
    return sample, output
    
def run_evaluations(save_evaluation_path,
                    run_values,
                    sampling_values,
                    ground_truth_path,
                    hyperparameters_type,
                    quality,
                    gt_type,
                    save_models_path,
                    num_run):      # Checks which run and sample has already been evaluated and starts the sample missing or the next run
    if not os.path.exists(save_evaluation_path):
        create_empty_json_file(
            run_values, 
            sampling_values, 
            save_evaluation_path)
        
    ground_truth_df = pd.read_csv(
        ground_truth_path
    ) 

    labels = ground_truth_df.columns[1:]
    problem_type = ["binary"] * len(labels)
    es = EvaluationSettings(
        train_test_split_value=0.8,
        save_models_path=save_models_path,
        labels=labels,
        problem_type=problem_type,
        time_limit=None,
        hyperparameters=get_hyperparameters(hyperparameters_type),
        fit_quality=quality,
    )
    
    run_done = 0
    for run in run_values:
        run_index = "run_" + run
        all_evaluations_df = json.load(open(save_evaluation_path))     # Load the whole dataset into a dataframe
        tasks = []
        for sample in sampling_values:
            sample_index = "sampling_" + sample
            lc = LogClass(f"logs/{gt_type}", sample)
            if (all_evaluations_df[run_index][sample_index] == {} or all_evaluations_df[run_index][sample_index] == None):
                print(f"Running run {run} and sample {sample}")
                lc.log(f"Starting run {run} and sample {sample}")
                task = ray_multhithread_framework.remote(run, sample, gt_type, es, ground_truth_df)
                tasks.append(task)
            else:
                lc.log(
                    f"Run {run} and sample {sample} already evaluated, skipping"
                )
                print(f"Skiping run {run} and sample {sample}")
                
        results = ray.get(tasks)
            
        for sample, result in results:         # Update the evaluation dictionary with the new results
            all_evaluations_df[run_index]["sampling_" + sample] = result

        if tasks.__len__() != 0:
            json.dump(all_evaluations_df, open(save_evaluation_path, "w"))     # Rewrite the whole dataset into a json file TODO: try and save it in a more efficient way

        if save_models_path and os.path.exists(save_models_path):         # Delete the models folder
            shutil.rmtree(save_models_path)

        if num_run is not None:            # If the number of runs is set, the program will stop after the number of runs
            run_done += 1
            if run_done >= num_run:
                break

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
   
    if args.save_models is not None:
        save_model_path = "./models/" + args.save_models + "/"
    else:
        save_model_path = None
        

    print(f"Taking the ground truth from: {bin_ground_truth_path}")
    print(f"Saving the evaluation in: {save_evaluation_path}")
    print(f"Saving the models in: {save_model_path}")
    print(f"Using quality of: {args.quality}")
    print(f"Taking the hyperparameters from: {args.hyp_type}")
    print(f"Time limit: {args.time_limit}")
    print(f"Num run: {args.runs}")

    # er = EvaluationsRunner(          # The labels are the names of the columns of the binarized ground truth df
    #     ground_truth_path=bin_ground_truth_path,  # Give the binarized ground truth data
    #     gt_type=args.gt_type,
    #     runs_path=runs_path,
    #     data_path=data_path,
    #     fit_quality=args.quality,
    #     hyperparameters_type= args.hyp_type,
    #     save_evaluation_path=save_evaluation_path,
    #     sampling_values=sampling_values,
    #     run_values=run_values,
    #     num_run=args.runs,
    #     train_test_split_value=train_test_split_value,
    #     time_limit=args.time_limit,
    #     save_models_path=save_model_path,
    # ) 

    # er.run_evaluations()
    run_evaluations(save_evaluation_path=save_evaluation_path,
                    run_values=run_values,
                    sampling_values=sampling_values,
                    ground_truth_path=bin_ground_truth_path,
                    hyperparameters_type=args.hyp_type,
                    quality=args.quality,
                    gt_type=args.gt_type,
                    save_models_path=save_model_path,
                    num_run=args.runs,)
