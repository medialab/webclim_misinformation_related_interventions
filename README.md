## Truth and Trust online 2021

## General installation

The code was developped on Python 3.9.0.

To install the needed libraries, run in your terminal:

```
pip install -r requirements.txt
```

## Collect the data

All the collected data will be saved as CSV files in the `data` folder.

### YouTube:
- For collecting youtube data run ```python3 code/collect_youtube_data.py 'Your_Youtube_API_key' 'Channel_id' ```
- a new csv file will be genrated in the data file with the name of the channel and it will contain the videos posted for the selected channel since 2019/01/01 with the date of publishing, likes, dislikes, comments count.
- The channels the study investigated are:
    - One America News Network and its channel id is ```UCNbIDJNNgaRrXOD7VllIMRQ```
    - Tony Heller and its channel id is ```UCprclkVrNPls7PR-nHhf1Ow```


### Facebook:

To collect the Trump Facebook data from CrowdTangle, run (the collection takes around 2 minutes):

```
./code/collect_facebook_crowdtangle_trump_data.sh 1559721
```

To collect the Infowars Facebook data from CrowdTangle, run (the collection takes around 30 minutes):

```
./code/collect_facebook_crowdtangle_infowars_data.sh
```

## Plot the figures

Once the collected data is in CSV files in the `data` folder, you can plot it using:

```
python code/create_figures.py
```

The created PNG figures will appear in the `figure` folder.