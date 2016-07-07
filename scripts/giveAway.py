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

track_list = []
ignore_list = []
follow_list = []
fav_list = []
user_list = []

auth, api = load_auth("KEYS.json")
listener = GiveawayBot(api, follow_list, fav_list, ignore_list, user_list, verbose_level=1)

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

