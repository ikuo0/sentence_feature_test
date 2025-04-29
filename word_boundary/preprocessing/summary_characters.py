
import os
import random
import sys
from typing import List, Tuple
from word_boundary.preprocessing import normalize_text
from concurrent.futures import ThreadPoolExecutor


def enum_data_file(data_directory: str) -> List[str]:
    txt_files = []
    for current_dir, sub_dirs, files in os.walk(data_directory):
        for file in files:
            if file.endswith(".txt"):
                txt_files.append(os.path.join(current_dir, file))
    return txt_files


def read_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def read_livedoor_file(file_path: str) -> Tuple[dict, str]:
    body = read_file(file_path)
    # １行目はURL、２行目は公開日
    lines = body.splitlines()
    info = {
        "url": lines[0],
        "published_date": lines[1],
    }
    body = "\n".join(lines[2:])
    return info, body


def summary_characters(text: str):
    data = {}
    for c in text:
        if c in data:
            data[c] += 1
        else:
            data[c] = 1
    return data


def summary_file(file_path: str) -> dict:
    text = read_file(file_path)
    text = normalize_text.normalize(text)
    data = summary_characters(text)
    return data


def summary_livedoor_file(file_path: str) -> dict:
    info, text = read_livedoor_file(file_path)
    text = normalize_text.normalize(text)
    data = summary_characters(text)
    return data


def merge_summary_data(data1: dict, data2: dict) -> dict:
    result = {}
    all_keys = set(data1.keys()) | set(data2.keys())
    for k in all_keys:
        v1 = data1.get(k, 0)
        v2 = data2.get(k, 0)
        result[k] = v1 + v2
    return result


class Charcter:
    def __init__(self, c: str, count: int):
        self.c = c
        self.count = count
        self.index = -1

    def __str__(self):
        return f"{self.c}: {self.count}"

    def __repr__(self):
        return str(self.c) + ": " + str(self.count)


def sorted_summary(data: dict) -> List[Charcter]:
    """
    Sort the summary data by count in descending order.
    """
    sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    return [Charcter(c, count) for c, count in sorted_data]


def summary_files(file_list: List[str]) -> dict:
    """
    Summarize the characters in a list of files.
    """
    data = {}
    for file_path in file_list:
        sub_data = summary_file(file_path)
        data = merge_summary_data(data, sub_data)
    return data


def summary_livedoor_files(file_list: List[str]) -> dict:
    """
    Summarize the characters in a list of livedoor files.
    """
    data = {}
    for file_path in file_list:
        sub_data = summary_livedoor_file(file_path)
        data = merge_summary_data(data, sub_data)
    return data


def save_summary_to_file(file_path: str, characters: List[Charcter]):
    lines = []
    for index, character in enumerate(characters):
        character.index = index
        line = "\t".join([
            str(character.index),
            str(character.count),
            str(character.c),
        ])
        lines.append(line)
    body = "\n".join(lines)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(body)


def remove_files_by_name(file_list: List[str], ignore_file_names: List[str]) -> List[str]:
    result = []
    for full_path in file_list:
        file_name = os.path.basename(full_path)
        if file_name in ignore_file_names:
            continue
        result.append(full_path)
    return result


class SamplingConfig:
    def __init__(
            self,
            sampling_count: int = 0,
            sampling_rate: int = 0
        ):
        self.sampling = False
        self.sampling_type = "none"
        self.sampling_count = sampling_count
        self.sampling_rate = sampling_rate
        self.sample_for_confirmation = False
        if self.sampling_count > 0:
            self.sampling = True
            self.sampling_type = "count"
        elif self.sampling_rate > 0:
            self.sampling = True
            self.sampling_type = "rate"


class SummaryCharacters:
    @classmethod
    def enum_files(cls, data_directory: str, sampling_config: SamplingConfig, ignore_file_names: List[str] = []) -> List[str]:
        files = enum_data_file(data_directory)
        if sampling_config.sampling:
            if sampling_config.sampling_type == "count":
                sampling_count = sampling_config.sampling_count
            elif sampling_config.sampling_type == "rate":
                sampling_count = int(len(files) * sampling_config.sampling_rate)
            else:
                raise ValueError(f"Invalid sampling type: {sampling_config.sampling_type}")
            files = random.sample(files, sampling_count)
        files = remove_files_by_name(files, ignore_file_names)
        return files

    @classmethod
    def summary(
        cls,
        data_directory: str,
        out_put_file_name: str,
        sampling_config: SamplingConfig,
        ignore_file_names: List[str] = []
    ) -> dict:
        data = {}
        files = cls.enum_files(
            data_directory=data_directory,
            sampling_config=sampling_config,
            ignore_file_names=ignore_file_names
        )
        for file in files:
            sub_data = summary_livedoor_file(file)
            data = merge_summary_data(data, sub_data)
        sorted_data = sorted_summary(data)
        save_summary_to_file(out_put_file_name, sorted_data)
        return data


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
    def summary_parallel(cls,
        data_directory: str,
        out_put_file_name: str,
        batch_size: int,
        max_workers: int,
        sampling_config: SamplingConfig,
        ignore_file_names: List[str] = []
    ) -> dict:
        data = {}
        files = cls.enum_files(
            data_directory=data_directory,
            sampling_config=sampling_config,
            ignore_file_names=ignore_file_names
        )
        batches = cls.split_batch(files, batch_size)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for batch in batches:
                future = executor.submit(summary_livedoor_files, batch)
                futures.append((future, batch))

            for future, batch in futures:
                sub_data = future.result()
                data = merge_summary_data(data, sub_data)
        sorted_data = sorted_summary(data)
        save_summary_to_file(out_put_file_name, sorted_data)
        return data
