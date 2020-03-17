# Simple Twitter crawler written in Python

## Installation

1. Download the project

```bash
git clone https://github.com/twbrandon7/python-twitter-crawler.git
cd python-twitter-crawler
```

2. Install virtualenv

```bash
pip3 install virtualenv
virtualenv .env
```

3. Activate virtual environment

```bash
source ./.env/bin/activate # for linux
.\.env\Script\activate.ps1 # for windows powershell
```

4. Install dependencies

```bash
pip3 install -r requirements.txt
```

## Usage

It is fine to use the crawler in command line. The explanation of the command is as following:

```bash
$ python crawler.py -h
usage: crawler.py [-h] [-f FOLDER] [-mr MAX_RESULT] [-thd MAX_THREAD]
                  [-sd SLEEP_DURATION] [-mt MAX_TIMELINES]
                  [-tl TIMELINE_LENGTH] [-trd TOKEN_REFRESH_DURATION]
                  keyword

positional arguments:
  keyword               The keyword to search

optional arguments:
  -h, --help            show this help message and exit
  -f FOLDER, --folder FOLDER
                        The folder to save the tweets. The default folder is
                        './data'
  -mr MAX_RESULT, --max_result MAX_RESULT
                        The maximum amount of tweets to download. Default is
                        10. Set -1 for unlimiting.
  -thd MAX_THREAD, --max_thread MAX_THREAD
                        The maximum amount of threads to run. Default is 1.
  -sd SLEEP_DURATION, --sleep_duration SLEEP_DURATION
                        The time between each request for each thread.
  -mt MAX_TIMELINES, --max_timelines MAX_TIMELINES
                        The maximum amount of timelines (responses) to
                        download for each tweet. Set -1 for unlimiting.
                        Default is -1.
  -tl TIMELINE_LENGTH, --timeline_length TIMELINE_LENGTH
                        The maximum length of a timeline to download. Set -1
                        for unlimiting. Default is -1.
  -trd TOKEN_REFRESH_DURATION, --token_refresh_duration TOKEN_REFRESH_DURATION
                        The time duration in seconds to refresh the access
                        tokens. Default is 300 seconds.
```

### Examples

```bash
python crawler.py "spacex" -mr 5 -mt 5
python crawler.py "spacex" -mr 5 -mt 5 -th 3
```

## Development

It is welcome to contribute to this project by creating a [pull request](https://github.com/twbrandon7/python-twitter-crawler/pulls). There are several things that need for accomplishment.

### TODO

- [ ] Add time information to the downloaded tweet.
- [ ] Add more storage class. (See `tweet_crawler.storages`.)

### Unit test

```bash
python -m unittest tests.unit.test_tweet_fetcher
python -m unittest tests.unit.test_Tweet_object
python -m unittest tests.unit.test_TwitterSearch_object
python -m unittest tests.unit.storages.test_json_storage
```
