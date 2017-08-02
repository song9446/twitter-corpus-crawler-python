# twitter-corpus-crawler-python
deadly simple python based twitter crawler to gethering corpuses
1. fetch some number of the result tweets of keword searching in twitter
```python
from tccp import search
for tweet in search({"q":"microsoft"}, 3): 
    print(tweet["contents"])
# => New Deal:Microsoft Office Professional Plus 2016Price:\u20ac9.95 Delivery:24h Just 24h left! https://t.co/UdmXlHWvcQ
# => Microsoft Office 365 \u2013 https://t.co/CJFadmm3yT
# => Visit the Snapzu "tribe" of the hour: /hashtag/Microsoft?src=hash - Feel free to submit related blog posts or media!
```
2. *fetch some number of the result conversations of keword searching in twitter*
```python
from tccp import search_conversation
for conversation in search_conversation({"q":"sexy", "l": "en"}, 1): 
    for tweet in conversation:
        print(tweet["author"] + ": " + tweet["contents"])
# => lyndeyhighan: i hate to brag but this is my boyfriend
# => condorsix: This the sexiest dude I know on god
# => vasquezlaziah21: Umm......con?
# => condorsix: Bro peep that man. You can't tell ur homie he a sexy dude are u really his homie?
```
3. *continue searching from the last searched tweet(even if terminated by exception when last searching)*
```python
from tccp import search
for tweet in search({"q":"microsoft"}, 1, continue_path="last_searching.tmp"): 
    print(tweet["contents"])
# => New Deal:Microsoft Office Professional Plus 2016Price:\u20ac9.95 Delivery:24h Just 24h left! https://t.co/UdmXlHWvcQ

for tweet in search({"q":"microsoft"}, 1, continue_path="last_searching.tmp"): 
    print(tweet["contents"])
# => Microsoft Office 365 \u2013 https://t.co/CJFadmm3yT
```

# usage
```python
# search
from tccp import search

# fetch 10 recent results of searching
for tweet in search({"q": "trump"}, 10):
    # properties
    print(tweet["author"])
    print(tweet["contents"])
    print(tweet["tweet_id"])
    print(tweet["has_parent_tweet"])
    print(tweet["num_replies"])
    print(tweet["num_retweet"])
    print(tweet["num_like"])
    print(tweet["mentions"])

# fetch tweets infinitly
for tweet in search({"q": "attack"}): 
    print(tweet)
    break

# search only conversations
from tccp import search_conversation

# fetch 10 recent conversation with keyword
for conversations in search_conversation({"q": "North korea"}, 10):
    print("conversation length: " + len(conversation))
    # conversation is list of tweets
    # each tweet has same properties as result of searching
    print("the first tweet of conversations: " + conversation[0])

# fetch conversations infinitly
for conversation in search_conversation({"q": "please"}):
    print(conversation)
    break

# fetch conversations continuesly
for conversation in search_conversation({"q": "please"}, continue_path="path_for_last_searching_file.tmp"):
    # load the last searching state at the path
    # it keeps saving last searching state to the path.
    print(conversation)
    break

for conversation in search_conversation({"q": "please"}, continue_path="path_for_last_searching_file.tmp"):
    print(conversation)
```
