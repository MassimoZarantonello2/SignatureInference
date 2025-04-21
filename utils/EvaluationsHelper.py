import json
def create_empty_json_file(run_values, sampling_values, save_evaluations_path):       # Create the structure of the json file
    run_dict = {}
    for run in run_values:
        run_index = "run_" + run
        sample_dict = {}
        for sample in sampling_values:
            sample_index = "sampling_" + sample
            sample_dict[sample_index] = {}
            run_dict[run_index] = sample_dict
    json.dump(run_dict, open(save_evaluations_path, "w+"))  # Save the json file
        
def format_model_result(predictor, test_df):
    evaluations = predictor.evaluate(test_df)
    results = []
    for signature in evaluations:
        model_predictor = predictor.get_predictor(signature)
        metrics = evaluations[signature]
        info = model_predictor.info()
        model_info = info["model_info"]

        best_model_name = info["best_model"]
        best_model_info = model_info[best_model_name]

        ensemble_model_names = best_model_info.get("features", [])

        ensemble_info = [
            {
                "model_name": model,
                "val_score": model_info[model].get("val_score"),
                "fit_time": model_info[model].get("fit_time"),
            }
            for model in ensemble_model_names
        ]

        result = {
            "signature": signature,
            "best_model": best_model_name,
            "best_model_val_score": best_model_info.get("val_score"),
            "best_model_metrics": metrics,
            "best_model_fit_time": best_model_info.get("fit_time"),
            "ensemble_models": ensemble_model_names,
            "ensemble_info": ensemble_info,
        }
        results.append(result)
    return results