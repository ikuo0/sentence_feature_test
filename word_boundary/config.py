
import os
FILE_DIR = os.path.dirname(__file__)
DATA_DIR_RELATIVE = "../../data/livedoor_corpus/text"
DATA_DIR_ABS = os.path.abspath(os.path.join(FILE_DIR, DATA_DIR_RELATIVE))

IGNORE_FILE_NAMES = [
    "LICENSE.txt",
    "CHANGES.txt",
    "README.txt"
]
