import abc
 
class Storage(abc.ABC):
 
    @abc.abstractmethod
    def save_tweet(self, parsed_tweet):
        """save parsed tweet object


        Args:
            parsed_tweet: see `tweet_crawler.tweet_parser.Tweet.get_tweets`
        
        Returns:
            None
        """
        return NotImplemented
 
    @abc.abstractmethod
    def append_timeline(self, tweet_id, timeline):
        """append parsed timeline


        Args:
            tweet_id: the id of the tweet to append
            timeline: see `tweet_crawler.tweet_parser.Tweet.get_tweets`
        
        Returns:
            None
        """
        return NotImplemented