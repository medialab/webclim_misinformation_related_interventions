#from __future__ import absolute_import

import requests
import csv
#import dotenv
import time
import json
import os
import os.path

from csv import writer
#from dotenv import load_dotenv
from time import sleep

#documentation: https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all
#max_results: A number between 10 and the system limit (currently 500). By default, a request response will return 10 results.
#300 requests per 15-minute window (app auth)
#Updates: max results is now 100


def connect_to_endpoint(bearer_token, query, start_time, end_time, next_token=None):

    max_results=100

    headers = {"Authorization": "Bearer {}".format(bearer_token)}

    params = {"tweet.fields" : "in_reply_to_user_id,author_id,context_annotations,created_at,public_metrics,entities,geo,id,possibly_sensitive,lang,referenced_tweets", "user.fields":"username,name,description,location,created_at,entities,public_metrics","expansions":"author_id,referenced_tweets.id"}

    if (next_token is not None):
        url = "https://api.twitter.com/2/tweets/search/all?max_results={}&query={}&start_time={}&end_time={}&next_token={}".format(max_results, query, start_time, end_time, next_token)
    else:
        url = "https://api.twitter.com/2/tweets/search/all?max_results={}&start_time={}&end_time={}&query={}".format(max_results, start_time, end_time, query)

    with requests.request("GET", url, params=params, headers=headers) as response:

        if response.status_code != 200:
            raise Exception(response.status_code, response.text)

        return response.json()


def write_results(json_response, filename):

    with open(filename, "a+") as tweet_file:

        writer = csv.DictWriter(tweet_file,
                                ["type_of_tweet",
                                 "id", "author_id",
                                 "username",
                                 "name",
                                 "created_at",
                                 "text",
                                 "possibly_sensitive",
                                 "in_reply_to_user_id",
                                 "mentions_username",
                                 "retweet_count",
                                 "reply_count",
                                 "like_count",
                                 "lang",
                                 "expanded_urls",
                                 "theme",
                                 "theme_description",
                                 "user_created_at",
                                 "user_profile_description",
                                 "user_location",
                                 "user_expanded_url",
                                 "followers_count",
                                 "following_count",
                                 "tweet_count",
                                 "listed_count"],
                                extrasaction='ignore')


        if "data" and "includes" in json_response:

            for tweet in json_response["data"]:

                if "referenced_tweets" in tweet.keys():
                    tweet["type_of_tweet"] = tweet["referenced_tweets"][0]["type"]

                    if tweet["referenced_tweets"][0]["type"] == "retweeted":

                        if "tweets" in json_response["includes"]:

                            for tw in json_response["includes"]["tweets"]:
                                if tweet["referenced_tweets"][0]["id"] == tw["id"] :
                                    tweet['retweet_count'] = tw["public_metrics"]["retweet_count"]
                                    tweet['reply_count'] = tw["public_metrics"]["reply_count"]
                                    tweet['like_count'] = tw["public_metrics"]["like_count"]
                                    tweet['possibly_sensitive'] = tw['possibly_sensitive']

                    elif (tweet["referenced_tweets"][0]["type"] == "quoted" or tweet["referenced_tweets"][0]["type"] == "replied_to"):
                        tweet['retweet_count'] = tweet["public_metrics"]["retweet_count"]
                        tweet['reply_count'] = tweet["public_metrics"]["reply_count"]
                        tweet['like_count'] = tweet["public_metrics"]["like_count"]

                else:

                    tweet['retweet_count'] = tweet["public_metrics"]["retweet_count"]
                    tweet['reply_count'] = tweet["public_metrics"]["reply_count"]
                    tweet['like_count'] = tweet["public_metrics"]["like_count"]


                if "entities" in tweet:
                    #multiple mentions
                    if "mentions" in tweet["entities"]:
                        l=len(tweet["entities"]['mentions'])
                        tweet['mentions_username'] = [tweet["entities"]['mentions'][0]['username']]
                        if l>1:
                            for i in range(1,l):
                                a = tweet["entities"]['mentions'][i]['username']
                                tweet['mentions_username'].append(a)
                    else:
                        tweet['mentions_username'] = []
                    # multiple URLs
                    if "urls" in tweet["entities"]:
                        lu=len(tweet["entities"]['urls'])
                        tweet['expanded_urls'] =[tweet["entities"]['urls'][0]['expanded_url']]
                        if lu>1:
                            for i in range(1,lu):
                                b=tweet["entities"]['urls'][i]['expanded_url']
                                tweet['expanded_urls'].append(b)
                    else:
                        tweet['expanded_urls'] = []

                if "context_annotations" in tweet:
                    if "domain" in tweet["context_annotations"][0]:
                        tweet['theme']=tweet["context_annotations"][0]["domain"]["name"]
                        if "description" in tweet["context_annotations"][0]["domain"]:
                            tweet['theme_description']=tweet["context_annotations"][0]["domain"]['description']
                    else:
                        tweet['theme']=''
                        tweet['theme_description']=''

                user_index = {}

                for user in json_response["includes"]["users"]:

                    if 'id' in user.keys():
                        user_index[user['id']] = user

                        if tweet['author_id'] == user['id']:

                            tweet['username'] = user['username']
                            tweet['name'] = user['name']
                            tweet['user_created_at'] = user['created_at']
                            tweet["followers_count"] = user["public_metrics"]["followers_count"]
                            tweet['following_count'] = user["public_metrics"]["following_count"]
                            tweet['tweet_count'] = user["public_metrics"]["tweet_count"]
                            tweet['listed_count'] = user["public_metrics"]["listed_count"]

                            if 'description' in user.keys():
                                tweet['user_profile_description']= user ['description']

                            if "location" in user.keys():
                                tweet['user_location'] = user['location']

                            #if "entities" in user.keys():
                            #    if "url" in user['entities']:
                            #        if "urls" in user['entities']['url']:
                            #            tweet['user_expanded_url']=user['entities']['url']['urls'][0]['expanded_url']

                writer.writerow(tweet)

        else:
            raise ValueError("User not found")


def get_next_token(query, token, count, filename, start_time, end_time, bearer_token):
    json_response = connect_to_endpoint(bearer_token, query, start_time, end_time, token)
    result_count = json_response['meta']['result_count']

    if 'next_token' in json_response['meta']:
        sleep(3)
        next_token = json_response['meta']['next_token']
        #print(next_token)
        if result_count is not None and result_count > 0:

            count += result_count
            print(count)
        write_results(json_response, filename)
        return next_token, count
    else:
        write_results(json_response, filename)
        return None, count

def collect_twitter_data(query, start_time, end_time, bearer_token, filename):
#def collect_twitter_data(queries, start_time, end_time, bearer_token):

    #for query in queries:

    #filename = '/Users/shadenshabayek/Documents/Webclim/Data/Tw/infowars/tweets_' + str(query)[5:] + '_' + str(timestr) + '.csv'
    print(query)

    flag = True
    count = 0
    file_exists = os.path.isfile(filename)

    with open(filename, "a+") as tweet_file:
        writer = csv.DictWriter(tweet_file,
                                ["type_of_tweet",
                                 "id",
                                 "author_id",
                                 "username",
                                 "name",
                                 "created_at",
                                 "text",
                                 "possibly_sensitive",
                                 "in_reply_to_user_id",
                                 "mentions_username",
                                 "retweet_count",
                                 "reply_count",
                                 "like_count",
                                 "lang",
                                 "expanded_urls",
                                 "theme",
                                 "theme_description",
                                 "user_created_at",
                                 "user_profile_description",
                                 "user_location",
                                 "user_expanded_url",
                                 "followers_count",
                                 "following_count",
                                 "tweet_count",
                                 "listed_count"], extrasaction='ignore')
        if not file_exists:
            writer.writeheader()
    try:
        next_token, count = get_next_token(query, None, count, filename, start_time, end_time, bearer_token)

    except ValueError as error:
        print(type(error), error)
        flag = False

    except Exception as error:
        code, text = error.args
        if code == 429:
            print("Too many requests, sleeping and retry")
            time.sleep(3)
            next_token, count = get_next_token(query, None, count, filename, start_time, end_time, bearer_token)
        if code == 503:
            print("service unav, sleeping and retry")
            time.sleep(3)
            next_token, count = get_next_token(query, None, count, filename, start_time, end_time, bearer_token)

    except ConnectionError as error:
        code, text = error.args
        if code == 54:
            print("Connection error, sleeping and retry")
            time.sleep(3)
            next_token, count = get_next_token(query, None, count, filename, start_time, end_time, bearer_token)

    while flag:
        next_token, count = get_next_token(query, next_token, count, filename, start_time, end_time, bearer_token)
        if count >= 1000000:
            break
        if next_token is None:
            flag = False


    print("Total Tweet IDs saved: {}".format(count))


#tic toc !

def TicTocGenerator():
    # Generator that returns time differences
    ti = 0           # initial time
    tf = time.time() # final time
    while True:
        ti = tf
        tf = time.time()
        yield tf-ti # returns the time difference

TicToc = TicTocGenerator() # create an instance of the TicTocGen generator

# This will be the main function through which we define both tic() and toc()
def toc(tempBool=True):
    # Prints the time difference yielded by generator instance TicToc
    tempTimeInterval = next(TicToc)
    if tempBool:
        print( "Elapsed time: %f seconds.\n" %tempTimeInterval )

def tic():
    # Records a time in TicToc, marks the beginning of a time interval
    toc(False)
