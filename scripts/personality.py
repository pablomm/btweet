#!/usr/bin/env python2

from __future__ import print_function

import operator
import sys
import twitter
from watson_developer_cloud import PersonalityInsightsV2 as PersonalityInsights

"""
Analizes the personality insights of two twitter users using the last
200 tweets of their publics twitter accounts.
Utilizes the IBM Bluemix Personality Insights API to analize the text
and the twitter API to get the statuses.

To get twitter credentials go to  https://apps.twitter.com and create a "New App"
Create a IBM bluemix account and an instance of the Personality Insights service
to get the PI credentials
"""

#Twitter API credentials
twitter_consumer_key = ''
twitter_consumer_secret = ''
twitter_access_token = ''
twitter_access_secret = ''

#IBM Bluemix credentials for Personality Insights
pi_username = ''
pi_password = ''

#Creates an instance of the twitter api
twitter_api = twitter.Api(consumer_key=twitter_consumer_key, consumer_secret=twitter_consumer_secret, 
	access_token_key=twitter_access_token, access_token_secret=twitter_access_secret)

#Instance of Personality Insights API
personality_insights = PersonalityInsights(username=pi_username, password=pi_password)

def analyze(handle): 
	"""
	Analizes the personality insights of a twitter account
	handle: Screen name of the account
	tweet_count number of tweets to process

	It have been an instance of the twitter api an the personality
	insights API. Only analyizes english tweets
	"""
	max_id = None
	text = ""
	tweet_count = 0
	for _ in range(16):

		#First case wihout max_id
		if not max_id:
			statuses = twitter_api.GetUserTimeline(screen_name=handle, count=200, include_rts=False)
		#Rest if cases with max_id
		else:
			statuses = twitter_api.GetUserTimeline(screen_name=handle, count=200, max_id=max_id,include_rts=False)
		#Update max_id
		max_id = statuses[len(statuses) - 1].id - 1
		#Writing english statuses in text variable
		for status in statuses:
			if (status.lang =='en'): #English tweets
				text += status.text.encode('utf-8') + " "
				tweet_count += 1

	#Process the personality insights
	pi_result = personality_insights.profile(text)
	
	return pi_result, tweet_count

def flatten(orig):
	"""
	Flattens the personality insigths results
	orig: personality insights
	"""
	data = {}
	for c in orig['tree']['children']:
		if 'children' in c:
			for c2 in c['children']:
				if 'children' in c2:
					for c3 in c2['children']:
						if 'children' in c3:
							for c4 in c3['children']:
								if (c4['category'] == 'personality'):
									data[c4['id']] = c4['percentage']
									if 'children' not in c3:
										if (c3['category'] == 'personality'):
												data[c3['id']] = c3['percentage']
	return data

def compare(dict1, dict2):
	"""
	Compares the distance betweet two dictionaries
	"""
	compared_data = {}
	for keys in dict1:
		if dict1[keys] != dict2[keys]:
				compared_data[keys]=abs(dict1[keys] - dict2[keys])
	return compared_data

def progress(count, total, suffix=''):
	"""
	Prints a progress bar
	Why a progress bar? Because it's cool
	count: current step
	total: number of steps
	suffix: progress bar message
	"""
	bar_len = 30
	filled_len = int(round(bar_len * count / float(total)))

	percents = round(100.0 * count / float(total), 1)
	bar = '#' * filled_len + '-' * (bar_len - filled_len)

	sys.stdout.write('[%s] %s%s %s\r' % (bar, percents, '%', suffix))
	sys.stdout.flush()
 
#Handle twitter accounts
user1_handle = "@HillaryClinton" #Hillary Clinton
user2_handle = "@realDonaldTrump" #Donald Trump

def main():
	#Analyze handles
	progress(0,5,"analyzing tweets of %-17s" % user1_handle)
	user1_result, user1_count = analyze(user1_handle)

	progress(1,5,"analyzing tweets of %-17s" % user2_handle)
	user2_result, user2_count = analyze(user2_handle)

	#Flatten the results from the Watson PI API
	progress(2,5,"%-40s" % "flatten results")
	user1 = flatten(user1_result)
	user2 = flatten(user2_result)

	#Compare the results calculating the distance between traits
	progress(3,5,"%-40s" % "comparing results")
	compared_results = compare(user1,user2)

	#Sorts the dictionaries
	progress(4,5,"%-40s" % "sorting results")
	sorted_result = sorted(compared_results.items(), key=operator.itemgetter(1))
	#Progress completed
	progress(5,5,"%-40s" % "Completed")
	print("")

	#Print the results
	print("Tweets analyzed:")
	print("%-17s: %d" % (user1_handle,user1_count))
	print("%-17s: %d" % (user2_handle,user2_count))

	print ("Personality Insights %-17s %-17s Distance" % (user1_handle, user2_handle))
	for keys, value in sorted_result:
		print ("%20s" % keys, end=" ")
		print ("%.12f ->" % user1[keys], end=" ")
		print ("%.12f ->" % user2[keys], end=" ")
		print ("%.12f" %compared_results[keys])

#Starts the program
if __name__ == "__main__":
	main()