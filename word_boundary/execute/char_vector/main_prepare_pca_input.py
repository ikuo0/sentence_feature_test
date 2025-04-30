import os
import scipy.sparse
import time
from word_boundary import util
from word_boundary.char_vector.prepare_pca_input import prepare_pca_input


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


def main():
    with util.Timer() as timer:
        sample_count = None
        output_path = os.path.join(PREPARE_PCA_DEST_DIR, "stacked_matrix.npz")
        prepare_pca_input(
            input_directory=SETUPED_VECTOR_DIR,
            output_path=output_path,
            sample_count=sample_count)
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0
        sx = scipy.sparse.load_npz(output_path)
        print("#" * 100)
        print(sx.shape)


if __name__ == "__main__":
    main()
