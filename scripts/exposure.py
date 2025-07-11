import pandas as pd
import sys
sys.path.append("./")
from utils.MultiLabelPredictor import MultilabelPredictor


labels = ["S1 (SBS1 - 0.99)_y","S2 (SBS2 - 0.99)_y","S3 (SBS3 - 0.97)_y","S4 (SBS4 - 0.98)_y","S5 (SBS5 - 0.98)_y","S6 (SBS7a - 1.00)_y","S7 (SBS7b - 0.96)_y","S8 (SBS8 - 0.92)_y","S9 (SBS9 - 0.94)_y","S10 (SBS10a - 1.00)_y","S11 (SBS10d - 0.98)_y","S12 (SBS11 - 0.99)_y","S13 (SBS13 - 0.99)_y","S14 (SBS14 - 0.98)_y","S15 (SBS15 - 0.97)_y","S16 (SBS17 - 0.99)_y","S17 (SBS18 - 0.97)_y","S18 (SBS19 - 0.95)_y","S19 (SBS20 - 0.98)_y","S20 (SBS22 - 0.99)_y","S21 (SBS23 - 0.94)_y","S22 (SBS26 - 0.94)_y","S23 (SBS28 - 0.96)_y","S24 (SBS31 - 0.98)_y","S25 (SBS32 - 0.94)_y","S26 (SBS44 - 0.97)_y","S27 (SBS88 - 0.92)_y","S28 (SBS92 - 0.95)_y","S29 (SBS97 - 0.95)_y"]
predictor = MultilabelPredictor(path='models/exposures_autogluon',
                                labels=labels)

bin_exposure = pd.read_csv('simulations/ground_truth/bin_exposures.csv')
mutation_count = pd.read_csv('simulations/data/run_1/trinucleotides_counts_sampling_0.03.csv')
target_exposures = pd.read_csv('simulations/ground_truth/exposures.csv')
df = pd.merge(bin_exposure, mutation_count, on="Unnamed: 0")
train_df = pd.merge(df, target_exposures, on="Unnamed: 0")


train_df.drop(columns=["Unnamed: 0"], inplace=True)

predictor.fit(train_data=train_df,
              presets='high_quality')