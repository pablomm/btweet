
from __future__ import print_function


class Verbose:
	def __init__(self, verbose_level=0):
		self.verbose_level = verbose_level

	def lprint(self, level, line):
		if self.verbose_level >= level:
			print(line)

	def vprint(self, line):
		self.lprint(1, line)

	def vvprint(self, line):
		self.lprint(2, line)


class QueuedInteraction:

	def __init__(self, api=None, **options):
		pass
