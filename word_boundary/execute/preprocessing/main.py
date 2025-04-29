
import os
import zoneinfo
import time
import datetime
from types import SimpleNamespace
from word_boundary.preprocessing.summary_characters import SamplingConfig, SummaryCharacters
from word_boundary.preprocessing.text_to_index import SamplingConfig, TextToIndex

FILE_DIR = os.path.dirname(__file__)
DATA_DIR_RELATIVE = "../../../data/livedoor_corpus/text"
DATA_DIR_ABS = os.path.abspath(os.path.join(FILE_DIR, DATA_DIR_RELATIVE))
OUT_DIR_RELATIVE = "../../../out/livedoor"
OUT_DIR_ABS = os.path.abspath(os.path.join(FILE_DIR, OUT_DIR_RELATIVE))


class Timer:
    def __enter__(self):
        self.start_time = time.time()
        print("処理開始")
        return self

    def time_to_jst_string(self, timestamp: float) -> str:
        # UTCベースでdatetimeを作成
        utc_dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
        # JSTタイムゾーンに変換
        jst = zoneinfo.ZoneInfo('Asia/Tokyo')
        jst_dt = utc_dt.astimezone(jst)
        return jst_dt.strftime("%Y-%m-%d %H:%M:%S")

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time.time()
        self.elapsed = self.end_time - self.start_time
        print(f"開始時間: {self.time_to_jst_string(self.start_time)}, 終了時間 {self.time_to_jst_string(self.end_time)}, 経過時間: {self.elapsed:.3f} 秒")


def preprocessing():
    sampling_config = SamplingConfig()
    batch_size=100
    max_workers=12
    summary_characters_output_file = os.path.join(OUT_DIR_ABS, "summary_characters.txt")
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
        out_put_directory=OUT_DIR_ABS,
        sampling_config=sampling_config,
        batch_size=batch_size,
        max_workers=max_workers,
        ignore_file_names=["CHANGES.txt", "README.txt", "LICENSE.txt"]
    )

    return SimpleNamespace(
        data_directory=DATA_DIR_ABS,
        out_put_directory=OUT_DIR_ABS,
        summary_characters_output_file=summary_characters_output_file,
        batch_size=batch_size,
        max_workers=max_workers,
        sampling_config=sampling_config,
        ignore_file_names=["CHANGES.txt", "README.txt", "LICENSE.txt"]
    )


def test1():
    with Timer() as timer:
        time.sleep(3)


def main():
    with Timer() as timer:
        preprocess_info = preprocessing()
        print("=== Report ===")
        for key, value in vars(preprocess_info).items():
            print(f"{key}: {value}")
        print("==============")


if __name__ == "__main__":
    main()
