# -*- coding: UTF-8 -*-

from os import makedirs
from os.path import exists, isdir, realpath

__all__ = ["check_folder_path", "read_file", "write_file"]


def check_folder_path(path: str) -> str:
    path: str = realpath(path)

    if (not exists(path)) and (not isdir(path)):
        makedirs(path, exist_ok=True)

    return path


def read_file(path: str) -> str:
    with open(path, "r", encoding="UTF-8") as file_handle:
        return file_handle.read()


def write_file(data: str, path: str):
    with open(path, "w", encoding="UTF-8") as file_handle:
        file_handle.write(data)
