import pandas as pd

df = pd.read_csv("trinucleotides_counts_sampling_0.03.csv")
df = df.set_index("Sample")
df.to_csv("trinucleotides_counts_sampling_0.03.txt", sep="\t")