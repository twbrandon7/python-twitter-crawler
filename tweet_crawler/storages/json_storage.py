import os
import json

from tweet_crawler.storages.framework import Storage

class JsonStorage(Storage):
    """Save tweets as json file
    """

    def __init__(self, folder):
        """
        Args:
            folder: the folder to save tweets
        """
        self.folder = folder
    
    def _ensure_folder(self, folder):
        if not os.path.exists(folder):
            os.makedirs(folder)
        return folder

    def save_tweet(self, parsed_tweet):
        """save parsed tweet object


        Args:
            parsed_tweet: see `tweet_crawler.tweet_parser.Tweet.get_tweets`
        
        Returns:
            None
        """
        self._ensure_folder(self.folder)
        json_str = json.dumps(parsed_tweet)

        output_path = os.path.join(self.folder, "{}.json".format(parsed_tweet["tweet_id"]))

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_str)
    
    def append_timeline(self, tweet_id, timeline):
        """append parsed timeline


        Args:
            tweet_id: the id of the tweet to append
            timeline: see `tweet_crawler.tweet_parser.Tweet.get_tweets`
        
        Returns:
            None
        """

        output_path = os.path.join(self.folder, "{}.json".format(tweet_id))
        with open(output_path, "r", encoding="utf-8") as f:
            json_str = f.read()
        
        obj = json.loads(json_str)
        obj["timelines"] += timeline

        with open(output_path, "w", encoding="utf-8") as f:
            json_str = json.dumps(obj)
            f.write(json_str)

