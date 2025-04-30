

import os
from word_boundary.preprocessing.text_to_index import SamplingConfig, TextToIndex, load_index_data, load_characters, characters_to_index_dict


FILE_DIR = os.path.dirname(__file__)
DATA_DIR_RELATIVE = "../../data/livedoor_corpus/text"
DATA_DIR_ABS = os.path.abspath(os.path.join(FILE_DIR, DATA_DIR_RELATIVE))
OUT_DIR_RELATIVE = "../../out/test"
OUT_DIR_ROOT = os.path.abspath(os.path.join(FILE_DIR, OUT_DIR_RELATIVE))
OUT_DIR_ABS = os.path.join(OUT_DIR_ROOT, "preprocessing", "text_to_index")

SUMMARY_CHARACTER_DEST_DIR = os.path.join(OUT_DIR_ROOT, "preprocessing", "summary_characters")
CHARACTERS_FILE_PATH = os.path.join(SUMMARY_CHARACTER_DEST_DIR, "test_summary_parallel_all.txt")

class TestTextToIndex:
    # pytest -s -vv word_boundary/preprocessing/text_to_index_test.py::TestTextToIndex

    def test_enum_file(self):
        # pytest -s -vv word_boundary/preprocessing/text_to_index_test.py::TestTextToIndex::test_enum_file
        # Test the enum_file function
        config = SamplingConfig(sampling_count=10)
        files = TextToIndex.enum_file(DATA_DIR_ABS, config, ignore_file_names=["LICENSE.txt", "CHANGES.txt", "README.txt"])
        print(f"len(files): {len(files)}")
        print(files[:10])
        assert isinstance(files, list)

    def test_save_index_data(self):
        # Test the save_index_data function
        original_path_name = "/workspaces/000110_word_feature/data/livedoor_corpus/text/dokujo-tsushin/dokujo-tsushin-4778030.txt"
        index_data = [1, 2, 3]
        TextToIndex.save_index_data(original_path_name, index_data, OUT_DIR_ABS)
        assert os.path.exists(os.path.join(OUT_DIR_ABS, "dokujo-tsushin-4778030.npy"))
        assert os.path.exists(os.path.join(OUT_DIR_ABS, "dokujo-tsushin-4778030.yaml"))
        write_data = load_index_data(os.path.join(OUT_DIR_ABS, "dokujo-tsushin-4778030.npy"))
        assert write_data == index_data

    def test_livedoor_file_to_index(self):
        # pytest -s -vv word_boundary/preprocessing/text_to_index_test.py::TestTextToIndex::test_livedoor_file_to_index
        # Test the livedoor_file_to_index function
        input_path = os.path.join(DATA_DIR_ABS, "dokujo-tsushin/dokujo-tsushin-4778030.txt")
        characters = load_characters(CHARACTERS_FILE_PATH)
        TextToIndex.livedoor_file_to_index(input_path=input_path, output_directory=OUT_DIR_ABS, characters=characters)
        write_data = load_index_data(os.path.join(OUT_DIR_ABS, "dokujo-tsushin-4778030.npy"))
        characters_index = characters_to_index_dict(characters)
        for idx in write_data:
            if idx < 0:
                print("?", end="")
            else:
                print(characters_index[idx], end="")
        print()

    def test_text_to_index(self):
        # Test the text_to_index function
        data_directory = DATA_DIR_ABS
        out_put_directory = OUT_DIR_ABS
        sampling_config = SamplingConfig(sampling_count=10)
        TextToIndex.text_to_index(
            data_directory=data_directory,
            characters_file_path=CHARACTERS_FILE_PATH,
            out_put_directory=out_put_directory,
            sampling_config=sampling_config,
            ignore_file_names=["LICENSE.txt", "CHANGES.txt", "README.txt"]
        )

    def test_text_to_index_parallel(self):
        # Test the text_to_index_parallel function
        data_directory = DATA_DIR_ABS
        out_put_directory = OUT_DIR_ABS
        sampling_config = SamplingConfig(sampling_count=10)
        TextToIndex.text_to_index_parallel(
            data_directory=data_directory,
            characters_file_path=CHARACTERS_FILE_PATH,
            out_put_directory=out_put_directory,
            sampling_config=sampling_config,
            ignore_file_names=["LICENSE.txt", "CHANGES.txt", "README.txt"]
        )
