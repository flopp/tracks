#!/usr/bin/env python

# Copyright 2018 Florian Pigorsch. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import datetime
import fitparse
import gpxpy
import os
import s2sphere
from typing import List, Optional

from .trackpoint import TrackPoint
from .utils import serialize_time, deserialize_time


class Track:
    def __init__(self):
        self._error = None
        self._file_name = None
        self._hash = None
        self._type = None
        self._start_time = None
        self._end_time = None
        self._points = []
        self._segments = []
        self._distance = None
        self._elapsed_time = None
        self._timer_time = None
        self._location = None
        self._bbox = None
        self._pois = []

    def clear(self):
        self._error = None
        self._file_name = None
        self._hash = None
        self._type = None
        self._start_time = None
        self._end_time = None
        self._points = []
        self._segments = []
        self._distance = None
        self._elapsed_time = None
        self._timer_time = None
        self._location = None
        self._bbox = None
        self._pois = []

    def get_title(self) -> str:
        title = self._start_time.strftime("%Y-%m-%d %H:%M:%S")
        if self._location is not None:
            title += f": {self._location}"
        if self._distance is not None:
            title += f"; d={self._distance * 0.001:.1f}km"
        if self._elapsed_time is not None:
            seconds = int(self._elapsed_time.total_seconds())
            hours = seconds // 3600
            seconds -= 3600 * hours
            minutes = seconds // 60
            seconds -= 60 * minutes
            title += f"; t={hours}:{minutes:02}:{seconds:02}"
        return title

    def load(self, file_name: str):
        self._segments = []
        if file_name.endswith(".fit"):
            self._load_fit(file_name)
        elif file_name.endswith(".gpx"):
            self._load_gpx(file_name)
        else:
            raise Exception(f"Unknown file type: {file_name}")
        self._file_name = file_name
        self._compute_bbox()

    def get_start_pos(self) -> Optional[s2sphere.LatLng]:
        for segment in self._segments:
            for point in segment:
                return point._lat_lng
        return None

    def _compute_bbox(self):
        self._bbox = s2sphere.LatLngRect()
        for segment in self._segments:
            for point in segment:
                b = s2sphere.LatLngRect.from_point(point._lat_lng)
                self._bbox = self._bbox.union(b)
        if not self._bbox.is_empty():
            self._bbox = self._bbox.expanded(s2sphere.LatLng.from_degrees(0.01, 0.01))

    def _update_time_bounds(self, time: datetime.datetime):
        if self._start_time is None:
            self._start_time = time
            self._end_time = time
        elif time < self._start_time:
            self._start_time = time
        elif time > self._start_time:
            self._end_time = time

    def _load_fit(self, file_name: str):
        self.clear()
        fit = fitparse.FitFile(file_name)
        segment: List[TrackPoint] = []
        debug = False
        for message in fit.get_messages():
            if debug:
                print(
                    message.mesg_type.name
                    if message.mesg_type is not None
                    else message.mesg_type
                )
                print(message.get_values())
            if message.mesg_type is not None:
                if message.mesg_type.name == "session":
                    self._parse_fit_session_message(message)
                elif (message.mesg_type.name == "sport") or (
                    message.mesg_type.name == "lap"
                ):
                    self._parse_fit_sport_message(message)
                elif message.mesg_type.name == "event":
                    event = message.get_values()["event"]
                    event_type = message.get_values()["event_type"]
                    if event == "timer":
                        if (event_type == "stop") or (event_type == "stop_all"):
                            if len(segment) != 0:
                                self._segments.append(segment)
                                segment = []
                elif message.mesg_type.name == "record":
                    time = None
                    lat = None
                    lng = None
                    altitude = None
                    if "timestamp" in message.get_values():
                        time = message.get_values()["timestamp"]
                        self._update_time_bounds(time)
                    if "position_lat" in message.get_values():
                        lat = message.get_values()["position_lat"]
                    if "position_long" in message.get_values():
                        lng = message.get_values()["position_long"]
                    if "altitude" in message.get_values():
                        altitude = message.get_values()["altitude"]
                    if (time is not None) and (lat is not None) and (lng is not None):
                        lat = 180.0 * (float(lat) / float(0x7FFFFFFF))
                        lng = 180.0 * (float(lng) / float(0x7FFFFFFF))
                        p = TrackPoint(
                            time, s2sphere.LatLng.from_degrees(lat, lng), altitude
                        )
                        segment.append(p)
        if len(segment) != 0:
            self._segments.append(segment)

    def _parse_fit_session_message(self, message):
        if "total_elapsed_time" in message.get_values():
            self._elapsed_time = datetime.timedelta(
                seconds=message.get_values()["total_elapsed_time"]
            )
        if "total_timer_time" in message.get_values():
            self._timer_time = datetime.timedelta(
                seconds=message.get_values()["total_timer_time"]
            )
        if "total_distance" in message.get_values():
            self._distance = message.get_values()["total_distance"]

    def _parse_fit_sport_message(self, message):
        sport = None
        sub_sport = None
        type = None
        if "sport" in message.get_values():
            sport = message.get_values()["sport"]
        if "sub_sport" in message.get_values():
            sub_sport = message.get_values()["sub_sport"]
        if sport == "generic":
            if (sub_sport == "generic") or (sub_sport is None):
                pass
        elif sport == "running":
            type = "Running"
            if (sub_sport == "generic") or (sub_sport is None):
                pass
            elif sub_sport == "trail":
                type = "Trail-Running"
            elif sub_sport == "treadmill":
                type = "Indoor"
            else:
                print(f"unknown sport: {sport} / {sub_sport}")
        elif sport == "hiking":
            type = "Hiking"
            if (sub_sport == "generic") or (sub_sport is None):
                pass
            else:
                print(f"unknown sport: {sport} / {sub_sport}")
        elif sport == "walking":
            type = "Walking"
            if (sub_sport == "generic") or (sub_sport is None):
                pass
            else:
                print(f"unknown sport: {sport} / {sub_sport}")
        elif sport == "cycling":
            type = "Cycling"
            if (sub_sport == "generic") or (sub_sport is None):
                pass
            else:
                print(f"unknown sport: {sport} / {sub_sport}")
        elif sport == "training":
            type = "Indoor"
            if (sub_sport == "generic") or (sub_sport is None):
                pass
            elif sub_sport == "cardio_training":
                pass
            else:
                print(f"unknown sport: {sport} / {sub_sport}")
        else:
            print(f"unknown sport: {sport} / {sub_sport}")

        if self._type is not None:
            if type is not None:
                if type != self._type:
                    print(f'Multiple sports in fit file: "{self._type}" and "{type}"')
        else:
            self._type = type

    def _load_gpx(self, file_name: str):
        self.clear()
        with open(file_name, "r") as file:
            raw_data = file.read()
        gpx = gpxpy.parse(raw_data)
        track_type = None
        for t in gpx.tracks:
            if t.type is not None:
                if track_type is not None:
                    if t.type != track_type:
                        print(
                            f'{file_name}: tracks with differing types: "{track_type}" and "{t.type}"'
                        )
                else:
                    track_type = t.type
            for s in t.segments:
                segment = []
                for p in s.points:
                    self._update_time_bounds(p.time)
                    segment.append(
                        TrackPoint(
                            p.time,
                            s2sphere.LatLng.from_degrees(p.latitude, p.longitude),
                            p.elevation,
                        )
                    )
                if len(segment) != 0:
                    self._segments.append(segment)
        self._type = self._map_track_type(track_type)
        (
            moving_time,
            stopped_time,
            moving_distance,
            stopped_distance,
            max_speed,
        ) = gpx.get_moving_data()
        self._distance = moving_distance
        if moving_time is not None:
            self._timer_time = datetime.timedelta(seconds=moving_time)
        if stopped_time is not None:
            self._elapsed_time = datetime.timedelta(seconds=stopped_time)

    def load_from_cache(self, cache_file_name: str, file_name: str):
        self.clear()
        with open(cache_file_name, "r") as file:
            segment: List[TrackPoint] = []
            in_header = True
            last_point = None
            for line in file:
                line = line.strip()
                if in_header:
                    if line.startswith("---"):
                        in_header = False
                        continue
                    key_value = line.split(":", 1)
                    key, value = key_value[0], key_value[1]
                    if key == "hash":
                        self._hash = value
                    elif key == "start":
                        self._start_time = deserialize_time(value)
                    elif key == "end":
                        self._end_time = deserialize_time(value)
                    elif key == "distance":
                        self._distance = float(value)
                    elif key == "elapsed_time":
                        self._elapsed_time = datetime.timedelta(seconds=float(value))
                    elif key == "timer_time":
                        self._timer_time = datetime.timedelta(seconds=float(value))
                    elif key == "location":
                        self._location = value
                    elif key == "type":
                        self._type = value
                    elif key == "error":
                        self._error = value
                    else:
                        print(f"unknown header line: {line}")
                elif line.startswith("---"):
                    if len(segment) != 0:
                        self._segments.append(segment)
                        segment = []
                else:
                    last_point = TrackPoint.deserialize(line, last_point)
                    segment.append(last_point)
            if len(segment) != 0:
                self._segments.append(segment)
        self._file_name = file_name

    def save_to_cache(self, cache_file_name: str):
        os.makedirs(os.path.dirname(cache_file_name), exist_ok=True)
        with open(cache_file_name, "w") as file:
            header = [
                ("hash", self._hash),
                ("start", serialize_time(self._start_time)),
                ("end", serialize_time(self._end_time)),
            ]
            if self._error is not None:
                header.append(("error", self._error))
            if self._distance is not None:
                header.append(("distance", f"{self._distance:.1f}"))
            if self._elapsed_time is not None:
                header.append(
                    ("elapsed_time", f"{self._elapsed_time.total_seconds():.1f}")
                )
            if self._timer_time is not None:
                header.append(("timer_time", f"{self._timer_time.total_seconds():.1f}"))
            if self._location is not None:
                header.append(("location", self._location))
            if self._type is not None:
                header.append(("type", self._type))
            for (key, value) in header:
                file.write(f"{key}:{value}\n")
            file.write("---\n")

            last_point = None
            for segment in self._segments:
                for point in segment:
                    file.write(point.serialize(last_point))
                    file.write("\n")
                    last_point = point
                file.write("---\n")

    @staticmethod
    def _map_track_type(t: Optional[str]) -> Optional[str]:
        if t is None:
            return None
        if (t == "1") or (t == "cycling"):
            return "Cycling"
        if (t == "9") or (t == "running"):
            return "Running"
        if t == "trail_running":
            return "Trail-Running"
        print(f"Cannot map track type: {t}")
        return None
