import pandas as pd
import os
import argparse
import requests
import json

from io import StringIO
from utils import Logger, FEATURE_SET_NAME

from prepare import load_features, init_default_store


def create_featureset():
    init_default_store()
    load_features(FEATURE_SET_NAME)


def prepare():
    pass


def train():
    pass


def search():
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Import Redis data into MySQL.')

    parser.add_argument('-e', '--feature', required=False, default="ALL",
                        help='Ecompany to run the script for.')
    parser.add_argument('-mo', '--model', required=False, default="ALL",
                        help='The redis model that will be imported.')
    parser.add_argument('-me', '--metric', required=False, default="ALL",
                        help='The redis metric that will be imported.')
    parser.add_argument('-st', '--start_ts', required=False, type=long, default=None,
                        help='Time range start on the data slice in miliseconds.')
    parser.add_argument('-et', '--end_ts', required=False, type=long, default=now(),
                        help='Time range end on the data slice in miliseconds.')
    parser.add_argument('--days-back', required=False, type=int, default=None,
                        help='Relative time range based on ending timestamp in days.')
    # this one maybe should be required
    parser.add_argument('--hours-back', required=False, type=int, default=None,
                        help='Relative time range based on ending timestamp in hours.')
    parser.add_argument('--override', required=False, type=bool, default=True,
                        help='Whether we should override the MySQL data.')

    args = parser.parse_args()