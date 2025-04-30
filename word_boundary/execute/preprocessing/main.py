
import os
import time
from types import SimpleNamespace
from word_boundary.preprocessing.summary_characters import SamplingConfig, SummaryCharacters
from word_boundary.preprocessing.text_to_index import SamplingConfig, TextToIndex
from word_boundary import util


FILE_DIR = os.path.dirname(__file__)
DATA_DIR_RELATIVE = "../../../data/livedoor_corpus/text"
DATA_DIR_ABS = os.path.abspath(os.path.join(FILE_DIR, DATA_DIR_RELATIVE))
OUT_DIR_RELATIVE = "../../../out/livedoor"
OUT_DIR_ABS = os.path.abspath(os.path.join(FILE_DIR, OUT_DIR_RELATIVE))

SUMMARY_CHARACTER_DEST_DIR = os.path.join(OUT_DIR_ABS, "preprocessing", "summary_characters")
SUMMARY_CHARACTER_FILE_PATH = os.path.join(SUMMARY_CHARACTER_DEST_DIR, "characters.txt")
INDEXED_TEXT_FILE_DIR = os.path.join(OUT_DIR_ABS, "preprocessing", "text_to_index")


def preprocessing():
    sampling_config = SamplingConfig()
    batch_size=100
    max_workers=12
    summary_characters_output_file = SUMMARY_CHARACTER_FILE_PATH
    SummaryCharacters.summary_parallel(
        data_directory=DATA_DIR_ABS,
        out_put_file_name=summary_characters_output_file,
        batch_size=batch_size,
        max_workers=max_workers,
        sampling_config=sampling_config
    )

    sampling_config = SamplingConfig()
    TextToIndex.text_to_index_parallel(
        data_directory=DATA_DIR_ABS,
        characters_file_path=summary_characters_output_file,
        out_put_directory=INDEXED_TEXT_FILE_DIR,
        sampling_config=sampling_config,
        batch_size=batch_size,
        max_workers=max_workers,
        ignore_file_names=["CHANGES.txt", "README.txt", "LICENSE.txt"]
    )

    return SimpleNamespace(
        data_directory=DATA_DIR_ABS,
        out_put_directory=INDEXED_TEXT_FILE_DIR,
        summary_characters_output_file=summary_characters_output_file,
        batch_size=batch_size,
        max_workers=max_workers,
        sampling_config=sampling_config,
        ignore_file_names=["CHANGES.txt", "README.txt", "LICENSE.txt"]
    )


def test1():
    with util.Timer() as timer:
        time.sleep(3)


def main():
    with util.Timer() as timer:
        preprocess_info = preprocessing()
        print("=== Report ===")
        for key, value in vars(preprocess_info).items():
            print(f"{key}: {value}")
        print("==============")


if __name__ == "__main__":
    main()
