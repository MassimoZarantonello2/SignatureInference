import sys
sys.path.append("./")
from utils.EvaluationsHelper import format_model_result
from utils.MultiLabelPredictor import MultilabelPredictor

class EvaluationSettings:
    def __init__(self, train_test_split_value, save_models_path, labels, problem_type, time_limit, hyperparameters, fit_quality):
        self.train_test_split_value = train_test_split_value
        self.save_models_path = save_models_path
        self.labels = labels
        self.problem_type = problem_type
        self.time_limit = time_limit
        self.hyperparameters = hyperparameters
        self.fit_quality = fit_quality
        
    def get_train_test_split_value(self):
        return self.train_test_split_value
    def get_save_models_path(self):
        return self.save_models_path
    def get_labels(self):
        return self.labels
    def get_problem_type(self):
        return self.problem_type
    def get_time_limit(self):
        return self.time_limit
    def get_hyperparameters(self):
        return self.hyperparameters
    def get_fit_quality(self):  
        return self.fit_quality 

class MultiLabelEvaluator:
    def __init__(self, sample, evaluation_df, lc, evaluation_settings):
        self.sample = sample
        self.evaluation_df = evaluation_df
        self.lc = lc
        self.settings = evaluation_settings
         
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
            frac=self.settings.get_train_test_split_value(), 
            random_state=42
        )
        test_df = evaluation_df.drop(train_df.index)
        lc.log(f"For sample {sample} the train and test dataframes are created")
        try:
            predictor = MultilabelPredictor(         #Creates the MultiLabel predictor
                path=self.settings.get_save_models_path(),
                labels=self.settings.get_labels(),
                problem_types=self.settings.get_problem_type(),
                verbosity=2,
            )
            predictor.fit(
                train_df, 
                time_limit=self.settings.get_time_limit(), 
                hyperparameters=self.settings.get_hyperparameters(), 
                presets=self.settings.get_fit_quality(), 
            )            
            lc.log(f"For sample {sample} the models are trained")
            signature_model_info = format_model_result(predictor, test_df)
            lc.log(f"For sample {sample} the best models are saved")
            return signature_model_info

        except Exception as e:
            lc.log(f"Error: {e}")
            print(f"Error: {e}")
            return {}