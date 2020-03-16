# Simple Tweeter crawler written in Python

## Installation

1. Download the project

```bash
git clone https://github.com/twbrandon7/python-tweeter-crawler.git
cd python-tweeter-crawler
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

## Development

### Unit test

```bash
python -m unittest tests.unit.test_Tweet_object.test_tweet_fetcher
python -m unittest tests.unit.test_Tweet_object.TestTweetObject
```