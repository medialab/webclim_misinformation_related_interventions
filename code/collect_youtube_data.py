from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pandas as pd
import sys


def get_channel_videos(channel_id,youtube):
    # get Uploads playlist id
    res = youtube.channels().list(id=channel_id,
                                  part='contentDetails').execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    videos = []
    next_page_token = None

    while 1:
        res = youtube.playlistItems().list(playlistId=playlist_id,
                                           part='snippet',
                                           maxResults=50,
                                           pageToken=next_page_token).execute()
        videos += res['items']
        next_page_token = res.get('nextPageToken')

        if next_page_token is None:
            break
    return videos

def timestamp(video):
    return (datetime.strptime(video['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%fZ")
            + timedelta(hours=5, minutes=30))

def video_title(video):
    return video['snippet']['title']

def collect_data(API_key, channel_id):
    youtube = build('youtube', 'v3', developerKey=API_key)


    videos = get_channel_videos(channel_id,youtube)

    titles = [video_title(video) for video in videos]

    publish_timestamps = [timestamp(video) for video in videos]

    videos_df = pd.DataFrame({'Upload_date':publish_timestamps,'video_titles':titles})
    videos_df.to_csv('data/youtube_data.csv')


if __name__=="__main__":

    collect_data(sys.argv[1],sys.argv[2])