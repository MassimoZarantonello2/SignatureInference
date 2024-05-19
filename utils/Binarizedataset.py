import pandas as pd
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