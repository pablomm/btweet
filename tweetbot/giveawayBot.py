from __future__ import absolute_import

import time
from tweepy import StreamListener
from tweepy.error import TweepError
from tweepy.models import Status
from tweepy.utils import import_simplejson

from tweetbot.utils import Verbose


class GiveawayBot(StreamListener, Verbose):

	def __init__(self, api=None, follow_list=[], fav_list=[], ignore_list=[], **options):

		StreamListener.__init__(self,api)
		Verbose.__init__(self, options.get("verbose_level", 1))

		self.json = import_simplejson()
		self.follow_list = follow_list
		self.fav_list = fav_list
		self.ignore_list = ignore_list

		self.at = options.get("at", False)
		self.original = options.get("original", False)
		self.quoted = options.get("quoted", False)
		self.favs = options.get("favs", 3)
		self.retweets = options.get("retweets", 3) 
		self.retweet_time = options.get("retweet_time", 0)
		self.fav_time = options.get("fav_time", 0)
		self.follow_time = options.get("follow_time", 0)
		self.error_time = options.get("error_time", 0)
		self.interaction_time = options.get("interaction_time", 0)


	def on_data(self, data):

		try:
			status = self._get_status(data)
			text = self._filter(status)

		except Exception, e:
			self.vvprint(e)
			return True

		time = 0

		if self.retweets > status.retweet_count:
			self.vvprint(">> Not enought retweets: %d/%d" % (status.retweet_count, self.retweets))
		else:
			try:
				status.retweet()
				time += self.retweet_time
				self.vprint(">> New retweet @%s: %s" % (status.user.screen_name, status.text))
			except Exception, e:
				time += self.error_time
				self.vvprint(">> Retweet error: %s" % e)
				return True


		if self.favs > status.favorite_count:
			self.vvprint(">> Not enought favorites to check: %d/%d" % (status.favorite_count, self.favs))
		else:
			for fav_word in self.fav_list:
				if fav_word in text:
					try:
						status.favorite()
						time += self.fav_time
						self.vprint(">> New favorite @%s: %s" % (status.user.screen_name, status.text))
						break
					except Exception, e:
						time += self.error_time
						self.vvprint(">> Favorite error: %s" % e)
						return True

		for follow_word in self.follow_list:
			if follow_word in text:
				if not status.user.following:
					status.user.follow()	
					time += self.follow_time			
				self.vprint(">> Follow to @%s: %s" % (status.user.screen_name, status.user.name))
				break

		if time:
			sleep(time)

		return True

	def _get_status(self, data):

		status = Status.parse(self.api, self.json.loads(data))
		try:
			status = status.retweeted_status
		except AttributeError, atr:
			if not self.original:
				raise TweepError(">> Original tweet ignored: %s" % status.text)

		if status.is_quote_status:
			if self.quoted:
				status = status.quoted_status
			else:
				raise TweepError(">> Quoted tweet ignored: %s" % status.text)

		return status

	def _checklist(self, word_list, text):
		return any(word in text for word in word_list)

	def _filter(self,status):
		if status.text.startswith('@') and not self.at:
			raise TweepError(">> At(@) tweet ignored: %s" % status.text)
			
		if status.retweeted or status.favorited:
			raise TweepError(">> Tweet previously parsed: %s" % status.text)

		text = status.text.lower()

		if self._checklist(self.ignore_list,text):
			raise TweepError(">> Tweet ignored: %s" % status.text)

		return text


	def on_error(self, status):
		self.vprint(status)

	

