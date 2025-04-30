
from typing import List, Tuple
import numpy as np
import os
import random
import yaml
import csv
from concurrent.futures import ThreadPoolExecutor
from word_boundary.preprocessing import normalize_text


def enum_file(data_directory: str) -> List[str]:
    txt_files = []
    for current_dir, sub_dirs, files in os.walk(data_directory):
        for file in files:
            if file.endswith(".txt"):
                txt_files.append(os.path.join(current_dir, file))
    return txt_files


def text_to_index(text: str, characters: dict) -> List[int]:
    result = []
    for c in text:
        if c in characters:
            result.append(characters[c])
        else:
            result.append(-1)
    return result


def read_livedoor_file(file_path: str) -> Tuple[dict, str]:
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    # 先頭２行の情報を取得し別途返却
    # １行目はURL
    # ２行目は記事の公開日時
    lines = text.splitlines()
    info = {
        "url": lines[0],
        "published_date": lines[1]
    }
    body = "\n".join(lines[2:])
    return info, body



def list_int_to_binary(data: List[int]) -> bytes:
    """
    Convert a list of integers to a binary matrix.
    """
    array = np.array(data, dtype=np.int32)
    return array.tobytes()


def save_binary_to_file(int_array: List[int], file_path: str) -> None:
    """バイナリデータをファイルに保存する"""
    x = np.array(int_array, dtype=np.int32)
    np.save(file_path, x)


def load_binary_from_file(file_path: str) -> np.ndarray:
    """バイナリデータをファイルから読み込む"""
    return np.load(file_path, allow_pickle=True)


def binary_to_list_int(binary_data: bytes) -> list[int]:
    """バイナリデータを読み込み、List[int] に復元する"""
    array = np.frombuffer(binary_data, dtype=np.int32)
    return array.tolist()


def load_index_data(file_path: str) -> List[int]:
    """バイナリデータをファイルから読み込み、List[int] に復元する"""
    ndarray_data = load_binary_from_file(file_path)
    return ndarray_data.tolist()


def remove_files_by_name(file_list: List[str], ignore_file_names: List[str]) -> List[str]:
    result = []
    for full_path in file_list:
        file_name = os.path.basename(full_path)
        if file_name in ignore_file_names:
            continue
        result.append(full_path)
    return result


def load_characters(file_path: str) -> dict:
    """
0	540874	$
1	416138	０
2	244186	の
    """
    x = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # 行末の改行を除去してタブで分割
            x.append(line.rstrip('\n').split('\t'))
    result = {}
    for ix in x:
        result[ix[2]] = int(ix[0])
    return result


def characters_to_index_dict(characters: dict) -> dict:
    size = len(characters)
    result = [""] * size
    for k in characters:
        idx = characters[k]
        result[idx] = k
    return result


class SamplingConfig:
    def __init__(self, sampling_count: int = 0, sampling_rate: int = 0):
        self.sampling_count = sampling_count
        self.sampling_rate = sampling_rate
        self.sampling = False
        self.sampling_type = ""
        if self.sampling_count > 0:
            self.sampling = True
            self.sampling_type = "count"
        elif self.sampling_rate > 0:
            self.sampling = True
            self.sampling_type = "rate"


class TextToIndex:
    @classmethod
    def enum_file(cls, data_directory: str, sampling_config: SamplingConfig, ignore_file_names=[]) -> List[str]:
        files = enum_file(data_directory)
        if sampling_config.sampling:
            sample_count = 0
            if sampling_config.sampling_type == "count":
                sample_count = sampling_config.sampling_count
            elif sampling_config.sampling_type == "rate":
                sample_count = int(len(files) * sampling_config.sampling_rate)
            else:
                raise ValueError(f"Invalid sampling type: {sampling_config.sampling_type}")
            files = random.sample(files, sample_count)
        files = remove_files_by_name(files, ignore_file_names)
        return files

    @classmethod
    def livedoor_file_to_index(cls, input_path: str, output_directory: str, characters: dict):
        info, body = read_livedoor_file(input_path)
        normalize = normalize_text.normalize(body)
        indexes = text_to_index(normalize, characters)
        basename = os.path.basename(input_path)
        basename = os.path.splitext(basename)[0]
        info_path = os.path.join(output_directory, f"{basename}.yaml")
        bin_data_path = os.path.join(output_directory, f"{basename}.npy")
        yaml.dump(info, open(info_path, 'w'), allow_unicode=True)
        save_binary_to_file(indexes, bin_data_path)

    @classmethod
    def livedoor_files_to_index(cls, file_list: List[str], characters: dict, out_put_directory: str) -> None:
        for file in file_list:
            cls.livedoor_file_to_index(file, out_put_directory, characters)

    @classmethod
    def save_index_data(cls, original_path_name: str, index_data: List[int], out_put_directory: str) -> None:
        base_name = os.path.basename(original_path_name)
        file_name = os.path.splitext(base_name)[0]
        out_data_file_path = os.path.join(out_put_directory, f"{file_name}.npy")
        out_info_file_path = os.path.join(out_put_directory, f"{file_name}.yaml")
        info_data = {
            "original_path_name": original_path_name,
            "size": len(index_data),
        }
        save_binary_to_file(int_array=index_data, file_path=out_data_file_path)
        yaml.dump(info_data, open(out_info_file_path, 'w'), allow_unicode=True)

    @classmethod
    def text_to_index(
        cls,
        data_directory: str,
        characters_file_path: str,
        out_put_directory: str,
        sampling_config: SamplingConfig,
        ignore_file_names: List[str] = []
    ) -> None:
        files = cls.enum_file(
            data_directory=data_directory,
            sampling_config=sampling_config,
            ignore_file_names=ignore_file_names
        )
        characters = load_characters(characters_file_path)
        for file in files:
            info, body = read_livedoor_file(file)
            index_data = text_to_index(body, characters)
            cls.save_index_data(original_path_name=file, index_data=index_data, out_put_directory=out_put_directory)

    @classmethod
    def split_batch(cls, file_list: List[str], batch_size: int) ->List[List[str]]:
        """
        Split the file list into batches of a specified size.
        """
        batches = []
        for i in range(0, len(file_list), batch_size):
            batch = file_list[i:i + batch_size]
            batches.append(batch)
        return batches

    @classmethod
    def text_to_index_parallel(
        cls,
        data_directory: str,
        characters_file_path: str,
        out_put_directory: str,
        sampling_config: SamplingConfig,
        batch_size: int = 10,
        max_workers: int = 4,
        ignore_file_names: List[str] = []
    ) -> None:
        files = cls.enum_file(
            data_directory=data_directory,
            sampling_config=sampling_config,
            ignore_file_names=ignore_file_names
        )
        characters = load_characters(characters_file_path)
        batches = cls.split_batch(files, batch_size)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for batch in batches:
                executor.submit(cls.livedoor_files_to_index, batch, characters, out_put_directory)
