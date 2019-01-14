#!/usr/bin/env python

# Copyright 2018 Florian Pigorsch. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import datetime
import s2sphere


class TrackPoint:
    def __init__(self, time: datetime.datetime, lat_lng: s2sphere.LatLng, altitude: float):
        self._time = time
        self._lat_lng = lat_lng
        self._altitude = altitude

    def serialize(self, base_time: datetime.datetime) -> str:
        time = int((self._time - base_time).total_seconds())
        lat = self._lat_lng.lat().degrees
        lng = self._lat_lng.lng().degrees
        if self._altitude is not None:
            return f'{time},{lat:.6f},{lng:.6f},{self._altitude:.1f}'
        return f'{time},{lat:.6f},{lng:.6f}'

    @staticmethod
    def deserialize(s: str, base_time: datetime.datetime) -> 'TrackPoint':
        tokens = s.split(',')
        if (len(tokens) != 3) and (len(tokens) != 4):
            raise Exception(f'cannot deserialize track point: {s}')

        time = base_time + datetime.timedelta(seconds=int(tokens[0]))
        lat = float(tokens[1])
        lng = float(tokens[2])
        altitude = None
        if len(tokens) == 4:
            altitude = float(tokens[3])

        return TrackPoint(
            time,
            s2sphere.LatLng.from_degrees(lat, lng),
            altitude)
