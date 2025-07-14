import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import sys
import os
from sklearn.model_selection import KFold


sys.path.append("./")
from utils.MultiLabelPredictor import MultilabelPredictor

def print_stats(r2_1, mse_1, thresholds=[0.5, 0.8], output_file="0.03_results.txt"):
    r2_1, mse_1 = np.array(r2_1), np.array(mse_1)

    def summary_stats(metric):
        return (np.nanmean(metric), np.nanmedian(metric), np.nanmax(metric), np.nanmin(metric))

    r2_1_stats = summary_stats(r2_1)
    mse_1_stats = summary_stats(mse_1)

    lines = []
    lines.append(f"Model 1 R²: Mean={r2_1_stats[0]:.4f}, Median={r2_1_stats[1]:.4f}, Max={r2_1_stats[2]:.4f}, Min={r2_1_stats[3]:.4f}")
    lines.append(f"Model 1 MSE: Mean={mse_1_stats[0]:.2e}, Median={mse_1_stats[1]:.2e}, Max={mse_1_stats[2]:.2e}, Min={mse_1_stats[3]:.2e}")
    
    for t in thresholds:
        count1 = np.sum(r2_1 > t)
        lines.append(f"Signatures with R² > {t}: {count1}")

    # Stampa su console
    for line in lines:
        print(line)

    # Scrittura su file
    with open(output_file, "w") as f:
        for line in lines:
            f.write(line + "\n")

sample_size = '1'

# Definizione delle label
labels = ["S1 (SBS1 - 0.99)_y", "S2 (SBS2 - 0.99)_y", "S3 (SBS3 - 0.97)_y", "S4 (SBS4 - 0.98)_y", 
          "S5 (SBS5 - 0.98)_y", "S6 (SBS7a - 1.00)_y", "S7 (SBS7b - 0.96)_y", "S8 (SBS8 - 0.92)_y",
          "S9 (SBS9 - 0.94)_y", "S10 (SBS10a - 1.00)_y", "S11 (SBS10d - 0.98)_y", "S12 (SBS11 - 0.99)_y",
          "S13 (SBS13 - 0.99)_y", "S14 (SBS14 - 0.98)_y", "S15 (SBS15 - 0.97)_y", "S16 (SBS17 - 0.99)_y",
          "S17 (SBS18 - 0.97)_y", "S18 (SBS19 - 0.95)_y", "S19 (SBS20 - 0.98)_y", "S20 (SBS22 - 0.99)_y",
          "S21 (SBS23 - 0.94)_y", "S22 (SBS26 - 0.94)_y", "S23 (SBS28 - 0.96)_y", "S24 (SBS31 - 0.98)_y",
          "S25 (SBS32 - 0.94)_y", "S26 (SBS44 - 0.97)_y", "S27 (SBS88 - 0.92)_y", "S28 (SBS92 - 0.95)_y",
          "S29 (SBS97 - 0.95)_y"]

# Caricamento dati
bin_exposure = pd.read_csv('simulations/ground_truth/bin_exposures.csv')
mutation_count = pd.read_csv(f'simulations/data/run_1/trinucleotides_counts_sampling_{sample_size}.csv')
target_exposures = pd.read_csv('simulations/ground_truth/exposures.csv')
df = pd.merge(bin_exposure, mutation_count, on="Unnamed: 0")
train_df = pd.merge(df, target_exposures, on="Unnamed: 0")
train_df.drop(columns=["Unnamed: 0"], inplace=True)
# Split e salvataggio indici test
train_df_indexed = train_df.reset_index(drop=True)
train_idx, test_idx = train_test_split(train_df_indexed.index, test_size=0.2, random_state=42)
train_data = train_df_indexed.loc[train_idx].reset_index(drop=True)

if not os.path.exists(f'models/{sample_size}_exposures_autogluon'):
    print("Model doesn't exists training it from scratch")
    np.savetxt(f"{sample_size}_test_indices.txt", test_idx, fmt='%d')

    # Training e salvataggio modello
    #predictor = MultilabelPredictor(path=f'models/{sample_size}_exposures_autogluon', labels=labels)
    #predictor.fit(train_data=train_data, time_limit = 240)
else:
    print('Model already exists loading it')
    # Caricamento modello
    predictor = MultilabelPredictor.load(path=f'models/{sample_size}_exposures_autogluon')

    # Caricamento indici di test
    test_idx = np.loadtxt(f"{sample_size}_test_indices.txt", dtype=int)
    test_data = train_df_indexed.loc[test_idx].reset_index(drop=True)

    # Predizione sul test set
    prediction = predictor.predict(test_data)

    # Caricamento ground truth
    signature_exposure = test_data[labels]

    # Calcolo metriche
    r2_list = []
    mse_list = []
    signatures = prediction.columns.intersection(signature_exposure.columns)

    for sig in signatures:
        r2 = r2_score(signature_exposure[sig], prediction[sig])
        mse = mean_squared_error(signature_exposure[sig], prediction[sig])
        r2_list.append(r2)
        mse_list.append(mse)

    # Stampa statistiche
    print_stats(r2_list, mse_list)
    print("\n[Valutazione su test set alternativi]")

    all_idx = np.arange(len(train_df_indexed))
    train_idx_set = np.setdiff1d(all_idx, test_idx)  # sample non visti

    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    r2_scores_per_fold = []
    mse_scores_per_fold = []

    for i, (_, test_idx_alt) in enumerate(kf.split(train_idx_set)):
        idx = train_idx_set[test_idx_alt]
        test_data_alt = train_df_indexed.loc[idx].reset_index(drop=True)
        prediction_alt = predictor.predict(test_data_alt)
        gt_alt = test_data_alt[labels]

        r2_list = []
        mse_list = []
        for sig in prediction_alt.columns.intersection(gt_alt.columns):
            r2 = r2_score(gt_alt[sig], prediction_alt[sig])
            mse = mean_squared_error(gt_alt[sig], prediction_alt[sig])
            r2_list.append(r2)
            mse_list.append(mse)

        r2_scores_per_fold.append(np.nanmean(r2_list))
        mse_scores_per_fold.append(np.nanmean(mse_list))

     # Salva risultati in DataFrame
    results_df = pd.DataFrame({
        "fold": np.arange(1, len(r2_scores_per_fold) + 1),
        "R2_mean": r2_scores_per_fold,
        "MSE_mean": mse_scores_per_fold
    })

    print("\nValutazione su test set alternativi:")
    print(results_df)

    # Salva anche su CSV per uso successivo (opzionale)
    results_df.to_csv(f"{sample_size}_testset_variability.csv", index=False)
