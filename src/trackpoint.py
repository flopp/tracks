#!/usr/bin/env python

# Copyright 2018 Florian Pigorsch. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import datetime
import s2sphere
from typing import Optional

from .utils import serialize_time, deserialize_time


class TrackPoint:
    def __init__(
        self,
        time: datetime.datetime,
        lat_lng: s2sphere.LatLng,
        altitude: Optional[float],
    ):
        self._time = time
        self._lat_lng = lat_lng
        self._altitude = altitude

    def serialize(self, prev: "TrackPoint") -> str:
        if prev is None:
            time = serialize_time(self._time)
            lat = int(self._lat_lng.lat().degrees * 1000000.0)
            lng = int(self._lat_lng.lng().degrees * 1000000.0)
            altitude = int(self._altitude) if self._altitude is not None else None
        else:
            time = int((self._time - prev._time).total_seconds())
            lat = int(self._lat_lng.lat().degrees * 1000000.0) - int(
                prev._lat_lng.lat().degrees * 1000000.0
            )
            lng = int(self._lat_lng.lng().degrees * 1000000.0) - int(
                prev._lat_lng.lng().degrees * 1000000.0
            )
            altitude = (
                int(self._altitude) - int(prev._altitude)
                if self._altitude is not None and prev._altitude is not None
                else None
            )
        if altitude is None:
            return f"{time},{lat},{lng}"
        return f"{time},{lat},{lng},{altitude}"

    @staticmethod
    def deserialize(s: str, prev: Optional["TrackPoint"]) -> "TrackPoint":
        tokens = s.split(",")
        if (len(tokens) != 3) and (len(tokens) != 4):
            raise Exception(f"cannot deserialize track point: {s}")

        if prev is None:
            time = deserialize_time(tokens[0])
            lat = int(tokens[1]) / 1000000.0
            lng = int(tokens[2]) / 1000000.0
            altitude = float(tokens[3]) if len(tokens) == 4 else None
        else:
            time = prev._time + datetime.timedelta(seconds=int(tokens[0]))
            lat = prev._lat_lng.lat().degrees + (int(tokens[1]) / 1000000.0)
            lng = prev._lat_lng.lng().degrees + (int(tokens[2]) / 1000000.0)
            altitude = (
                (float(tokens[3]) + prev._altitude)
                if len(tokens) == 4 and prev._altitude is not None
                else None
            )

        return TrackPoint(time, s2sphere.LatLng.from_degrees(lat, lng), altitude)
