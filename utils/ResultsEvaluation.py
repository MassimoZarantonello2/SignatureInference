import json

class ResultsEvaluation:
    
    def __init__(self, file_name):
        self.evaluations_df = json.load(open(f'../results/{file_name}'))
        self.run_labels, self.sampling_labels, self.signature_labels = self.get_runs_sample_labels()
        self.per_run_accuracy = self.get_runs_sample_metrics('accuracy')
        self.per_run_balanced_accuracy = self.get_runs_sample_metrics('balanced_accuracy')
        self.per_run_f1_score = self.get_runs_sample_metrics('f1')
        self.per_run_mcc = self.get_runs_sample_metrics('mcc')
        self.per_run_fit_time = self.get_runs_sample_siganture_fit_time()
        
    def get_runs_sample_labels(self):
        run_labels = []
        for run in list(self.evaluations_df.keys()):
            if self.evaluations_df[run]['sampling_0.01'] != {}:
                run_labels.append(run)  

        sampling_labels = self.evaluations_df[run_labels[0]].keys()
        sampling_labels = list(sampling_labels)
        signature_labels = []
        for i in range(len(self.evaluations_df[run_labels[0]][sampling_labels[0]])):
            signature_labels.append(self.evaluations_df[run_labels[0]][sampling_labels[0]][i]['signature'])

        return run_labels, sampling_labels, signature_labels
    
    def get_metrics(self, run, sample, signature, metrics):
        return self.evaluations_df[run][sample][self.signature_labels.index(signature)]['best_model_metrics'][metrics]
    
    def get_runs_sample_metrics(self, metrics, section = 'best_model_metrics'):
        per_run_metric = []
        for run in self.run_labels:
            per_sample_metric = []
            for sampling in self.sampling_labels:
                per_signature_metric = []
                for i in range(len(self.signature_labels)):
                    per_signature_metric.append(self.evaluations_df[run][sampling][i][section][metrics])# Save the accuracy of each signarure for one sample

                per_sample_metric.append(per_signature_metric)
            per_run_metric.append(per_sample_metric)
        return per_run_metric   
    
    def get_runs_sample_siganture_fit_time(self):
        per_run_fit_time = []
        for run in self.run_labels:
            per_sample_fit_time = []
            for sampling in self.sampling_labels:
                per_signature_fit_time = []
                for i in range(len(self.signature_labels)):
                    per_signature_fit_time.append(self.evaluations_df[run][sampling][i]['best_model_fit_time'])# Save the accuracy of each signarure for one sample

                per_sample_fit_time.append(per_signature_fit_time)
            per_run_fit_time.append(per_sample_fit_time)
        return per_run_fit_time