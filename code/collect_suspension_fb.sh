#!/bin/bash

LIST=$1
TODAY_DATE=$(date +"%Y-%m-%d")

minet ct posts --list-ids $LIST --start-date 2019-01-01 > \
  "./data/crowdtangle_facebook_trump_${TODAY_DATE}.csv"
