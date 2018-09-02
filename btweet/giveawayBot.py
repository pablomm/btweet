# BTweet
# Copyright 2016 Pablo Marcos
# See LICENSE for details.

from __future__ import absolute_import

from tweepy.error import TweepError
from tweepy.models import Status
from tweepy.utils import import_simplejson

from btweet.utils import Interaction, QueuedListener


class GiveawayBot(QueuedListener):

	def __init__(self, api=None, **options):

		QueuedListener.__init__(self,api, **options)
		self.json = import_simplejson()
		self.follow_list = options.get("follow_list", [])
		self.fav_list = options.get("fav_list", [])
		self.ignore_list = options.get("ignore_list", [])
		self.block_users = options.get("block_users", [])

		self.at = options.get("at", False)
		self.original = options.get("original", False)
		self.quoted = options.get("quoted", False)
		self.favs = options.get("favs", 3)
		self.retweets = options.get("retweets", 3)


	def on_data(self, data):

		try:
			status = self._get_status(data)
			lower_text = self._filter(status)

		except TweepError as e:
			self.vvprint(e)
			return True
		except Exception as e:
			self.vvprint(">> Unexpected error: %s" % e)
			return True

		if self._checkretweet(status):
			self.add_interaction(status, True, self._checkfavorite(status,lower_text), self._checkfollow(status,lower_text))

		return True

	def on_error(self, status):
		self.vprint(status)

	def _get_status(self, data):

		status = Status.parse(self.api, self.json.loads(data))

		if status.user.screen_name in self.block_users:
			raise TweepError(">> User ignored: @%s" % status.user.screen_name)
		try:
			status = status.retweeted_status
		except AttributeError as atr:
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

	def _checkretweet(self, status):
		return not self.retweets > status.retweet_count

	def _checkfavorite(self, status, text):
		return self._checklist(self.fav_list, text) and self.favs <= status.favorite_count

	def _checkfollow(self, status, text):
		return not status.user.following and self._checklist(self.follow_list, text)


	def _filter(self,status):
		if status.text.startswith('@') and not self.at:
			raise TweepError(">> At(@) tweet ignored: %s" % status.text)

		if status.retweeted or status.favorited:
			raise TweepError(">> Tweet previously parsed: %s" % status.text)

		text = status.text.lower()

		if self._checklist(self.ignore_list,text):
			raise TweepError(">> Tweet ignored: %s" % status.text)

		if status.user.screen_name in self.block_users:
			raise TweepError(">> User ignored: @%s" % status.user.screen_name)
		return text
