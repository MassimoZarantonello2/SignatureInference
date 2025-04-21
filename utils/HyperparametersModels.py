def get_hyperparameters(type):
    if type.lower() == "tree":
        print("Using Hyperparameters for Tree Models")
        hyperparameters = {
            "GBM": [
                {"extra_trees": True, "ag_args": {"name_suffix": "XT"}},
                {},
                "GBMLarge",
            ],
            "RF": [
                {
                    "criterion": "gini",
                    "ag_args": {
                        "name_suffix": "Gini",
                        "problem_types": ["binary", "multiclass"],
                    },
                },
                {
                    "criterion": "entropy",
                    "ag_args": {
                        "name_suffix": "Entr",
                        "problem_types": ["binary", "multiclass"],
                    },
                },
                {
                    "criterion": "squared_error",
                    "ag_args": {"name_suffix": "MSE", "problem_types": ["regression"]},
                },
            ],
            "XT": [
                {
                    "criterion": "gini",
                    "ag_args": {
                        "name_suffix": "Gini",
                        "problem_types": ["binary", "multiclass"],
                    },
                },
                {
                    "criterion": "entropy",
                    "ag_args": {
                        "name_suffix": "Entr",
                        "problem_types": ["binary", "multiclass"],
                    },
                },
                {
                    "criterion": "squared_error",
                    "ag_args": {"name_suffix": "MSE", "problem_types": ["regression"]},
                },
            ],
        }
    elif type.lower() == "lightgbmxt":
        hyperparameters = {
            "GBM": [
            {"extra_trees": True, "ag_args": {"name_suffix": "XT"}}
    ]
}
    else:
        print("Using common Hyperparameters ")
        hyperparameters = {
            "GBM": [
                {"extra_trees": True, "ag_args": {"name_suffix": "XT"}},
                {},
                "GBMLarge",
            ],
            "CAT": {},
            "XGB": {},
            "RF": [
                {
                    "criterion": "gini",
                    "ag_args": {
                        "name_suffix": "Gini",
                        "problem_types": ["binary", "multiclass"],
                    },
                },
                {
                    "criterion": "entropy",
                    "ag_args": {
                        "name_suffix": "Entr",
                        "problem_types": ["binary", "multiclass"],
                    },
                },
                {
                    "criterion": "squared_error",
                    "ag_args": {"name_suffix": "MSE", "problem_types": ["regression"]},
                },
            ],
            "XT": [
                {
                    "criterion": "gini",
                    "ag_args": {
                        "name_suffix": "Gini",
                        "problem_types": ["binary", "multiclass"],
                    },
                },
                {
                    "criterion": "entropy",
                    "ag_args": {
                        "name_suffix": "Entr",
                        "problem_types": ["binary", "multiclass"],
                    },
                },
                {
                    "criterion": "squared_error",
                    "ag_args": {"name_suffix": "MSE", "problem_types": ["regression"]},
                },
            ],
            "KNN": [
                {"weights": "uniform", "ag_args": {"name_suffix": "Unif"}, "n_jobs": 4},
                {
                    "weights": "distance",
                    "ag_args": {"name_suffix": "Dist"},
                    "n_jobs": 4,
                },
            ],
        }
    return hyperparameters
