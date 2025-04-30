
import os
import numpy as np
from scipy import sparse
import random

FILE_DIR = os.path.dirname(__file__)
DATA_DIR_RELATIVE = "../../../data/livedoor_corpus/text"
DATA_DIR_ABS = os.path.abspath(os.path.join(FILE_DIR, DATA_DIR_RELATIVE))
OUT_DIR_RELATIVE = "../../../out/livedoor"
OUT_DIR_ABS = os.path.abspath(os.path.join(FILE_DIR, OUT_DIR_RELATIVE))

SUMMARY_CHARACTER_DEST_DIR = os.path.join(OUT_DIR_ABS, "preprocessing", "summary_characters")
SUMMARY_CHARACTER_FILE_PATH = os.path.join(SUMMARY_CHARACTER_DEST_DIR, "characters.txt")
INDEXED_TEXT_FILE_DIR = os.path.join(OUT_DIR_ABS, "preprocessing", "text_to_index")
SETUPED_VECTOR_DIR = os.path.join(OUT_DIR_ABS, "char_vector", "setup_char_vector")
PREPARE_PCA_DEST_DIR = os.path.join(OUT_DIR_ABS, "char_vector", "prepare_pca_input")

def load_and_stack_npz(folder_path, sample_count=None):
    stacked = None
    npz_files = sorted(f for f in os.listdir(folder_path) if f.endswith(".npz"))

    if sample_count is not None:
        npz_files = random.sample(npz_files, sample_count)

    for filename in npz_files:
        path = os.path.join(folder_path, filename)
        sx = sparse.load_npz(path)
        # loader = np.load(path)
        # matrix = loader['arr_0']  # 通常 `scipy.sparse.save_npz()` で保存するとこのキー

        if not sparse.issparse(sx):
            raise ValueError(f"{filename} is not a sparse matrix")

        if stacked is None:
            stacked = sx
        else:
            stacked = sparse.vstack([stacked, sx], format="csr")

    return stacked


def save_stacked_npz(stacked, output_path):
    if sparse.issparse(stacked):
        sparse.save_npz(output_path, stacked)
    else:
        raise ValueError("Input is not a sparse matrix")


def prepare_pca_input(input_directory: str, output_path: str, sample_count=None):
    stacked_matrix = load_and_stack_npz(input_directory, sample_count=sample_count)
    save_stacked_npz(stacked_matrix, output_path)
