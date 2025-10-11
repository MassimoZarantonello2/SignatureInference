import argparse
import textwrap
import pandas as pd
from utils.MultiLabelPredictor import MultilabelPredictor

def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract active mutational signatures from a mutation count matrix.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=textwrap.dedent("""\
            Example usage:
              python tool.py \n
                  --input data/mutation_counts.csv \n
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
        "-o", "--output",
        type=str,
        default="results/",
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
    
    mutations_count = pd.read_csv(args.input)
    

