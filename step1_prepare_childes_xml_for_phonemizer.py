#!/usr/bin/env python
# coding: utf-8
import re, csv, os, nltk, io, glob
from nltk.corpus import cmudict
from nltk.corpus.reader import CHILDESCorpusReader

# get username
import getpass
uname = getpass.getuser()


# utterance limit? value of zero means include all utterances
#limit = 0
limit = 10000


# work through all corpora in the CHILDES XML directory: must have 'language/collection/(subcorpus)/*.xml' structure
directory = '/Users/' + uname + '/Corpora/CHILDES/xml/'
corpuscount = 0
for corpuspath in glob.glob(directory+'*/*/', recursive=True):
    print("Loading data from: %s" % corpuspath)
    corpus_root = nltk.data.find(corpuspath)
    corpus = CHILDESCorpusReader(corpus_root, '.*.xml')
    fileidlist = corpus.fileids()
    
    # get corpus name and language
    pathsegs = corpuspath.split('/')
    nsegs = len(pathsegs)
    collection = pathsegs[nsegs-2]
    language = pathsegs[nsegs-3]
    
    # split filenames by any child subcorpora
    corpora = {}
    for fid in fileidlist:
        filesegs = fid.split('/')
        nsegs = len(filesegs)
        if nsegs > 1:
            child = filesegs[0]
        else:
            child = collection
        if child in corpora:
            corpora[child].append(fid)
        else:
            corpora[child] = [fid]
    
    # work thru subcorpora
    for child in corpora:
        corpuscount += 1
        print("Processing corpus %s from collection %s in language %s" % (child, collection, language))
        fidlist = corpora[child]
        
        # make a list of all participants other than children
        partislist = corpus.participants(fidlist)
        plist = []
        patt = re.compile('CHI')
        for pdict in partislist:
            for p in pdict.keys():
                if not patt.match(p):
                    #print('not a child, this is', p)
                    if p not in plist:
                        plist.append(p)
                        #print('added to list, list is now', len(plist), 'items long')
        
        # for each corpus, fetch all non-child utterances and reformat
        sents = []
        sentcount = 0
        underscore = re.compile('\w+_\w+')
        fileout = '/Users/' + uname + '/Corpora/CHILDES/non_child_utterances/' + language + '_' + collection + '_' + child + '_max' + str(limit) + '_utterances.txt'  # andrew
        with io.open(fileout, 'w', encoding='utf8') as myfile:
            for fid in fidlist:
                sentslist = corpus.sents(fid, speaker=plist)
                for sent in sentslist:
                    sent = [w.lower() for w in sent if not re.match('.*(www|xxx|yyy|zzz).*|\W|^(h*m{2,}h*m*|m*hmh*|pft|pst|pjj|t(fu){2,}|xxs|uh+uh)$', w)]  # lowercase each word and exclude fillers
                    for i, w in enumerate(sent):  # check for merged underscore tokens in sentence and split if necessary
                        if underscore.match(w):
                            words = w.split('_')  # unmerge token
                            sent[i] = words[0]
                            sent.insert(i+1, words[1])
                    if (len(sent)>0) and (limit==0 or sentcount<limit):  # check for content in utterance
                        text = re.sub('\s+', ' ', ' '.join(sent).lstrip())
                        if (len(text)>0):
                            sentcount += 1
                            myfile.write(text+"\n")
                            #print(text)
        myfile.close()
        print("N non-child utterances in corpus = %d" % sentcount)
        print("Saved to %s" % fileout)

print("FINISHED: processed %d corpora" % corpuscount)
