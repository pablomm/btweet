from __future__ import absolute_import, print_function
from tweepy import API, OAuthHandler, Stream
from tweetbot.giveawayBot import GiveawayBot


#Auth Keys 
consumer_key= ""
consumer_secret= ""
access_token= ""
access_token_secret= ""

#Bot lists
track_list = ["retweet to win","sorteo RT","concurso RT"]
ignore_list = ["plz","ayuda","gracias","please","favor","signup","thanks","justin","bieber","5sos","vma","minecraft","vote","vota","twitch"]
follow_list = ["#follow","follow","sigue","sigueme","seguir","following","siguiendo","seguidores","seguidor","rt+follow"]
fav_list = ["fav","rt+fav","fave","favorito","favorite"]

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

