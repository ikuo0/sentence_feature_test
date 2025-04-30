import os
from word_boundary.char_vector.setup_char_vector import SamplingConfig, SetupVector
from word_boundary import util

FILE_DIR = os.path.dirname(__file__)
DATA_DIR_RELATIVE = "../../../data/livedoor_corpus/text"
DATA_DIR_ABS = os.path.abspath(os.path.join(FILE_DIR, DATA_DIR_RELATIVE))
OUT_DIR_RELATIVE = "../../../out/livedoor"
OUT_DIR_ABS = os.path.abspath(os.path.join(FILE_DIR, OUT_DIR_RELATIVE))

SUMMARY_CHARACTER_DEST_DIR = os.path.join(OUT_DIR_ABS, "preprocessing", "summary_characters")
SUMMARY_CHARACTER_FILE_PATH = os.path.join(SUMMARY_CHARACTER_DEST_DIR, "characters.txt")
INDEXED_TEXT_FILE_DIR = os.path.join(OUT_DIR_ABS, "preprocessing", "text_to_index")
SETUPED_VECTOR_DIR = os.path.join(OUT_DIR_ABS, "char_vector", "setup_char_vector")


def create_vector():
    sampling_config = SamplingConfig()
    SetupVector.create_vector_parallel(
        characters_file_path=SUMMARY_CHARACTER_FILE_PATH,
        input_directory=INDEXED_TEXT_FILE_DIR,
        output_directory=SETUPED_VECTOR_DIR,
        sampling_config=sampling_config,
        window_size=5,
        batch_size=100,
        max_workers=12
    )


def main():
    with util.Timer() as timer:
        create_vector()
        # print("=== Report ===")
        # for key, value in vars(preprocess_info).items():
        #     print(f"{key}: {value}")
        # print("==============")


if __name__ == "__main__":
    main()
