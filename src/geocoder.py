# Copyright 2018 Florian Pigorsch. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import geopy
import os
import s2sphere

from .config import __agent__


class Geocoder:
    def __init__(self):
        self._geocoder = geopy.geocoders.Nominatim(user_agent=__agent__)
        self._cache_dir = None
        self._cache = {}

    def set_cache_dir(self, directory: str):
        self._cache_dir = directory

    def get_location(self, latlng: s2sphere.LatLng) -> str:
        lat1000 = int(round(latlng.lat().degrees * 1000))
        lng1000 = int(round(latlng.lng().degrees * 1000))
        key = f'{lat1000}:{lng1000}'

        if key in self._cache:
            return self._cache[key]

        if self._load_cache(key):
            return self._cache[key]

        location = self._geocoder.reverse(f'{lat1000 * 0.001:f}, {lng1000 * 0.001:f}')
        if 'address' in location.raw:
            address = location.raw['address']
            country = address['country'] if 'country' in address else None
            city = None
            for city_key in ['hamlet', 'village', 'town', 'city']:
                if city_key in address:
                    city = address[city_key]
                    break
            a = []
            if city is not None:
                a.append(city)
            if country is not None:
                a.append(country)
            if len(a) > 0:
                self._cache[key] = ', '.join(a)
            else:
                self._cache[key] = 'Unknown'
        else:
            self._cache[key] = 'Unknown'

        self._store_cache(key)

        return self._cache[key]

    def _load_cache(self, key: str) -> bool:
        cache_file_name = os.path.join(self._cache_dir, 'location', key)
        if os.path.isfile(cache_file_name):
            with open(cache_file_name) as file:
                self._cache[key] = file.read()
            return True
        return False

    def _store_cache(self, key: str):
        cache_file_name = os.path.join(self._cache_dir, 'location', key)
        os.makedirs(os.path.dirname(cache_file_name), exist_ok=True)
        with open(cache_file_name, 'w') as file:
            file.write(self._cache[key])

