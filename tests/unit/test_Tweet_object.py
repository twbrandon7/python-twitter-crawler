import unittest

from tweet_crawler.tweet_parser import Tweet
from tweet_crawler.tweet_fetcher import get_tokens

import json


class TestTweetObject(unittest.TestCase):
    # def test_constructor(self):
    #     """
    #     Test if the constructor works
    #     """
    #     tweet_id = "1238007172786577408"
    #     tokens = get_tokens()
    #     tweet = Tweet(tweet_id, access_token=tokens["access_token"], csrf_token=tokens["csrf_token"], guest_token=tokens["guest_token"])
    #     self.assertTrue(len(tweet.entries) > 0)
    
    def test_get_tweets(self):
        tweet_id = "1239125355866099712"
        tokens = get_tokens()
        tweet = Tweet(tweet_id, access_token=tokens["access_token"], csrf_token=tokens["csrf_token"], guest_token=tokens["guest_token"])
        out = tweet.get_tweets()
        self.assertEqual(out["tweet"], "TWEEEET!")

    def test_get_tweets_with_bound(self):
        tweet_id = "1238007172786577408"
        tokens = get_tokens()
        tweet = Tweet(tweet_id, access_token=tokens["access_token"], csrf_token=tokens["csrf_token"], guest_token=tokens["guest_token"])
        out = tweet.get_tweets(max_timelines=10, timeline_length=2)
        self.assertEqual(len(out["timelines"]), 10)

    # def test_constructor_with_cursor(self):
    #     tweet_id = "1238007172786577408"
    #     cursor = "LBlmhICmiaempa4igMCihbHHpK4igICoqazWsa4igoCoibe6pa4igoCmscfgpq4igMChqdD/pK4iJQISAAA="
    #     tokens = get_tokens()
    #     tweet = Tweet(
    #         tweet_id,
    #         access_token=tokens["access_token"],
    #         csrf_token=tokens["csrf_token"],
    #         guest_token=tokens["guest_token"],
    #         cursor=cursor)
    #     self.assertTrue(len(tweet.entries) > 0)

if __name__ == '__main__':
    unittest.main()