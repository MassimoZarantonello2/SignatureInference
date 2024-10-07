import ijson

read_path = 'results/models_evaluations.json'
sampling_values = ['1','0.9','0.8','0.7','0.6','0.5','0.4','0.3','0.2','0.15','0.1','0.05','0.04','0.03','0.02','0.01']
run_values = [str(i) for i in range(1, 101)]

with open(read_path, 'r') as f:
    for run in run_values:
        run_index = 'run_' + run
        for sample in sampling_values:
            sample_index = 'sampling_' + sample
            
            x = ijson.items(f, run_index + '.' + sample_index)
            for item in x:
                print(item)
            break