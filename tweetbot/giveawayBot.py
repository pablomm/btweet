from __future__ import absolute_import, print_function

import time
from tweepy import StreamListener
from tweepy.models import Status
from tweepy.utils import import_simplejson


class GiveawayBot(StreamListener):

	def __init__(self, api=None, follow_list=[], fav_list=[], ignore_list=[], **options):

		StreamListener.__init__(self,api)
		self.json = import_simplejson()
		self.follow_list = follow_list
		self.fav_list = fav_list
		self.ignore_list = ignore_list

		self.verbose_level = options.get("verbose_level", 1)
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

		status = Status.parse(self.api, self.json.loads(data))
		try:
			status = status.retweeted_status
		except AttributeError, atr:
			if not self.original:
				self._vvprint(">> Original tweet ignored: %s" % status.text)
				return True

		if status.is_quote_status:
			if self.quoted:
				status = status.quoted_status
			else:
				self._vvprint(">> Quoted tweet ignored: %s" % status.text)
				return True

		if status.text.startswith('@') and not self.at:
			self._vvprint(">> At tweet ignored: %s" % status.text)
			return True

		print("RT %s FAV %s FOL %s" % (status.retweeted, status.favorited, status.user.following))
		if status.retweeted or status.favorited:
			self._vvprint(">> Tweet previously parsed: %s" % status.text)
			return True

		text = status.text.lower()
		"""
		print(self.ignore_list)
		for ignore_word in self.ignore_list:
			print(ignore_word)
			if ignore_word in text:
				self._vvprint(">> Tweet ignored for \"%s\": %s" % (ignore_word, status.text))
	        	return True
		"""
		time = 0

		if self.retweets > status.retweet_count:
			self._vvprint(">> Not enought retweets: %d/%d" % (status.retweet_count, self.retweets))
		else:
			try:
				status.retweet()
				time += self.retweet_time
				self._vprint(">> New retweet @%s: %s" % (status.user.screen_name, status.text))
			except Exception, e:
				time += self.error_time
				self._vvprint(">> Retweet error: %s" % e)
				return True


		if self.favs > status.favorite_count:
			self._vvprint(">> Not enought favorites to check: %d/%d" % (status.favorite_count, self.favs))
		else:
			for fav_word in self.fav_list:
				if fav_word in text:
					try:
						status.favorite()
						time += self.fav_time
						self._vprint(">> New favorite @%s: %s" % (status.user.screen_name, status.text))
						break
					except Exception, e:
						time += self.error_time
						self._vvprint(">> Favorite error: %s" % e)
						return True

		for follow_word in self.follow_list:
			if follow_word in text:
				if not status.user.following:
					status.user.follow()	
					time += self.follow_time			
				self._vprint(">> Follow to @%s: %s" % (status.user.screen_name, status.user.name))
				break

		if time:
			sleep(time)

		return True

	def on_error(self, status):
		self._vprint(status)

	def _vprint(self, line):
		if self.verbose_level > 0:
			print(line)

	def _vvprint(self, line):
		if self.verbose_level > 1:
			print(line)

