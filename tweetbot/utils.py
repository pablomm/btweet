# Tweetbot
# Copyright 2016 Pablo Marcos
# See LICENSE for details.

from __future__ import absolute_import, print_function

from Queue import Queue
from threading import Thread
from time import sleep

from tweepy.models import Status
from tweepy.streaming import StreamListener

class Verbose:

	def __init__(self, verbose_level=1):
		self.verbose_level = verbose_level

	def lprint(self, level=1, line=""):
		if self.verbose_level >= level:
			print(line)

	def vprint(self, line):
		self.lprint(1, line)

	def vvprint(self, line):
		self.lprint(2, line)

class Interaction:
	def __init__(self, status, retweet=False, favorite=False, follow=False):
		self.status = status
		self.retweet = retweet
		self.favorite = favorite
		self.follow = follow

class OrganizedList:
	def __init__(self, maximun=0):
		self.list = list()
		self.maximun = maximun

	def __str__(self):
		return str(self.list)

	def check(self,element):
		if not element in self.list:
			self.list.insert(0, element)
			if len(self.list) > self.maximun and self.maximun:
				self.list.pop()
			return False

		i = self.list.index(element)
		if i:
			self.list[i-1], self.list[i] = self.list[i], self.list[i-1]
		return True

class QueuedListener(StreamListener, Verbose):

	def __init__(self, api=None, **options):
		
		StreamListener.__init__(self,api)
		Verbose.__init__(self, options.get("verbose_level", 1))

		self.queue = Queue(maxsize = options.get("queue_size", 100) )
		self.queue_thread = Thread(target=self._listen)
		self.tweet_list = OrganizedList(options.get("list_size", 50))

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
		self.queue_thread.start()

	def stop(self):
		self.vprint(">> Stopping queue thread")
		self.queue_thread.join()

	def add_interaction(self,interaction):
		self.queue.put(interaction)

	def _load_timeline(self):
		pass

	def _retweet(self,interaction):
		if interaction.retweet:
			try:
				interaction.status.retweet()
				self.vprint(">> New retweet @%s: %s" % (interaction.status.user.screen_name, interaction.status.text))
				sleep(self.retweet_time)
			except TweepError, e:
				raise TweepError(">> Retweet error: %s" % e.reason)
		return

	def _favorite(self,interaction):
		if interaction.favorite:
			try:
				interaction.status.favorite()
				self.vprint(">> New favorite @%s: %s" % (interaction.status.user.screen_name, interaction.status.text))
				sleep(self.fav_time)
			except TweepError, e:
				raise TweepError(">> Favorite error: %s" % e.reason)
		return

	def _follow(self, interaction):
		if interaction.follow:
			try:
				status.user.follow()	
				self.vprint(">> Follow to @%s: %s" % (interaction.status.user.screen_name, interaction.status.user.name))
				sleep(self.follow_time)
			except TweepError, e:
				raise TweepError(">> Follow error: %s" % e)
		return

	def _listen(self):
		
		while True:

			interaction = self.queue.get()

			if self.tweet_list.check(interaction.status.id_str):
				self.vvprint(">> Status already parsed: %s" % interaction.status.text)
				continue

			sleep(self.interaction_time)
			try:
				self._retweet(interaction)
				self._favorite(interaction)
				self._follow(interaction)

			except Exception, e:
				self.vvprint(e)
				sleep(self.error_time)


