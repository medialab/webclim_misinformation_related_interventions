## Truth and Trust online 2021

## General installation

The code was developped on Python 3.9.0.

To install the needed libraries, run in your terminal:

```
pip install -r requirements.txt
```

[Explain the .env file]

## Collect the data

All the collected data will be saved as CSV files in the `data` folder.

### YouTube:
- For collecting youtube data run
```
  python3 code/collect_youtube_data.py 
```
- Two new csv files will be generated in the data file with the name of the channels, and they will contain the videos posted for the selected channels since 2019/01/01 with the date of publishing, likes, dislikes, comments count.
- The study focused on two channels OANN and Tony Heller. The ids of these channels are included in the code. To add/remove channels, you can change the list ``` list_id ``` under ``` collect_youtube_data.py``` file.


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

To collect the Lifesitenews data from Twitter API v2, run (~5 min):
```
python3 ./code/collect_twitter_lifesitenews_data.py
python3 ./code/collect_twitter_lifesitenews_domain_data.py
```

## Plot the figures

Once the collected data is in CSV files in the `data` folder, you can plot it using:

```
python code/create_figures.py
```

The created PNG figures will appear in the `figure` folder.
