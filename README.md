# twitter-corpus-crawler-python
python based twitter crawler to gethering corpuses

# Usage
```python
# search
from tccp import search

# fetch 10 recent results of searching
for tweet in search("North korea", 10):
    # properties
    print(tweet["author"])
    print(tweet["contents"])
    print(tweet["tweet_id"])
    print(tweet["has_parent_tweet"])
    print(tweet["num_replies"])
    print(tweet["num_retweet"])
    print(tweet["num_relike"])
    print(tweet["mentions"])

# fetch infinitly
for tweet in search("North korea"): 
    print(tweet)
    break

# search only conversations
from tccp import search_conversation

# fetch 10 recent conversation with keyword
for conversation in search_conversation("North korea", 10):
    print("conversation length: " + len(conversation))
    # conversation is list of tweetssss
    # each tweet has same properties as result of searching
    print("the first tweet of conversations: " + conversation[0])

for conversation in search_conversation("North korea"):
    print(conversation)
    break
from tccp import search

for tweet in search("North korea", 10):
    print tweet
```
