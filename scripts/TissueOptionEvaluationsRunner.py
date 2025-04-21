import json
import os
import shutil
import threading
import pandas as pd
import argparse
import sys
sys.path.append("./")

from utils.MultiLabelPredictor import MultilabelPredictor
from utils.HyperparametersModels import get_hyperparameters
from utils.Log import LogClass


class EvaluationsRunner:
    def __init__(
        self,
        ground_truth_path,
        gt_type,
        runs_path,
        data_path,
        save_evaluation_path,
        sampling_values,
        run_values,
        num_run,
        train_test_split_value,
        time_limit,
        problem_type,
        labels,
        save_models=False,
    ):
        self.data_path = data_path
        self.ground_truth = None
        self.gt_type = gt_type
        self.ground_truth_path = ground_truth_path
        self.labels = None
        self.problem_type = (
            problem_type if problem_type is None else ["binary"] * len(labels)
        )
        self.hyperparameters = get_hyperparameters()
        self.run_values = run_values
        self.num_run = num_run
        self.runs_path = runs_path
        self.sampling_values = sampling_values
        self.save_evaluation_path = save_evaluation_path
        self.save_models = False
        self.time_limit = time_limit
        self.train_test_split_value = train_test_split_value

    def create_empty_json_file(self):  # Create the structure of the json file
        run_dict = {}
        for run in self.run_values:
            run_index = "run_" + run
            sample_dict = {}
            for sample in self.sampling_values:
                sample_index = "sampling_" + sample
                sample_dict[sample_index] = {}
                run_dict[run_index] = sample_dict
        json.dump(run_dict, open(self.save_evaluation_path, "w+"))  # Save the json file

    def compute_evaluations_metrics(self, evaluation_df, sample, lc):
        """
        ### Input
        - evaluation_df: The dataset that will be used to train and test the model
        and returns the evaluation metrics for the model best trained on the sampled data and tested on the ground truth data
        ### Output
        - evaluation: A dictionary with the evaluation metrics of every signature for a specific run/sample \n
            "Signature Name": { \n
                    "accuracy":
                    "balanced_accuracy":
                    "balanced_accuracy":
                    "mcc":
                    "roc_auc":
                    "f1":
                    "roc_auc":
                    "f1":
                    "precision":
                    "recall":
                    "best_model":
        """
        train_df = evaluation_df.sample(
            frac=self.train_test_split_value, random_state=42
        )
        test_df = evaluation_df.drop(train_df.index)
        lc.log(f"For sample {sample} the train and test dataframes are created")
        try:
            predictor = MultilabelPredictor(
                labels=self.labels, problem_types=self.problem_type
            )
            predictor.fit(train_df, time_limit=self.time_limit, hyperparameters=self.hyperparameters, presets="medium_quality", num_cpus=16 )
            lc.log(f"For sample {sample} the models are trained")
            signature_model_info = self.save_results(predictor, test_df)
            lc.log(f"For sample {sample} the best models are saved")
            return signature_model_info

        except Exception as e:
            lc.log(f"Error: {e}")
            print(f"Error: {e}")
            return None


    def threaded_evaluation(self, run, sample, output_dict, tissues, lock, lc):
        """
        ### Input
        - run: The run number
        - sample: The sampling value
        - output_dict: The dictionary where the evaluation metrics will be saved
        ### Output
        - None
        """
        run_sample_df = pd.read_csv(
            self.runs_path + run + self.data_path + sample + ".csv"
        )  # Create the evaluation dataframe
        # 2
        if tissues == "feature":
            tissues_df = pd.read_csv(self.tissues_path).drop(columns=["Cohort"])
            run_sample_df = pd.merge(run_sample_df, tissues_df, on="Unnamed: 0")
        evaluation_df = pd.merge(run_sample_df, self.ground_truth_df, on="Unnamed: 0")
        evaluation_df.drop(columns=["Unnamed: 0"], inplace=True)

        signature_model_info = self.compute_evaluations_metrics(evaluation_df, sample, lc)

        with lock:
            lc.log(f"Run {run} and sample {sample} lock aquired")
            lc.log(f"Run {run} and sample {sample} evaluation done")
            lc.log(f"Run {run} and sample {sample} lock released")
            lc.log("-----------------------------------")
            output_dict[sample] = signature_model_info

    def run_evaluations(self, tissues):
        if not os.path.exists(self.save_evaluation_path):
            self.create_empty_json_file()
        self.ground_truth_df = pd.read_csv(
            self.ground_truth_path
        )  # Create the ground truth dataframe

        # 3
        if tissues == "prediction":
            tissues_df = pd.read_csv(tissues_path).drop(columns=["Cohort"])
            self.ground_truth_df = pd.merge(
                self.ground_truth, tissues_df, on="Unnamed: 0"
            )
        self.labels = self.ground_truth_df.columns[1:]
        run_done = 0
        for run in self.run_values:
            run_index = "run_" + run
            signature_inference_thread = []
            all_evaluations_df = json.load(open(self.save_evaluation_path))
            lock = threading.Lock()
            output_dict = {}

            for sample in self.sampling_values:
                sample_index = "sampling_" + sample
                if (
                    all_evaluations_df[run_index][sample_index] == {}
                    or all_evaluations_df[run_index][sample_index] == None
                ):
                    print(f"Running run {run} and sample {sample}")
                    lc = LogClass(f"logs/{self.gt_type}", sample)
                    lc.log(f"Starting run {run} and sample {sample}")
                    t = threading.Thread(
                        target=self.threaded_evaluation,
                        args=(run, sample, output_dict, tissues, lock, lc),
                    )
                    signature_inference_thread.append(t)
                    t.start()
                else:
                    print(f"Skiping run {run} and sample {sample}")

            for t in signature_inference_thread:
                t.join()

            for key in output_dict:
                all_evaluations_df[run_index]["sampling_" + key] = output_dict[key]

            if signature_inference_thread.__len__() != 0:
                json.dump(all_evaluations_df, open(self.save_evaluation_path, "w"))

            if self.save_models and os.path.exists("../AutogluonModels"):
                shutil.rmtree("../AutogluonModels")

            if self.num_run is not None:
                run_done += 1
                if run_done >= self.num_run:
                    break

    def save_results(self, predictor, test_df):
        evaluations = predictor.evaluate(test_df)
        results = []
        for signature in evaluations:
            model_predictor = predictor.get_predictor(signature)
            metrics = evaluations[signature]
            info = model_predictor.info()
            model_info = info["model_info"]

            best_model_name = info["best_model"]
            best_model_info = model_info[best_model_name]

            ensemble_model_names = best_model_info.get("features", [])

            ensemble_info = [
                {
                    "model_name": model,
                    "val_score": model_info[model].get("val_score"),
                    "fit_time": model_info[model].get("fit_time"),
                }
                for model in ensemble_model_names
            ]

            result = {
                "signature": signature,
                "best_model": best_model_name,
                "best_model_val_score": best_model_info.get("val_score"),
                "best_model_metrics": metrics,
                "best_model_fit_time": best_model_info.get("fit_time"),
                "ensemble_models": ensemble_model_names,
                "ensemble_info": ensemble_info,
            }
            results.append(result)
        return results
    
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
    time_limit = args.time_limit
    num_run = args.num_run

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

    er = EvaluationsRunner(
        bin_ground_truth_path,  # Give the binarized ground truth data
        args.ground_truth_type,
        runs_path,
        data_path,
        save_evaluation_path,
        sampling_values,
        run_values,
        num_run,
        train_test_split_value,
        time_limit,
        problem_type=None,
        labels=None,
    )  # The labels are the names of the columns of the binarized ground truth df

    er.run_evaluations(tissues=None)