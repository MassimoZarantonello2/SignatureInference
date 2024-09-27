import json
import os
import threading
import pandas as pd
import tempfile
import sys
sys.path.append('./')
from utils.MultiLabelPredictor import MultilabelPredictor
from utils.ModelsHyperparameters import ModelsHyperparameters

class EvaluationsRunner:
    def __init__(self, ground_truth_path, runs_path, data_path, save_evaluation_path, sampling_values, run_values, train_test_split_value, time_limit, problem_type, labels):
        self.ground_truth_path = ground_truth_path
        self.ground_truth = None
        self.runs_path = runs_path
        self.data_path = data_path
        self.save_evaluation_path = save_evaluation_path
        self.sampling_values = sampling_values
        self.run_values = run_values
        self.train_test_split_value = train_test_split_value
        self.time_limit = time_limit
        self.problem_type = problem_type if problem_type is None else ['binary'] * len(labels)
        self.labels = None
        self.lock = threading.Lock()  # Create a lock object

    def create_empty_json_file(self):
        run_dict = {}
        for run in self.run_values:
            run_index = 'run_'+run
            sample_dict = {}
            for sample in self.sampling_values:
                sample_index = 'sampling_'+sample
                sample_dict[sample_index] = {}
                run_dict[run_index] = sample_dict

        # Ensure thread-safety during file creation
        with self.lock:
            json.dump(run_dict, open(self.save_evaluation_path, 'w+'))

    def threaded_evaluation(self, run, sample, output_dict, tissues):
        run_sample_df = pd.read_csv(self.runs_path + run + self.data_path + sample + '.csv')
        if tissues == 'feature':
            tissues_df = pd.read_csv(self.tissues_path).drop(columns=['Cohort'])
            run_sample_df = pd.merge(run_sample_df, tissues_df, on='Unnamed: 0')
        evaluation_df = pd.merge(run_sample_df, self.ground_truth_df, on='Unnamed: 0')
        evaluation_df.drop(columns=['Unnamed: 0'], inplace=True)

        evaluation = self.compute_evaluations_metrics(evaluation_df)
        output_dict[sample] = evaluation

    def run_evaluations(self, tissues):
        if not os.path.exists(self.save_evaluation_path):
            self.create_empty_json_file()

        self.ground_truth_df = pd.read_csv(self.ground_truth_path)
        if tissues == 'prediction':
            tissues_df = pd.read_csv(tissues_path).drop(columns=['Cohort'])
            self.ground_truth_df = pd.merge(self.ground_truth, tissues_df, on='Unnamed: 0')
        self.labels = self.ground_truth_df.columns[1:]

        for run in self.run_values:
            run_index = 'run_' + run
            signature_inference_thread = []
            output_dict = {}

            # Lock when reading from the file
            with self.lock:
                all_evaluations_df = json.load(open(self.save_evaluation_path))

            for sample in self.sampling_values:
                sample_index = 'sampling_' + sample
                if all_evaluations_df[run_index][sample_index] == {}:
                    print(f'Running run {run} and sample {sample}')
                    t = threading.Thread(target=self.threaded_evaluation, args=(run, sample, output_dict, tissues))
                    signature_inference_thread.append(t)
                    t.start()
                else:
                    print(f'Skiping run {run} and sample {sample}')

            for t in signature_inference_thread:
                t.join()

            # Update the JSON file safely
            with self.lock:
                for key in output_dict:
                    all_evaluations_df[run_index]['sampling_' + key] = output_dict[key]
                
                if signature_inference_thread:
                    json.dump(all_evaluations_df, open(self.save_evaluation_path, 'w'))

                # This is to stop the code after a run
                if(run == '10'):
                    break


if __name__ == "__main__":
    bin_ground_truth_path = './simulations/ground_truth/bin_exposures.csv'
    runs_path = './simulations/data/run_'
    data_path = '/trinucleotides_counts_sampling_'
    save_evaluation_path = './results/models_evaluations.json'
    tissues_path = './simulations/ground_truth/tumor_site.csv'
    sampling_values = ['1','0.9','0.8','0.7','0.6','0.5','0.4','0.3','0.2','0.15','0.1','0.05','0.04','0.03','0.02','0.01']
    run_values = [str(i) for i in range(1, 101)]
    train_test_split_value = 0.8
    time_limit = None

    #+------------------------(1)Normal run of models-------------------------   
    #|TRAIN                          |  TEST
    #|every sample mutation count    |  if a mutation is present in the sample
    # Sample_run: Normal             |  GT: Normal
    #+-------------------(2)Tissues as a train feature------------------------
    #|TRAIN                          | TEST
    #|every sample mutation count    |  if a mutation is present in the sample
    #|with the tissues               |  WITHOUT the tissues    
    # Sample_run: With tissues       |  GT: Normal
    #+-------------------(3)Tissues as a test feature--------------------------
    #|TRAIN                          |  TEST
    #|every sample mutation count    |  if a mutation is present in the sample
    #|WITHOUT the tissues            |  with the tissues
    # Sample_run: Normal             |  GT: Add the tissues -> add tissues label
    #+-------------------------------+---------------------------------------  

    er = EvaluationsRunner(bin_ground_truth_path,        # Give the binarized ground truth data
                           runs_path, 
                           data_path, 
                           save_evaluation_path, 
                           sampling_values, 
                           run_values, 
                           train_test_split_value, 
                           time_limit, 
                           problem_type = None,
                           labels = None)       # The labels are the names of the columns of the binarized ground truth df
    
    er.run_evaluations(tissues = None)
