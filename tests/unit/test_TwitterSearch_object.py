import unittest

from tweet_crawler.tweet_parser import TwitterSearch
from tweet_crawler.tweet_fetcher import get_tokens

import json

class TestTweetSearchObject(unittest.TestCase):

    def test_get_next_ids(self):
        keyword = "spacex"
        tokens = get_tokens()
        search = TwitterSearch(keyword, access_token=tokens["access_token"], csrf_token=tokens["csrf_token"], guest_token=tokens["guest_token"])
        
        result1 = search.get_next_ids()
        self.assertEqual(type(result1), list)
        self.assertGreater(len(result1), 0)

        result2 = search.get_next_ids()
        self.assertEqual(type(result2), list)
        self.assertGreater(len(result2), 0)

        self.assertNotEqual(search.next_cursor, None)
        self.assertNotEqual(search.previous_cursor, None)


if __name__ == '__main__':
    unittest.main()