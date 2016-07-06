# BTweet
# Copyright 2016 Pablo Marcos
# See LICENSE for details.

from __future__ import absolute_import, print_function

from tweepy import API, OAuthHandler, Stream

from btweet.giveawayBot import GiveawayBot


#Auth Keys 
consumer_key= ""
consumer_secret= ""
access_token= ""
access_token_secret= ""

#Bot lists
track_list = []
ignore_list = []
follow_list = []
fav_list = []

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = API(auth)

listener = GiveawayBot(api, follow_list, fav_list, ignore_list, verbose_level=2)

if __name__ == '__main__':

	while True:
		try:
			stream = Stream(auth, listener)
			stream.filter(track = track_list)

		except KeyboardInterrupt, k:
			if("y" in raw_input("Are you sure?")):
				listener.stop()
				exit()

		except UnicodeEncodeError:
			print(">> Unicode exception")

		except Exception, e:
			print(">> Exception %s" % e)
			listener.restart()
			sleep(10)

