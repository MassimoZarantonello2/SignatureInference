import json
import os
import shutil
import threading
import pandas as pd
import tempfile
import argparse
import sys
sys.path.append('./')
from utils.MultiLabelPredictor import MultilabelPredictor
from utils.ModelsHyperparameters import ModelsHyperparameters
from utils.Log import LogClass

class EvaluationsRunner:
    def __init__(self, ground_truth_path, runs_path, data_path, save_evaluation_path, sampling_values, run_values, train_test_split_value, time_limit, problem_type, labels, save_models = False):
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
        self.save_models = False

        self.predictors = None
        self.evaluations = []

    def create_empty_json_file(self):
        # Create the structure of the json file
        run_dict = {}
        for run in self.run_values:
            run_index = 'run_'+run
            sample_dict = {}
            for sample in self.sampling_values:
                sample_index = 'sampling_'+sample
                sample_dict[sample_index] = {}
                run_dict[run_index] = sample_dict

        # Save the json file
        json.dump(run_dict, open(self.save_evaluation_path, 'w+'))

    def compute_evaluations_metrics(self, evaluation_df,sample):
        '''
        ### Input
        - evaluation_df: The dataset that will be used to train and test the model
        and returns the evaluation metrics for the model best trained on the sampled data and tested on the ground truth data
        ### Output
        - evaluation: A dictionary with the evaluation metrics of every signature for a specific run/sample \n
            "Signature Name": { \n
                    "accuracy":
                    "balanced_accuracy": 
                    "mcc":
                    "roc_auc": 
                    "f1": 
                    "precision":
                    "recall":
                    "best_model": }
        '''
        train_df = evaluation_df.sample(frac=self.train_test_split_value, random_state=42)
        test_df = evaluation_df.drop(train_df.index)
        lc = LogClass(sample)
        lc.log(f'For sample {sample} the train and test dataframes are created')
        try:
            predictor = MultilabelPredictor(labels=self.labels, problem_types=self.problem_type)
            predictor.fit(train_df, time_limit=self.time_limit)
            self.predictor = predictor
            lc.log(f'For sample {sample} the models are trained')
            evaluations = predictor.evaluate(test_df)
            lc.log(f'For sample {sample} the models are evaluated')
            for evaluation in evaluations:
                self.evaluations.append(evaluation)
                target_class = predictor.get_predictor(evaluation)
                evaluations[evaluation]['best_model'] = target_class.leaderboard(silent=True).iloc[0]['model']
            lc.log(f'For sample {sample} the best models are saved')
            return evaluations
        except Exception as e:
            lc.log(f'Error: {e}')
            print(f'Error: {e}')
            return None
    
    def threaded_evaluation(self, run, sample, output_dict, tissues, lock):
        '''
        ### Input
        - run: The run number
        - sample: The sampling value
        - output_dict: The dictionary where the evaluation metrics will be saved
        ### Output
        - None
        '''
        # Create the evaluation dataframe
        run_sample_df =  pd.read_csv(self.runs_path + run + self.data_path + sample + '.csv')
        # 2
        if tissues == 'feature':
            tissues_df = pd.read_csv(self.tissues_path).drop(columns=['Cohort'])
            run_sample_df = pd.merge(run_sample_df, tissues_df, on='Unnamed: 0')
        evaluation_df = pd.merge(run_sample_df, self.ground_truth_df, on='Unnamed: 0')
        evaluation_df.drop(columns=['Unnamed: 0'], inplace=True)
        
        evaluation = self.compute_evaluations_metrics(evaluation_df, sample)
        lc = LogClass(sample)
        with lock:
            lc = LogClass(sample)
            lc.log(f'Run {run} and sample {sample} lock aquired')
            lc.log(f'Evaluation: {evaluation}')
            lc.log('-----------------------------------')
            output_dict[sample] = evaluation

    def run_evaluations(self, tissues):
        if not os.path.exists(self.save_evaluation_path):
            self.create_empty_json_file()

        # Create the ground truth dataframe
        self.ground_truth_df = pd.read_csv(self.ground_truth_path)
        # 3
        if tissues == 'prediction':
            tissues_df = pd.read_csv(tissues_path).drop(columns=['Cohort'])
            self.ground_truth_df = pd.merge(self.ground_truth, tissues_df, on='Unnamed: 0')
        self.labels = self.ground_truth_df.columns[1:]

        for run in self.run_values:
            run_index = 'run_' + run
            signature_inference_thread = []
            all_evaluations_df = json.load(open(self.save_evaluation_path))
            lock = threading.Lock()
            output_dict = {}
            # Creo la directory 
            for sample in self.sampling_values:
                sample_index = 'sampling_' + sample
                if all_evaluations_df[run_index][sample_index] == {} or all_evaluations_df[run_index][sample_index] == None:
                    print(f'Running run {run} and sample {sample}')
                    lc = LogClass(sample)
                    lc.log(f'Starting run {run} and sample {sample}')
                    t = threading.Thread(target=self.threaded_evaluation, args=(run, sample, output_dict, tissues, lock))
                    signature_inference_thread.append(t)
                    t.start()
                else:
                    print(f'Skiping run {run} and sample {sample}')

            for t in signature_inference_thread:
                t.join()

            for key in output_dict:
                all_evaluations_df[run_index]['sampling_' + key] = output_dict[key]

            if signature_inference_thread.__len__() != 0:
                json.dump(all_evaluations_df, open(self.save_evaluation_path, 'w'))


            if self.save_models and os.path.exists('./AutogluonModels'):
                shutil.rmtree('./AutogluonModels')

            # if num_run is not None:
            #     if run >= num_run:
            #         break

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Esecuzione del modello di valutazione con parametri opzionali")

    bin_ground_truth_path = './simulations/ground_truth/bin_exposures.csv'
    runs_path = './simulations/data/run_'
    data_path = '/trinucleotides_counts_sampling_'
    save_evaluation_path = './results/locked_models_evaluations.json'
    tissues_path = './simulations/ground_truth/tumor_site.csv'
    sampling_values = ['1','0.9','0.8','0.7','0.6','0.5','0.4','0.3','0.2','0.15','0.1','0.05','0.04','0.03','0.02','0.01']
    run_values = [str(i) for i in range(1, 101)]
    train_test_split_value = 0.8
    time_limit = None
    num_run = None

    parser.add_argument('--save_path', type=str, default='models_evaluations', help='Path per salvare i risultati dell\'evaluation')
    parser.add_argument('--time_limit', type=int, default=None, help='Tempo limite per il training dei modelli')
    parser.add_argument('--num_run', type=str, default=None, help='Numero specifico di run da eseguire')

    args = parser.parse_args()

    save_evaluation_path = './results/'+args.save_path+'.json'
    time_limit = args.time_limit
    num_run = args.num_run

    print(f"Save path: {save_evaluation_path}")
    print(f"Time limit: {time_limit}")
    print(f"Num run: {num_run}")

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