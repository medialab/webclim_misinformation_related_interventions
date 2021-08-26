#!/bin/bash

TODAY_DATE=$(date +"%Y-%m-%d")

minet ct summary url "./data/appearances_july.csv" \
 --posts "./data/facebook_false_links_${TODAY_DATE}.csv" \
 --sort-by total_interactions --start-date 2021-01-01 --platforms facebook

# On minet's new banch only for now. 

lminet fb post-flags post_url "./data/facebook_false_links_${TODAY_DATE}.csv" \
  -s post_url > "./data/facebook_false_links_flags_${TODAY_DATE}.csv"

# minet ct search \
# "https://beforeitsnews.com/eu/2021/04/stay-away-from-the-vaxxed-it-is-official-from-pfizers-own-documents-2671454.html" \
#   --search-field include_query_strings --platform facebook --start-date 2019-01-01 > \
#   "./data/facebook_crowdtangle_raw_false_link_${TODAY_DATE}.csv"
