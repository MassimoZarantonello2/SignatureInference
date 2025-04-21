import json
import os
import shutil
import threading
import pandas as pd
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
        gt_type,
        runs_path,
        data_path,
        fit_quality,
        hyperparameters_type,
        save_evaluation_path,
        sampling_values,
        run_values,
        num_run,
        train_test_split_value,
        time_limit,
        save_models_path,
    ):
        self.data_path = data_path
        self.ground_truth = None
        self.gt_type = gt_type
        self.ground_truth_path = ground_truth_path
        self.labels = None
        self.problem_type = None
        self.fit_quality = fit_quality
        self.hyperparameters = get_hyperparameters(hyperparameters_type)
        self.run_values = run_values
        self.num_run = num_run
        self.runs_path = runs_path
        self.sampling_values = sampling_values
        self.save_evaluation_path = save_evaluation_path
        self.save_models = False
        self.time_limit = time_limit
        self.train_test_split_value = train_test_split_value
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
                path=self.save_models_path,
                labels=self.labels,
                problem_types=self.problem_type,
                verbosity=0,
            )
            predictor.fit(
                train_df, 
                time_limit=self.time_limit, 
                hyperparameters=self.hyperparameters, 
                presets=self.fit_quality, 
                fit_strategy="parallel" )
            
            lc.log(f"For sample {sample} the models are trained")
            signature_model_info = format_model_result(predictor, test_df)
            lc.log(f"For sample {sample} the best models are saved")
            return signature_model_info

        except Exception as e:
            lc.log(f"Error: {e}")
            print(f"Error: {e}")
            return None


    def multhithread_framework(self, run, sample, lock, lc):       # Here the evaluation for a single sample are done and the output_dic is filled
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

        with lock:
            lc.log(f"Run {run} and sample {sample} lock aquired")
            lc.log(f"Run {run} and sample {sample} evaluation done")
            if signature_model_info is not None:
                update_json_file(self.save_evaluation_path, run, sample, signature_model_info)  # Update the json file with the evaluations
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
        self.problem_type = ["binary"] * len(self.labels)
        
        run_done = 0
        for run in self.run_values:
            run_index = "run_" + run
            signature_inference_thread = []
            all_evaluations_df = json.load(open(self.save_evaluation_path))     # Load the whole dataset into a dataframe
            lock = threading.Lock()

            for sample in self.sampling_values:
                sample_index = "sampling_" + sample
                lc = LogClass(f"logs/{self.gt_type}", sample)
                if (all_evaluations_df[run_index][sample_index] == {} or all_evaluations_df[run_index][sample_index] == None):
                    print(f"Running run {run} and sample {sample}")
                    lc.log(f"Starting run {run} and sample {sample}")
                    t = threading.Thread(
                        target=self.multhithread_framework,
                        args=(run, sample, lock, lc),
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

            if self.save_models_path and os.path.exists(self.save_models_path):         # Delete the models folder
                shutil.rmtree(self.save_models_path)

            if self.num_run is not None:            # If the number of runs is set, the program will stop after the number of runs
                run_done += 1
                if run_done >= self.num_run:
                    break
