from datetime import datetime, timedelta
import re
import os

import pandas as pd
import numpy as np
from googleapiclient.discovery import build
from dotenv import load_dotenv


def get_channel_videos(channel_id, youtube):
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


def video_id(video):
        return video['snippet']['resourceId']['videoId']


def collect_data(API_key, channel_id):
    youtube = build('youtube', 'v3', developerKey=API_key)
    videos = get_channel_videos(channel_id,youtube)
    titles = [video_title(video) for video in videos]

    publish_timestamps = [timestamp(video) for video in videos]
    video_ids = [video_id(video) for video in videos]
    videos_df = pd.DataFrame({'Upload_date':publish_timestamps,'video_titles':titles,'video_id':video_ids})
    videos_df = videos_df[videos_df['Upload_date']>'2019-01-01']
    videos_ids_filtered = list(videos_df['video_id'])


    for i in range(0,len(videos_ids_filtered)):
        data_header = pd.DataFrame([],
                                   columns=['video_title', 'view_counts', 'likes', 'dislikes', 'comments', 'video_id',
                                            'channel_name', 'channel_id', 'published_at', 'duration'])
        video_data = get_data_video(videos_ids_filtered[i], youtube)
        r_series = pd.Series(video_data, index=data_header.columns)
        channel_name = r_series['channel_name']
        path = 'data/' + channel_name + '_youtube_data.csv'
        if (i==0):
            data_header.to_csv(path,index=False)
        data_header = data_header.append(r_series, ignore_index=True)
        data_header.to_csv(path, mode='a', header=False,index=False)




    #path = 'data/' + channel_name + '_youtube_data.csv'
    #data.to_csv(path)


def get_data_video(vid_id, youtube):
        data = np.array([])
        vid_suff = vid_id
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=vid_suff
        )
        response = request.execute()
        try:
            # print(response)

            main_info = response['items'][0]['snippet']
            channel_name = main_info['channelTitle']
            video_title = main_info['title']
            channel_ids = main_info['channelId']
            published_ats = main_info['publishedAt']
            video_ids = response['items'][0]['id']
            view_counts = response['items'][0]['statistics']['viewCount']
            try:
                likes = response['items'][0]['statistics']['likeCount']
            except:
                likes = 'non'
            try:
                dislikes = response['items'][0]['statistics']['dislikeCount']
            except:
                dislikes = 'non'
            try:
                comments = response['items'][0]['statistics']['commentCount']
            except:
                comments = 'non'
            duration = re.findall(r'\d+', response['items'][0]['contentDetails']['duration'])

            data = np.append(data, np.array(
                [video_title, view_counts, likes, dislikes, comments, video_ids, channel_name, channel_ids,
                 published_ats, duration]))

            # data = np.append(data)
        except:
            print('An issue with collecting a video it can be that you run out of tokens in youtube API')
        return data

if __name__=="__main__":
    load_dotenv()
    # the list_is correspond to the id of channels [OANN, Tony Heller]
    list_id = ['UCprclkVrNPls7PR-nHhf1Ow','UCNbIDJNNgaRrXOD7VllIMRQ']
    for i in list_id:
        collect_data(os.getenv('YOUTUBE_TOKEN'),i)