## Truth and Trust online 2021

## General installation

The code was developped on Python 3.9.0.

To install the needed libraries, run in your terminal:

```
pip install -r requirements.txt
```

To reproduce our data collection, you will need tokens or codes to access the CrowdTangle, BuzzSumo, Twitter and YouTube APIs. Tokens should be written in an .env or .minetrc file depending on the tools used to collect the data.

## Collect the data

All the collected data will be saved as CSV files in the `data` folder.

### YouTube:
For collecting youtube data run
```
  python3 code/collect_youtube_data.py 
```
- Two new csv files will be generated in the data file with the name of the channels, and they will contain the videos posted for the selected channels since 2019/01/01 with the date of publishing, likes, dislikes, comments count.
- The study focused on two channels OANN and Tony Heller. The ids of these channels are included in the code. To add/remove channels, you can change the list ``` list_id ``` under ``` collect_youtube_data.py``` file.

To get the information panels below the False YT videos, run:
```
python3 code/collect_youtube_panels.py
```
- A browser will be opened through a driver and when it finishes it will terminate. you can check the results in the command line.


To collect the recommendations of a video for two levels, run:
```
  python3 code/collect_youtube_recommendation_reduce.py "['video_id_1','video_id_2']"
```
### Facebook:

To collect the Trump Facebook data from CrowdTangle, run (the collection takes around 2 minutes):

```
./code/collect_facebook_crowdtangle_trump_data.sh 1559721
```

To collect the Beauty of Life Facebook data from Buzzsumo, run (~6 min):
```
python code/collect_facebook_buzzsumo_thebl_data.py
```

To collect the Infowars Facebook data from CrowdTangle, run (~20 min):

```
./code/collect_facebook_crowdtangle_infowars_data.sh
```

To collect the Infowars Facebook data from Buzzsumo, run (~4 min):
```
python code/collect_facebook_buzzsumo_infowars_data.py
```

### Twitter:

To collect the tweets of the Twitter account @LifeSite (Lifesitenews.com) from Twitter API v2, run (~5 min):
```
python3 ./code/collect_twitter_lifesitenews_data.py
```

To collect the tweets containing the domain name Lifesitenews.com from Twitter API v2, run (~x min):
```
python3 ./code/collect_twitter_lifesitenews_domain_data.py
```

To collect the tweets containing the domain name globalresearch.ca from Twitter API v2, run (~30 min):
```
python3 ./code/collect_twitter_globalresearch_domain_data.py 
```

## Plot the figures

Once the collected data is in CSV files in the `data` folder, you can plot it using:

```
python code/create_figures.py
```

The created PNG figures will appear in the `figure` folder.
