import pandas as pd
import sys
sys.path.append('./')
from utils.MultiLabelPredictor import MultilabelPredictor
import json
import time
import threading
import os

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

def compute_evaluations_metrics(key, output_dict):
    # Load the dataset for traning based on the sampling size
    sampled_dataset = pd.read_csv(runs_path + run + data_path + sample + '.csv')
    tissues_dataset = pd.read_csv(tissues_path)
    
    # Merge the sampled dataset with the ground truth dataset and drop the column
    run_dataset = pd.merge(sampled_dataset, bin_gt_df, on='Unnamed: 0')
    run_dataset = pd.merge(run_dataset, tissues_dataset, on='Unnamed: 0')
    run_dataset.drop(columns=['Unnamed: 0'], inplace=True)
    run_dataset.drop(columns=['Cohort'], inplace=True)

    # Split the dataset into training and testing
    train_df = run_dataset.sample(frac = train_test_split_value, random_state=42)
    test_df = run_dataset.drop(train_df.index)
    # Create the model
    predictor = MultilabelPredictor(labels=labels, problem_types=problem_type)
    predictor.fit(train_df, time_limit=time_limit)

    # Evaluate the model on the test set, and for every signature save the evaluation metrics in a dictionary
    evaluation = predictor.evaluate(test_df)
    output_dict[key] = evaluation
    return output_dict 

if __name__ == '__main__':
    bin_ground_truth_path = './simulations/ground_truth/bin_exposures.csv'
    runs_path = './simulations/data/run_'
    data_path = '/trinucleotides_counts_sampling_'
    save_evaluation_path = './results/with_tissues_evaluations.json'
    tissues_path = './simulations/ground_truth/tumor_site.csv'

    # Load the binarized ground truth data
    bin_gt_df = pd.read_csv(bin_ground_truth_path)

    # The training data is sampled based on these values, each sampling dataset is composed by a fraction of the total data
    # NOTE: this script will generate a thread for every sampling value
    sampling_values = ['1','0.9','0.8','0.7','0.6','0.5','0.4','0.3','0.2','0.15','0.1','0.05','0.04','0.03','0.02','0.01']
    run_values = [str(i) for i in range(1, 101)]
    train_test_split_value = 0.8

    # Get the leabels which are the names of the columns or the signature names and other parameters for tuning the model
    labels = bin_gt_df.columns[1:]
    problem_type = ['binary'] * len(labels)
    time_limit = 5

    if not os.path.exists(save_evaluation_path):
        create_empty_json_file()

    for run in run_values:
        run_index = 'run_'+run
        signature_inference_threads = []
        json_df = json.load(open(save_evaluation_path))
        output_dict = {}

        for sample in sampling_values:
            sample_index = 'sampling_'+sample
            # If it already exists, skip the computation
            if json_df[run_index][sample_index] == {}:
                # Else generate a thread to compute the specific sample
                t = threading.Thread(target=compute_evaluations_metrics, args=(sample, output_dict))
                signature_inference_threads.append(t)
                t.start()

        for t in signature_inference_threads:
            t.join()

        # After all the threads stopped save the results contained inside output_dic in the json file
        for key in output_dict:
            json_df['run_'+run]['sampling_'+key] = output_dict[key]

        if signature_inference_threads.__len__() != 0:
            json.dump(json_df, open(save_evaluation_path, 'w'))

        break
