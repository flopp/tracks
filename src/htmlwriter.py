# Copyright 2018 Florian Pigorsch. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import datetime
import jinja2
import os
import shutil
from typing import Optional

from .track import Track
from .tracks import Tracks


class HtmlWriter:
    def __init__(self):
        self._base_url = None
        self._export_dir = None
        self._assets_dir = None
        self._jinja = None

    def set_base_url(self, url: str):
        self._base_url = url

    def set_export_dir(self, directory: str):
        self._export_dir = directory

    def set_templates_dir(self, directory: str):
        self._jinja = jinja2.Environment(loader=jinja2.FileSystemLoader(directory))
        self._jinja.filters['datetime'] = self._format_datetime
        self._jinja.filters['timedelta'] = self._format_timedelta
        self._jinja.filters['distance'] = self._format_distance

    @staticmethod
    def _format_datetime(t: Optional[datetime.datetime]) -> str:
        if t is None:
            return 'n/a'
        return t.strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def _format_timedelta(t: Optional[datetime.timedelta]) -> str:
        if t is None:
            return 'n/a'
        seconds = int(t.total_seconds())
        hours = seconds // 3600
        seconds -= 3600 * hours
        minutes = seconds // 60
        seconds -= 60 * minutes
        return f'{hours}:{minutes:02}:{seconds:02}'

    @staticmethod
    def _format_distance(d: Optional[float]) -> str:
        if d is None:
            return 'n/a'
        return f'{d * 0.001:.2f} km'

    def set_assets_dir(self, directory: str):
        self._assets_dir = directory

    def export(self, tracks: Tracks):
        assert self._export_dir is not None
        assert self._assets_dir is not None
        assert self._jinja is not None

        self._copy_asset('map.js', os.path.join(self._export_dir, 'assets', 'map.js'))
        self._copy_asset('map2.js', os.path.join(self._export_dir, 'assets', 'map2.js'))
        self._copy_asset('style.css', os.path.join(self._export_dir, 'assets', 'style.css'))

        #self._export_tracks_list(tracks)
        #for index, track in enumerate(tracks._tracks):
        #    self._export_track(track,
        #                       tracks._tracks[index + 1] if index + 1 < len(tracks._tracks) else None,
        #                       tracks._tracks[index - 1] if index > 0 else None)
        #
        with open(os.path.join(self._export_dir, 'assets', 'data.js'), 'w') as file:
            file.write('const data = [\n')
            for track in tracks._tracks:
                file.write('{\n')
                self.write_field(file, 'hash', track._hash)
                self.write_field(file, 'type', track._type)
                self.write_field(file, 'location', track._location)
                self.write_field(file, 'distance', track._distance, self.format_distance)
                self.write_field(file, 'start_time', track._start_time, self.format_time)
                self.write_field(file, 'timer_time', track._timer_time, self.format_timedelta)
                self.write_field(file, 'elapsed_time', track._elapsed_time, self.format_timedelta)
                self.write_field(file, 'pois', track._pois, self.format_list)
                file.write('},\n')
            file.write('];\n')
        with open(os.path.join(self._export_dir, 'index.html'), 'w') as file:
            template = self._jinja.get_template('index2.html')
            file.write(template.render(base_dir='.'))
        for track in tracks._tracks:
            with open(os.path.join(self._export_dir, 'assets', f'track-{track._hash}.json'), 'w') as file:
                file.write('{"polyline":  [')
                first = True
                for segment in track._segments:
                    for point in segment:
                        if not first:
                            file.write(',')
                        else:
                            first = False
                        file.write(f'\n[{point._lat_lng.lat().degrees:.5f},{point._lat_lng.lng().degrees:.5f}]')
                file.write('\n]}\n')

    def write_field(self, file, label, value, formatter=None):
        if value is None:
            file.write(f'"{label}": "n/a",\n')
        elif formatter is None:
            file.write(f'"{label}": "{value}",\n')
        else:
            file.write(f'"{label}": {formatter(value)},\n')

    def format_distance(self, value):
        return f'"{value * 0.001:.2f} km"'

    def format_time(self, value):
        return value.strftime('"%Y-%m-%d %H:%M:%S"')

    def format_timedelta(self, value):
        seconds = int(value.total_seconds())
        hours = seconds // 3600
        seconds -= 3600 * hours
        minutes = seconds // 60
        seconds -= 60 * minutes
        return f'"{hours}:{minutes:02}:{seconds:02}"'

    def format_list(self, value):
        return '[' + ', '.join([f'"{v}"' for v in value]) + ']'

    def _copy_asset(self, file_name: str, target_file_name: str):
        os.makedirs(os.path.dirname(target_file_name), exist_ok=True)
        shutil.copyfile(os.path.join(self._assets_dir, file_name), target_file_name)

    def _export_tracks_list(self, tracks: Tracks):
        os.makedirs(self._export_dir, exist_ok=True)
        file_name = os.path.join(self._export_dir, 'index.html')
        with open(file_name, 'w') as file:
            template = self._jinja.get_template('index.html')
            file.write(template.render(tracks=tracks._tracks, base_dir='.'))

    def _export_track(self, track: Track, prev_track: Track, next_track: Track):
        os.makedirs(os.path.join(self._export_dir, 'activity'), exist_ok=True)
        file_name = os.path.join(self._export_dir, 'activity', f'{track._id}.html')
        with open(file_name, 'w') as file:
            template = self._jinja.get_template('activity.html')
            file.write(template.render(track=track, prev_track=prev_track, next_track=next_track, base_dir='..'))

