
def hamming(a, b):
    return len([i for i in filter(lambda x: x[0] != x[1], zip(a, b))])

def main():
    original_word = input("input words: ")
    compare_word = input("input compare word: ")
    result = hamming(original_word, compare_word)
    print("different number:", result)

