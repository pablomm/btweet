#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""This file is part of BTweet.

    BTweet is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    BTweet is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with BTweet.  If not, see <https://www.gnu.org/licenses/>.
"""

# File created: 1 Aug 2018, Pablo Marcos
# Last modified: 1 Aug 2018, Pablo Marcos

from __future__ import print_function, absolute_import

import argparse
import os

from time import sleep

# Fix Python 2.x.
try:
	input = raw_input
except NameError:
	pass

from tweepy import API, OAuthHandler


# Lists of commands
commands = ['auth', 'help', 'run', 'start', 'stats', 'stop', 'options', 'words']

# Script folders and files
folder = os.path.dirname(os.path.realpath(__file__))
data_folder = os.path.join(folder, 'data')
credentials_file = os.path.join(data_folder, 'credentials.json')

def suggestion(candidate, words):
    """ Provides the most similar word in the list based on the levenshtein
    distance, if the python-Levenshtein library is installed. In other case
    returns None
    """

    try:
        from Levenshtein import distance
    except ImportError:
        return None

    best = words[0]
    score = distance(candidate, best)

    for c in words[1:]:
        s = distance(candidate, c)

        if s < score:
            score = s
            best = c

    return best

def load_auth(data):

    try:
        auth = OAuthHandler(data["consumer_key"], data["consumer_secret"])
        auth.set_access_token(data["access_token"], data["access_token_secret"])
        return auth, API(auth)

    except Exception:
        print("Error loading credentials, check your internet conection or "
              "the credentials provided")

    return None

def request_credentials():

    import json

    credentials = {}
    credentials["consumer_key"] = input("Consumer Key: ")
    credentials["consumer_secret"] = input("Consumer Secret: ")
    credentials["access_token"] = input("Access Token: ")
    credentials["access_token_secret"] = input("Access Token Secret: ")

    with open(credentials_file, 'w+') as f:
        json.dump(credentials, f)

def check_credentials(credentials):
    # Check the integrity of the json
    for k in ["consumer_key", "consumer_secret", "access_token", "access_token_secret"]:
        if k not in credentials:
            print("btweet: Error, corrupt file.\n" \
                  "Use 'btweet help auth' for get some help.")
            return False

    auth, api = load_auth(credentials)

    print("Using credentials of @" + auth.get_username())

    return True


def credentials_json(filename):
    import json

    if not os.path.isfile(filename):
        print("btweet: Error, file '%s' not found." \
              "Use 'btweet help auth' for get some help." % filename)
        return

    with open(filename, 'r') as f:
        credentials = json.load(f)

    if not check_credentials(credentials):
        return


    with open(credentials_file, 'w+') as f:
        json.dump(credentials, f)


def delete_credentials():

    if os.path.isfile(credentials_file):
        os.unlink(credentials_file)
    else:
        print("There aren't credentials to delete.\n" \
              "Use 'btweet help auth' for get some help.")

def load_credentials():

    import json

    if not os.path.isfile(credentials_file):
        print("There aren't credentials to load.\n" \
              "Use 'btweet help auth' for get some help.")
        credentials = None
    else:
        with open(credentials_file, 'r') as f:
            credentials = json.load(f)

        if not check_credentials(credentials):
            credentials = None

    return credentials


class Parser:

    def __init__(self):

        # Creates the parser to call the submodules
        self.parser = argparse.ArgumentParser(add_help=False)
        self.parser.add_argument('command',default='usage',type=str,nargs='?')

    def __call__(self):

        parsed = self.parser.parse_known_args()
        command = parsed[0].command

        if command in commands:
            getattr(self, command)(parsed[1])
        elif command == 'usage':
            self.usage(parsed[1])
        else:
            msg = "btweet: '%s' is not a command. See 'btweet --help'" % command
            suggest = suggestion(command, commands)

            if suggest:
                msg += "\nThe most similar command is '%s'" % suggest

            print(msg)

    def auth(self, args):

        auth_parser = argparse.ArgumentParser(prog='btweet auth')
        auth_parser.add_argument('-a', '--add', action='store_true',
                                 help='add or replace the twitter api credentials')
        auth_parser.add_argument('-d', '--delete', action='store_true',
                                 help='delete the current twitter api credentials')
        auth_parser.add_argument('-f', '--file', type=str,
                                 help='file with the credentials in json format')

        parsed = auth_parser.parse_args(args)

        if parsed.add and not parsed.file:
            credentials = request_credentials()
        elif parsed.file:
            credentials = credentials_json(parsed.file)
        elif parsed.delete:
            delete_credentials()
        else:
            credentials = load_credentials()


    def help(self, args):
        help_parser = argparse.ArgumentParser(prog='btweet help')
        help_parser.add_argument('command', nargs='?', default=None, choices=commands,
                            help='command to get help', type=str)

        parsed = help_parser.parse_args(args)

    def run(self, args):

        from tweepy import Stream
        from btweet.giveawayBot import GiveawayBot

        print("Running giveaway bot")
        credentials = load_credentials()
        if credentials == None: return

        track_list = ["retweet to win","sorteo RT","concurso RT"]
        ignore_list = ["plz","ayuda","gracias","please","favor","signup","thanks","justin","bieber","5sos","vma","minecraft","vote","vota","twitch"]
        follow_list = ["#follow","follow","sigue","sigueme","seguir","following","siguiendo","seguidores","seguidor","rt+follow"]
        fav_list = ["fav","rt+fav","fave","favorito","favorite","like","mg"]
        user_list = ["jazzmaniatico"]

        auth, api = load_auth(credentials)
        listener = GiveawayBot(api, follow_list, fav_list, ignore_list, user_list, verbose_level=1)


        while True:
            try:
                stream = Stream(auth, listener)
                stream.filter(track = track_list)

            except KeyboardInterrupt:
                if("y" in input("Are you sure?")):
                    listener.stop()
                    stream.disconnect()
                    exit()

            except UnicodeEncodeError:
                print(">> Unicode exception")

            except Exception as e:
                print(">> Exception %s" % e)
                listener.restart()
                sleep(10)


    def start(self, args):
        print('start')

    def stats(self, args):
        print('stats')

    def stop(self, args):
        print('stop')

    def options(self, args):
        print('options')

    def words(self, args):
        print('words')

    def usage(self, args):
        print('usage')


def main():

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    parser = Parser()
    parser()


if __name__ == '__main__':
     main()
