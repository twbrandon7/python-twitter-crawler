from tweet_crawler import tweet_fetcher

class Tweet:
    """The object that represent a tweet and it's responses
    """

    def __init__(self, tweet_id, access_token, csrf_token, guest_token, cursor=None):
        """
            Args:
                tweet_id: the id of the target tweet
        """
        self.tweet_id = tweet_id
        self.access_token = access_token
        self.csrf_token = csrf_token
        self.guest_token = guest_token

        self.source = tweet_fetcher.fetch_tweet(tweet_id, access_token, csrf_token, guest_token, cursor=cursor)

        self.tweets = self.source["globalObjects"]["tweets"]
        self.instructions = self.source["timeline"]["instructions"]
        self.entries = self.instructions[0]["addEntries"]["entries"]
        self.output = {}
        self.__init_output()

    
    def __init_output(self):
        self.output = {
            "tweet": "",
            "timelines": []
        }


    def get_tweets(self, max_timelines=-1, timeline_length=-1):
        """getting tweet including it's timeline (the responses of a response)
        

        Args:
            max_timelines: the maximum responses (timelines) of the main tweet to get. set -1 to download all responses.
            timeline_length: the maximun length of a timeline. -1 to get the whole timeline.

        Returns: a dictionary. for example:
            {
                "tweet": "the main tweet",
                "timelines": [
                    ["response 1", "response 1-1", "response 1-2", ...... ],
                    ["response 2", "response 2-1", "response 2-2", ...... ],
                    ......
                ]
            }
        """

        self.__init_output()
        self.__parse_entries(entries=self.entries, max_timelines=max_timelines, timeline_length=timeline_length)

        if max_timelines != -1:
            self.output["timelines"] = self.output["timelines"][:max_timelines]

        return self.output


    def __parse_entries(self, entries, max_timelines=-1, timeline_length=-1):
        """parse entries from the json object of twitter

        Args:
            entries: a json object which contains all responses
            max_timelines: the maximum responses to get
            timeline_length: the maximum length of a timeline
        """
        responses_count = 0
        for entry in entries:
            if max_timelines == 0:
                break
            content = entry["content"]
            if "item" in content:
                self.output["tweet"] = self.__get_tweet_text(content["item"]["content"])
            elif "timelineModule" in content:
                self.process_timeline_module(content, timeline_length=timeline_length)
                responses_count += 1
            elif "operation" in content:
                if max_timelines != -1:
                    _max_timelines = max_timelines - responses_count
                    if _max_timelines < 0:
                        _max_timelines = 0
                else:
                    _max_timelines = -1
                self.process_operation(content, max_timelines=_max_timelines, timeline_length=timeline_length)
            else:
                print("Not defined")


    def process_timeline_module(self, content, timeline_length=-1):
        """extract timeline from the json object of twitter


        Args:
            content: json object which contains several "items"
            timeline_length: the maximum length of a timeline

        Returns: None
        """
        items = content["timelineModule"]["items"]
        final_timeline = []
        
        timeline, next_cursor = self.__parse_timeline_items(items)
        final_timeline += timeline

        while next_cursor is not None:
            timeline, next_cursor = self.__fetch_data_with_cursor(cursor=next_cursor)
            final_timeline += timeline

            if timeline_length != -1 and len(final_timeline) > timeline_length:
                break
        
        if timeline_length != -1:
            final_timeline = final_timeline[:timeline_length]

        self.output["timelines"].append(final_timeline)


    def __fetch_data_with_cursor(self, cursor):
        """fetch more tweet with cursor

        Args:
            cursor: the cursor of the timeline
        
        Returns: see `__parse_timeline_items()`
        """
        obj = tweet_fetcher.fetch_tweet(self.tweet_id, self.access_token, self.csrf_token, self.guest_token, cursor=cursor)
        self.tweets.update(obj["globalObjects"]["tweets"])

        instructions = obj["timeline"]["instructions"]
        items = instructions[0]["addToModule"]["moduleItems"]
        return self.__parse_timeline_items(items)


    def __parse_timeline_items(self, items):
        """extract timeline text from items


        Args:
            items: the items object from twitter

        Returns:
            timeline: the array of multiple timeline text
            next_cursor: the curosr use to fetch more text. return None if no cursor.
        """
        
        timeline = []
        next_cursor = None

        for item in items:
            content = item["item"]["content"]
            if "tweet" in content:
                timeline.append(self.__get_tweet_text(content))
            elif "timelineCursor" in content:
                timelineCursor = content["timelineCursor"]
                next_cursor = timelineCursor["value"]
        
        return timeline, next_cursor


    def process_operation(self, content, max_timelines=-1, timeline_length=-1):
        """getting more timeline

        Args:
            content: the json object which contains the cursor of next batch of timelines
            max_timelines: see `__parse_entries()`
            timeline_length: see `__parse_entries()`
        
        Returns: None
        """
        cursor = content["operation"]["cursor"]
        value = cursor["value"]
        new_tweets = Tweet(self.tweet_id, self.access_token, self.csrf_token, self.guest_token, cursor=value)
        out = new_tweets.get_tweets(max_timelines=max_timelines, timeline_length=timeline_length)
        self.output["timelines"] += out["timelines"]


    def __get_tweet_text(self, content):
        """getting the text of the tweet
        
        Args:
            content: the "content" object from the response of twitter

        Returns: the text of the tweet (string)
        """
        tweet_id = content["tweet"]["id"]
        if tweet_id in self.tweets:
            tweet = self.tweets[tweet_id]
            return tweet["full_text"]
        else:
            return "[ERROR]"

