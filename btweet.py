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
import signal

from daemonize import Daemonize
from time import sleep

# Fix Python 2.x.
try:
    input = raw_input
except NameError:
    pass

from tweepy import API, OAuthHandler

from btweet.utils import load_options, restore_options, load_filters, restore_filters


# Lists of commands
commands = ['auth', 'get', 'help', 'run',
            'set', 'start', 'stats', 'stop', 'filter']

# Script folders and files
folder = os.path.dirname(os.path.realpath(__file__))
data_folder = os.path.join(folder, 'data')
credentials_file = os.path.join(data_folder, 'credentials.json')
options_file = os.path.join(data_folder, 'options.json')
filters_file = os.path.join(data_folder, 'filters.json')
pid_file = os.path.join(data_folder, 'btweet.pid')
man_folder = os.path.join(folder, 'man')

listener = None
stream = None
daemon = None

usage_text = """usage: btweet [--help] <command> [<args>]

List of available commands:
  auth    set the credentials to twitter
  get     get the value of an option
  set     set the value of an option
  run     start the bot in a terminal
  start   start the bot in background mode
  stop    stop the bot in background mode
  filter  get and modify the filters lists
  help    get extensive help about a command

Use 'btweet <command> -h' to get help of a command."""

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
        auth.set_access_token(data["access_token"],
                              data["access_token_secret"])
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

    check_credentials(credentials)

    with open(credentials_file, 'w+') as f:
        json.dump(credentials, f)


def check_credentials(credentials):
    # Check the integrity of the json
    for k in ["consumer_key", "consumer_secret", "access_token", "access_token_secret"]:
        if k not in credentials:
            print("btweet: Error, corrupt file.\n"
                  "Use 'btweet help auth' for get some help.")
            return False

    auth, api = load_auth(credentials)

    print(">> Using credentials of @" + auth.get_username())

    return True


def credentials_json(filename):
    import json

    if not os.path.isfile(filename):
        print("btweet: Error, file '%s' not found."
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
        print("There aren't credentials to delete.\n"
              "Use 'btweet help auth' for get some help.")


def options_values(options):
    values = {}

    for op in options:
        values[op] = options[op]['value']

    return values


def load_credentials():

    import json

    if not os.path.isfile(credentials_file):
        print("There aren't credentials to load.\n"
              "Use 'btweet help auth' for get some help.")
        credentials = None
    else:
        with open(credentials_file, 'r') as f:
            credentials = json.load(f)

        if not check_credentials(credentials):
            credentials = None

    return credentials


def handler(signum, frame):
    print("\r", end='')
    global listener
    global daemon
    global stream

    if listener:
        tmp = listener
        listener = None
        tmp.stop()
    if stream:
        stream.disconnect()
        stream = None
    if daemon:
        daemon.exit()
        daemon = None
    exit()


def launch_giveaway(verbose_level=0):
    from tweepy import Stream
    from btweet.giveawayBot import GiveawayBot

    global listener
    global stream

    print("btweet: Running giveaway bot")
    credentials = load_credentials()
    if credentials == None:
        return

    options = load_options(options_file)

    options = options_values(options)
    filters = load_filters(filters_file)
    options = {**filters, **options}
    track_list = filters['track_list']

    auth, api = load_auth(credentials)

    options['user_list'].append(auth.get_username())

    listener = GiveawayBot(api, verbose_level=verbose_level, **options)

    signal.signal(signal.SIGINT, handler)

    while True:
        try:
            stream = Stream(auth, listener)
            stream.filter(track=track_list)

        except UnicodeEncodeError:
            print(">> Unicode exception")

        except Exception as e:
            print(">> Exception %s" % e)
            listener.restart()
            sleep(10)


def show_options(option):
    options = load_options(options_file)

    if option == 'all':
        print("Available options")
        for op in options:
            print(op, options[op]['value'], options[op]['description'])
    else:

        options_names = list(options.keys())
        if not option in options_names:
            op = suggestion(option, options_names)
            print("btweet: Invalid option. The most similar option is '" + op + "'.")
            print("Use 'btweet help get' for get some help.")

        else:
            print(option, options[option]['value'],
                  options[option]['description'])


def set_option(option, value):
    import json
    options = load_options(options_file)

    options_names = list(options.keys())

    if not option in options_names:
        op = suggestion(option, options_names)
        print("btweet: Invalid option. The most similar option is '" + op + "'.")
        print("Use 'btweet help get' for get some help.")
        return

    try:
        if options[option]['type'] == 'int':
            value = int(value)
        elif options[option]['type'] == 'bool':
            if value.lower() in ("yes", "true", "t", "1"):
                value = True
            elif value.lower() in ("no", "false", "f", "0"):
                value = False
            else:
                raise ValueError

    except:
        print("btweet: Invalid value. Must be", options[option]['type'] + ".")
        return

    options[option]['value'] = value

    with open(options_file, 'w') as f:
        json.dump(options, f)


def check_daemon():

    if not os.path.exists(pid_file):
        return 0

    with open(pid_file) as f:
        pid = int(f.read())

    try:
        os.kill(pid, 0)
    except OSError:
        return 0
    else:
        return pid


class Parser:

    def __init__(self):

        # Creates the parser to call the submodules
        self.parser = argparse.ArgumentParser(add_help=False)
        self.parser.add_argument(
            'command', default='usage', type=str, nargs='?')

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
        group = auth_parser.add_mutually_exclusive_group()
        group.add_argument('-a', '--add', action='store_true',
                                 help='add or replace the twitter api credentials')
        group.add_argument('-d', '--delete', action='store_true',
                                 help='delete the current twitter api credentials')
        group.add_argument('-f', '--file', type=str,
                                 help='file with the credentials in json format')

        parsed = auth_parser.parse_args(args)

        if parsed.add:
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

        cmd = os.path.join(man_folder, "btweet")

        if parsed.command:
            cmd += "-" + parsed.command

        cmd += ".7"

        if not os.path.exists(cmd):
            print("btweet: Error, help not found. Try with 'btweet %s -h'." % parsed.command)
        else:
            os.execvp("man", ["-M", cmd ])

    def run(self, args):

        run_parser = argparse.ArgumentParser(prog='btweet run')
        run_parser.add_argument('-v', '--verbose', action='count', default=0,
                                help='verbose mode')
        parsed = run_parser.parse_args(args)

        launch_giveaway(parsed.verbose + 1)

    def start(self, args):

        run_parser = argparse.ArgumentParser(prog='btweet start')
        run_parser.parse_args(args)
        pid = check_daemon()

        if pid:
            print("btweet: Error, the daemon is already running with pid %d." % pid)
            return
        global daemon

        daemon = Daemonize(app="btweet", pid=pid_file, action=launch_giveaway)
        daemon.start()

    def stats(self, args):
        print('stats')

    def stop(self, args):
        run_parser = argparse.ArgumentParser(prog='btweet stop')
        run_parser.parse_args(args)
        pid = check_daemon()

        if pid:
            os.kill(pid, signal.SIGINT)
            print("btweet: Stopping daemon running with pid %d." % pid)
        else:
            print("btweet: Error, the daemon is not running.")

    def get(self, args):

        options_parser = argparse.ArgumentParser(prog='btweet get')
        options_parser.add_argument('option', nargs='?', default='all',
                                    help='option to get value', type=str)

        parsed = options_parser.parse_args(args)

        show_options(parsed.option)

    def set(self, args):

        options_parser = argparse.ArgumentParser(prog='btweet set')

        options_parser.add_argument('option', nargs=1,
                                    help='option to set value')
        options_parser.add_argument('value', nargs='?',
                                    help='value to set')

        parsed = options_parser.parse_args(args)

        if parsed.option[0] == "default":
            restore_options(options_file)
            print("btweet: Default options restored.")
        elif parsed.value != None:
            set_option(parsed.option[0], parsed.value)
        else:
            print("btweet: Error. Must set a value to the option.")

    def filter(self, args):

        import json
        filters = load_filters(filters_file)
        filters_names = list(filters.keys())

        filter_parser = argparse.ArgumentParser(prog='btweet filter')
        subparsers = filter_parser.add_subparsers(dest='filter')

        for p in filters_names:
            sparser = subparsers.add_parser(p)

            group = sparser.add_mutually_exclusive_group()

            group.add_argument('-a', '--add', nargs=1,
                                        help='word or phrase to add')
            group.add_argument('-d', '--delete', nargs=1,
                                        help='word or phrase to delete')


        subparsers.add_parser('default')

        parsed = filter_parser.parse_args(args)

        if parsed.filter == None:
            print("btweet: Use 'btweet filter -h' to show the help.")
            return

        if parsed.filter == "default":

            restore_filters(filters_file)

        elif not parsed.add and not parsed.delete:
            print("btweet: %s:" % parsed.filter)
            for w in filters[parsed.filter]:
                print("\t",w)
        else:
            if parsed.add:
                filters[parsed.filter].append(parsed.add[0])
            else:
                filters[parsed.filter].remove(parsed.delete[0])

            with open(filters_file,"w") as f:
                json.dump(filters,f)



    def usage(self, args):

        if check_daemon():
            print("btweet: the bot is running in background.")

        print(usage_text)



def main():

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    parser = Parser()
    parser()


if __name__ == '__main__':
    main()
