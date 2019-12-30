#!/usr/bin/env python

# Copyright 2018 Florian Pigorsch. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.


import argparse
import datetime
import os
import time

from src.tracks import Tracks
from vendor.garminexport.garminexport import backup, garminclient, retryer


def sync(directory, username, password):
    os.makedirs(directory, exist_ok=True)
    retry = retryer.Retryer(
        delay_strategy=retryer.ExponentialBackoffDelayStrategy(
            initial_delay=datetime.timedelta(seconds=1)
        ),
        stop_strategy=retryer.MaxRetriesStopStrategy(2),
    )
    formats = ["fit"]
    with garminclient.GarminClient(username, password) as client:
        activities = set(retry.call(client.list_activities))
        print(f"{username} has {len(activities)} activities")
        missing_activities = backup.need_backup(activities, directory, formats)
        print(f"missing activities: {len(missing_activities)}")
        for activity in missing_activities:
            activity_id, start = activity
            print(f"fetching: {activity_id} / {start}")
            backup.download(client, activity, retry, directory, formats)


def copy_file(source, target, timestamp):
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(source, "r") as f:
        data = f.read()
    data = data.replace("{{TIMESTAMP}}", timestamp)
    with open(target, "w") as f:
        f.write(data)


def main():
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument("--cache-dir", dest="cache_dir", metavar="DIR", type=str)
    args_parser.add_argument(
        "--export-dir", dest="export_dir", metavar="DIR", type=str, default="export"
    )
    args_parser.add_argument("--poi-file", dest="poi_file", metavar="FILE", type=str)
    args_parser.add_argument("--sync", dest="sync", action="store_true")
    args_parser.add_argument("--clear-cache", dest="clear_cache", action="store_true")
    args = args_parser.parse_args()

    t = Tracks()
    if args.poi_file:
        t.set_poi_file(args.poi_file)
    t.set_export_dir(args.export_dir)
    if args.cache_dir:
        t.set_cache_dir(args.cache_dir)
    if args.clear_cache:
        t.clear_cache_dir()

    tracks_data_dir = os.path.join(t._cache_dir, "garmin-connect")
    os.makedirs(tracks_data_dir, exist_ok=True)

    if args.sync:
        print("syncing")
        GARMIN_ACCOUNT = os.environ["GARMIN_ACCOUNT"]
        GARMIN_PASSWORD = os.environ["GARMIN_PASSWORD"]
        sync(tracks_data_dir, GARMIN_ACCOUNT, GARMIN_PASSWORD)

    print("loading & exporting")
    t.load_tracks(tracks_data_dir)

    timestamp = f"{int(time.time())}"
    copy_file(
        "assets/index.html", os.path.join(args.export_dir, "index.html"), timestamp
    )
    copy_file(
        "assets/style.css",
        os.path.join(args.export_dir, "assets", "style.css"),
        timestamp,
    )
    copy_file(
        "assets/map.js", os.path.join(args.export_dir, "assets", "map.js"), timestamp
    )


if __name__ == "__main__":
    main()
