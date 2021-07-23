import os
from datetime import date
from dotenv import load_dotenv
from utils_twitter import collect_twitter_data
from utils_twitter import tic
from utils_twitter import toc

tic()

#collect tweets that share globalresearch.ca domain name

if __name__=="__main__":

    load_dotenv()
    collect_twitter_data(
        query = 'globalresearch.ca',
        start_time = '2020-12-31T23:00:00Z',
        end_time = '2021-07-01T23%3A59%3A59Z',
        bearer_token= os.getenv('TWITTER_TOKEN'),
        filename = os.path.join('.', 'data', 'twitter_globalresearch_domain_name_' + str(date.today()) + '.csv'),
    )
    toc()
