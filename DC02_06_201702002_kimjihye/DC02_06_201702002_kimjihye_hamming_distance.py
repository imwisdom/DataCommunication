import random
import numpy as np
import pandas as pd
from hamming_practice import hamming

df = pd.read_csv('sample.csv', names=['word', 'bin'])

count = 0
min_ham = hamming(df.iloc[0, 1], df.iloc[1, 1])

i=0
for i in list(range(i, 99)):
    j=i+1
    for j in list(range(j, 100)):
        hd = hamming(df.iloc[i, 1], df.iloc[j,1])
        count = count+1
        print(count, "(", df.iloc[i,0], df.iloc[j,0],") hamming_distance: ", hd)
        if min_ham>hd:
            min_ham=hd

print("min hamming distance", min_ham)

