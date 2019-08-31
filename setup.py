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

from setuptools import setup




setup(
    name = "btweet",
    version = "0.1",
    author = "Pablo Marcos",
    author_email = "pablo.marcosm@protonmail.com",
    description = "Customizable twitter bot",
    data_files=[
        ('man', ['man/btweet.7',
                'man/btweet-auth.7',
                'man/btweet-filter.7',
                'man/btweet-get.7',
                'man/btweet-help.7',
                'man/btweet-run.7',
                'man/btweet-set.7',
                'man/btweet-start.7',
                'man/btweet-stats.7',
                'man/btweet-stop.7'
                ]
         ),
    ],
    license = "GPLv3",
    keywords = "twitter bot",
    url = "https://github.com/pablomm/btweet",
    packages=['btweet'],
    install_requires=['tweepy<=3.7', 'daemonize'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
    ],
    entry_points = {
        'console_scripts': ['btweet=btweet:main'],
    }
)
