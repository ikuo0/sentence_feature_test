
import os
import numpy as np

FILE_DIR = os.path.dirname(__file__)
DATA_DIR_RELATIVE = "../../out/livedoor"
DATA_DIR_ABS = os.path.abspath(os.path.join(FILE_DIR, DATA_DIR_RELATIVE))

def confirm_sentence_indexes():
    file_path = os.path.join(DATA_DIR_ABS, "dokujo-tsushin-4778030.npy")
    x = np.load(file_path)
    print(x)

if __name__ == "__main__":
    confirm_sentence_indexes()
