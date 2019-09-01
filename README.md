# BTweet

#### Customizable twitter bot


[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


BTweet is a small command line tool that allows you to configure your own twitter bot in a simple way to stream twitter 
based on a list of words. The bot is able to retweet, like and follow users based on the content of 
tweets and various customizable filters.
The [@jazzmaniatico](https://twitter.com/jazzmaniatico) account is an example of possible use for this tool, 
in which it has been configured to search for twitter giveaways.

## Installation 

The easiest way to install the latest version
is by using pip/easy_install to pull it from PyPI:

    pip install btweet

You may also use Git to clone the repository from
GitHub and install it manually:

    git clone https://github.com/btweet/btweet.git
    cd btweet
    python setup.py install
    
It depends on the packages [tweepy](https://github.com/tweepy/tweepy)
and [daemonize](https://github.com/thesharp/daemonize), which are installed automatically,
and optionally on [python-levenshtein](https://github.com/ztane/python-Levenshtein),
which can be installed manually via PyPI:

    pip install python-levenshtein


## Getting started
The CLI can be executed with the command `btweet` or `python -m btweet`

    $ btweet
    usage: btweet [--help] <command> [<args>]

    List of available commands:
      auth    set the credentials to twitter
      get     get the value of an option
      set     set the value of an option
      run     start the bot in a terminal
      start   start the bot in background mode
      stop    stop the bot in background mode
      filter  get and modify the filters lists
      help    get extensive help about a command
      
To get information about a command use `btweet help <command>`.
  

#### Twitter credentials

Four credentials are required to run the bot in your twitter account: API key, API secret key, Access token and 
Access secret token. If you do not have them, go to [developer.twitter.com](https://developer.twitter.com/)
and create an App. Then run `btweet auth -a` to add the credentials to the tool.
You can check if they have been added correctly:

    $ btweet auth
    >> Using credentials of @jazzmaniatico

#### Running the bot

The bot can be launch with the command `btweet run`, or as a daemon process with `btweet start` and `btweet stop`:

    $ btweet run 
    btweet: Running giveaway bot
    >> Using credentials of @jazzmaniatico
    >> Loading timeline of size 2500
    >> Starting queue thread
    >> Proccessing @pccomponentes
    >> New retweet
    ...

#### Configuration

The bot is preconfigured with some example parameters and filters. 

To change parameters, such as interaction times, use `btweet get` and `btweet set`. 
It is important to set enough time between the bot actions. For instance, to set a wait 
time of 40 seconds after a retweet use `btweet set retweet_time 40`. 
All the parameters are listed with the `get` command.


The actions of the bot are based on four lists of words:

* *track_list*: list of words used to 
[stream](https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters.html) twitter.
* *follow_list*: list of words used to follow a tweet author.
* *fav_list*: list of words use to give like a tweet.
* *ignore_list*: list of words to ignore a tweet.
* *user_list*: list of user to be ignored.

To add a word to a list use `btweet filter <list_name> -a "<word or sentence>"`. To delete it use the flag `-d`.


## Contributions

This is a hobby project made for fun, not actively maintained. Any kind of contribution is welcome, 
you can collaborate by opening an issue or making a pull request to the develop branch.

## License

The code is under the GPLv3 license. You can find a copy of the license [here](https://github.com/btweet/btweet/blob/master/LICENSE).
