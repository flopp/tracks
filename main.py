#!/usr/bin/env python

# Copyright 2018 Florian Pigorsch. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.


import argparse
import datetime
import os

from src.htmlwriter import HtmlWriter
from src.tracks import Tracks
from vendor.garminexport.garminexport import (backup, garminclient, retryer)


def sync(data_dir, username, password):
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)
    retry = retryer.Retryer(
        delay_strategy=retryer.ExponentialBackoffDelayStrategy(
            initial_delay=datetime.timedelta(seconds=1)),
        stop_strategy=retryer.MaxRetriesStopStrategy(2))
    formats = ['fit']
    with garminclient.GarminClient(username, password) as client:
        activities = set(retry.call(client.list_activities))
        missing_activities = backup.need_backup(activities, data_dir, formats)
        for activity in missing_activities:
            backup.download(client, activity, retry, data_dir, formats)


def main():
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('--data-dir', dest='data_dir', metavar='DIR', type=str, required=True)
    args_parser.add_argument('--cache-dir', dest='cache_dir', metavar='DIR', type=str)
    args_parser.add_argument('--export-dir', dest='export_dir', metavar='DIR', type=str, default='export')
    args_parser.add_argument('--templates-dir', dest='templates_dir', metavar='DIR', type=str, default='templates')
    args_parser.add_argument('--assets-dir', dest='assets_dir', metavar='DIR', type=str, default='assets')
    args_parser.add_argument('--base-url', dest='base_url', metavar='URL', type=str)
    args_parser.add_argument('--clear-cache', dest='clear_cache', action='store_true')
    args = args_parser.parse_args()

    print('syncing')
    GARMIN_ACCOUNT = os.environ['GARMIN_ACCOUNT']
    GARMIN_PASSWORD = os.environ['GARMIN_PASSWORD']
    sync(os.path.join(args.data_dir, 'garmin-connect'), GARMIN_ACCOUNT, GARMIN_PASSWORD)
    
    print('loading')
    t = Tracks()
    t.set_poi_file('poi.txt')
    if args.cache_dir:
        t.set_cache_dir(args.cache_dir)
    if args.clear_cache:
        t.clear_cache_dir()
    t.load_tracks(args.data_dir)

    print('exporting')
    h = HtmlWriter()
    h.set_export_dir(args.export_dir)
    h.set_templates_dir(args.templates_dir)
    h.set_assets_dir(args.assets_dir)
    h.set_base_url(args.base_url)
    h.export(t)


if __name__ == '__main__':
    main()
