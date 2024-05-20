import pandas as pd
import numpy as np
from utils.MultiLabelPredictor import MultilabelPredictor
import csv
import os
import json
import time
import threading
import logging

def create_empty_json_file():
# Create the structure of the json file
    run_dict = {}
    for run in run_values:
        run_index = 'run_'+run
        sample_dict = {}
        for sample in sampling_values:
            sample_index = 'sampling_'+sample
            sample_dict[sample_index] = {}
            run_dict[run_index] = sample_dict
    # Save the json file
    json.dump(run_dict, open(save_evaluation_path, 'w+'))

def compute_evaluations_metrics(key, run_number, sampling_number, output_dict):
    run_index = 'run_'+run_number
    sample_index = 'sampling_'+sampling_number
    json_df = json.load(open(save_evaluation_path))
    if json_df[run_index][sample_index] == {}:
        return None
    else:
        # Load the dataset for traning based on the sampling size
        sampled_dataset = pd.read_csv(runs_path + run + data_path + sample + '.csv')
        
        # Merge the sampled dataset with the ground truth dataset and drop the column
        run_dataset = pd.merge(sampled_dataset, bin_gt_df, on='Unnamed: 0')
        run_dataset.drop(columns=['Unnamed: 0'], inplace=True)

        # Split the dataset into training and testing
        train_df = run_dataset.sample(frac = train_test_split_value, random_state=42)
        test_df = run_dataset.drop(train_df.index)
        # Create the model
        predictor = MultilabelPredictor(labels=labels, problem_types=problem_type)
        predictor.fit(train_df, time_limit=time_limit)

        # Evaluate the model on the test set, and for every signature save the evaluation metrics in a dictionary
        evaluation = predictor.evaluate(test_df)
        output_dict[key] = evaluation
        return evaluation

if __name__ == '__main__':
    bin_ground_truth_path = './simulations/ground_truth/bin_exposures.csv'
    runs_path = './simulations/data/run_'
    data_path = '/trinucleotides_counts_sampling_'
    save_evaluation_path = './evaluations.json'

    # Load the binarized ground truth data
    bin_gt_df = pd.read_csv(bin_ground_truth_path)

    # The training data is sampled based on these values, each sampling dataset is composed by a fraction of the total data
    sampling_values = ['1','0.9','0.8','0.7','0.6','0.5','0.4','0.3','0.2','0.15','0.1','0.05','0.04','0.03','0.02','0.01']
    run_values = [str(i) for i in range(1, 101)]
    train_test_split_value = 0.8

    if not os.path.exists(save_evaluation_path):
        create_empty_json_file()

    # Get the leabels which are the names of the columns or the signature names and other parameters for tuning the model
    labels = bin_gt_df.columns[1:]
    problem_type = ['binary'] * len(labels)
    time_limit = 5
    output_dict = {}

    signature_inference_threads = []
    for run in run_values:
        for sample in sampling_values:
            t = threading.Thread(target=compute_evaluations_metrics, args=(sample, run, sample,output_dict))
            signature_inference_threads.append(t)
            t.start()

        for t in signature_inference_threads:
            t.join()
        print(output_dict)