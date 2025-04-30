
import os
from word_boundary.char_vector.setup_char_vector import SamplingConfig, SetupVector
from word_boundary.char_vector.setup_char_vector import load_characters, get_max_index, load_vector, extract_valid_columns

FILE_DIR = os.path.dirname(__file__)
DATA_DIR_RELATIVE = "../../data/livedoor_corpus/text"
DATA_DIR_ABS = os.path.abspath(os.path.join(FILE_DIR, DATA_DIR_RELATIVE))
OUT_DIR_RELATIVE = "../../out/test"
OUT_DIR_ROOT = os.path.abspath(os.path.join(FILE_DIR, OUT_DIR_RELATIVE))
OUT_DIR_ABS = os.path.join(OUT_DIR_ROOT, "char_vector", "setup_char_vector")

TEXT_INDEX_FILE_DIR = os.path.join(OUT_DIR_ROOT, "preprocessing", "text_to_index")
SUMMARY_CHARACTER_DEST_DIR = os.path.join(OUT_DIR_ROOT, "preprocessing", "summary_characters")
CHARACTERS_FILE_PATH = os.path.join(SUMMARY_CHARACTER_DEST_DIR, "test_summary_parallel_all.txt")

class TestSetupVector:
    # pytest -s -vv word_boundary/char_vector/setup_char_vector_test.py::TestSetupVector

    def test_enum_file(self):
        # pytest -s -vv word_boundary/calculate/setup_char_vector_test.py::TestSetupVector::test_enum_file
        sampling_config = SamplingConfig(sampling_count=0, sampling_rate=0)
        files = SetupVector.enum_file(sampling_config, TEXT_INDEX_FILE_DIR)
        assert len(files) > 0
        assert all(os.path.isfile(file) for file in files)
        for file in files:
            assert file.endswith(".npy")

    def test_load_characters(self):
        # pytest -s -vv word_boundary/calculate/setup_char_vector_test.py::TestSetupVector::test_load_characters
        characters = load_characters(file_path=CHARACTERS_FILE_PATH)
        assert len(characters) > 0
        max_index = get_max_index(characters)
        assert max_index == (len(characters) - 1)

    def test_create_vector(self):
        # pytest -s -vv word_boundary/calculate/setup_char_vector_test.py::TestSetupVector::test_create_vector
        input_directory = TEXT_INDEX_FILE_DIR
        output_directory = OUT_DIR_ABS
        sampling_config = SamplingConfig(sampling_count=5, sampling_rate=0)
        SetupVector.create_vector(
            characters_file_path=CHARACTERS_FILE_PATH,
            input_directory=input_directory,
            output_directory=output_directory,
            sampling_config=sampling_config,
            window_size=5
        )
        assert os.path.exists(output_directory)
        assert len(os.listdir(output_directory)) > 0

    def test_create_vector_parallel(self):
        # pytest -s -vv word_boundary/calculate/setup_char_vector_test.py::TestSetupVector::test_create_vector_parallel
        input_directory = TEXT_INDEX_FILE_DIR
        output_directory = OUT_DIR_ABS
        batch_size = 2
        sampling_config = SamplingConfig(sampling_count=10, sampling_rate=0)
        SetupVector.create_vector_parallel(
            characters_file_path=CHARACTERS_FILE_PATH,
            input_directory=input_directory,
            output_directory=output_directory,
            batch_size=batch_size,
            sampling_config=sampling_config,
            window_size=5
        )
        assert os.path.exists(output_directory)
        assert len(os.listdir(output_directory)) > 0

    def test_check_sparse_vector(self):
        # pytest -s -vv word_boundary/char_vector/setup_char_vector_test.py::TestSetupVector::test_check_sparse_vector
        characters = load_characters(file_path=CHARACTERS_FILE_PATH)
        max_index = get_max_index(characters)
        # file_name = "/workspaces/000110_word_feature/out/test/char_vector/setup_char_vector/sports-watch-6348483.npz"
        file_name = "/workspaces/000110_word_feature/out/test/char_vector/setup_char_vector/topic-news-6684719.npz"

        sx = load_vector(file_name)
        assert sx is not None
        assert len(sx) > 0
        assert sx.shape[1] == max_index
        valid_vectors = extract_valid_columns(x=sx, start_idx=110, get_size=10)
        for r in valid_vectors:
            for c in r:
                index = c[0]
                value = c[1]
                print(f"{characters[index][2]}:{value}", end=",")
            print("")
