import argparse
import textwrap
import pandas as pd
import os
from utils.MultiLabelPredictor import MultilabelPredictor
import numpy as np
from scipy.optimize import nnls
from scipy.spatial.distance import cosine

def update_W_nnls_masked(V, H, mask):
    """
    Calcola W dato V e H fisso usando NNLS riga per riga,
    con vincolo: alcune componenti di W fissate a 0 (mask=0).

    V: (n_samples, n_features)
    H: (n_components, n_features)
    mask: (n_samples, n_components), valori binari (1=attiva, 0=fissata a 0)

    Ritorna:
    W: (n_samples, n_components)
    """
    n_samples, n_features = V.shape
    n_components = H.shape[0]
    W = np.zeros((n_samples, n_components))

    for i in range(n_samples):
        active_idx = np.where(mask[i] == 1)[0]   # firme attive per sample i
        if len(active_idx) == 0:
            continue  # nessuna firma attiva -> tutto zero

        A = H[active_idx].T   # (n_features, n_active)
        b = V[i, :]
        w_active, _ = nnls(A, b)

        # reinserisci nei posti giusti
        W[i, active_idx] = w_active

    return W

def evaluate_results(W, W_predicted):
    cos_similarity_per_patient = [1-cosine(W[i, :], W_predicted[i, :]) for i in range(W.shape[0])]
    mean_cos_similarity = np.mean(cos_similarity_per_patient)
    print(f"Cosine similarity: {mean_cos_similarity}")
    return cos_similarity_per_patient

def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract active mutational signatures from a mutation count matrix.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent("""\
            Example usage:
              python tool.py
                  --input data/mutation_counts.csv
                  --dataset cosmic
        """),
    )

    parser.add_argument(
        "-i", "--input",
        required=True,
        type=str,
        help="Path to the mutation count matrix file (CSV).",
    )

    parser.add_argument(
        "-d", "--dataset",
        type=str,
        default="default",
        choices=["default", "cosmic", "reference"],
        help="Dataset to use for signature extraction.\n"
             "Available options: default, cosmic, reference.",
    )
    parser.add_argument(
        "-s", "--sequencing",
        type=str,
        default="wgs",
        choices=["wgs", "wes"],
        help="The type of sequencing used to extrapolate the input mutations counts. \n"
             "Available option: wgs 100, wes 2.",
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default="results",
        help="Directory where output files will be saved (default: ./results).",
    )

    return parser.parse_args()

if __name__ == '__main__':
    print('='*70)
    print(' __  __ _    _ _______       _   _          _  __     ______________ ')
    print('|  \/  | |  | |__   __|/\   | \ | |   /\   | | \ \   / /___  /  ____|')
    print('| \  / | |  | |  | |  /  \  |  \| |  /  \  | |  \ \_/ /   / /| |__   ')
    print('| |\/| | |  | |  | | / /\ \ | . ` | / /\ \ | |   \   /   / / |  __|  ')
    print('| |  | | |__| |  | |/ ____ \| |\  |/ ____ \| |____| |   / /__| |____ ')
    print('|_|  |_|\____/   |_/_/    \_\_| \_/_/    \_\______|_|  /_____|______| \n')                                          
    print('='*70)
    
    
    # take in input some parameters to define the execution
    #   1. Input file complete path to the mutation count for one or more patient
    #   2. What type of datasets should be used (default COSMIC or Reference)
    #   3. Output file complete path to where you want to save the file of the active segnature plus some additional info 

    args = parse_args()
    
    mutations_count = pd.read_csv(args.input)       #TODO check the input format of the file
    portion = '1' if args.sequencing.lower() == 'wgs' else '0.02' 
    # print(f'./models/{args.dataset}/Predictor-{portion}')
    predictor = MultilabelPredictor.load(f'tool/models/{args.dataset}/Predictor-{portion}')
    for label in predictor.labels:
        predictor.predictors[label] = os.path.join(f'tool/models/{args.dataset}/Predictor-{portion}', f'Predictor_{label}')
    
    signatures = pd.read_csv(f'tool/utils/signatures_{args.dataset}.csv')
    H = signatures.iloc[:, 1:].values
    columns = signatures.iloc[:,0].values
    predictions = np.array(predictor.predict(mutations_count))
    exposures = update_W_nnls_masked(V = np.array(mutations_count.iloc[:, 1:].values), H = H, mask = predictions)
    if not os.path.exists(f'tool{args.output}'):
        os.mkdir(f'tool/{args.output}')
    pd.DataFrame(exposures, columns=columns, index = mutations_count.iloc[:,0]).to_csv(f'tool/{args.output}/exposures.csv')
