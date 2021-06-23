from datetime import datetime, timedelta
import time
import csv

import requests


def call_buzzsumo_once(params):

    api_call_attempt = 0

    while True:

        if api_call_attempt == 0:
            start_call_time = time.time()
        # if second try or more, wait an exponential amount of time (first 2 sec, then 4, then 16...)
        else: 
            time.sleep(2**(api_call_attempt - 1))
        
        r = requests.get('https://api.buzzsumo.com/search/articles.json', params=params)
        print(r.status_code)

        # if first try, add a sleep function so that we wait at least 1.05 seconds between two calls
        if api_call_attempt == 0:
            end_call_time = time.time()
            if (end_call_time - start_call_time) < 1.2:
                time.sleep(1.2 - (end_call_time - start_call_time))

        if r.status_code == 200:
            break
        else:
            api_call_attempt += 1

    return r.json()['results']


def call_buzzsumo_all_pages(params, writer, data_to_keep):

    page = 0

    while True:

        params['page'] = page
        results = call_buzzsumo_once(params)

        if results == []:
            break
        else:
            for result in results:
                writer.writerow([result[column_name] for column_name in data_to_keep])
            page += 1



def collect_buzzsumo_data_for_one_domain(domain, token, output_path, begin_date, end_date):

    data_to_keep = [
        'url',
        'published_date',
        'domain_name',
        'total_facebook_shares',
        'facebook_likes',
        'facebook_comments',
        'facebook_shares'
    ]

    params = {
        'q': domain,
        'api_key': token,
        'begin_date': datetime.strptime(begin_date, '%Y-%m-%d').timestamp(),
        'end_date': datetime.strptime(end_date, '%Y-%m-%d').timestamp(),
        'num_results': 100
    }

    f = open(output_path, 'w')
    with f:
        writer = csv.writer(f)
        writer.writerow(data_to_keep)

        call_buzzsumo_all_pages(params, writer, data_to_keep)
