import pandas as pd
import numpy as np
import plot


df = pd.read_csv('data_tmp/build_failures.csv', index_col=0)
print(df.head())
print(df['failures'].median())
#plot.histogram(df['failures'])