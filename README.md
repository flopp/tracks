![License MIT](https://img.shields.io/badge/license-MIT-lightgrey.svg?style=flat)]

# tracks
A static generator for a single-page, map-based website showing your activities from Garmin Connect.

Demo site: https://tracks.flopp.net/

## Install

```
git clone --recurse-submodules https://github.com/flopp/tracks.git
cd tracks

# setup python
python3.6 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt
```

## Run

```
GARMIN_ACCOUNT='my-garmin-account'
GARMIN_PASSWORD='my-garmin-password'
venv/bin/python main.py --sync --export-dir my-export-dir
```

This may take a while (especially on the first run), since all (new) activities are fetched from Garmin Connect.


## Third-Party Stuff

- https://github.com/petergardfjall/garminexport


## License
Copyright 2018, 2019 Florian Pigorsch & Contributors. All rights reserved.

Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.