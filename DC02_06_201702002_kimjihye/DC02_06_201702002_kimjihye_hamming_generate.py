import random
import numpy as np
import pandas as pd


df = pd.read_csv('sample.csv', name=['word', 'ascii'])

def generate_random_ascii():
        for i in range(0, 100):
            make_str = list()
            make_ascii = list()
            make_hex = list()
            for j in range(0, 4):
                num = random.randint(97, 122)
                make_str.append(str(chr(num)))
            string = ''.join(make_str)
            binary = bin(int.from_bytes(string.encode(), 'big'))

        return string, binary


for k in range(0, 100) :
    string, binary = generate_random_ascii()
    df.iloc[k, 0] = string
    df.iloc[k, 1] = "0"+binary[2:]
df.to_csv('sample.csv', header=False, index=False)




