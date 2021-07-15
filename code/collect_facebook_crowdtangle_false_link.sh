#!/bin/bash

TODAY_DATE=$(date +"%Y-%m-%d")

minet ct search \
"https://beforeitsnews.com/eu/2021/04/stay-away-from-the-vaxxed-it-is-official-from-pfizers-own-documents-2671454.html" \
  --search-field include_query_strings --platform facebook --start-date 2019-01-01 > \
  "./data/facebook_crowdtangle_raw_false_link_${TODAY_DATE}.csv"

# On minet's new banch only for now. 
# TO DO: change when minet's new version will be released.

lminet fb post-stats post_url "./data/facebook_crowdtangle_raw_false_link_${TODAY_DATE}.csv" \
  -s post_url > "./data/facebook_crowdtangle_false_link_${TODAY_DATE}.csv"