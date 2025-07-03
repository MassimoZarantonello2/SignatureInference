import json
import os
import shutil
import threading
import pandas as pd
import numpy as np
import sys
sys.path.append("./")

from utils.MultiLabelPredictor import MultilabelPredictor
from utils.HyperparametersModels import get_hyperparameters
from utils.EvaluationsHelper import format_model_result, create_empty_json_file, update_json_file
from utils.Log import LogClass


class EvaluationsRunner:
    def __init__(
        self,
        ground_truth_path,
        input_problem_type,
        fit_quality,
        hyperparameters_type,
        save_evaluation_path,
        save_evaluation_name,
        num_run,
        time_limit,
        label_correlation,
        save_models_path,
    ):
        self.data_path = "/trinucleotides_counts_sampling_"
        self.ground_truth_path = ground_truth_path
        self.input_problem_type = input_problem_type
        self.labels = None
        self.problem_type = None
        self.fit_quality = fit_quality
        self.hyperparameters = get_hyperparameters(hyperparameters_type)
        self.run_values = [str(i) for i in range(1, 101)]
        self.num_run = num_run
        self.runs_path = "./simulations/data/run_"
        self.sampling_values = [
        "1",       
    ]
        self.save_evaluation_path = save_evaluation_path
        self.save_evaluation_name = save_evaluation_name
        self.save_models = False
        self.time_limit = time_limit
        self.label_correlation = label_correlation
        self.train_test_split_value = 0.8
        self.save_models_path = save_models_path

    def train_and_evaluate_framework(self, evaluation_df, sample, lc):
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
            frac=self.train_test_split_value, 
            random_state=42
        )
        test_df = evaluation_df.drop(train_df.index)
        lc.log(f"For sample {sample} the train and test dataframes are created")
        try:
            predictor = MultilabelPredictor(         #Creates the MultiLabel predictor
                path=os.path.join(self.save_models_path, f"Predictor-{sample}"),                
                labels=self.labels,
                problem_types=self.problem_type,
                consider_labels_correlation=self.label_correlation,
            )
            predictor.fit(
                train_df, 
                time_limit=self.time_limit, 
                hyperparameters=self.hyperparameters, 
                presets=self.fit_quality,
            )            
            lc.log(f"For sample {sample} the models are trained")
            signature_model_info = format_model_result(predictor, test_df)
            lc.log(f"For sample {sample} the best models are saved")
            return signature_model_info

        except Exception as e:
            lc.log(f"Error: {e}")
            return None


    def multhithread_framework(self, run, sample, output_dict, lock, lc):       # Here the evaluation for a single sample are done and the output_dic is filled
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
        evaluation_df = pd.merge(
            run_sample_df, 
            self.ground_truth_df, 
            on="Unnamed: 0")
        
        evaluation_df.drop(columns=["Unnamed: 0"], inplace=True)
        signature_model_info = self.train_and_evaluate_framework(evaluation_df, sample, lc)     # Eva
        lc.log(f"Run {run} and sample {sample} evaluation done")
        with lock:
            lc.log(f"Run {run} and sample {sample} lock aquired")
            output_dict[sample] = signature_model_info
            lc.log
            lc.log(f"Run {run} and sample {sample} lock released")
        lc.log("-----------------------------------")
        
    def run_evaluations(self):      # Checks which run and sample has already been evaluated and starts the sample missing or the next run
        if not os.path.exists(self.save_evaluation_path):
            create_empty_json_file(
                self.run_values, 
                self.sampling_values, 
                self.save_evaluation_path)
            
        self.ground_truth_df = pd.read_csv(
            self.ground_truth_path
        )

        self.labels = self.ground_truth_df.columns[1:]
        if self.input_problem_type == "binary":
            self.problem_type = ["binary"] * len(self.labels)

        
        run_done = 0
        for run in self.run_values:
            run_index = "run_" + run
            signature_inference_thread = []
            all_evaluations_df = json.load(open(self.save_evaluation_path))     # Load the whole dataset into a dataframe
            lock = threading.Lock()
            output_dict = {}
            
            for sample in self.sampling_values:
                sample_index = "sampling_" + sample
                lc = LogClass(f"logs/{self.save_evaluation_name}", sample)
                if (all_evaluations_df[run_index][sample_index] == {} or all_evaluations_df[run_index][sample_index] == None):
                    print(f"Running run {run} and sample {sample}")
                    lc.log(f"Starting run {run} and sample {sample}")
                    t = threading.Thread(
                        target=self.multhithread_framework,
                        args=(run, sample, output_dict, lock, lc),
                    )
                    signature_inference_thread.append(t)
                    t.start()
                else:
                    lc.log(
                        f"Run {run} and sample {sample} already evaluated, skipping"
                    )
                    print(f"Skiping run {run} and sample {sample}")

            for t in signature_inference_thread:        # Wait for all the threads relative to each sample in a run to finish
                t.join()
                
            for key in output_dict:         # Update the evaluation dictionary with the new results
                all_evaluations_df[run_index]["sampling_" + key] = output_dict[key]

            if signature_inference_thread.__len__() != 0:
                json.dump(all_evaluations_df, open(self.save_evaluation_path, "w"))     # Rewrite the whole dataset into a json file TODO: try and save it in a more efficient way

            if self.save_models_path and os.path.exists(self.save_models_path):         # Delete the models folder
                pass
                #shutil.rmtree(self.save_models_path)

            if self.num_run is not None:            # If the number of runs is set, the program will stop after the number of runs
                run_done += 1
                if run_done >= self.num_run:
                    break
