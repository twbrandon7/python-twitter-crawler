import unittest

from tweet_crawler.tweet_parser import Tweet
from tweet_crawler.tweet_fetcher import get_tokens


class TestTweetObject(unittest.TestCase):
    def test_constructor(self):
        """
        Test if the constructor works
        """
        tweet_id = "1238007172786577408"
        tokens = get_tokens()
        tweet = Tweet(tweet_id, access_token=tokens["access_token"], csrf_token=tokens["csrf_token"], guest_token=tokens["guest_token"])
        self.assertTrue(len(tweet.entries) > 0)
    
    def test_get_tweets(self):
        tweet_id = "1238007172786577408"
        tokens = get_tokens()
        tweet = Tweet(tweet_id, access_token=tokens["access_token"], csrf_token=tokens["csrf_token"], guest_token=tokens["guest_token"])
        tweet.get_tweets()
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()