# -*- coding: utf-8 -*-

"""Search dict.cc translations."""

from albertv0 import *
from urllib import request, parse
import os
import re
import sys

__iid__ = 'PythonInterface/v0.1'
__prettyname__ = 'dict.cc'
__version__ = '1.0'
__trigger__ = 't '
__author__ = 'Thomas Hirsch'
__dependencies__ = []

iconPath = iconLookup('dictcc')
if not iconPath:
    iconPath = os.path.dirname(__file__) + '/dictcc.png'
MAX_RESULTS = 20

def sanitizeWord(word):
    word = word.replace("\\", "")
    return word.strip("\" ")

def getResponse(word):
    # Trick to avoid dict.cc from denying the request: change User-agent to firefox's
    url = "http://www.dict.cc/?s=" + word
    req = request.Request(url, headers={'User-agent': 'Mozilla/6.0'})
    f = request.urlopen(req)
    return str(f.read())

# Find 'var c1Arr' and 'var c2Arr'
def parseResponse(response):
    engLine = re.findall('var c1Arr = new Array\(.*?\);', response)[0]
    deLine = re.findall('var c2Arr = new Array\(.*?\);', response)[0]

    if not engLine or not deLine:
        return [], []

    pattern = "\"[^,]+\""

    # Return list of matching strings
    return list(map(sanitizeWord, re.findall(pattern, engLine))), list(map(sanitizeWord, re.findall(pattern, deLine)))  # eng, de


def prepareResults(query, engWords, deWords):
    results = []
    if not engWords or not deWords:
        return results.append(Item(id=__prettyname__,
                                   icon=iconPath,
                                   text='%s not found' % query.string.strip(),
                                   actions=[]))
    else:
        minWords = len(engWords) if len(engWords) <= len(deWords) else len(deWords)
        lenResults = minWords if minWords <= MAX_RESULTS else MAX_RESULTS

        for word_idx in range(lenResults):
            if engWords[word_idx] == "\"\"": continue
            results.append(Item(id=__prettyname__,
                                icon=iconPath,
                                text=engWords[word_idx],
                                subtext=deWords[word_idx],
                                actions=[ClipAction('Copy translation to clipboard', deWords[word_idx])]))
    return results

def handleQuery(query):
    if query.isTriggered:
        response = getResponse(parse.quote(query.string.strip()))
        engWords, deWords = parseResponse(response)
        return prepareResults(query, engWords, deWords)

