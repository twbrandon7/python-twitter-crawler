from tweet_crawler import tweet_fetcher

class Tweet:
    """The object that represent a tweet and it's responses
    """

    def __init__(self, tweet_id, access_token, csrf_token, guest_token):
        """
            Args:
                tweet_id: the id of the target tweet
        """
        self.tweet_id = tweet_id
        self.source = tweet_fetcher.fetch_tweet(tweet_id, access_token, csrf_token, guest_token)

        self.tweets = self.source["globalObjects"]["tweets"]
        self.instructions = self.source["timeline"]["instructions"]
        self.entries = self.instructions[0]["addEntries"]["entries"]
        self.parsed_data = []


    def get_tweets(self, max_response=-1, timeline_length=-1):
        """getting tweet including it's timeline (the responses of a response)
        

        Args:
            max_timeline: the maximum response of the main tweet to get. set -1 to download all responses.
            timeline_length: the maximun response in a timeline. -1 to get the whole timeline.

        Returns: a dictionary. for example:
            {
                "tweet": "the main tweet",
                "timeline": [
                    ["response 1", "response 1-1", "response 1-2", ...... ],
                    ["response 2", "response 2-1", "response 2-2", ...... ],
                    ......
                ]
            }
        """
        for entry in self.entries:
            content = entry["content"]
            if "item" in content:
                self.__get_tweet_text(content["item"]["content"])
            elif "timelineModule" in content:
                self.process_timeline_module(content)
            elif "operation" in content:
                self.process_operation(content)
            else:
                print("Not defined")


    def process_timeline_module(self, content):
        items = content["timelineModule"]["items"]
        for item in items:
            content = item["item"]["content"]
            if "tweet" in content:
                self.__get_tweet_text(content)
            elif "timelineCursor" in content:
                timelineCursor = content["timelineCursor"]
                print("[MORE COMMENT] " + timelineCursor["value"])


    def process_operation(self, content):
        cursor = content["operation"]["cursor"]
        value = cursor["value"]
        print("[MORE TWEET] " + value)


    def __get_tweet_text(self, content):
        """getting the text of the tweet
        
        Args:
            content: the "content" object from the response of tweeter

        Returns: the text of the tweet (string)
        """
        tweet_id = content["tweet"]["id"]
        tweet = self.tweets[tweet_id]
        print(tweet["full_text"])
        return tweet["full_text"]

