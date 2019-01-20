import datetime
import hashlib
import os
import s2sphere
from typing import Generator, List


def compute_hash(file_name: str, data: bytes) -> str:
    hash_object = hashlib.sha256()
    hash_object.update(file_name.encode('utf-8'))
    hash_object.update(data)
    return hash_object.hexdigest()


def collect_files(directory: str, extensions: List[str]) -> Generator[str, None, None]:
    abs_dir = os.path.abspath(directory)
    if not os.path.isdir(abs_dir):
        raise Exception(f'Not a directory: {directory}')
    for root, dirs, files in os.walk(abs_dir):
        for file_name in files:
            for extension in extensions:
                if file_name.endswith(extension):
                    yield os.path.join(root, file_name)


def serialize_time(d: datetime.datetime) -> str:
    return d.strftime('%Y-%m-%d %H:%M:%S')


def deserialize_time(s: str) -> datetime.datetime:
    return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')


def distance(p0: s2sphere.LatLng, p1: s2sphere.LatLng) -> float:
    return p0.get_distance(p1).radians * 6378100.0
