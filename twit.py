"""
Example code to search for a string in tweets.

"""
import collections
import configparser
import sys
from time import sleep
from twitter import OAuth, Twitter

def auth(): 
    config = configparser.ConfigParser()
    config.read("api.config")
    api = config["api"]
    auth_details = OAuth(api["token"],
                        api["token_secret"],
                        api["con_key"], 
                        api["con_secret"])

    return Twitter(auth=auth_details)
    
def initial_max_id(searcher):
    """
    Perform the search returning the max_id in order to initialize the
    high-water mark for finding new tweets."""

    results = searcher.twitter.search.tweets(q=searcher.query, result_type="recent")
    return results["search_metadata"]["max_id"]

def run_search(searcher, max_id):
    rate_limit = 5 #seconds to delay between searches in order to not trip the API limit
    while True:
        print(".")
        results = searcher.twitter.search.tweets(q=searcher.query, 
                                   since_id=max_id,
                                   result_type="recent")
        for hit in results["statuses"]:
            yield hit
        max_id = results["search_metadata"]["max_id"]
        sleep(rate_limit)
        
def print_result(result):
    """This is printing from the dictionary of statuses found"""
    print("GOT A HIT!!!\n\n")
    print("User name = " + result["user"]["screen_name"])
    print("Text = " + result["text"])
    print("--------\n\n")   
        
if __name__ == "__main__":
    query = sys.argv[1]
    print("Searching for " + query)
    
    Searcher = collections.namedtuple("Searcher", "twitter query")
    searcher = Searcher(twitter=auth(), query=query)
    
    max_id = initial_max_id(searcher)
    for result in run_search(searcher, max_id):
        print_result(result)
    