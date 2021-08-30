import os
#from datetime import timedelta, date
from datetime import datetime, timedelta, date

import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches #new addition to create the boxes in the legend for the shaded areas
import ural


def import_data(file_name):
    data_path = os.path.join(".", "data", file_name)
    df = pd.read_csv(data_path, low_memory=False)
    return df

def save_figure(figure_name):
    figure_path = os.path.join('.', 'figure', figure_name)
    plt.savefig(figure_path)
    print("The '{}' figure is saved.".format(figure_name))

def plot_format(ax, plt, suspension):

    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.locator_params(axis='y', nbins=4)
    ax.xaxis.set_tick_params(length=0)

    ax.grid(axis='y')
    handles, labels = ax.get_legend_handles_labels()

    if suspension == 1 :
        patch = mpatches.Patch(color='pink',
                               label='Suspension Period')
        handles.append(patch)

    plt.legend(handles=handles)

    plt.setp(ax.get_xticklabels(), rotation=45)

    plt.tight_layout()

def arrange_plot(ax, df):

    plt.legend()

    ax.set_frame_on(False)
    ax.grid(axis="y")
    plt.locator_params(axis='y', nbins=4)

    plt.xticks(
        [np.datetime64('2019-06-30'), np.datetime64('2020-06-30'), np.datetime64('2021-04-30')],
        ['2019', '2020', '2021'], fontsize='large'
    )
    ax.xaxis.set_tick_params(length=0)
    plt.axvspan(np.datetime64('2020-01-01'), np.datetime64('2020-12-31'),
                ymin=0, ymax=200000, facecolor='k', alpha=0.05)
    plt.xlim(np.min(df['date']), np.max(df['date']))


def create_facebook_trump_figure():

    print()

    df = import_data('facebook_crowdtangle_trump_2021-06-21.csv')

    df['date'] = pd.to_datetime(df['date'])
    serie_to_plot = df.resample('D', on='date')['date'].agg('count')
    serie_to_plot = serie_to_plot.append(pd.Series(
        [0, 0],
        index=[pd.Timestamp(2021, 1, 7), pd.Timestamp(2021, 6, 15)]
    ))

    plt.figure(figsize=(10, 4))
    plt.title("'" + df.account_name.iloc[0] + "' Facebook page (data from CrowdTangle)")

    ax = plt.subplot(111)
    plt.plot(serie_to_plot, color='royalblue', label='Number of posts per day')
    arrange_plot(ax, df)
    plt.axvline(np.datetime64("2021-01-07"), color='C3', linestyle='--')
    plt.xlim(
        np.datetime64(datetime.strptime('2019-12-31', '%Y-%m-%d')),
        np.datetime64(datetime.strptime('2021-06-15', '%Y-%m-%d'))
    )
    plt.ylim(-.3, 55)

    plt.tight_layout()
    save_figure('facebook_crowdtangle_trump.png')


def create_buzzsumo_thebl_figure():

    print()

    df = import_data('facebook_buzzsumo_thebl_2021-07-01.csv')
    df = clean_buzzsumo_data(df)

    #fig = plt.figure(figsize=(10, 8))
    fig = plt.figure(figsize=(10, 4)) #
    fig.suptitle('The Beauty of Life (data from Buzzsumo)')

    #ax = plt.subplot(211)
    ax = plt.subplot(111)#
    plt.plot(df.resample('D', on='date')['facebook_comments'].mean(),
        label="Facebook comments per article", color='lightskyblue')
    plt.plot(df.resample('D', on='date')['facebook_shares'].mean(),
        label="Facebook shares per article", color='royalblue')
    plt.plot(df.resample('D', on='date')['facebook_likes'].mean(),
        label="Facebook reactions (likes, ...) per article", color='navy')
    arrange_plot(ax, df)
    plt.axvline(np.datetime64("2019-12-01"), color='C3', linestyle='--')
    plt.ylim(-100, 10000)

    plt.tight_layout()#
    save_figure('facebook_buzzsumo_thebl_1.png')#

    fig = plt.figure(figsize=(10, 4)) #
    fig.suptitle('The Beauty of Life (data from Buzzsumo)')

    #ax = plt.subplot(212)
    ax = plt.subplot(111) #
    plt.plot(df.resample('D', on='date')['date'].agg('count'),
            label='Number of articles published per day', color='grey')
    arrange_plot(ax, df)
    plt.axvline(np.datetime64("2019-12-01"), color='C3', linestyle='--')
    plt.ylim(0, 80)

    plt.tight_layout()
    save_figure('facebook_buzzsumo_thebl_2.png')#
    #save_figure('facebook_buzzsumo_thebl.png')


def clean_crowdtangle_data(df):

    df['date'] = pd.to_datetime(df['date'])

    df['reaction'] = df[[
        "actual_like_count", "actual_favorite_count", "actual_love_count",
        "actual_wow_count", "actual_haha_count", "actual_sad_count",
        "actual_angry_count", "actual_thankful_count", "actual_care_count"
    ]].sum(axis=1).astype(int)
    df['share'] = df["actual_share_count"].astype(int)
    df['comment'] = df["actual_comment_count"].astype(int)

    df['link'] = df['link'].apply(lambda x: ural.normalize_url(str(x).strip()))
    df['domain_name'] = df['link'].astype(str).apply(lambda x: ural.get_domain_name(x))
    df = df[df['domain_name']=='infowars.com']

    return df[['date', 'link', 'reaction', 'share', 'comment']]


def calculate_percentage_change(before, after):
    return str(int((after - before) * 100 / before))


def print_the_percentage_changes(df, columns, date='2019-05-02', period=60):

    df_before = df[df['date'] < np.datetime64(date)]
    df_before = df_before[df_before['date'] >= np.datetime64(datetime.strptime(date, '%Y-%m-%d') - timedelta(days=period))]

    df_after = df[df['date'] > np.datetime64(date)]
    df_after = df_after[df_after['date'] <= np.datetime64(datetime.strptime(date, '%Y-%m-%d') + timedelta(days=period))]

    text_to_print = 'Drop after the ' + date + ': '
    for column in columns:
        text_to_print += column + ': ' + calculate_percentage_change(df_before[column].sum(), df_after[column].sum()) + '%, '
    print(text_to_print)


def create_facebook_crowdtangle_infowars_figure():

    print()

    df = import_data('facebook_crowdtangle_infowars_2021-06-29.csv')
    df = clean_crowdtangle_data(df)
    print('There are {} posts after removing the indirect links in the CrowdTangle Infowars date.'.format(len(df)))
    #print_the_percentage_changes(df, columns=['reaction', 'share', 'comment'])

    #plt.figure(figsize=(10, 8))

    plt.figure(figsize=(10, 4))#

    #ax = plt.subplot(211)
    ax = plt.subplot(111)#
    plt.title('Facebook public posts sharing an Infowars link (data from CrowdTangle)')

    plt.plot(df.resample('D', on='date')['date'].agg('count'),
        label='Number of posts per day', color='royalblue')
    arrange_plot(ax, df)
    plt.axvline(np.datetime64("2019-05-02"), color='C3', linestyle='--')
    plt.ylim(0, 160)

    plt.tight_layout()#
    save_figure(figure_name='facebook_crowdtangle_infowars_1.png')#

    plt.figure(figsize=(10, 4))#
    plt.title('Facebook public posts sharing an Infowars link (data from CrowdTangle)')#

    #ax = plt.subplot(212)
    ax = plt.subplot(111)#

    plt.plot(df.resample('D', on='date')['comment'].mean(),
        label="Comments per post", color='lightskyblue')
    plt.plot(df.resample('D', on='date')['share'].mean(),
        label="Shares per post", color='royalblue')
    plt.plot(df.resample('D', on='date')['reaction'].mean(),
        label="Reactions (likes, ...) per post", color='navy')
    arrange_plot(ax, df)
    plt.axvline(np.datetime64("2019-05-02"), color='C3', linestyle='--')
    plt.ylim(0, 78)

    plt.tight_layout()
    save_figure(figure_name='facebook_crowdtangle_infowars_2.png')#


def clean_buzzsumo_data(df):

    df['date'] = [datetime.fromtimestamp(x).date() for x in df['published_date']]
    df['date'] = pd.to_datetime(df['date'])

    df = df.drop_duplicates(subset=['url'])

    return df


def filter(df, column):

    s0 = df.resample('D', on='date')['date'].agg('count')
    dates_to_filter = s0[s0 < 5].index

    s = df.resample('D', on='date')[column].mean()
    s[s.index.isin(dates_to_filter)] = np.nan

    return s


def create_facebook_buzzsumo_infowars_figure():

    print()

    df = import_data('facebook_buzzsumo_infowars_2021-06-29.csv')
    df = clean_buzzsumo_data(df)
    print('There are {} Infowars articles for 2019 and 2020 in the Buzzsumo API.'.format(len(df)))
    print_the_percentage_changes(df, columns=['facebook_likes', 'facebook_shares', 'facebook_comments'])

    print('There are {} Infowars articles collected from Buzzsumo between 2020-06-11 and 2020-07-11.'.format(
        np.sum(df.resample('D', on='date')['date'].agg('count').loc['2020-06-11':'2020-07-11']))
    )

    fig = plt.figure(figsize=(10, 4))
    plt.title('Facebook engagement for the Infowars articles (data from Buzzsumo)')

    ax = plt.subplot(111)
    plt.plot(filter(df, 'facebook_comments'),
        label="Comments per article", color='lightskyblue')
    plt.plot(filter(df, 'facebook_shares'),
        label="Shares per article", color='royalblue')
    plt.plot(filter(df, 'facebook_likes'),
        label="Reactions (likes, ...) per article", color='navy')
    arrange_plot(ax, df)
    plt.axvline(np.datetime64("2019-05-02"), color='C3', linestyle='--')
    plt.ylim(0, 3000)

    plt.tight_layout()
    save_figure(figure_name='facebook_buzzsumo_infowars.png')


def preprocess_youtube_data():
    oann = import_data('One America News Network_youtube_data.csv')
    tony_heller = import_data('Tony Heller_youtube_data.csv')
    list_df = [oann,tony_heller]
    for df in list_df:
        df['published_at'] = pd.to_datetime(df['published_at'])
        df['published_at'] = pd.to_datetime(df['published_at'], format='%m/%d/%Y')
        df['date'] = ''
        for i in range(0, df.shape[0]):
            df['date'].iloc[i] = df['published_at'].iloc[i].date()
            if (df['comments'].iloc[i] == 'non'):
                df['comments'].iloc[i] = 0
            if (df['likes'].iloc[i] == 'non'):
                df['likes'].iloc[i] = 0
            if (df['dislikes'].iloc[i] == 'non'):
                df['dislikes'].iloc[i] = 0
        df['likes'] = df['likes'].astype('int64')
        df['dislikes'] = df['dislikes'].astype('int64')
        df['comments'] = df['comments'].astype('int64')
        df['view_counts'] = df['view_counts'].astype('int64')
    return oann,tony_heller


def plot_view_count_youtube(data, date_begin_sus, date_end_sus, date_begin_graph, date_end_graph, height_keyword, fig_name, title):
    window_num = 1

    df_tlm_views = data.groupby(['published_at'])['view_counts'].sum().to_frame('view_counts')
    df_tlm_views = df_tlm_views.resample('D').sum().fillna(0).reset_index()
    df_tlm_vol_rolling_views = df_tlm_views.groupby(['published_at']).mean().rolling(window=window_num,
                                                                                     win_type='triang',
                                                                                     center=True).mean()
    df_tlm_vol_rolling_views['published_at'] = df_tlm_vol_rolling_views.index
    df_tlm_vol = data.groupby(['published_at']).size().to_frame('size')
    df_tlm_vol = df_tlm_vol.resample('D').sum().fillna(0).reset_index()
    df_tlm_vol_rolling = df_tlm_vol.groupby(['published_at']).mean().rolling(window=window_num, win_type='triang',
                                                                             center=True).mean()
    df_tlm_vol_rolling['published_at'] = df_tlm_vol_rolling.index

    fig, ax = plt.subplots(1, figsize=(10, 4))
    plt.locator_params(axis='y', nbins=4)
    plt.setp(ax.get_xticklabels(), rotation=45)

    ax.xaxis.set_tick_params(length=0)
    ax.plot(df_tlm_vol_rolling_views['published_at'],
             df_tlm_vol_rolling_views['view_counts'],
             color='red', label='view count of YouTube videos') #

    ax.set(
       title = title ) #

    ax.set_xlim([date_begin_graph, date_end_graph])

    plt.axvspan(np.datetime64(date_begin_sus), np.datetime64(date_end_sus),
                    ymin=0, ymax=200000, facecolor='r', alpha=0.05)

    plot_format(ax, plt, suspension = 1)

    save_figure(figure_name=fig_name)


def plot_video_count_youtube(data, date_begin_sus, date_end_sus, date_begin_graph, date_end_graph, height_keyword, fig_name, title):
    window_num = 1

    df_tlm_vol = data.groupby(['published_at']).size().to_frame('size')
    df_tlm_vol = df_tlm_vol.resample('D').sum().fillna(0).reset_index()

    df_tlm_vol_rolling = df_tlm_vol.groupby(['published_at']).mean().rolling(window=window_num, win_type='triang',
                                                                             center=True).mean()
    df_tlm_vol_rolling['published_at'] = df_tlm_vol_rolling.index
    fig, ax = plt.subplots(1, figsize=(10, 4))
    ax.plot(df_tlm_vol['published_at'],
             df_tlm_vol['size'],
             color='red', label='Number of YouTube videos uploaded')
    ax.set(
       title = title )

    plt.axvspan(np.datetime64(date_begin_sus), np.datetime64(date_end_sus),
                ymin=0, ymax=200000, facecolor='r', alpha=0.05)

    ax.set_xlim([date_begin_graph, date_end_graph])

    plot_format(ax, plt, suspension = 1)

    save_figure(figure_name=fig_name)


def create_plot_top_channel_youtube(path_to_data):
    # the path to the data created from collect_youtube_recommendation
    df = pd.read_csv(path_to_data)
    channel_fre = df['channel_name'].value_counts().reset_index().iloc[0:10]
    y_pos = np.arange(len(channel_fre['index']))
    # Create horizontal bars
    plt.rcdefaults()
    fig, ax = plt.subplots()
    plt.barh(y_pos, channel_fre['channel_name'], color='red', alpha=0.6)
    plt.xticks(alpha=0.7)
    # Create names on the x-axis
    plt.yticks(y_pos, channel_fre['index'], alpha=0.7)
    ax.set_xlabel('Number of video recommendations at the Channel level')
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.yaxis.set_label_position("right")
    #ax.yaxis.tick_right()
    plt.gca().invert_yaxis()
    fig_name = "reduce_youtube"
    figure_path = os.path.join('.', 'figure', fig_name)
    plt.savefig(figure_path, bbox_inches="tight")
    print("The '{}' figure is saved.".format(fig_name))


def create_youtube_graph():

    oann, tony_heller = preprocess_youtube_data()
    plot_view_count_youtube(oann, '2020-11-25', '2020-12-01', date(2020, 11, 1), date(2021, 1, 1),
                            2680000,'delete_youtube_2_oann.png',
                            title = 'View count of videos by the YouTube channel OANN')
    plot_view_count_youtube(tony_heller, '2020-09-29', '2020-10-05', date(2020, 9, 1),
                            date(2020, 11, 15), 1500000,'delete_youtube_4_tony_heller.png',
                            title = 'View count of videos by the YouTube channel Tony Heller')

    plot_video_count_youtube(oann, '2020-11-25', '2020-12-01', date(2020, 11, 1), date(2021, 1, 1),
                             32,'delete_youtube_1_oann.png',
                            title = 'Video uploads by the YouTube channel OANN')
    plot_video_count_youtube(tony_heller, '2020-09-29', '2020-10-05', date(2020, 9, 1),
                             date(2020, 11, 15), 10,'delete_youtube_3_tony_heller.png',
                             title = 'Video uploads by the YouTube channel Tony Heller')


def create_twitter_Lifesite_figure(filename, figure_name, title, zeros):

    df = import_data(filename)
    df = df.drop_duplicates()

    df['type_of_tweet'] = df['type_of_tweet'].replace(np.nan, 'created_content')
    df['total_engagement'] = (df['retweet_count'] + df['like_count'] + df['reply_count'])
    df['date'] = pd.to_datetime(df['created_at']).dt.date
    #df_volume = df.groupby(['date','type_of_tweet'], as_index=False).size()
    df_volume = df.groupby(['date'], as_index=False).size()

    if zeros == 1 :
        add_zeros = [{'date': datetime.date(2019, 12, 10), 'type_of_tweet': 'created_content', 'size': 0}, {'date': datetime.date(2019, 12, 10), 'type_of_tweet': 'replied_to', 'size': 0},{'date': datetime.date(2019, 12, 10), 'type_of_tweet': 'quoted', 'size': 0}, {'date': datetime.date(2019, 12, 10), 'type_of_tweet': 'retweeted', 'size': 0},{'date': datetime.date(2020, 10, 11), 'type_of_tweet': 'created_content', 'size': 0}, {'date': datetime.date(2020, 10, 11), 'type_of_tweet': 'replied_to', 'size': 0}, {'date': datetime.date(2020, 10, 11), 'type_of_tweet': 'quoted', 'size': 0}, {'date': datetime.date(2020, 10, 11), 'type_of_tweet': 'retweeted', 'size': 0}, {'date': datetime.date(2021, 1, 25), 'type_of_tweet': 'created_content', 'size': 0}, {'date': datetime.date(2021, 6, 30), 'type_of_tweet': 'created_content', 'size': 0}]
        df_volume = df_volume.append(add_zeros , ignore_index = True)
        df_volume = df_volume .sort_index().reset_index(drop = True)
        df_volume = df_volume.sort_values(by = "date")

    fig, ax = plt.subplots(figsize=(10, 4))

    d = df[(df['date']> datetime.date(2019, 1, 1) ) & (df['date']<datetime.date(2021, 7, 1))]
    total = d['id'].count()

    ax.plot(df_volume['date'],
        df_volume['size'],
        color='deepskyblue',
        label='Number of Tweets per day')

    ax.set(
       title = title )

    ax.set_xlim([datetime.date(2019, 1, 1), datetime.date(2021, 6, 30)])

    plt.axvspan(np.datetime64('2019-12-09'),
                np.datetime64('2020-10-12'),
                ymin=0, ymax=200000,
                facecolor='r',
                alpha=0.05)

    plt.axvspan(np.datetime64('2021-01-25'),
                np.datetime64('2021-06-30'),
                ymin=0,
                ymax=200000,
                facecolor='r',
                alpha=0.05)

    plot_format(ax, plt, suspension = 1)

    save_figure(figure_name)
    #plt.show()

def create_twitter_globalresearch_figure(filename, figure_name, title, zeros):

    df = import_data(filename)
    df = df.drop_duplicates()

    df['date'] = pd.to_datetime(df['created_at']).dt.date

    d=df[(df['date']> datetime.date(2021,1,1) ) & (df['date'] < datetime.date(2021, 6, 30) )]
    total=d['id'].count()

    fig, ax = plt.subplots(figsize=(10, 4))

    if zeros == 1:

        df_tw_vol1=df.groupby(['date']).size().to_frame('size')
        df_tw_vol_rolling1=df_tw_vol1.groupby(['date']).sum().rolling(window=1, win_type='triang', center=True).mean()
        df_tw_vol_rolling1['date'] = df_tw_vol_rolling1.index

        ax.plot(df_tw_vol_rolling1['date'],
                df_tw_vol_rolling1['size'],
                color='deepskyblue',
                label='Number of Tweets per day')

        ax.set_ylim([0, 600])
        plt.text(np.datetime64("2021-06-15"), 420, "screenshot date", fontsize=10, color='C3')

    elif zeros == 0:

        df_s=df.groupby(['date'],as_index=False)[['like_count','retweet_count','reply_count']].sum()
        df_s_rolling=df_s.groupby(['date'])[['like_count','retweet_count','reply_count']].sum().rolling(window=1, win_type='triang', center=True).mean()
        df_s_rolling['date'] = df_s_rolling.index

        ax.plot(df_s_rolling['date'],
                df_s_rolling['like_count'],
                color='lightblue',label='Like Count')

        ax.plot(df_s_rolling['date'],
                df_s_rolling['reply_count'],
                color='lightgreen',label='Reply Count')

        ax.plot(df_s_rolling['date'],
                df_s_rolling['retweet_count'],
                color='pink',label='Retweet Count')

        ax.set_ylim([0, 2000])

        plt.text(np.datetime64("2021-06-15"), 1400, "screenshot date", fontsize=10, color='C3')

    ax.set_xlim([datetime.date(2021, 4, 15), datetime.date(2021, 8, 15)])

    ax.set(
        title = title)

    #ax.set_xlim([datetime.date(2021,1,1), datetime.date(2021, 6, 30)])
    plt.axvline(np.datetime64("2021-06-14"), color='C3', linestyle='--')


    #plt.axvspan(np.datetime64('2021-05-25'), np.datetime64('2021-08-15'),
    #        ymin=0, ymax=200000, facecolor='r', alpha=0.05)


    plot_format(ax, plt, suspension = 0)

    save_figure(figure_name)


def create_twitter_figures():

    create_twitter_Lifesite_figure(
    filename = 'twitter_lifesitenews_2021-07-22.csv',
    figure_name = 'lifesite.jpg',
    title = f"Tweets by @LifeSite Twitter account",
    zeros = 1
    )

    create_twitter_Lifesite_figure(
    filename = 'twitter_lifesitenews_domain_name_2021-07-29.csv',
    figure_name = 'lifesite_domain.jpg',
    title = f"Tweets containing the domain name lifesitenews.com",
    zeros = 0
    )

    create_twitter_globalresearch_figure(
    filename = 'twitter_globalresearch_domain_name_2021-08-17.csv',
    figure_name = 'globalresearch_domain_2021-08-17.jpg',
    title = f"Tweets containing the domain name globalresearch.ca",
    zeros = 1
    )

    create_twitter_globalresearch_figure(
    filename = 'twitter_globalresearch_domain_name_2021-08-17.csv',
    figure_name = 'globalresearch_domain_engagement_2021-08-17.jpg',
    title = f"Tweets containing the domain name globalresearch.ca",
    zeros = 0
    )


if __name__=="__main__":

    create_facebook_trump_figure()
    create_buzzsumo_thebl_figure()
    create_facebook_crowdtangle_infowars_figure()
    create_facebook_buzzsumo_infowars_figure()
    
    create_youtube_graph()

    create_twitter_figures()
    
    create_plot_top_channel_youtube('./data/experiment2_health_full_data.csv')