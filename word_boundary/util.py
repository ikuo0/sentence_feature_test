import os
import time
import datetime
import zoneinfo


def make_directory(directory: str):
    try:
        os.makedirs(directory, exist_ok=True)
    except:
        pass


def make_file_directory(file_path: str):
    directory = os.path.dirname(file_path)
    make_directory(directory)


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
