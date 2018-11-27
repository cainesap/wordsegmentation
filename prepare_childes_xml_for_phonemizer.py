#!/usr/bin/env python
# coding: utf-8

import re, csv, os, nltk, io
from nltk.corpus import cmudict
from nltk.corpus.reader import CHILDESCorpusReader

## 0) which child? e.g. Adam, Eve, Sarah
#child = 'Adam'
child = 'Laura'

## utterance limit? value of zero means include all utterances
limit = 0

## 1) load corpus
#corpuspath = 'C:\\Users\\Emma\\AppData\\Roaming\\nltk_data\\corpora\\Brown\\' + child  # Emma
#corpuspath = '/Users/apc38/Dropbox/workspace/Corpora/CHILDES/xml/BrownXML/' + child  # Andrew
corpuspath = '/Users/apc38/Dropbox/workspace/Corpora/CHILDES/xml/LauraXML/' + child
corpus_root = nltk.data.find(corpuspath)
corpus = CHILDESCorpusReader(corpus_root, '.*.xml')
fileidlist = corpus.fileids()

## 2) make a list of all participants other than children
partislist = corpus.participants(fileidlist)
plist = []
patt = re.compile('CHI')
for pdict in partislist:
    for p in pdict.keys():
        if patt.match(p):
            print('ignoring child')
        else:
            print('not a child, this is', p)
            if p not in plist:
                plist.append(p)
                print('added to list, list is now', len(plist), 'items long')

## 3) for each file, fetch all non-child utterances and reformat
sents = []
sentcount = 0
underscore = re.compile('\w+_\w+')
#exclude = [' ', 'www', 'xxx', 'zzz']  # tokens to exclude
#fileout = 'C:\\Users\\Emma\\Documents\\0School\\0Uni\\0Work\\' + child.lower() + 'sents.txt'  # emma
fileout = '/Users/apc38/Dropbox/workspace/gitHub/wordsegmentation/CHILDES_corpora/child_directed_utterances/' + child.lower() + 'sentsapc.txt'  # andrew
with io.open(fileout, 'w', encoding='utf8') as myfile:
    for fid in fileidlist:
        sentslist = corpus.sents(fid, speaker=plist)
        for sent in sentslist:
            sent = [w.lower() for w in sent if not re.match('.*(www|xxx|yyy|zzz).*|\W|^(h*m{2,}h*m*|m*hmh*|pft|pst|pjj|t(fu){2,}|xxs|uh+uh)$', w)]  # lowercase each word
            for i, w in enumerate(sent):  # check for merged underscore tokens in sentence and split if necessary
                if underscore.match(w):
                    words = w.split('_')  # unmerge token
                    sent[i] = words[0]
                    sent.insert(i+1, words[1])
            if (len(sent)>0) and (limit==0 or sentcount<=limit):  # check for content in utterance
                text = re.sub('\s+', ' ', ' '.join(sent).lstrip())
                if (len(text)>0):
                    sentcount += 1
                    myfile.write(text+"\n")
                    print(text)

myfile.close()
print('number of non-child utterances in corpus =', sentcount)
