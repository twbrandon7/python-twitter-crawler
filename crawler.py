import time
import threading
import signal
import sys

from tweet_crawler import logger
from tweet_crawler import tweet_fetcher
from tweet_crawler.tweet_parser import TwitterSearch
from tweet_crawler.tweet_parser import Tweet
from tweet_crawler.storages.json_storage import JsonStorage

class CrawlerManager:
    
    def __init__(self, keyword, storage, max_result=-1, max_thread=3, sleep_duration=0.5, max_timelines=-1, timeline_length=-1, token_refresh_duration=300):
        self.keyword = keyword
        self.storage = storage
        self.max_result = max_result
        self.max_thread = max_thread
        self.sleep_duration = sleep_duration
        self.max_timelines = max_timelines
        self.timeline_length = timeline_length
        self.token_refresh_duration = token_refresh_duration

        self.tokens = None
        self.last_token_refresh = None
        self.search = None

        self.run = True

        self.fetched_ids = 0
        self.id_buffer = []
        self.__running_threads = {}
        self.__thread_fetch_ids = None
        self.__thread_thread_manager = None


    def refresh_token(self, force=False):
        if force or self.last_token_refresh is None or time.time() - self.last_token_refresh >= self.token_refresh_duration:
            logger.info("Start refresh tokens")
            self.tokens = tweet_fetcher.get_tokens()
            logger.info("Tokens refreshed")
            self.last_token_refresh = time.time()


    def start(self):
        self.refresh_token()
        self.search = TwitterSearch(self.keyword, self.tokens["access_token"], self.tokens["csrf_token"], self.tokens["guest_token"])

        self.__fetch_ids()
        self.__thread_fetch_ids = threading.Thread(target=self.__search_ids, args=())
        self.__thread_fetch_ids.start()

        self.__thread_thread_manager = threading.Thread(target=self.__thread_manager, args=())
        self.__thread_thread_manager.start()


    def stop(self):
        logger.info("Stopping...")
        self.run = False
        self.__thread_fetch_ids.join()
        self.__thread_thread_manager.join()

        for th in self.__running_threads:
            th.join()


    def __thread_manager(self):
        while self.run:
            if len(self.__running_threads) < self.max_thread and len(self.id_buffer) > 0:
                tweet_id = self.id_buffer.pop(0)
                thd = threading.Thread(target=self.__download_twitter, args=(tweet_id,))
                self.__running_threads[tweet_id] = thd
                self.__running_threads[tweet_id].start()
            
            print("Running threads: {}, Buffer ids: {}".format(len(self.__running_threads), len(self.id_buffer)), end="\r")

            if self.max_result != -1 and self.fetched_ids >= self.max_result and len(self.__running_threads) == 0:
                logger.info("All tasks have been completed.")
                break


    def __search_ids(self):
        while self.run:
            if self.max_result != -1 and self.fetched_ids >= self.max_result:
                logger.info("Reached max_result. Stop searching.")
                break

            self.__fetch_ids()

            time.sleep(self.sleep_duration)
        

    def __fetch_ids(self):
        self.refresh_token()
        if len(self.id_buffer) <= self.max_thread:
            ids = self.search.get_next_ids()
            
            if self.max_result != -1 and len(ids) + self.fetched_ids > self.max_result:
                ids = ids[:(self.max_result - self.fetched_ids)]
            
            self.id_buffer += ids
            self.fetched_ids += len(ids)
            logger.info("Fetch {} search results.".format(len(ids)))


    def __download_twitter(self, tweet_id):
        logger.info("Start download tweet {}.".format(tweet_id))
        tweet = Tweet(
            tweet_id=tweet_id,
            access_token=self.tokens["access_token"],
            csrf_token=self.tokens["csrf_token"],
            guest_token=self.tokens["guest_token"])

        main_tweet = tweet.get_main_tweet(self.timeline_length)
        self.storage.save_tweet(main_tweet)
        timeline_ctn = len(main_tweet["timelines"])

        while self.run:
            if (tweet.get_next_cursor() is None) or (self.max_timelines != -1 and timeline_ctn >= self.max_timelines):
                break

            timelines = tweet.get_next_timelines()
            if self.max_timelines != -1 and timeline_ctn + len(timelines) > self.max_timelines:
                timelines = timelines[:(self.max_timelines - timeline_ctn)]
            
            timeline_ctn += len(timelines)
            self.storage.append_timeline(tweet_id, timelines)

            time.sleep(self.sleep_duration)
        
        logger.info("Tweet {} finished.".format(tweet_id))
        del self.__running_threads[tweet_id]
            

if __name__ == '__main__':
    keyword = "spacex"
    output_folder = "./data"

    mgr = CrawlerManager(
        keyword="台灣",
        storage=JsonStorage(output_folder),
        max_result=10,
        max_thread=3,
        sleep_duration=2,
        max_timelines=-1,
        timeline_length=-1,
        token_refresh_duration=300
    )
    mgr.start()
    
    def signal_handler(signal, frame):
        logger.debug("HOLD HOLD HOLD")
        mgr.stop()

    signal.signal(signal.SIGINT, signal_handler)
    while mgr.run:
        pass
