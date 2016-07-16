# BTweet
# Copyright 2016 Pablo Marcos
# See LICENSE for details.

from __future__ import absolute_import, print_function

from time import sleep

from tweepy import Stream

import os.path, sys

#Adding parent dir to import btweet library
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from btweet.giveawayBot import GiveawayBot
from btweet.utils import load_auth

# Fix Python 2.x.
try: 
	input = raw_input
except NameError: 
	pass

track_list = ["retweet to win","sorteo RT","concurso RT"]
ignore_list = ["plz","ayuda","gracias","please","favor","signup","thanks","justin","bieber","5sos","vma","minecraft","vote","vota","twitch"]
follow_list = ["#follow","follow","sigue","sigueme","seguir","following","siguiendo","seguidores","seguidor","rt+follow"]
fav_list = ["fav","rt+fav","fave","favorito","favorite","like","mg"]
user_list = ["ElisaNyan01","jazzmaniatico"]

auth, api = load_auth("KEYS.json")
listener = GiveawayBot(api, follow_list, fav_list, ignore_list, user_list, verbose_level=1)

if __name__ == '__main__':

	while True:
		try:
			stream = Stream(auth, listener)
			stream.filter(track = track_list)

		except KeyboardInterrupt:
			if("y" in raw_input("Are you sure?")):
				listener.stop()
				stream.disconnect()
				exit()

		except UnicodeEncodeError:
			print(">> Unicode exception")

		except Exception as e:
			print(">> Exception %s" % e)
			listener.restart()
			sleep(10)

