import os
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

#note by shaden for Héloïse: I suggest for this function to use:
# df = pd.concat([pd.read_csv(f) for f in glob.glob('./somefile_name_*.csv')], ignore_index = True)
# because when we recollect the dates will change, like this in our function we can put facebook_crowdtangle_trump__*.csv for example

def save_figure(figure_name):
    figure_path = os.path.join('.', 'figure', figure_name)
    plt.savefig(figure_path)
    print("The '{}' figure is saved.".format(figure_name))


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

    fig = plt.figure(figsize=(10, 8))
    fig.suptitle('The Beauty of Life (data from Buzzsumo)')

    ax = plt.subplot(211)
    plt.plot(df.resample('D', on='date')['facebook_comments'].mean(),
        label="Facebook comments per article", color='lightskyblue')
    plt.plot(df.resample('D', on='date')['facebook_shares'].mean(),
        label="Facebook shares per article", color='royalblue')
    plt.plot(df.resample('D', on='date')['facebook_likes'].mean(),
        label="Facebook reactions (likes, ...) per article", color='navy')
    arrange_plot(ax, df)
    plt.axvline(np.datetime64("2019-12-01"), color='C3', linestyle='--')
    plt.ylim(-100, 10000)

    ax = plt.subplot(212)
    plt.plot(df.resample('D', on='date')['date'].agg('count'),
            label='Number of articles published per day', color='grey')
    arrange_plot(ax, df)
    plt.axvline(np.datetime64("2019-12-01"), color='C3', linestyle='--')
    plt.ylim(0, 80)

    plt.tight_layout()
    save_figure('facebook_buzzsumo_thebl.png')


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
    print_the_percentage_changes(df, columns=['reaction', 'share', 'comment'])

    plt.figure(figsize=(10, 8))

    ax = plt.subplot(211)
    plt.title('Facebook public posts sharing an Infowars link (data from CrowdTangle)')

    plt.plot(df.resample('D', on='date')['date'].agg('count'),
        label='Number of posts per day', color='royalblue')
    arrange_plot(ax, df)
    plt.axvline(np.datetime64("2019-05-02"), color='C3', linestyle='--')
    plt.ylim(0, 160)

    ax = plt.subplot(212)
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
    save_figure(figure_name='facebook_crowdtangle_infowars.png')


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


def plot_view_count_youtube(data, date_begin_sus, date_end_sus, date_begin_graph, date_end_graph, height_keyword, fig_name):
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
    fig, ax1 = plt.subplots(1, figsize=(15, 4))
    plt.locator_params(axis='y', nbins=4)
    plt.setp(ax1.get_xticklabels(), rotation=45)

    ax1.xaxis.set_tick_params(length=0)
    ax1.plot(df_tlm_vol_rolling_views['published_at'],
             df_tlm_vol_rolling_views['view_counts'],
             color='red', label='view count')
    ax1.set_xlim([date_begin_graph, date_end_graph])
    plt.setp(ax1.get_xticklabels(), rotation=45)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.grid(axis="y")
    ax1.xaxis.set_tick_params(length=0)

    plt.axvspan(np.datetime64(date_begin_sus), np.datetime64(date_end_sus),
                ymin=0, ymax=200000, facecolor='r', alpha=0.05)
    ax1.text(np.datetime64(date_begin_sus), height_keyword, 'suspension', color='grey')
    plt.ylabel('View count')
    plt.xlabel('Date')
    plt.legend()
    plt.tight_layout()
    save_figure(figure_name=fig_name)


def plot_video_count_youtube(data, date_begin_sus, date_end_sus, date_begin_graph, date_end_graph, height_keyword, fig_name):
    window_num = 1

    df_tlm_vol = data.groupby(['published_at']).size().to_frame('size')
    df_tlm_vol = df_tlm_vol.resample('D').sum().fillna(0).reset_index()

    df_tlm_vol_rolling = df_tlm_vol.groupby(['published_at']).mean().rolling(window=window_num, win_type='triang',
                                                                             center=True).mean()
    df_tlm_vol_rolling['published_at'] = df_tlm_vol_rolling.index
    fig, ax1 = plt.subplots(1, figsize=(15, 4))
    ax1.plot(df_tlm_vol['published_at'],
             df_tlm_vol['size'],
             color='red', label='Video Uploads')

    ax1.set_xlim([date_begin_graph, date_end_graph])
    plt.setp(ax1.get_xticklabels(), rotation=45)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.grid(axis="y")
    plt.axvspan(np.datetime64(date_begin_sus), np.datetime64(date_end_sus),
                ymin=0, ymax=200000, facecolor='r', alpha=0.05)
    ax1.text(np.datetime64(date_begin_sus), height_keyword, 'suspension', color='grey')
    plt.ylabel('Video count')
    plt.xlabel('Date')
    plt.legend()
    plt.tight_layout()
    save_figure(figure_name=fig_name)


def create_youtube_graph():

    oann, tony_heller = preprocess_youtube_data()
    plot_view_count_youtube(oann, '2020-11-25', '2020-12-01', date(2020, 11, 1), date(2021, 1, 1),
                            2680000,'OANN_views_yt.png')
    plot_view_count_youtube(tony_heller, '2020-09-29', '2020-10-05', date(2020, 9, 1),
                            date(2020, 11, 15), 1500000,'Tony_Heller_views_yt.png')
    plot_video_count_youtube(oann, '2020-11-25', '2020-12-01', date(2020, 11, 1), date(2021, 1, 1),
                             32,'OANN_videos_yt.png')
    plot_video_count_youtube(tony_heller, '2020-09-29', '2020-10-05', date(2020, 9, 1),
                             date(2020, 11, 15), 10,'Tony_Heller_videos_yt.png')

def create_twitter_Lifesite_figure(filename, figure_name, title, zeros):

    df = import_data(filename)
    df = df.drop_duplicates()

    df['type_of_tweet'] = df['type_of_tweet'].replace(np.nan, 'created_content')
    df['total_engagement'] = (df['retweet_count'] + df['like_count'] + df['reply_count'])
    df['date'] = pd.to_datetime(df['created_at']).dt.date
    df_volume = df.groupby(['date','type_of_tweet'], as_index=False).size()

    if zeros == 1 :
        add_zeros = [{'date': datetime.date(2019, 12, 10), 'type_of_tweet': 'created_content', 'size': 0}, {'date': datetime.date(2019, 12, 10), 'type_of_tweet': 'replied_to', 'size': 0},{'date': datetime.date(2019, 12, 10), 'type_of_tweet': 'quoted', 'size': 0}, {'date': datetime.date(2019, 12, 10), 'type_of_tweet': 'retweeted', 'size': 0},{'date': datetime.date(2020, 10, 11), 'type_of_tweet': 'created_content', 'size': 0}, {'date': datetime.date(2020, 10, 11), 'type_of_tweet': 'replied_to', 'size': 0}, {'date': datetime.date(2020, 10, 11), 'type_of_tweet': 'quoted', 'size': 0}, {'date': datetime.date(2020, 10, 11), 'type_of_tweet': 'retweeted', 'size': 0}, {'date': datetime.date(2021, 1, 25), 'type_of_tweet': 'created_content', 'size': 0}, {'date': datetime.date(2021, 5, 15), 'type_of_tweet': 'created_content', 'size': 0}]
        df_volume = df_volume.append(add_zeros , ignore_index = True)
        df_volume = df_volume .sort_index().reset_index(drop = True)
        df_volume = df_volume.sort_values(by = "date")

    cc = df_volume[df_volume['type_of_tweet'] == 'created_content']
    reply = df_volume[df_volume['type_of_tweet'] == 'replied_to']
    quote = df_volume[df_volume['type_of_tweet'] == 'quoted']
    retweeted = df_volume[df_volume['type_of_tweet'] == 'retweeted']

    fig, ax = plt.subplots(figsize=(10, 5))

    d = df[(df['date']> datetime.date(2019, 1, 1) ) & (df['date']<datetime.date(2021, 7, 1))]
    total = d['id'].count()

    ax.plot(reply['date'],
        reply['size'],
        color='lightblue',
        label='Replied to')

    ax.plot(quote['date'],
        quote['size'],
        color='lightgreen',
        label='Quoted')

    ax.plot(retweeted['date'],
        retweeted['size'],
        color='pink',
        label='Retweeted')

    ax.plot(cc['date'],
        cc['size'],
        color='deepskyblue',
        label='Created content')

    ax.set(
       title = title )

    ax.set_xlim([datetime.date(2019, 1, 1), datetime.date(2021, 5, 15)])

    plt.axvspan(np.datetime64('2019-12-09'),
                np.datetime64('2020-10-12'),
                ymin=0, ymax=200000,
                facecolor='r',
                alpha=0.05)

    plt.axvspan(np.datetime64('2021-01-25'),
                np.datetime64('2021-05-15'),
                ymin=0,
                ymax=200000,
                facecolor='r',
                alpha=0.05)

    #ax.text(np.datetime64('2020-02-09') , 50, 'suspension \n period', color='red')
    #ax.text(np.datetime64('2021-02-09') , 50, 'suspension \n period', color='red')

    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.locator_params(axis='y', nbins=4)

    ax.grid(axis='y')
    handles, labels = ax.get_legend_handles_labels()
    patch = mpatches.Patch(color='pink',
                           label='Suspension Period')
    handles.append(patch)

    plt.legend(handles=handles)

    plt.setp(ax.get_xticklabels(), rotation=45)

    plt.tight_layout()

    save_figure(figure_name)
    #plt.savefig('./lifesite.jpg', bbox_inches='tight')
    #plt.show()

def create_twitter_figures():

    create_twitter_Lifesite_figure(
    filename = 'twitter_lifesitenews_2021-07-22.csv',
    figure_name = 'lifesite.jpg',
    title = f"Total number of tweets per day of @LifeSite",
    zeros = 1
    )

    create_twitter_Lifesite_figure(
    filename = 'twitter_lifesitenews_domain_name_2021-07-22.csv',
    figure_name = 'lifesite_domain.jpg',
    title = f"Total number of tweets per day sharing a lifesitenews.com link)",
    zeros = 0
    )

if __name__=="__main__":

    create_facebook_trump_figure()
    create_buzzsumo_thebl_figure()
    create_facebook_crowdtangle_infowars_figure()
    create_facebook_buzzsumo_infowars_figure()

    create_youtube_graph()

    create_twitter_figures()
