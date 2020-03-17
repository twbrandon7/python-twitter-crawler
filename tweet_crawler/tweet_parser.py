from tweet_crawler import tweet_fetcher

class Tweet:
    """The object that represent a tweet and it's responses
    """

    def __init__(self, tweet_id, access_token, csrf_token, guest_token, cursor=None):
        """
            Args:
                tweet_id: the id of the target tweet
                access_token: the access token to pass the oauth
                csrf_token: the csrf_token hidden in twitter page or cookie
                guest_token: the guest_token is calculate by twitter server. see `tweet_fetcher.fetch_guest_token()`.
        """
        self.tweet_id = tweet_id
        self.access_token = access_token
        self.csrf_token = csrf_token
        self.guest_token = guest_token
        self.cursor = cursor
        self.__next_cursor = None

        self.entries = None

        self.__is_first = True


    def __prepare(self):
        self.source = tweet_fetcher.fetch_tweet(self.tweet_id, self.access_token, self.csrf_token, self.guest_token, cursor=self.cursor)

        self.tweets = self.source["globalObjects"]["tweets"]
        self.instructions = self.source["timeline"]["instructions"]

        instruction = None
        for instruction in self.instructions:
            if "addEntries" in instruction:
                break
        
        if instruction is not None:
            self.entries = self.instructions[0]["addEntries"]["entries"]

        self.output = {}
        self.__init_output()

    
    def __init_output(self):
        self.output = {
            "tweet": "",
            "tweet_id": self.tweet_id,
            "timelines": []
        }


    def get_next_cursor(self):
        return self.__next_cursor


    def get_main_tweet(self, timeline_length=-1):
        """get the tweet and it's first timelines
        

        Args:
            timeline_length: the maximun length of a timeline. -1 to get the whole timeline.

        Returns: a dictionary. for example:
            {
                "tweet": "the main tweet",
                "tweet_id": "the_tweet_id",
                "timelines": [
                    ["response 1", "response 1-1", "response 1-2", ...... ],
                    ["response 2", "response 2-1", "response 2-2", ...... ],
                    ......
                ]
            }
        """

        if self.__is_first:
            self.__prepare()
            self.__is_first = False

        self.__init_output()
        if self.entries is not None:
            self.__parse_entries(entries=self.entries, timeline_length=timeline_length)

        return self.output


    def get_next_timelines(self, timeline_length=-1):
        """get the tweet and it's first timelines
        

        Args:
            timeline_length: the maximun length of a timeline. -1 to get the whole timeline.

        Returns: a list of timelines. for example:
            [
                ["response 1", "response 1-1", "response 1-2", ...... ],
                ["response 2", "response 2-1", "response 2-2", ...... ],
                ......
            ]

            Return None if `self.__next_cursor` is None.
        """
        
        if self.__next_cursor is None:
            return None
        else:
            new_tweets = Tweet(self.tweet_id, self.access_token, self.csrf_token, self.guest_token, cursor=self.__next_cursor)
            out = new_tweets.get_main_tweet(timeline_length=timeline_length)
            self.__next_cursor = new_tweets.get_next_cursor()
            return out["timelines"]


    def __parse_entries(self, entries, timeline_length=-1):
        """parse entries from the json object of twitter

        Args:
            entries: a json object which contains all responses
            timeline_length: the maximum length of a timeline
        """
        responses_count = 0
        for entry in entries:
            content = entry["content"]
            if "item" in content:
                self.output["tweet"] = self.__get_tweet_text(content["item"]["content"])
            elif "timelineModule" in content:
                self.process_timeline_module(content, timeline_length=timeline_length)
                responses_count += 1
            elif "operation" in content:
                self.process_operation(content)
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


    def process_operation(self, content):
        """getting more timeline

        Args:
            content: the json object which contains the cursor of next batch of timelines
        
        Returns: None
        """
        cursor = content["operation"]["cursor"]
        value = cursor["value"]
        self.__next_cursor = value


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


class TwitterSearch:
    def __init__(self, keyword, access_token, csrf_token, guest_token):
        """
            Args:
                keyword: the keyword to search
                access_token: the access token to pass the oauth
                csrf_token: the csrf_token hidden in twitter page or cookie
                guest_token: the guest_token is calculate by twitter server. see `tweet_fetcher.fetch_guest_token()`.
        """
        self.keyword = keyword
        self.access_token = access_token
        self.csrf_token = csrf_token
        self.guest_token = guest_token

        self.next_cursor = None
        self.previous_cursor = None
        
    
    def get_next_ids(self):
        """get the next batch of tweet ids
        
        Args: None

        Returns: a list of tweet id
        """
        entries = self.__fetch_data(cursor=self.next_cursor)
        tweet_ids = self.__parse_data(entries)
        return tweet_ids


    def __fetch_data(self, cursor=None):
        """fetch the search result

        Args:
            cursor: the cursor of the search result
        """
        source = tweet_fetcher.fetch_search_result(self.keyword, self.access_token, self.csrf_token, self.guest_token, cursor=cursor)
        instructions = source["timeline"]["instructions"]
        entries = instructions[0]["addEntries"]["entries"]
        return entries
        

    def __parse_data(self, entries):
        """find the tweet ids in the search result

        Args:
            entries: a json object from the result of `__fetch_data`

        Returns: a list of tweet id
        """
        ids = []
        for entry in entries:
            content = entry["content"]
            if "item" in content:
                ids.append(content["item"]["content"]["tweet"]["id"])
            elif "operation" in content:
                val = content["operation"]["cursor"]["value"]
                if "scroll" in val:
                    self.next_cursor = val
                elif "refresh" in val:
                    self.previous_cursor = val
        return ids
