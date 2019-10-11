import subprocess
import numpy as np
import pandas as pd
from hamming_practice import hamming


def input_your_code():
    python_file = input("input your python project:(테스트코드와 같은 폴더안에 있어야함)")
    result=subprocess.check_output(["python3 "+python_file],shell=True,encoding='utf-8')
    result_list = result.split('\n')
    final_result = result_list[-2]
    return final_result

def sol():
    df = pd.read_csv('sample.csv',names=['word','bin'])

    min = 1000000000
    count = 1
    for i in range(0,len(df)):
        for j in range(i+1,len(df)):
            hd = hamming(df.iloc[i,1],df.iloc[j,1])
            if min > hd:
                min = hd
            count += 1
    return min


def main():
    your_result = input_your_code()
    solution = sol()
    print("your_result:",your_result.split(' ')[-1])
    print("solution:",solution)
    if your_result == solution:
        print("PASS")
main()
