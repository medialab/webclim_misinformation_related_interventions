import os
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ural


def import_data(file_name):
    data_path = os.path.join(".", "data", file_name)
    df = pd.read_csv(data_path, low_memory=False)
    return df


def save_figure(figure_name):
    figure_path = os.path.join('.', 'figure', figure_name)
    plt.savefig(figure_path)
    print("The '{}' figure is saved.".format(figure_name))


def create_suspension_facebook_trump_figure():

    print()

    df = import_data('facebook_crowdtangle_trump_2021-06-21.csv')

    df['date'] = pd.to_datetime(df['date'])
    serie_to_plot = df.resample('D', on='date')['date'].agg('count')
    serie_to_plot = serie_to_plot.append(pd.Series(
        [0, 0], 
        index=[pd.Timestamp(2021, 1, 7), pd.Timestamp(2021, 6, 15)]
    ))

    plt.figure(figsize=(8, 3))
    plt.title(df.account_name.iloc[0])
    plt.plot(serie_to_plot, color='royalblue', label='Number of Facebook posts per day')
    plt.legend()

    ax = plt.subplot(111)
    ax.set_frame_on(False)
    ax.grid(axis="y")
    plt.locator_params(axis='y', nbins=4)

    plt.xlim(
        np.datetime64(datetime.strptime('2019-12-31', '%Y-%m-%d')), 
        np.datetime64(datetime.strptime('2021-06-15', '%Y-%m-%d'))
    )
    plt.ylim(-1, 55)

    xticks = [np.datetime64('2020-01-01'), np.datetime64('2020-04-01'), 
              np.datetime64('2020-07-01'), np.datetime64('2020-10-01'),
              np.datetime64('2021-01-01'), np.datetime64('2021-04-01'),
             ]
    plt.xticks(xticks, rotation=30, ha='right')
    plt.axvspan(np.datetime64('2021-01-06'), np.datetime64('2021-06-15'), 
                ymin=0, ymax=200000, facecolor='r', alpha=0.05)

    plt.text(np.datetime64('2021-02-07'), 45, 'Suspension period', color='r')

    plt.tight_layout()
    save_figure('facebook_crowdtangle_trump.png')


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
    return int((after - before) * 100 / before)


def print_the_percentage_changes(df, date='2019-05-02', period=60):

    df_before = df[df['date'] < np.datetime64(date)]
    df_before = df_before[df_before['date'] >= np.datetime64(datetime.strptime(date, '%Y-%m-%d') - timedelta(days=period))]

    df_after = df[df['date'] > np.datetime64(date)]
    df_after = df_after[df_after['date'] <= np.datetime64(datetime.strptime(date, '%Y-%m-%d') + timedelta(days=period))]

    print('Drop after the', date, ': Reactions:',
        calculate_percentage_change(df_before['reaction'].sum(), df_after['reaction'].sum())
        , '%, Shares:',
        calculate_percentage_change(df_before['share'].sum(), df_after['share'].sum()), 
        '%, Comments:',
        calculate_percentage_change(df_before['comment'].sum(), df_after['comment'].sum()),
        '%.'
    )

def arrange_plot(ax):

    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.grid(axis="y")
    plt.locator_params(axis='y', nbins=4)

    plt.xlim(
        np.datetime64(datetime.strptime('2019-01-01', '%Y-%m-%d')), 
        np.datetime64(datetime.strptime('2021-06-15', '%Y-%m-%d'))
    )
    plt.xticks(
        [np.datetime64('2019-06-30'), np.datetime64('2020-06-30'), np.datetime64('2021-04-30')],
        ['2019', '2020', '2021'], fontsize='large'
    )
    ax.xaxis.set_tick_params(length=0)
    plt.axvspan(np.datetime64('2020-01-01'), np.datetime64('2020-12-31'), 
                ymin=0, ymax=200000, facecolor='k', alpha=0.05)

    plt.plot([np.datetime64("2019-05-02"), np.datetime64("2019-05-02")], [0, 70], color='C3', linestyle='--')
    plt.text(np.datetime64(datetime.strptime("2019-05-02", '%Y-%m-%d') - timedelta(days=5)), 
                71, "reduction", size='medium', color='C3', rotation=30)


def create_facebook_crowdtangle_infowars_figure():

    print()

    df = import_data('facebook_crowdtangle_infowars_2021-06-29.csv')
    df = clean_crowdtangle_data(df)
    print('There are {} posts after removing the indirect links in the CrowdTangle Infowars date.'.format(len(df)))
    print_the_percentage_changes(df, date='2019-05-02', period=60)

    fig = plt.figure(figsize=(10, 8))
    fig.suptitle('Facebook posts sharing an Infowars link (CrowdTangle)')
    
    ax = plt.subplot(211)
    plt.plot(df.resample('D', on='date')['date'].agg('count'),
        label='Number of Facebook posts per day', color='royalblue')
    plt.legend()
    arrange_plot(ax)
    plt.ylim(0, 160)

    ax = plt.subplot(212)
    plt.plot(df.resample('D', on='date')['comment'].mean(),
        label="Comments per post", color='lightskyblue')
    plt.plot(df.resample('D', on='date')['share'].mean(),
        label="Shares per post", color='royalblue')
    plt.plot(df.resample('D', on='date')['reaction'].mean(),
        label="Reactions (likes, ...) per post", color='navy')
    plt.legend()
    arrange_plot(ax)
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

    fig = plt.figure(figsize=(10, 4))
    fig.suptitle('Facebook engagement for the Infowars articles (Buzzsumo)')

    ax = plt.subplot(111)
    plt.plot(filter(df, 'facebook_comments'),
        label="Comments per article", color='lightskyblue')
    plt.plot(filter(df, 'facebook_shares'),
        label="Shares per article", color='royalblue')
    plt.plot(filter(df, 'facebook_likes'),
        label="Reactions (likes, ...) per article", color='navy')
    plt.legend()
    arrange_plot(ax)
    plt.ylim(0, 3000)

    plt.tight_layout()
    save_figure(figure_name='facebook_buzzsumo_infowars.png')    


if __name__=="__main__":

    # create_suspension_facebook_trump_figure()
    # create_facebook_crowdtangle_infowars_figure()
    create_facebook_buzzsumo_infowars_figure()
