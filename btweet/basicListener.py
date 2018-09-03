from __future__ import absolute_import, print_function

from time import sleep

from tweepy.models import Status
from tweepy.streaming import StreamListener
from tweepy.utils import import_simplejson


class BasicListener(StreamListener):

    def __init__(self, api=None, **options):
        StreamListener.__init__(self, api)
        self.json = import_simplejson()
        self.print_data = options.get("print_data", False)
        self.print_data = options.get("created_at", False)
        self.print_data = options.get("user", False)
        self.print_data = options.get("id", False)
        self.print_data = options.get("favorite_count", False)
        self.print_data = options.get("retweet_count", False)
        self.print_data = options.get("text", False)
        self.print_data = options.get("source_url", False)
        self.print_data = options.get("print_data", False)
        self.print_data = options.get("print_data", False)
        self.delay = int(options.get("delay", 0))

    def on_data(self, data):

        if self.print_data:
            print(data)

        self. _print_status(Status.parse(self.api, self.json.loads(data)))
        sleep(self.delay)

    def _print_status(self, status):
        print(dir(status))
