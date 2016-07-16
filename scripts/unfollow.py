"""
Code from svenmalvik/tweepy

"""

import tweepy
import time
import os


timeout = 1
max_friends_to_destroy = 3000

auth, api = load_auth("KEYS.json")

friends = []
followers = []

def my_friends():
	for page in tweepy.Cursor(api.friends_ids).pages():
		friends.extend(page)

def my_followers():
	for page in tweepy.Cursor(api.followers_ids).pages():
		followers.extend(page)

my_friends()
my_followers()
unfollow_friends = list(set(friends) - set(followers))

def unfollow():
  i = 0
  for userid in unfollow_friends:
	api.destroy_friendship(id=userid)
    print("iUnfollow user: " + str(userid))
    i = i + 1
    if i == int(max_friends_to_destroy):
      break
    time.sleep(int(timeout))

unfollow()
