import requests
import json
import random
import re
from bs4 import BeautifulSoup
from urllib.parse import quote


def fetch_twitter_home_page():
    """get the twitter home page

    Args: None
    Returns: 
        html in string. if the response code is not 200, return None.
    """
    headers = {
        'authority': 'twitter.com',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'sec-fetch-dest': 'document',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,ja;q=0.5',
    }

    params = (
        ('lang', 'zh-tw'),
    )

    response = requests.get('https://twitter.com/', headers=headers, params=params)

    if response.status_code == 200:
        return response.text
    else:
        return None


def get_main_js_url(html):
    """get the main.*.js from twitter


    Args:
        html: the html from twitter home page
    
    Returns: the full url of main.*.js
    """
    soup = BeautifulSoup(html, 'html.parser')
    tags = soup.find_all('link', {"as": "script"})
    
    pattern = re.compile("main\..+\.js")
    href = None

    for tag in tags:
        href = tag["href"]
        if pattern.match(href):
            break

    return href


def fetch_main_js(url):
    """get the main.*.js content


    Args:
        url: the url of the main.*.js
    
    Returns: the content of the main.*.js. return None if the response code of the url is not 200.
    """
    headers = {
        'Referer': 'https://twitter.com/?lang=zh-tw',
        'Origin': 'https://twitter.com',
        'Sec-Fetch-Dest': 'script',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        return None


def get_access_token(main_js):
    """extract access token from main.*.js


    Args:
        main_js: the javascript code in the main.*.js

    Returns: the access token. return None if not found
    """
    pattern = re.compile(",s=\"(AAAA.+?)\",c=")
    result = pattern.search(main_js)
    if len(result.groups()) == 1:
        return result.group(1)
    else:
        return None


def generate_csrf_token():
    """generate the csrf token

    The original JavaScript code is:
    ```javascript
    ci = (n('jfn0'), function () {
        var e = window.crypto || window.msCrypto;
        if (e) {
            var t = new Uint8Array(32);
            e.getRandomValues(t);
            for (var n = '', r = 0; r < t.length; r++) n += t[r].toString(16).substr( - 1);
            return n
        }
    }),
    ```
    """
    seed = [format(random.randint(0, 255))[-1] for _ in range(32)]
    return "".join(seed)


def fetch_guest_token(access_token, csrf_token):
    """request guest token by access_token and csrf_token


    Args:
        access_token: the access token to pass the oauth
        csrf_token: the csrf_token hidden in twitter page or cookie
    
    Returns: the guest token. return None if error occured.
    """
    headers = {
        'authority': 'api.twitter.com',
        'content-length': '0',
        'x-twitter-client-language': 'zh-tw',
        'x-csrf-token': csrf_token,
        'authorization': 'Bearer {}'.format(access_token),
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'sec-fetch-dest': 'empty',
        'x-twitter-active-user': 'yes',
        'accept': '*/*',
        'origin': 'https://twitter.com',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'referer': 'https://twitter.com/CKYwww/status/1238007172786577408',
        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,ja;q=0.5',
    }

    response = requests.post('https://api.twitter.com/1.1/guest/activate.json', headers=headers)

    if response.status_code == 200:
        obj = None
        try:
            obj = json.loads(response.text)
        except Exception:
            pass

        if obj is not None and "guest_token" in obj:
            return obj["guest_token"]
        else:
            return None
    else:
        return None


def get_tokens():
    """get `access_token`, `csrf_token` and `guest_token`
    
    
    Args: None

    Returns: a dictionary. for example:
        {
            "access_token": "AAAAA......",
            "csrf_token": "123......",
            "guest_token": "123......"
        }
    """
    html = fetch_twitter_home_page()
    main_js_url = get_main_js_url(html)
    main_js = fetch_main_js(main_js_url)

    access_token = get_access_token(main_js)
    csrf_token = generate_csrf_token()
    guest_token = fetch_guest_token(access_token, csrf_token)

    return {
        "access_token": access_token,
        "csrf_token": csrf_token,
        "guest_token": guest_token
    }


def fetch_tweet(tweet_id, access_token, csrf_token, guest_token, cursor=None):
    """Fetch tweets by id


    Args:
        tweet_id: the target tweet id
        access_token: the access token to pass the oauth
        csrf_token: the csrf_token hidden in twitter page or cookie
        cursor: getting more response tweet start from this cursor

    Returns: 
        the json object return from twitter server (which is parsed as a python dictionary).
        if the request is faild, return None.

    """

    headers = {
        'authority': 'api.twitter.com',
        'x-twitter-client-language': 'zh-tw',
        'x-csrf-token': csrf_token,
        'authorization': 'Bearer {}'.format(access_token),
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'sec-fetch-dest': 'empty',
        'x-guest-token': guest_token,
        'x-twitter-active-user': 'yes',
        'accept': '*/*',
        'origin': 'https://twitter.com',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'referer': 'https://twitter.com/AnandWrites/status/1238618579882389504',
        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        # 'cookie': 'personalization_id="v1_lSl0sw+l4lgXZY8rmiBYqQ=="; guest_id=v1%3A158416861107452973; ct0={}; _ga=GA1.2.224857067.1584168612; _gid=GA1.2.1486957857.1584168612; _twitter_sess=BAh7CSIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCFSyztdwAToMY3NyZl9p%250AZCIlNTZiODBjMzUxZjYwZjVmODFlMzA0YmFmMGY4ODBmZWU6B2lkIiVlNjUy%250AMGJlZmFjOGE5Yjg1ODE3MDNjNjBlNmZlNjQwOQ%253D%253D--c97a40633e0e0d441a1e2e70feb74a755da28237; external_referer=padhuUp37zjgzgv1mFWxJ12Ozwit7owX||8e8t2xd8A2w%3D; tfw_exp=1; gt=1238768435112194048'.format(csrf_token),
    }

    params = [
        ('include_profile_interstitial_type', '1'),
        ('include_blocking', '1'),
        ('include_blocked_by', '1'),
        ('include_followed_by', '1'),
        ('include_want_retweets', '1'),
        ('include_mute_edge', '1'),
        ('include_can_dm', '1'),
        ('include_can_media_tag', '1'),
        ('skip_status', '1'),
        ('cards_platform', 'Web-12'),
        ('include_cards', '1'),
        ('include_composer_source', 'true'),
        ('include_ext_alt_text', 'true'),
        ('include_reply_count', '1'),
        ('tweet_mode', 'extended'),
        ('include_entities', 'true'),
        ('include_user_entities', 'true'),
        ('include_ext_media_color', 'true'),
        ('include_ext_media_availability', 'true'),
        ('send_error_codes', 'true'),
        ('simple_quoted_tweets', 'true'),
        ('ext', 'mediaStats,highlightedLabel,cameraMoment'),
    ]

    if cursor is not None:
        params.append(('cursor', cursor))

    response = requests.get('https://api.twitter.com/2/timeline/conversation/{}.json'.format(tweet_id), headers=headers, params=params)

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None


def fetch_search_result(keyword, access_token, csrf_token, guest_token, cursor=None):
    """Fetch search results by keyword


    Args:
        keyword: the keyword to search
        access_token: the access token to pass the oauth
        csrf_token: the csrf_token hidden in twitter page or cookie
        cursor: getting more response tweet start from this cursor

    Returns: 
        the json object return from twitter server (which is parsed as a python dictionary).
        if the request is faild, return None.

    """
    headers = {
        'authority': 'api.twitter.com',
        'x-twitter-client-language': 'zh-tw',
        'x-csrf-token': csrf_token,
        'authorization': 'Bearer {}'.format(access_token),
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'sec-fetch-dest': 'empty',
        'x-guest-token': guest_token,
        'x-twitter-active-user': 'yes',
        'accept': '*/*',
        'origin': 'https://twitter.com',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'referer': 'https://twitter.com/search?q={}&src=typed_query'.format(quote(keyword)),
        'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,ja;q=0.5',
    }

    params = [
        ('include_profile_interstitial_type', '1'),
        ('include_blocking', '1'),
        ('include_blocked_by', '1'),
        ('include_followed_by', '1'),
        ('include_want_retweets', '1'),
        ('include_mute_edge', '1'),
        ('include_can_dm', '1'),
        ('include_can_media_tag', '1'),
        ('skip_status', '1'),
        ('cards_platform', 'Web-12'),
        ('include_cards', '1'),
        ('include_composer_source', 'true'),
        ('include_ext_alt_text', 'true'),
        ('include_reply_count', '1'),
        ('tweet_mode', 'extended'),
        ('include_entities', 'true'),
        ('include_user_entities', 'true'),
        ('include_ext_media_color', 'true'),
        ('include_ext_media_availability', 'true'),
        ('send_error_codes', 'true'),
        ('simple_quoted_tweets', 'true'),
        ('q', keyword),
        ('count', '20'),
        ('query_source', 'typed_query'),
        ('pc', '1'),
        ('spelling_corrections', '1'),
        ('ext', 'mediaStats,highlightedLabel,cameraMoment'),
    ]

    if params is not None:
        params.append(('cursor', cursor))

    response = requests.get('https://api.twitter.com/2/search/adaptive.json', headers=headers, params=params)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None
