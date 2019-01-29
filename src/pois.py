# Copyright 2018 Florian Pigorsch. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import s2sphere
from typing import (List, Optional)

from .track import Track
from .utils import distance


class Pois:
    def __init__(self):
        self._pois = []

    def set_poi_file(self, file_name: str):
        self._pois = []
        with open(file_name) as f:
            for line in f:
                line = line.strip()
                split_line = line.split(';')
                if len(split_line) != 3:
                    continue
                self._pois.append(
                    (split_line[2],
                     s2sphere.LatLng.from_degrees(float(split_line[0]), float(split_line[1])))
                )

    def get_pois(self, track: Track) -> List[str]:
        candidates = []
        for poi in self._pois:
            latlng = poi[1]
            if track._bbox.contains(latlng):
                candidates.append(poi)
        if len(candidates) == 0:
            return []
        pois = []
        for segment in track._segments:
            for point in segment:
                new_candidates = []
                for poi in candidates:
                    if distance(poi[1], point._lat_lng) <= 100:
                        pois.append(poi[0])
                    else:
                        new_candidates.append(poi)
                if len(new_candidates) < len(candidates):
                    candidates = new_candidates
                    if len(candidates) == 0:
                        return pois
        return pois

    def get_coordinates(self, name: str) -> Optional[s2sphere.LatLng]:
        for poi in self._pois:
            if poi[0] == name:
                return poi[1]
        return None
