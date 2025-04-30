
import os
from typing import List, Tuple
import math
import random
import numpy as np
import scipy
import scipy.sparse
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from syslog import syslog, LOG_ERR, LOG_INFO


def load_characters(file_path: str) -> np.ndarray:
    """
0	5851	$
1	3217	の
2	2899	０
3	2559	い
    """
    indexes = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        vec2 = []
        for line in lines:
            splited = line.split('\t')
            if len(splited) != 3:
                continue
            index = int(splited[0])
            indexes.append(index)
            vec2.append([index, int(splited[1]), splited[2].strip()])
    if max(indexes) != len(vec2) - 1:
        raise ValueError("Index mismatch: max index does not match the number of characters.")
    return np.array(vec2, dtype=object)


def get_max_index(characters: np.ndarray) -> int:
    max_index = 0
    for c in characters:
        if c[0] > max_index:
            max_index = c[0]
    return max_index


def index_to_char(characters: np.ndarray, index: int) -> str:
    """
    Convert an index to a character using the provided character mapping.

    Args:
        characters (np.ndarray): The array containing character mappings.
        index (int): The index to convert.

    Returns:
        str: The corresponding character.
    """
    for c in characters:
        if c[0] == index:
            return c[2]
    raise ValueError(f"Index {index} not found in characters.")


def enum_file(directory: str, ignore_file_names: List[str] = []) -> List[str]:
    """
    拡張子 npy のファイルを列挙
    """
    files = []
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".npy") and filename not in ignore_file_names:
                files.append(os.path.join(root, filename))
    return files


def load_indexed_file(file_path: str) -> np.ndarray:
    x = np.load(file_path, allow_pickle=True)
    return x


def create_vector(indexes: np.ndarray, max_index: int, window_size: int = 5) -> np.ndarray:
    vector2 = []
    for i in range(len(indexes) - window_size + 1):
        wnd = indexes[i:i + window_size]
        vec = [0] * max_index
        for ii, idx in enumerate(wnd):
            if idx < 0:
                continue
            vec[idx] += (1 / (ii + 1))
            # vec[idx] += math.exp(0.5 * ii)
            # vec[idx] += 1 / math.log(ii + 2)
        vector2.append(vec)
    return np.array(vector2, dtype=np.float32)


def save_vector(vector: np.ndarray, file_path: str) -> None:
    # convert to sparse matrix
    x = scipy.sparse.csr_matrix(vector)
    scipy.sparse.save_npz(file_path, x)


def load_vector(file_path: str) -> np.ndarray:
    x = scipy.sparse.load_npz(file_path)
    return x.toarray()


def extract_valid_columns(x: np.ndarray, start_idx: int = 0, get_size: int=10) -> List[List[Tuple[[int, float]]]]:
    result = []
    for r in x[start_idx:start_idx + get_size]:
        filterd_indexes = np.where(r > 0)[0]
        result_sub = []
        for i in filterd_indexes:
            result_sub.append([i, r[i]])
        result_sub.sort(key=lambda xx: xx[1], reverse=True)
        result.append(result_sub)
    return result


def create_vector_from_file(
    file_path: str,
    max_index: int,
    output_file_path: str,
    window_size: int = 5
) -> SimpleNamespace:
    exit_status = None
    try:
        indexes = load_indexed_file(file_path)
        vector = create_vector(indexes=indexes, max_index=max_index, window_size=window_size)
        save_vector(vector, output_file_path)
        exit_status = SimpleNamespace(
            success=True,
            file_path=file_path,
            output_file_path=output_file_path,
            vector_width=vector.shape[1],
            vector_height=vector.shape[0],
            message="success"
        )
    except Exception as e:
        exit_status = SimpleNamespace(
            success=False,
            file_path=file_path,
            output_file_path=output_file_path,
            vector_width=-1,
            vector_height=-1,
            message=f"error: {str(e)}"
        )
        syslog(LOG_ERR, exit_status.message)
    finally:
        syslog(LOG_INFO, f"create_vector_from_file, status=f{exit_status.success}, file_path={exit_status.file_path}, output_file_path={exit_status.output_file_path}, message={exit_status.message}")
        return exit_status


def create_vector_from_files(
    files: List[str],
    max_index: int,
    output_directory: str,
    window_size: int = 5
) -> List[SimpleNamespace]:
    exit_statuses = []
    for file_path in files:
        file_name = os.path.basename(file_path)
        # 拡張子を npz に修正
        base_file_name = os.path.splitext(file_name)[0]
        output_file_path = os.path.join(output_directory, f"{base_file_name}.npz")
        exit_status = create_vector_from_file(
            file_path=file_path,
            max_index=max_index,
            output_file_path=output_file_path,
            window_size=window_size
        )
        exit_statuses.append(exit_status)
    return exit_statuses


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
        if self.sampling_count > 0:
            self.sampling = True
            self.sampling_type = "count"
        elif self.sampling_rate > 0:
            self.sampling = True
            self.sampling_type = "rate"


class SetupVector:
    @classmethod
    def enum_file(cls, sampling_config: SamplingConfig, directory: str, ignore_file_names: List[str] = []) -> List[str]:
        files = enum_file(directory, ignore_file_names=ignore_file_names)
        if sampling_config.sampling:
            sampling_count = 0
            if sampling_config.sampling_type == "count":
                sampling_count = sampling_config.sampling_count
            elif sampling_config.sampling_type == "rate":
                sampling_count = int(len(files) * sampling_config.sampling_rate)
            else:
                raise ValueError(f"Invalid sampling type: {sampling_config.sampling_type}")
            files = random.sample(files, sampling_count)
        return files

    @classmethod
    def create_vector(
        cls,
        characters_file_path: str,
        input_directory: str,
        output_directory: str,
        sampling_config: SamplingConfig,
        window_size: int
    ):
        """
        Create vectors from files in the input directory and save them to the output directory.

        Args:
            input_directory (str): The directory containing input files.
            output_directory (str): The directory to save output vectors.
        """
        characters = load_characters(file_path=characters_file_path)
        max_index = get_max_index(characters)
        files = cls.enum_file(sampling_config=sampling_config, directory=input_directory, ignore_file_names=[])
        create_vector_from_files(
            files=files,
            max_index=max_index,
            output_directory=output_directory,
            window_size=window_size
        )

    @classmethod
    def split_batches(cls, files: List[str], batch_size: int) -> List[List[str]]:
        batches = []
        for i in range(0, len(files), batch_size):
            batches.append(files[i:i + batch_size])
        return batches

    @classmethod
    def create_vector_parallel(
        cls,
        characters_file_path: str,
        input_directory: str,
        output_directory: str,
        batch_size: int,
        sampling_config: SamplingConfig,
        window_size: int,
        max_workers: int
    ):
        characters = load_characters(file_path=characters_file_path)
        max_index = get_max_index(characters)
        files = cls.enum_file(sampling_config=sampling_config, directory=input_directory, ignore_file_names=[])
        batches = cls.split_batches(files, batch_size)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for batch in batches:
                future = executor.submit(
                    create_vector_from_files,
                    files=batch,
                    max_index=max_index,
                    output_directory=output_directory,
                    window_size=window_size
                )
                futures.append(future)

            for future in futures:
                future.result()

