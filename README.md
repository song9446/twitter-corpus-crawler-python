# twitter-corpus-crawler-python
deadly simple python based twitter crawler to gethering corpuses
```python
from tccp import search
for tweet in search("microsoft", 3): 
    print(tweet["contents"])
# => (fetch contents of three recent tweets)
# New Deal:Microsoft Office Professional Plus 2016Price:\u20ac9.95 Delivery:24h Just 24h left! https://t.co/UdmXlHWvcQ
# Microsoft Office 365 \u2013 https://t.co/CJFadmm3yT
# Visit the Snapzu "tribe" of the hour: /hashtag/Microsoft?src=hash - Feel free to submit related blog posts or media!
```
# usage
```python
# search
from tccp import search

# fetch 10 recent results of searching
for tweet in search("trump", 10):
    # properties
    print(tweet["author"])
    print(tweet["contents"])
    print(tweet["tweet_id"])
    print(tweet["has_parent_tweet"])
    print(tweet["num_replies"])
    print(tweet["num_retweet"])
    print(tweet["num_like"])
    print(tweet["mentions"])

# fetch infinitly
for tweet in search("attack"): 
    print(tweet)
    break

# search only conversations
from tccp import search_conversation

# fetch 10 recent conversation with keyword
for conversation in search_conversation("North korea", 10):
    print("conversation length: " + len(conversation))
    # conversation is list of tweets
    # each tweet has same properties as result of searching
    print("the first tweet of conversations: " + conversation[0])

for conversation in search_conversation("please"):
    print(conversation)
    break
```
