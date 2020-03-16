import unittest

import os
from tweet_crawler import tweet_fetcher


TEST_DATA_FOLDER = os.path.join(os.path.dirname(__file__), '../data/')


class TestTweetFetcher(unittest.TestCase):
    def test_fetch_twitter_home_page(self):
        """
        Checking the ability to get Twitter home page
        """
        html = tweet_fetcher.fetch_twitter_home_page()
        self.assertNotEqual(html, None)


    def test_get_main_js_url(self):
        with open(os.path.join(TEST_DATA_FOLDER, 'homepage.html'), 'r', encoding='utf-8') as f:  
            html = f.read() 
            url = tweet_fetcher.get_main_js_url(html)
        self.assertEqual(url, "https://abs.twimg.com/responsive-web/web/main.6ad4f064.js")


    def test_fetch_main_js(self):
        url = "https://abs.twimg.com/responsive-web/web/main.6ad4f064.js"
        result = tweet_fetcher.fetch_main_js(url)
        self.assertNotEqual(result, None)

    
    def test_get_access_token(self):
        with open(os.path.join(TEST_DATA_FOLDER, 'main.6ad4f064.js'), 'r', encoding='utf-8') as f:  
            main_js = f.read()
            token = tweet_fetcher.get_access_token(main_js)
        self.assertEqual(token, "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA")


    def test_fetch_guest_token(self):
        access_token = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
        csrf_token = "c284dd882b5d16165e8de3717a4f19fc"
        res = tweet_fetcher.fetch_guest_token(access_token, csrf_token)
        self.assertNotEqual(res, None)


    def test_get_tokens(self):
        tokens = tweet_fetcher.get_tokens()
        self.assertTrue(
            tokens["access_token"] is not None and tokens["csrf_token"] is not None and tokens["guest_token"] is not None
        )


    def test_fetch_tweet(self):
        html = tweet_fetcher.fetch_twitter_home_page()
        main_js_url = tweet_fetcher.get_main_js_url(html)
        main_js = tweet_fetcher.fetch_main_js(main_js_url)

        access_token = tweet_fetcher.get_access_token(main_js)
        csrf_token = tweet_fetcher.generate_csrf_token()

        guest_token = tweet_fetcher.fetch_guest_token(access_token, csrf_token)

        result = tweet_fetcher.fetch_tweet("1238007172786577408", access_token=access_token, csrf_token=csrf_token, guest_token=guest_token)

        self.assertNotEqual(result, None)
    

    def test_fetch_tweet_with_cursor(self):
        tweet_id = "1238007172786577408"
        cursor = "TBwcFoDAotWMz6SuIhUCAAAYJmNvbnZlcnNhdGlvblRocmVhZC0xMjM4MDA3MzM4NzYzNTcxMjAwAAA="
        tokens = tweet_fetcher.get_tokens()

        result = tweet_fetcher.fetch_tweet(tweet_id, access_token=tokens["access_token"], csrf_token=tokens["csrf_token"], guest_token=tokens["guest_token"], cursor=cursor)
        self.assertNotEqual(result, None)


if __name__ == '__main__':
    unittest.main()