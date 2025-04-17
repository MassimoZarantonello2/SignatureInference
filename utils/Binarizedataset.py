import pandas as pd
import argparse
import sys
sys.path.append("./")

def binarize_df(dataframe,treshold:float,save_csv_path=None):
    '''
    With this function you can binarize a dataframe based on a treshold given as input and have 
    the option of saving the resulted dataframe in CSV if given a path. The dataframe in output
    is a copy of the one in input.

    Parameters
    --------------------------
    df: The dataframe used as input
    treshold: tha value use to split the elements of the dataframe
    save_csv_path: if given saves the dataframe in the relative path
    '''
    first_colum = dataframe.iloc[:,0]
    df = dataframe.iloc[:,1:] > treshold
    df = pd.concat([first_colum, df], axis=1)
    if save_csv_path is not None:
        df.to_csv(save_csv_path, index = False)
    
    return df

if __name__ == "__main__":   
    parser = argparse.ArgumentParser(
    description="Esecuzione del modello di valutazione con parametri opzionali")
    
    parser.add_argument(
        "--input_csv",
        type=str,
        help="Path to the input CSV file",
        required=True,
    )
    parser.add_argument(
        "--output_csv",
        type=str,
        help="Path to the output CSV file",
        required=True,
    )
    parser.add_argument(
        "--treshold",
        type=float,
        help="Treshold for binarization",
        required=True,
    )
    args = parser.parse_args()
    # Load the CSV file into a DataFrame
    df = pd.read_csv(args.input_csv)
    # Binarize the DataFrame
    binarized_df = binarize_df(df, args.treshold, args.output_csv)
    
    
    