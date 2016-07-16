# BTweet
# Copyright 2016 Pablo Marcos
# See LICENSE for details.

from tweepy import Stream

import os.path, sys

#Adding parent dir to import btweet library
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

from btweet.basicListener import BasicListener
from btweet.utils import load_auth

track_list = ["hola"]

auth, api = load_auth("KEYS.json")
listener = BasicListener(api, delay=1)

if __name__ == '__main__':

	try:
		print("HEY")
		stream = Stream(auth, listener)
		stream.filter(track = track_list)

	except KeyboardInterrupt:
		stream.disconnect()
		exit()
