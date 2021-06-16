import os
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def import_data(file_name):
    data_path = os.path.join(".", "data", file_name)
    df = pd.read_csv(data_path, low_memory=False)
    return df


def save_figure(figure_name):
    figure_path = os.path.join('.', 'figure', figure_name)
    plt.savefig(figure_path)
    print("The '{}' figure is saved.".format(figure_name))


def create_suspension_facebook_trump_figure():

    df = import_data('crowdtangle_facebook_trump_2021-06-16.csv')
    df['date'] = pd.to_datetime(df['date'])
    serie_to_plot = df.resample('D', on='date')['date'].agg('count')
    serie_to_plot = serie_to_plot.append(pd.Series([0, 0], index=[pd.Timestamp(2021, 1, 7), pd.Timestamp(2021, 6, 8)]))

    plt.figure(figsize=(8, 3.5))
    plt.title(df.account_name.iloc[0])
    plt.plot(serie_to_plot, color='royalblue', label='Number of Facebook posts per day')
    plt.legend()

    ax = plt.subplot(111)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.grid(axis="y")
    plt.locator_params(axis='y', nbins=4)

    plt.xlim(
        np.datetime64(datetime.strptime('2019-12-31', '%Y-%m-%d')), 
        np.datetime64(datetime.strptime('2021-06-10', '%Y-%m-%d'))
    )
    xticks = [np.datetime64('2020-01-01'), np.datetime64('2020-04-01'), 
              np.datetime64('2020-07-01'), np.datetime64('2020-10-01'),
              np.datetime64('2021-01-01'), np.datetime64('2021-04-01'),
             ]
    plt.xticks(xticks, rotation=30, ha='right')
    plt.axvspan(np.datetime64('2021-01-06'), np.datetime64('2021-06-08'), 
                ymin=0, ymax=200000, facecolor='r', alpha=0.05)

    plt.text(np.datetime64('2021-01-31'), 45, 'Suspension period', color='r')

    plt.tight_layout()
    save_figure('suspension_facebook_trump.png')


if __name__=="__main__":

    create_suspension_facebook_trump_figure()
