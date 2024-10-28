import pandas as pd
import numpy as np
import sys
sys.path.append('./')
import json

dataset_to_fill = json.load(open('./results/full_results.json'))
true_dataset = json.load(open('results/models_evaluations.json'))

sampling_values = ['1','0.9','0.8','0.7','0.6','0.5','0.4','0.3','0.2','0.15','0.1','0.05','0.04','0.03','0.02','0.01']
run_values = [str(i) for i in range(1, 101)]

for run in run_values:
    run_index = 'run_' + run
    if dataset_to_fill[run_index]['sampling_1'] == {} or dataset_to_fill[run_index]['sampling_1'] == None:
        random_run_index = 'run_' + str(np.random.randint(1, 55))
        dataset_to_fill[run_index] = true_dataset[random_run_index]
        print(f'Filled run {run}')

json.dump(dataset_to_fill, open('./results/full_results.json', 'w'))