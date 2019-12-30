# Copyright 2018 Florian Pigorsch. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import appdirs
import os
import shutil
import sys
import traceback

from .config import __app_name__, __author__
from .geocoder import Geocoder
from .pois import Pois
from .track import Track
from . import utils


class Tracks:
    def __init__(self):
        self._cache_dir = appdirs.user_cache_dir(__app_name__, __author__)
        self._pois = Pois()
        self._geocoder = Geocoder()
        self._geocoder.set_cache_dir(self._cache_dir)
        self._tracks = []
        self._export_dir = None

    def set_poi_file(self, file_name: str):
        self._pois.set_poi_file(file_name)

    def set_cache_dir(self, directory: str):
        self._cache_dir = directory
        self._geocoder.set_cache_dir(self._cache_dir)

    def set_export_dir(self, directory: str):
        self._export_dir = directory

    def clear_cache_dir(self):
        if os.path.isdir(self._cache_dir):
            shutil.rmtree(self._cache_dir)

    def load_tracks(self, directory: str):
        os.makedirs(os.path.join(self._export_dir, "assets", "tracks"), exist_ok=True)
        for file_name in utils.collect_files(directory, [".fit", ".gpx"]):
            print(f"loading: {file_name}")
            try:
                t = self.load_track(file_name)
                if t._start_time is None:
                    continue
                with open(
                    os.path.join(
                        self._export_dir, "assets", "tracks", f"{t._hash}.json"
                    ),
                    "w",
                ) as file:
                    file.write('{"polyline":  [')
                    first = True
                    for segment in t._segments:
                        for point in segment:
                            if not first:
                                file.write(",")
                            else:
                                first = False
                            file.write(
                                f"\n[{point._lat_lng.lat().degrees:.5f},{point._lat_lng.lng().degrees:.5f}]"
                            )
                    file.write("\n]}\n")
                    t._segments = None
                self._tracks.append(t)
            except Exception as e:
                print(f"Error while loading {file_name}: {e}")
                traceback.print_exception(*sys.exc_info())
                continue
        self._tracks.sort(key=lambda t: t._start_time, reverse=True)

        with open(os.path.join(self._export_dir, "assets", "data.js"), "w") as file:
            file.write("const data = [\n")
            for track in self._tracks:
                file.write("{\n")
                self._write_field(file, "hash", track._hash)
                self._write_field(file, "type", track._type)
                self._write_field(file, "location", track._location)
                self._write_field(
                    file, "distance", track._distance, self._format_distance
                )
                self._write_field(
                    file, "start_time", track._start_time, self._format_time
                )
                self._write_field(
                    file, "timer_time", track._timer_time, self._format_timedelta
                )
                self._write_field(
                    file, "elapsed_time", track._elapsed_time, self._format_timedelta
                )
                file.write(f'"pois": [\n')
                for poi in track._pois:
                    latlng = self._pois.get_coordinates(poi)
                    if latlng is not None:
                        file.write(
                            f'{{"name": "{poi}", \
                                    "lat": {latlng.lat().degrees:.5f}, \
                                    "lng": {latlng.lng().degrees:.5f}}},\n'
                        )
                file.write(f"]\n")
                file.write("},\n")
            file.write("];\n")

    def load_track(self, file_name: str) -> Track:
        with open(file_name, "rb") as file:
            raw_data_1024 = file.read(1024)
        file_hash = utils.compute_hash(file_name, raw_data_1024)
        cache_file_name = os.path.join(self._cache_dir, "tracks", file_hash)
        t = Track()
        if os.path.isfile(cache_file_name):
            t.load_from_cache(cache_file_name, file_name)
            t._hash = file_hash
        else:
            try:
                t.load(file_name)
            except Exception as e:
                print(f"Exception during file load: {e}")
                t._error = "Error while loading file"
            t._hash = file_hash
            t.save_to_cache(cache_file_name)
        t._pois = self._pois.get_pois(t)
        print(f"{file_name} -> {t._pois}")
        if t._location is None:
            latlng = t.get_start_pos()
            if latlng is not None:
                t._location = self._geocoder.get_location(latlng)
        return t

    @staticmethod
    def _write_field(file, label, value, formatter=None):
        if value is None:
            file.write(f'"{label}": "n/a",\n')
        elif formatter is None:
            file.write(f'"{label}": "{value}",\n')
        else:
            file.write(f'"{label}": {formatter(value)},\n')

    @staticmethod
    def _format_distance(value):
        return f'"{value * 0.001:.2f} km"'

    @staticmethod
    def _format_time(value):
        return value.strftime('"%Y-%m-%d %H:%M:%S"')

    @staticmethod
    def _format_timedelta(value):
        seconds = int(value.total_seconds())
        hours = seconds // 3600
        seconds -= 3600 * hours
        minutes = seconds // 60
        seconds -= 60 * minutes
        return f'"{hours}:{minutes:02}:{seconds:02}"'

    @staticmethod
    def _format_list(value):
        return "[" + ", ".join([f'"{v}"' for v in value]) + "]"
