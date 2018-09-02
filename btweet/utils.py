# BTweet
# Copyright 2016 Pablo Marcos
# See LICENSE for details.

from __future__ import absolute_import, print_function

try:
	#Python 3.x import
	from queue import Queue

except ImportError:
	#Python 2.x import
	from Queue import Queue

from threading import Thread
from time import sleep
from sys import exit
import os

import json

from tweepy import API, OAuthHandler
from tweepy.cursor import Cursor
from tweepy.error import TweepError
from tweepy.models import Status
from tweepy.streaming import StreamListener


def restore_options(options_file):

	default_options = {
		'username' : {'value' : None, 'type' : 'str', 'description': ''},
		'at': {'value' : False, 'type' : 'bool', 'description': ''},
		'original': {'value' : False, 'bool' : 'str', 'description': ''},
		'quoted': {'value' : False, 'type' : 'str', 'description': ''},
		'favs' : {'value' : 3, 'type' : 'int', 'description': ''},
		'retweets' : {'value' : 3, 'type' : 'int', 'description': ''},
		"queue_size" : {'value' : 20, 'type' : 'int', 'description': ''},
		"list_size" : {'value' : 250, 'type' : 'int', 'description': ''},
		"locked" : {'value' : True, 'type' : 'bool', 'description': ''},
		"retweet_time" : {'value' : 10, 'type' : 'int', 'description': ''},
		"fav_time" : {'value' : 10, 'type' : 'int', 'description': ''},
		"follow_time" : {'value' : 10, 'type' : 'int', 'description': ''},
		"error_time" : {'value' : 10, 'type' : 'int', 'description': ''},
		"empty_time" : {'value' : 10, 'type' : 'int', 'description': ''},
		"interaction_time" : {'value' : 0, 'type' : 'int', 'description': ''},
		"load_timeline" : {'value' : True, 'type' : 'bool', 'description': ''},
		"autostart" : {'value' : True, 'type' : 'bool', 'description': ''},
	}

	with open(options_file, 'w+') as f:
		json.dump(default_options, f)

	return default_options

def load_options(options_file):

	if not os.path.exists(options_file):
		return restore_options(options_file)

	with open(options_file) as f:
		options = json.load(f)

	return options

def load_auth(path_file):

	with open(path_file) as data_file:
		data = json.load(data_file)

	auth = OAuthHandler(data["consumer_key"], data["consumer_secret"])
	auth.set_access_token(data["access_token"], data["access_token_secret"])

	return auth, API(auth)

class Verbose(object):

	def __init__(self, verbose_level=1):
		self.verbose_level = verbose_level

	def lprint(self, level=1, line=""):
		if self.verbose_level >= level:
			print(line)

	def vprint(self, line):
		self.lprint(1, line)

	def vvprint(self, line):
		self.lprint(2, line)

class Interaction(object):
	def __init__(self, status, retweet=False, favorite=False, follow=False):
		self.status = status
		self.retweet = retweet
		self.favorite = favorite
		self.follow = follow

class OrganizedList(object):
	def __init__(self, maximun=0):
		self.list = list()
		self.maximun = maximun

	def __str__(self):
		return str(self.list)

	def add(self, element):
		self.list.insert(0, element)
		if len(self.list) > self.maximun and self.maximun:
			self.list.pop()
		return

	def check(self,element, add=True):
		if not element in self.list:
			if add:
				self.add(element)
			return False

		i = self.list.index(element)
		if i:
			self.list[i-1], self.list[i] = self.list[i], self.list[i-1]
		return True

class QueuedListener(StreamListener, Verbose):

	def __init__(self, api=None, **options):

		StreamListener.__init__(self,api)
		Verbose.__init__(self, options.get("verbose_level", 1))

		self.queue = Queue(maxsize = options.get("queue_size", 20))
		self.tweet_list = OrganizedList(options.get("list_size", 250))
		self.queue_thread = Thread(target=self._listen)
		self.queue_thread.daemon = True
		self.running = False

		self.locked = options.get("locked", True)
		self.retweet_time = options.get("retweet_time", 10)
		self.fav_time = options.get("fav_time", 10)
		self.follow_time = options.get("follow_time", 10)
		self.error_time = options.get("error_time", 10)
		self.empty_time = options.get("empty_time", 10)
		self.interaction_time = options.get("interaction_time", 0)

		if options.get("load_timeline",True):
			self._load_timeline()
		if options.get("autostart", True):
			self.start()

	def start(self):
		self.vprint(">> Starting queue thread")
		self.running = True
		self.queue_thread.start()

	def stop(self):
		self.vprint(">> Stopping queue thread")
		self.running = False
		self.queue_thread.join()

	def restart(self):
		if not self.queue_thread.isAlive():
			self.running = True
			self.queue_thread = Thread(target=self._listen)
			self.queue_thread.daemon = True

	def add_interaction(self, status, retweet=False, favorite=False, follow=False):
		if not self.tweet_list.check(status.id_str, False):
			self.queue.put(Interaction(status, retweet, favorite, follow))

	def _load_timeline(self):
		size = self.tweet_list.maximun if self.tweet_list.maximun else 20

		for page in Cursor(self.api.user_timeline, count=size, include_rts=True).pages(2):
			for status in page:
				try:
					status = status.retweeted_status
				except AttributeError as atr:
					pass
				self.tweet_list.check(status.id_str)

	def _retweet(self,interaction):
		if interaction.retweet:
			try:
				interaction.status.retweet()
				self.vprint(">> New retweet")
				sleep(self.retweet_time)
			except TweepError as e:
				raise TweepError(">> Retweet error: %s" % e.reason)
		return

	def _favorite(self,interaction):
		if interaction.favorite:
			try:
				interaction.status.favorite()
				self.vprint(">> New favorite")
				sleep(self.fav_time)
			except TweepError as e:
				raise TweepError(">> Favorite error: %s" % e.reason)
		return

	def _follow(self, interaction):
		if interaction.follow:
			try:
				interaction.status.user.follow()
				self.vprint(">> Follow to @%s: %s" % (interaction.status.user.screen_name, interaction.status.user.name))
				sleep(self.follow_time)
			except TweepError as e:
				raise TweepError(">> Follow error: %s" % e)
		return

	def _listen(self):

		while self.running:
			if not self.locked and self.queue.empty:
				sleep(self.empty_time)

			self._interact(self.queue.get())

		exit()

	def _interact(self, interaction):
		if self.tweet_list.check(interaction.status.id_str):
			self.vvprint(">> Status already parsed: %s" % interaction.status.text)
			return

		sleep(self.interaction_time)

		self.vprint(">> Proccessing @%s: %s" % (interaction.status.user.screen_name, interaction.status.id_str))
		self.vvprint(">> Text: %s" % interaction.status.text)

		try:
			self._retweet(interaction)
			self._favorite(interaction)
			self._follow(interaction)

		except TweepError as e:
			self.vvprint(e)
			sleep(self.error_time)
