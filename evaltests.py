import pandas as pd
import numpy as np
import plot


df = pd.read_csv('data_tmp/test_failures.csv', index_col=0)
print(df.head())
print(len(df['test'].unique()))
print(len(df['test']))


