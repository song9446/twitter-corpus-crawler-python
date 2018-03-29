import sys
import requests
import json
import re
import os.path

REQ_PARAMS = {
    #"l": "ko", # en / ko / ...
    #"src": "sprv", # sprv / typd
    # whatever query
    "q": "e OR t OR n OR o OR a OR i OR r OR s OR h OR l OR d OR c OR f OR u OR m OR y OR g OR p OR b OR v OR w OR k OR q OR j OR x OR z OR 0 OR 1 OR 2 OR 3 OR 4 OR 5 OR 6 OR 7 OR 8 OR 9 since:1994-08-01 until:2020-12-31",
    "src": "typd", # sprv / typd
    "f": "tweets",
    "vertical": "default",
    "reset_error_state": "false",
    "include_entities": "1",
    "include_available_features": "1",
}
REQ_TIMEOUT = 10
SEARCH_ADDRESS = "https://twitter.com/i/search/timeline"
TWEET_ADDRESS = "https://twitter.com/%s/status/%s" # % (user-id, conversation-id)
REQ_HEADERS = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36",
    "upgrade-insecure-requests": "1",
    "cache-control": "max-age=0",
    "accept-language": "ko,en-US;q=0.8,en;q=0.6",
    "accept-encoding": "gzip, deflate, sdch, br",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }

#MAX_POSITION_TAIL = "BD1UO2FFu9QAAAAAAAAETAAAAAcAAAASAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

def search_whatever_conversation(params, num=-1):
    params

def search_conversation(params, num=-1, continue_path=None):
    searching= search(params, continue_path=continue_path) 
    while num != 0:
        tweet = next(searching)
        if (tweet["num_replies"] == 0 and not tweet["has_parent_tweet"]): continue
        conversations = fatch_conversation(tweet["author"], tweet["tweet_id"])
        for conversation in conversations:
            if len(conversation) < 2: continue
            yield conversation
            num -= 1

def search(_params, num=-1, continue_path=None):
    params = REQ_PARAMS.copy()
    for i in _params:
        params[i] = _params[i]
    max_position = None
    max_tweet = None
    min_tweet = None
    first_time = True
    f = None
    initial_num = num
    if continue_path is not None:
        try:
            with open(continue_path, "r") as f:
                max_position = f.read()
        except:
            pass
        f = open(continue_path, "w")
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
                if first_time: 
                    max_tweet = tweet_id
                    first_time = False
                min_tweet = tweet_id
                if f is not None:
                    max_position = "TWEET-%s-%s" % (min_tweet, max_tweet)# + "-" + MAX_POSITION_TAIL
                    f.seek(0)
                    f.truncate()
                    f.write(max_position)
                yield {"author": author, "tweet_id": tweet_id, "permalink-path": permalink_path, "num_replies": int(num_replies), "has_parent_tweet": bool(has_parent_tweet), "contents": contents, "mentions": mentions, "num_retweet": num_retweet, "num_like": num_like, }
                num -= 1
                if num == 0: break
            max_position = "TWEET-%s-%s" % (min_tweet, max_tweet)# + "-" + MAX_POSITION_TAIL
            max_tweet = min_tweet
        except Exception as e:
            print(e)
    if f: f.close()

def fatch_conversation(author, _tweet_id):
    while True:
        try:
            res = requests.get(TWEET_ADDRESS % (author, _tweet_id), headers=REQ_HEADERS, timeout=REQ_TIMEOUT)
            break
        except Exception as e:
            print(e)
    html = res.text
    tweets = []
    conversation = []
    default_conversation = []
    after = False
    last = False
    last_author = False
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
        if contents is None: contents = ""
        contents = distruct_html(contents)
        num_replies, p = raw_parse(html, "data-tweet-stat-count=\"", "\"", p)
        num_retweet, p = raw_parse(html, "data-tweet-stat-count=\"", "\"", p)
        num_like, p = raw_parse(html, "data-tweet-stat-count=\"", "\"", p)
        tweet = {"author": author, "tweet_id": tweet_id, "permalink-path": permalink_path, "num_replies": int(num_replies), "has_parent_tweet": bool(has_parent_tweet), "contents": contents, "mentions": mentions, "num_retweet": num_retweet, "num_like": num_like, }
        if not last and last_author == author and mentions == author:
            if conversation is not None and len(conversation) > 0:
                tweet["contents"] = conversation.pop()["contents"]
            elif len(default_conversation) > 0:
                tweet["contents"] = default_conversation.pop()["contents"]
        if not after and _tweet_id != tweet_id:
            default_conversation.append(tweet)
        elif not after: 
            default_conversation.append(tweet)
            conversation = default_conversation[:]
            after = True
        else:
            conversation.append(tweet)
            if last:
                last = False
                tweets.append(conversation)
                conversation = default_conversation[:]
            conv, p = raw_parse(tweet_html, "\"ThreadedConversation-", "\"", p)
            if conv is None: break
            if conv in ("tweet last", "-loneTweet"):
                last = True
    if len(tweets) == 0:
        tweets.append(default_conversation)
    return tweets

def raw_parse(text, start, end, offset=0):
    s = text.find(start, offset)
    if s == -1: return None, 0
    s += len(start)
    e = text.find(end, s)
    if e == -1: return None, 0
    return text[s:e], e
    
DISTURCT_HTML_RULE = [
    (r'<a\s+href="([^"]+)"[^>]*>.*</a>' , r''), # remove all links
    #(r'<a\s+href="([^"]+)"[^>]*>.*</a>' , r' \1'), # show links instead of texts
    (r' +', ' '), # replace consecutive whitespace
    (r'[\n]+', '\n'), # multiple newline to single newline
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
    #for tweet in search({"q": keyword}, num):
    #    print(tweet)
    for conversation in search_conversation({"q": keyword}, num, "tmp"):
        for tweet in conversation:
            print(tweet["author"] + ": " + tweet["contents"])
        print("\n")
