from __future__ import absolute_import, print_function
from tweepy import API, OAuthHandler, Stream
from tweetbot.giveawayBot import GiveawayBot


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

auth = OAuthHandler(consumer_key, consumer_secret) #autentificacion para streaming
auth.set_access_token(access_token, access_token_secret)
api = API(auth)


if __name__ == '__main__':

	while True:
		try:
			stream = Stream(auth, GiveawayBot(api, follow_list, fav_list, ignore_list, verbose_level=2))
			stream.filter(track = track_list)

		except KeyboardInterrupt, k:
			if("y" in raw_input("Are you sure?")):
				exit()

