import unittest

from tweet_crawler.tweet_parser import Tweet
from tweet_crawler.tweet_fetcher import get_tokens

import json


class TestTweetObject(unittest.TestCase):    
    def test_get_main_tweet(self):
        tweet_id = "1239125355866099712"
        tokens = get_tokens()
        tweet = Tweet(tweet_id, access_token=tokens["access_token"], csrf_token=tokens["csrf_token"], guest_token=tokens["guest_token"])
        out = tweet.get_main_tweet()
        self.assertEqual(out["tweet"], "TWEEEET!")

    def test_get_tweets_with_bound(self):
        tweet_id = "1238007172786577408"
        tokens = get_tokens()
        tweet = Tweet(tweet_id, access_token=tokens["access_token"], csrf_token=tokens["csrf_token"], guest_token=tokens["guest_token"])
        out = tweet.get_main_tweet(timeline_length=2)
        max_len = -1
        
        for timeline in out["timelines"]:
            max_len = max(max_len, len(timeline))
            self.assertTrue(len(timeline) <= 2)
        self.assertEqual(max_len, 2)

    def test_get_next_timelines(self):
        tweet_id = "1238007172786577408"
        tokens = get_tokens()
        tweet = Tweet(tweet_id, access_token=tokens["access_token"], csrf_token=tokens["csrf_token"], guest_token=tokens["guest_token"])
        out = tweet.get_main_tweet(timeline_length=-1)
        
        self.assertNotEqual(out, None)

        timelines = tweet.get_next_timelines(timeline_length=-1)
        self.assertNotEqual(timelines, None)


if __name__ == '__main__':
    unittest.main()