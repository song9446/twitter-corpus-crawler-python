import sys
import requests
import json
import re

REQ_PARAMS = {
    #"l": "ko", # en / ko / ...
    "src": "sprv", # sprv / typd
    "f": "tweets",
    "vertical": "default",
    "reset_error_state": "false",
    "include_entities": "1",
    "include_available_features": "1",
}
REQ_TIMEOUT = 2
SEARCH_ADDRESS = "https://twitter.com/i/search/timeline"
TWEET_ADDRESS = "https://twitter.com/%s/status/%s" # user-id / conversation-id
REQ_HEADERS = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36",
    "upgrade-insecure-requests": "1",
    "cache-control": "max-age=0",
    "accept-language": "ko,en-US;q=0.8,en;q=0.6",
    "accept-encoding": "gzip, deflate, sdch, br",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

#MAX_POSITION_TAIL = "BD1UO2FFu9QAAAAAAAAETAAAAAcAAAASAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

def search_conversation(query, num=-1):
    searching= search(query) 
    while num != 0:
        tweet = next(searching)
        if (tweet["num_replies"] == 0 and not tweet["has_parent_tweet"]): continue
        conversation = fatch_conversation(tweet["author"], tweet["tweet_id"])
        if len(conversation) < 2: continue
        yield conversation
        num -= 1

def search(query, num=-1):
    params = REQ_PARAMS.copy()
    params["q"] = query
    max_position = None
    max_tweet = None
    min_tweet = None
    first_time = True
    while num != 0:
        try:
            if max_position is not None: params["max_position"] = max_position
            res = requests.get(SEARCH_ADDRESS, params=params, headers=REQ_HEADERS, timeout=REQ_TIMEOUT)
            result = json.loads(res.text)
            if result["new_latent_count"] == 0: break
            # has_more_items = result["has_more_items"]
            # <- It looks like does not mean that realy there're no more items
            html = result["items_html"]
            p = 0
            for _ in range(result["new_latent_count"]):
                tweet_html, _ = raw_parse(html, "class=\"tweet ", ">", p)
                has_parent_tweet, _ = raw_parse(tweet_html, "data-has-parent-tweet=\"", "\"")
                mentions, _ = raw_parse(tweet_html, "data-mentions=\"", "\"")
                tweet_id, p = raw_parse(html, "data-tweet-id=\"", "\"", p)
                permalink_path, p = raw_parse(html, "data-permalink-path=\"", "\"", p)
                author, p = raw_parse(html, "data-screen-name=\"", "\"", p)
                contents, p = raw_parse(html, "js-tweet-text-container\">" , "</div>", p)
                contents = distruct_html(contents)
                num_replies, p = raw_parse(html, "data-tweet-stat-count=\"", "\"", p)
                num_retweet, p = raw_parse(html, "data-tweet-stat-count=\"", "\"", p)
                num_like, p = raw_parse(html, "data-tweet-stat-count=\"", "\"", p)
                yield {"author": author, "tweet_id": tweet_id, "permalink-path": permalink_path, "num_replies": int(num_replies), "has_parent_tweet": bool(has_parent_tweet), "contents": contents, "mentions": mentions, "num_retweet": num_retweet, "num_like": num_like, }
                num -= 1
                if num == 0: break
                if first_time: 
                    max_tweet = tweet_id
                    first_time = False
                min_tweet = tweet_id
            max_position = "TWEET-%s-%s" % (min_tweet, max_tweet)# + "-" + MAX_POSITION_TAIL
            max_tweet = min_tweet
        except Exception as e:
            print(e)

def fatch_conversation(author, tweet_id):
    while True:
        try:
            res = requests.get(TWEET_ADDRESS % (author, tweet_id), headers=REQ_HEADERS, timeout=REQ_TIMEOUT)
            break
        except Exception as e:
            print(e)
    html = res.text
    tweets = []
    p = 0
    while True:
        tweet_html, _ = raw_parse(html, "class=\"tweet ", ">", p)
        if tweet_html is None: break
        mentions, _ = raw_parse(tweet_html, "data-mentions=\"", "\"")
        has_parent_tweet, _ = raw_parse(tweet_html, "data-has-parent-tweet=\"", "\"")
        tweet_id, p = raw_parse(html, "data-tweet-id=\"", "\"", p)
        permalink_path, p = raw_parse(html, "data-permalink-path=\"", "\"", p)
        author, p = raw_parse(html, "data-screen-name=\"", "\"", p)
        contents, p = raw_parse(html, "js-tweet-text-container\">", '</div>', p)
        contents = distruct_html(contents)
        tweets.append({"author": author, "tweet_id": tweet_id, "permalink_path": permalink_path, "mentions": mentions, "has-parent-tweet": bool(has_parent_tweet), "contents": contents})
    return tweets

def raw_parse(text, start, end, offset=0):
    s = text.find(start, offset)
    if s == -1: return None, 0
    s += len(start)
    e = text.find(end, s)
    if e == -1: return None, 0
    return text[s:e], e
    
DISTURCT_HTML_RULE = [
    (r'<a\s+href="([^"]+)"[^>]*>.*</a>' , r' \1'), # show links instead of texts
    (r'\s+', ' '), # replace consecutive whitespace
    (r'\s*<br\s*/?>\s*', '\n'), # newline after a <br>
    (r'[ \t]*<[^<]*?/?>', ''), # remove remaining tags
    (r'&nbsp;', ' '), 
    (r'&amp;', '&'), 
    (r'&quot;', '"'),
    (r'&lt;', '<'), 
    (r'&gt;', '>'),
    (r'&#39;', "'"),
]

def distruct_html(html):
    for (r, s) in DISTURCT_HTML_RULE:
        html = re.sub(r, s, html)
    return html.strip()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("usage: %s KEYWORD NUM_FATCH"%(sys.argv[0]))
        exit(2)
    keyword = sys.argv[1]
    num = int(sys.argv[2])
    for tweet in search(keyword, num):
        print(tweet)
    #for conversation in search_conversation(keyword, num):
    #    print(conversation)
