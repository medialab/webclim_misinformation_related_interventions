#!/bin/bash

LIST=$1
TODAY_DATE=$(date +"%Y-%m-%d")

minet ct posts --list-ids $LIST --start-date 2020-01-01 --end-date 2021-06-15 > \
  "./data/facebook_crowdtangle_trump_${TODAY_DATE}.csv"
