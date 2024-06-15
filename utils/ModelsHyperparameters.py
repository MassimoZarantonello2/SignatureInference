class ModelsHyperparameters:
    hyperparameters = {
                    'NN_TORCH': {},
                    'GBM': [
                        {'extra_trees': True, 'ag_args': {'name_suffix': 'XT'}},
                        {},
                        'GBMLarge',
                    ],
                    'CAT': {},
                    'XGB': {},
                    'FASTAI': {},
                    'RF': [
                        {'criterion': 'gini', 'ag_args': {'name_suffix': 'Gini', 'problem_types': ['binary', 'multiclass']}},
                        {'criterion': 'entropy', 'ag_args': {'name_suffix': 'Entr', 'problem_types': ['binary', 'multiclass']}},
                        {'criterion': 'squared_error', 'ag_args': {'name_suffix': 'MSE', 'problem_types': ['regression']}},
                    ],
                    'XT': [
                        {'criterion': 'gini', 'ag_args': {'name_suffix': 'Gini', 'problem_types': ['binary', 'multiclass']}},
                        {'criterion': 'entropy', 'ag_args': {'name_suffix': 'Entr', 'problem_types': ['binary', 'multiclass']}},
                        {'criterion': 'squared_error', 'ag_args': {'name_suffix': 'MSE', 'problem_types': ['regression']}},
                    ],
                    'KNN': [
                        {'weights': 'uniform', 'ag_args': {'name_suffix': 'Unif'}, 'n_jobs': 8},
                        {'weights': 'distance', 'ag_args': {'name_suffix': 'Dist'}, 'n_jobs': 8},
                    ],
                }
    
    def __init__(self):
        pass

    def get_hyperparameters(self):
        return self.hyperparameters
