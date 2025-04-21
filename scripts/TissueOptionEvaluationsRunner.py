import json
import os
import shutil
import threading
import pandas as pd
import argparse
import sys
sys.path.append("./")

from utils.MultiLabelPredictor import MultilabelPredictor
from utils.ModelsHyperparameters import get_hyperparameters
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