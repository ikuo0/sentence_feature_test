
import os
from word_boundary.preprocessing import summary_characters
from word_boundary.preprocessing.summary_characters import SamplingConfig, SummaryCharacters

FILE_DIR = os.path.dirname(__file__)
DATA_DIR_RELATIVE = "../../data/livedoor_corpus/text"
DATA_DIR_ABS = os.path.abspath(os.path.join(FILE_DIR, DATA_DIR_RELATIVE))
OUT_DIR_RELATIVE = "../../out/test"
OUT_DIR_ABS = os.path.abspath(os.path.join(FILE_DIR, OUT_DIR_RELATIVE))

class TestSummaryCharacters:
    def test_summary_characters(self):
        # Test the summary characters function

        # Example input
        text = "あいいうううええええおおおおお"

        # Expected output
        expected = {
            'あ': 1,
            'い': 2,
            'う': 3,
            'え': 4,
            'お': 5
        }

        # Call the function and check the result
        result = summary_characters.summary_characters(text)
        assert result == expected

    def test_summary_file(self):
        # pytest -s -vv word_boundary/preprocessing/summary_characters_test.py::TestSummaryCharacters::test_summary_file
        target_file = os.path.join(DATA_DIR_ABS, "dokujo-tsushin/dokujo-tsushin-4778030.txt")
        out_file = os.path.join(OUT_DIR_ABS, "test_summary_characters.txt")
        data = summary_characters.summary_file(target_file)
        sorted_data = summary_characters.sorted_summary(data)
        print(sorted_data)
        summary_characters.save_summary_to_file(out_file, sorted_data)

    def test_summary(self):
        # pytest -s -vv word_boundary/preprocessing/summary_characters_test.py::TestSummaryCharacters::test_summary
        sampling_config = SamplingConfig(
            sampling_count=10,
        )
        out_file = os.path.join(OUT_DIR_ABS, "test_summary.txt")
        SummaryCharacters.summary(
            data_directory=DATA_DIR_ABS,
            out_put_file_name=out_file,
            sampling_config=sampling_config,
            ignore_file_names=["CHANGES.txt", "README.txt", "LICENSE.txt"]
        )

    def test_summary_parallel(self):
        # pytest -s -vv word_boundary/preprocessing/summary_characters_test.py::TestSummaryCharacters::test_summary_parallel
        sampling_config = SamplingConfig(
            sampling_count=100,
        )
        out_file = os.path.join(OUT_DIR_ABS, "test_summary_parallel.txt")
        SummaryCharacters.summary_parallel(
            data_directory=DATA_DIR_ABS,
            out_put_file_name=out_file,
            batch_size=10,
            max_workers=4,
            sampling_config=sampling_config,
            ignore_file_names=["CHANGES.txt", "README.txt", "LICENSE.txt"]
        )
