# Copyright 2018 Florian Pigorsch. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import appdirs
import concurrent.futures
import os
import shutil

from .geocoder import Geocoder
from .peaks import Peaks
from .track import Track
from . import utils

__app_name__ = 'static-strava'
__app_author__ = 'flopp.net'


class Tracks:
    def __init__(self):
        self._cache_dir = appdirs.user_cache_dir(__app_name__, __app_author__)
        self._pois = Peaks()
        self._geocoder = Geocoder()
        self._geocoder.set_cache_dir(self._cache_dir)
        self._tracks = []

    def set_poi_file(self, file_name: str):
        self._pois.set_poi_file(file_name)

    def set_cache_dir(self, directory: str):
        self._cache_dir = directory
        self._geocoder.set_cache_dir(self._cache_dir)
        self._peaks.set_cache_dir(self._cache_dir)

    def clear_cache_dir(self):
        if os.path.isdir(self._cache_dir):
            shutil.rmtree(self._cache_dir)

    def load_tracks(self, directory: str):
        with concurrent.futures.ProcessPoolExecutor() as executor:
            future_to_file_name = {
                executor.submit(self.load_track, self._cache_dir, file_name):
                    file_name for file_name in utils.collect_files(directory, ['.fit', '.gpx'])
            }
        for future in concurrent.futures.as_completed(future_to_file_name):
            file_name = future_to_file_name[future]
            try:
                t = future.result()
            except Exception as e:
                print(f'Error while loading {file_name}: {e}')
            else:
                self._tracks.append(t)

        for i in range(len(self._tracks)):
            if self._tracks[i]._location is not None:
                continue
            latlng = self._tracks[i].get_start_pos()
            if latlng is None:
                continue
            self._tracks[i]._location = self._geocoder.get_location(latlng)

        for i in range(len(self._tracks)):
            pois = self._pois.get_pois(self._tracks[i])
            self._tracks[i]._pois = pois
            if len(pois) > 0:
                print(' '.join(pois))

        self._tracks.sort(key=lambda t: t._start_time, reverse=True)

    @staticmethod
    def load_track(cache_dir: str, file_name: str) -> Track:
        with open(file_name, 'rb') as file:
            raw_data_1024 = file.read(1024)
        hash = utils.compute_hash(file_name, raw_data_1024)
        cache_file_name = os.path.join(
            cache_dir,
            'tracks',
            hash
        )
        t = Track()
        if os.path.isfile(cache_file_name):
            t.load_from_cache(cache_file_name, file_name)
            t._hash = hash
        else:
            t.load(file_name)
            t._hash = hash
            t.save_to_cache(cache_file_name)
        return t
