def get_hyperparameters(type):
    if type.lower() == "tree":
        print("Using Hyperparameters for Tree Models")
        hyperparameters = {
            "GBM": [
                {"extra_trees": True, "ag_args": {"name_suffix": "XT"}},  # XT (più veloce e robusto)
                {"ag_args": {"name_suffix": "Light"}},  # LightGBM standard
            ],
            "RF": [
                {
                    "criterion": "gini",
                    "max_depth": 10,  # Limita profondità per velocizzare
                    "ag_args": {"name_suffix": "Gini", "problem_types": ["binary", "multiclass"]},
                },
            ],
            "XT": [
                {
                    "criterion": "gini",
                    "max_depth": 10,  # Come sopra, per consistenza
                    "ag_args": {"name_suffix": "Gini", "problem_types": ["binary", "multiclass"]},
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
        hyperparameters = None
        
    return hyperparameters