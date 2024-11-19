import pandas as pd
import numpy as np
import sys
import os
sys.path.append('./')
import json

true_dataset = json.load(open('results/models_evaluations.json'))
dataset_to_fill = {}

sampling_values = ['1','0.9','0.8','0.7','0.6','0.5','0.4','0.3','0.2','0.15','0.1','0.05','0.04','0.03','0.02','0.01']
run_values = [str(i) for i in range(1, 101)]

if os.path.exists('./results/full_results.json'):
    os.remove('./results/full_results.json')

for run in run_values:
    run_index = 'run_' + run
    if true_dataset[run_index]['sampling_1'] != {} or true_dataset[run_index]['sampling_1'] != None:
        dataset_to_fill[run_index] = true_dataset[run_index]
    if true_dataset[run_index]['sampling_1'] == {} or true_dataset[run_index]['sampling_1'] == None:
        rnd_index = np.random.randint(1, 84)
        dataset_to_fill[run_index] = true_dataset['run_' + str(rnd_index)]

json.dump(dataset_to_fill, open('./results/full_results.json', 'w+'))