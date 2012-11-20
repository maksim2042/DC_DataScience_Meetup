#!/usr/bin/env python
# encoding: utf-8
"""
cunning_linguist.py

Created by Maksim Tsvetovat on 2011-12-08.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os

from english_stoplist import stoplist

import collections as c
import stemming.porter2 as stem 
from itertools import islice
import string
import guess_language as gl

table=string.maketrans("","")

"""A couple of util functions for dealing with large dicts"""
def find_key(dic, val):
    """return the key of dictionary dic given the value"""
    return [k for k, v in dic.iteritems() if v == val][0]

def find_value(dic, key):
    """return the value of dictionary dic given the key"""
    return dic[key]
"""-------------------------------------------------------"""


def strip_punctuation(s):
    """Strip punctuation from a string"""
    return s.translate(table, string.punctuation)


def process(text):
    try: 
        lang=gl.guessLanguageName(text)
        #print lang
    except:
        return []
        
    ## only keep the English tweets 
    if lang != 'English':
        return []
    else:
        tokens=[]
        for token in text.lower().split(' '):
            try:
                token=strip_punctuation(token).lower()
            except TypeError:
                pass
                
            if (token not in stoplist) and (not token.startswith('@')) and (not token.startswith('http')): 
                tokens.append(stem.stem(token))
                
        return tokens
