#!/usr/bin/env python
# coding: utf-8
import re, csv, os, nltk, io, glob
from nltk.corpus import cmudict
from nltk.corpus.reader import CHILDESCorpusReader

# get username
import getpass
uname = getpass.getuser()


# utterance threshold? value of zero means there isn't one
# threshold = 0
threshold = 10000


# work through all corpora in the CHILDES XML directory: must have 'language/collection/(subcorpus)/*.xml' structure
directory = '/Users/' + uname + '/Corpora/CHILDES/xml/'
corpuscount = 0
statsfile = '/Users/' + uname + '/Corpora/CHILDES/corpus_statistics.txt'
with io.open(statsfile, 'w', encoding='utf8') as stats:
    stats.write("corpuscount\tlanguage\tcorpuscollection\tchild\tthreshold\tn.non-child.utterances\tn.words\n")
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
            wordcount = 0
            underscore = re.compile('\w+_\w+')
            cds = ''
            for fid in fidlist:
                sentslist = corpus.sents(fid, speaker=plist)
                for sent in sentslist:
                    sent = [w.lower() for w in sent if not re.match('.*(www|xxx|yyy|zzz).*|\W|^(h*m{2,}h*m*|m*hmh*|pft|pst|pjj|t(fu){2,}|xxs|uh+uh)$', w)]  # lowercase each word and exclude fillers
                    for i, w in enumerate(sent):  # check for merged underscore tokens in sentence and split if necessary
                        if underscore.match(w):
                            words = w.split('_')  # unmerge token
                            sent[i] = words[0]
                            sent.insert(i+1, words[1])
                    wordcount += len(sent)  # word count
                    if (len(sent)>0):  # check for content in utterance
                        text = re.sub('\s+', ' ', ' '.join(sent).lstrip())
                        if (len(text)>0):
                            sentcount += 1
                            cds += text+"\n"
            print("N non-child utterances in corpus = %d" % sentcount)
            if sentcount>=threshold or threshold==0:  # if we've reached the threshold, or there isn't one
                corpuscount += 1
                fileout = '/Users/' + uname + '/Corpora/CHILDES/non_child_utterances/' + language + '_' + collection + '_' + child + '_' + str(threshold) + 'utterances.txt'
                with io.open(fileout, 'w', encoding='utf8') as myfile:
                    myfile.write(cds)
                    myfile.close()
                    print("Saved to %s" % fileout)
                    statsline = str(corpuscount) + '\t' + language + '\t' + collection + '\t' + child + '\t' + str(threshold) + '\t' + str(sentcount) + '\t' + str(wordcount) + '\n'
                    stats.write(statsline)
            else:
                print("Not saved, didn't reach the threshold")

stats.close()
print("FINISHED: processed %d corpora" % corpuscount)
