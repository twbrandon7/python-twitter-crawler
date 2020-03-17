import unittest

import os
import json

from tweet_crawler.tweet_parser import Tweet
from tweet_crawler.tweet_fetcher import get_tokens
from tweet_crawler.storages.json_storage import JsonStorage

TEST_DATA_FOLDER = os.path.join(os.path.dirname(__file__), '../data/')

class TestDiskStorage(unittest.TestCase):
    """Save tweets as json file
    """
    
    def test_save_tweet(self):
        tweet_id = "1239125355866099712"
        tokens = get_tokens()
        tweet = Tweet(tweet_id, access_token=tokens["access_token"], csrf_token=tokens["csrf_token"], guest_token=tokens["guest_token"])
        out = tweet.get_tweets()
        storage = JsonStorage(TEST_DATA_FOLDER)
        storage.save_tweet(out)

        output_path = os.path.join(TEST_DATA_FOLDER, "{}.json".format(tweet_id))
        self.assertTrue(os.path.isfile(output_path))

        with open(output_path, "r", encoding="utf-8") as f:
            json_str = f.read()
        obj = json.loads(json_str)
        self.assertEqual(obj["tweet_id"], tweet_id)

        # clean up
        os.remove(output_path)
    
    def test_append_timeline(self):
        tweet_id = "1239125355866099712"
        tokens = get_tokens()
        tweet = Tweet(tweet_id, access_token=tokens["access_token"], csrf_token=tokens["csrf_token"], guest_token=tokens["guest_token"])
        out = tweet.get_tweets()

        storage = JsonStorage(TEST_DATA_FOLDER)
        storage.save_tweet(out)

        output_path = os.path.join(TEST_DATA_FOLDER, "{}.json".format(tweet_id))
        self.assertTrue(os.path.isfile(output_path))

        storage.append_timeline(tweet_id, out["timelines"])

        with open(output_path, "r", encoding="utf-8") as f:
            json_str = f.read()
        obj = json.loads(json_str)
        self.assertEqual(obj["tweet_id"], tweet_id)
        self.assertEqual(obj["timelines"][-1][0], "POP")

        # clean up
        os.remove(output_path)

