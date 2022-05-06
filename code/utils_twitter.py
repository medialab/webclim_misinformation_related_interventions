import requests
import csv
import time
import json
import os
import os.path

from csv import writer
from time import sleep

'''Functions to collect historical search twitter data from the API v2'''

#300 requests per 15-minute window (app auth)
#Updates: max results is now 100!

def connect_to_endpoint_historical_search(bearer_token, query, start_time, end_time, next_token=None):

    max_results=100

    headers = {'Authorization': 'Bearer {}'.format(bearer_token)}

    params = {'tweet.fields' : 'in_reply_to_user_id,author_id,context_annotations,created_at,public_metrics,entities,geo,id,possibly_sensitive,lang,referenced_tweets', 'user.fields':'username,name,description,location,created_at,entities,public_metrics','expansions':'author_id,referenced_tweets.id,attachments.media_keys'}

    if (next_token is not None):
        url = 'https://api.twitter.com/2/tweets/search/all?max_results={}&query={}&start_time={}&end_time={}&next_token={}'.format(max_results, query, start_time, end_time, next_token)
    else:
        url = 'https://api.twitter.com/2/tweets/search/all?max_results={}&start_time={}&end_time={}&query={}'.format(max_results, start_time, end_time, query)

    with requests.request('GET', url, params=params, headers=headers) as response:

        if response.status_code != 200:
            raise Exception(response.status_code, response.text)

        return response.json()

def write_results(json_response, filename, query):

    with open(filename, 'a+') as tweet_file:

        writer = csv.DictWriter(tweet_file,
                                ['query',
                                'type_of_tweet',
                                'referenced_tweet_id',
                                 'id',
                                 'author_id',
                                 'username',
                                 'name',
                                 'created_at',
                                 'text',
                                 'possibly_sensitive',
                                 'retweet_count',
                                 'reply_count',
                                 'like_count',
                                 'hashtags',
                                 'in_reply_to_user_id',
                                 'in_reply_to_username',
                                 'quoted_user_id',
                                 'quoted_username',
                                 'retweeted_username',
                                 'mentions_username',
                                 'lang',
                                 'expanded_urls',
                                 'domain_name',
                                 'user_created_at',
                                 'user_profile_description',
                                 'user_location',
                                 'followers_count',
                                 'following_count',
                                 'tweet_count',
                                 'listed_count',
                                 'collection_date',
                                 'collection_method',
                                 'errors',
                                 'error_type'],
                                extrasaction='ignore')

        if 'data' and 'includes' in json_response:

            for tweet in json_response['data']:

                user_index = {}

                for user in json_response['includes']['users']:

                    if 'id' in user.keys():

                        user_index[user['id']] = user

                        if tweet['author_id'] == user['id']:

                            tweet['username'] = user['username']
                            tweet['name'] = user['name']
                            tweet['user_created_at'] = user['created_at']
                            tweet['followers_count'] = user['public_metrics']['followers_count']
                            tweet['following_count'] = user['public_metrics']['following_count']
                            tweet['tweet_count'] = user['public_metrics']['tweet_count']
                            tweet['listed_count'] = user['public_metrics']['listed_count']

                            if 'description' in user.keys():
                                tweet['user_profile_description']= user ['description']

                            if 'location' in user.keys():
                                tweet['user_location'] = user['location']

                        if 'in_reply_to_user_id' in tweet.keys():

                            if tweet['in_reply_to_user_id'] == user['id']:

                                a = user['username'].lower()
                                tweet['in_reply_to_username'] = a

                if 'context_annotations' in tweet:
                    if 'domain' in tweet['context_annotations'][0]:
                        tweet['theme']=tweet['context_annotations'][0]['domain']['name']
                        if 'description' in tweet['context_annotations'][0]['domain']:
                            tweet['theme_description']=tweet['context_annotations'][0]['domain']['description']
                    else:
                        tweet['theme']=''
                        tweet['theme_description']=''

                if 'entities' in tweet:

                    if 'mentions' in tweet['entities']:

                        l=len(tweet['entities']['mentions'])

                        tweet['mentions_username'] = []

                        for i in range(0,l):

                            a = tweet['entities']['mentions'][i]['username']
                            a = a.lower()
                            tweet['mentions_username'].append(a)

                    else:
                        tweet['mentions_username'] = []

                    if 'urls' in tweet['entities']:

                        lu=len(tweet['entities']['urls'])

                        tweet['expanded_urls']=[]
                        tweet['domain_name']=[]

                        for i in range(0,lu):

                            link = tweet['entities']['urls'][i]['expanded_url']

                            if len(link) < 35:

                                if 'unwound_url' in tweet['entities']['urls'][i].keys():
                                    b = tweet['entities']['urls'][i]['unwound_url']
                                    c = get_domain_name(tweet['entities']['urls'][i]['unwound_url'])

                                elif 'unwound_url' not in tweet['entities']['urls'][i].keys():
                                    for result in multithreaded_resolve([link]):
                                        b = result.stack[-1].url
                                        c = get_domain_name(result.stack[-1].url)

                                else:
                                    b = tweet['entities']['urls'][i]['expanded_url']
                                    c = get_domain_name(tweet['entities']['urls'][i]['expanded_url'])

                                tweet['expanded_urls'].append(b)
                                tweet['domain_name'].append(c)


                            else:
                                d = tweet['entities']['urls'][i]['expanded_url']
                                e = get_domain_name(tweet['entities']['urls'][i]['expanded_url'])

                                tweet['expanded_urls'].append(d)
                                tweet['domain_name'].append(e)
                    else:
                        tweet['expanded_urls'] = []
                        tweet['domain_name'] = []

                    if 'hashtags' in tweet['entities']:
                        l=len(tweet['entities']['hashtags'])
                        tweet['hashtags'] = []

                        for i in range(0,l):
                            a = tweet['entities']['hashtags'][i]['tag']
                            tweet['hashtags'].append(a)
                    else:
                        tweet['hashtags'] = []
                else:
                    tweet['mentions_username'] = []
                    tweet['hashtags'] = []
                    tweet['expanded_urls'] = []
                    tweet['domain_name'] = []

                if 'referenced_tweets' in tweet.keys():

                    tweet['type_of_tweet'] = tweet['referenced_tweets'][0]['type']
                    tweet['referenced_tweet_id'] = tweet['referenced_tweets'][0]['id']

                    if (tweet['referenced_tweets'][0]['type'] == 'retweeted' or tweet['referenced_tweets'][0]['type'] == 'quoted' or tweet['referenced_tweets'][0]['type'] == 'replied_to'):

                        if 'tweets' in json_response['includes']:

                            for tw in json_response['includes']['tweets']:

                                if tweet['referenced_tweets'][0]['id'] == tw['id'] :

                                    tweet['retweet_count'] = tw['public_metrics']['retweet_count']
                                    tweet['reply_count'] = tw['public_metrics']['reply_count']
                                    tweet['like_count'] = tw['public_metrics']['like_count']
                                    tweet['possibly_sensitive'] = tw['possibly_sensitive']
                                    tweet['text'] = tw['text']

                                    if tweet['referenced_tweets'][0]['type'] == 'retweeted':

                                        if 'entities' in tweet :

                                            if 'mentions' in tweet['entities'].keys():

                                                if tweet['entities']['mentions'][0]['id'] == tw['author_id'] :

                                                    a = tweet['entities']['mentions'][0]['username']
                                                    b = a.lower()
                                                    tweet['retweeted_username'] = b

                                    if tweet['referenced_tweets'][0]['type'] == 'replied_to':

                                        if 'entities' in tweet :

                                            if 'mentions' in tweet['entities'].keys():

                                                if tweet['entities']['mentions'][0]['id'] == tweet['in_reply_to_user_id'] :

                                                    a = tweet['entities']['mentions'][0]['username']
                                                    b = a.lower()
                                                    tweet['in_reply_to_username'] = b


                                    if tweet['referenced_tweets'][0]['type'] == 'quoted':

                                        tweet['quoted_user_id'] = tw['author_id']

                                        if 'entities' in tweet.keys():

                                            if 'urls' in tweet['entities']:

                                                l = len(tweet['entities']['urls'])

                                                for i in range(0,l):

                                                    if 'expanded_url' in tweet['entities']['urls'][i].keys():

                                                        url = tweet['entities']['urls'][i]['expanded_url']

                                                        if tweet['referenced_tweets'][0]['id'] in url:

                                                            if 'https://twitter.com/' in url:

                                                                a = url.split('https://twitter.com/')[1]
                                                                b = a.split('/status')[0].lower()
                                                                tweet['quoted_username'] = b

                                    if 'entities' in  tw.keys():

                                        if 'urls' in tw['entities']:

                                            lu=len(tw['entities']['urls'])

                                            tweet['expanded_urls']=[]
                                            tweet['domain_name']=[]

                                            for i in range(0,lu):

                                                link = tw['entities']['urls'][i]['expanded_url']

                                                if len(link) < 35:

                                                    if 'unwound_url' in tw['entities']['urls'][i].keys():
                                                        b = tw['entities']['urls'][i]['unwound_url']
                                                        c = get_domain_name(tw['entities']['urls'][i]['unwound_url'])

                                                    elif 'unwound_url' not in tw['entities']['urls'][i].keys():
                                                        for result in multithreaded_resolve([link]):
                                                            b = result.stack[-1].url
                                                            c = get_domain_name(result.stack[-1].url)

                                                    else:
                                                        b = tw['entities']['urls'][i]['expanded_url']
                                                        c = get_domain_name(tw['entities']['urls'][i]['expanded_url'])

                                                    tweet['expanded_urls'].append(b)
                                                    tweet['domain_name'].append(c)

                                                else:
                                                    d = tw['entities']['urls'][i]['expanded_url']
                                                    e = get_domain_name(tw['entities']['urls'][i]['expanded_url'])

                                                    tweet['expanded_urls'].append(d)
                                                    tweet['domain_name'].append(e)

                                        else:
                                            tweet['expanded_urls'] = []
                                            tweet['domain_name'] = []

                                        if 'hashtags' in tw['entities']:
                                            l=len(tw['entities']['hashtags'])
                                            tweet['hashtags'] = []

                                            for i in range(0,l):
                                                a = tw['entities']['hashtags'][i]['tag']
                                                tweet['hashtags'].append(a)
                                        else:
                                            tweet['hashtags'] = []

                                        if 'mentions' in tw['entities']:

                                            l=len(tw['entities']['mentions'])

                                            for i in range(0,l):
                                                a = tw['entities']['mentions'][i]['username']
                                                a = a.lower()
                                                tweet['mentions_username'].append(a)

                else:

                    tweet['retweet_count'] = tweet['public_metrics']['retweet_count']
                    tweet['reply_count'] = tweet['public_metrics']['reply_count']
                    tweet['like_count'] = tweet['public_metrics']['like_count']

                tweet['query'] = query
                tweet['username'] = tweet['username'].lower()


                if len(tweet['mentions_username']) > 1:
                    tweet['mentions_username'] = list(set(tweet['mentions_username']))


                timestr = time.strftime('%Y-%m-%d')
                tweet['collection_date'] = timestr
                tweet['collection_method'] = 'Twitter API V2'

                if 'errors' in json_response:
                    for error in json_response['errors']:
                        if 'referenced_tweets' in tweet.keys():
                            if tweet['referenced_tweets'][0]['id'] == error['resource_id']:
                                tweet['errors'] = error['detail']
                                tweet['error_type'] = error['title']

                writer.writerow(tweet)

        else:
            #raise ValueError('User not found')
            pass

def get_next_token(query, token, count, filename, start_time, end_time, bearer_token):

    json_response = connect_to_endpoint_historical_search(bearer_token, query, start_time, end_time, token)

    result_count = json_response['meta']['result_count']

    if 'next_token' in json_response['meta']:
        sleep(3)
        next_token = json_response['meta']['next_token']
        if result_count is not None and result_count > 0:

            count += result_count
            print(count)
        #try:
        write_results(json_response, filename, query)
        return next_token, count
    else:
        write_results(json_response, filename, query)
        return None, count

def collect_twitter_data(query, start_time, end_time, bearer_token, filename):

    print(query)

    flag = True
    count = 0
    file_exists = os.path.isfile(filename)

    with open(filename, 'a+') as tweet_file:

        writer = csv.DictWriter(tweet_file,
                                ['query',
                                'type_of_tweet',
                                'referenced_tweet_id',
                                 'id',
                                 'author_id',
                                 'username',
                                 'name',
                                 'created_at',
                                 'text',
                                 'possibly_sensitive',
                                 'retweet_count',
                                 'reply_count',
                                 'like_count',
                                 'hashtags',
                                 'in_reply_to_user_id',
                                 'in_reply_to_username',
                                 'quoted_user_id',
                                 'quoted_username',
                                 'retweeted_username',
                                 'mentions_username',
                                 'lang',
                                 'expanded_urls',
                                 'domain_name',
                                 'user_created_at',
                                 'user_profile_description',
                                 'user_location',
                                 'followers_count',
                                 'following_count',
                                 'tweet_count',
                                 'listed_count',
                                 'collection_date',
                                 'collection_method',
                                 'errors',
                                 'error_type'], extrasaction='ignore')
        if not file_exists:
            writer.writeheader()

    next_token = None

    while flag:
        next_token, count = get_next_token(query, next_token, count, filename, start_time, end_time, bearer_token)
        if count >= 2000000:
            break
        if next_token is None:
            flag = False


    print('Total Tweet IDs saved: {}'.format(count))

def TicTocGenerator():
    ti = 0
    tf = time.time()
    while True:
        ti = tf
        tf = time.time()
        yield tf-ti

TicToc = TicTocGenerator()

def toc(tempBool=True):
    tempTimeInterval = next(TicToc)
    if tempBool:
        print( 'Elapsed time: %f seconds.\n' %tempTimeInterval )

def tic():
    toc(False)
