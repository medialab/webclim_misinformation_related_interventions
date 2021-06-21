#!/bin/bash

TODAY_DATE=$(date +"%Y-%m-%d")

minet ct search "infowars.com" --search-field include_query_strings \
  --platform facebook --start-date 2018-01-01 --end-date 2021-06-15 > \
  "./data/facebook_crowdtangle_infowars_${TODAY_DATE}.csv"