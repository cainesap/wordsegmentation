## make sure you have a 'tmp' folder in your home directory

## best run in a Python 3 virtual environment
## see https://wordseg.readthedocs.io
from __future__ import division
import io, collections, os, glob, csv, re
from scipy.stats import entropy
from copy import deepcopy

## get username
import getpass
uname = getpass.getuser()

## get corpus stats
def process_corpus(text, lang, corp, chi, utts, owus, pdict, bdict, fout):
    owu = owus/utts
    lineout1 = [lang, corp, chi, utts, owu]
    # corpus types, tokens
    ordered = sorted(pdict.items(), key=lambda pair: pair[1], reverse=True)
    tokencount = sum(pdict.values())
    lineout1.append(tokencount)
    typecount = len(ordered)
    lineout1.append(typecount)
    ttr = typecount / tokencount
    lineout1.append(ttr)
    # diphone distributions
    boundarydist = []
    diphonedist = []
    k=0
    with io.open(fout, 'w', encoding='utf8') as writefile:
        writefile.write('k\tf\type\n')
        for diph, denom in ordered:
            k+=1
            if bdict[diph]:
                num = bdict[diph]
            else:
                num = 0
            prob = num / denom  # boundary prob
            boundarydist.append(prob)
            relfreq = denom / tokencount  # diphone prob
            diphonedist.append(relfreq)
            writefile.write('%i\t%i\t%s\n' % (k, denom, diph))
    writefile.close()
    # entropy calcs
    boundaryH = entropy(boundarydist, qk=None, base=2)
    lineout1.append(boundaryH)
    diphoneH = entropy(diphonedist, qk=None, base=2)
    lineout1.append(diphoneH)
    # run Zipf LNRE fit (clear old file first)
    tmplnre = '/Users/' + uname + '/tmp/lnre.txt'
    cmd1 = 'rm '+ tmplnre
    os.system(cmd1)
    cmd2 = 'Rscript lnre.R '+ fout
    os.system(cmd2)
    if os.path.exists(tmplnre):
        with open(tmplnre, 'r') as lnre:
            for line in lnre:
                lineout1.append(line.rstrip())
        lnre.close()
    else:  # else 3 zeros
        lineout1.append(0)
        lineout1.append(0)
        lineout1.append(0)
    # get C_WALS stat
    #langcode = langcodes[lang]
    return lineout1

## run wordseg
def word_seg(text, algo, lineout1):
    # wordseg bit
    lineout2 = deepcopy(lineout1)
    tmpfile = '/Users/' + uname + '/tmp/tmp.txt'
    tmp = open(tmpfile, 'w')
    tmp.write(text)
    tmp.close()
    tmpgold = '/Users/' + uname + '/tmp/gold.txt'
    tmpprep = '/Users/' + uname + '/tmp/prepared.txt'
    tmpseg = '/Users/' + uname + '/tmp/segmented.' + algo + '.txt'
    tmpeval = '/Users/' + uname + '/tmp/eval.' + algo + '.txt'
    os.system('cat '+tmpfile+' | wordseg-prep -u phone --punctuation --gold '+tmpgold+' > '+tmpprep)  # ignore punctuation
    lineout2.append(algo)
    if algo=='dibs':  # dibs requires a training file
#        os.system('cat /Users/apc38/tmp/prepared.txt | wordseg-'+algo+' -t baseline '+tmpfile+' > /Users/apc38/tmp/segmented.'+algo+'.txt')
        os.system('cat '+tmpprep+' | wordseg-'+algo+' -t phrasal '+tmpfile+' > '+tmpseg)
    else:
        os.system('cat '+tmpprep+' | wordseg-'+algo+' > '+tmpseg)
    os.system('cat '+tmpseg+' | wordseg-eval '+tmpgold+' > '+tmpgold)
    # read eval, add to wordseg list
    with open(tmpeval, 'r') as eval:
        for line in eval:
            lineout2.append(re.sub('[^\d\.]', '', line.rstrip()))
    eval.close()
    print(lineout2)
    return lineout2


## open results file
statsfile = 'wordseg_experiment_stats.csv'
statsopen = open(statsfile,'wt')
statscsv = csv.writer(statsopen)
statscsv.writerow(('language', 'corpus', 'child', 'n.utterances', 'prop.owus', 'tokens', 'types', 'TTR', 'boundary.entropy', 'diphone.entropy', 'zm.alpha', 'zm.X2', 'zm.p', 'wordseg', 'typeP', 'typeR', 'typeF', 'tokenP', 'tokenR', 'tokenF', 'boundary.all.P', 'boundary.all.R', 'boundary.all.F', 'boundary.noedge.P', 'boundary.noedge.R', 'boundary.noedge.F'))

## input directory (the 10k files)
thousand = re.compile('000$')
algos = ['baseline', 'dibs', 'tp', 'puddle']  # wordseg algorithms available on Mac
directory = '/Users/' + uname + '/Corpora/CHILDES/phonemized/10000'
for filein in glob.glob(directory+'/**/*.espeak.txt', recursive=True):
    #print(filein)
    # parse filename
    patt = re.compile('10000.+10k')
    matched = patt.search(filein)
    parse1 = matched.group()
    parse2 = parse1.replace('10000/', '')
    parse3 = parse2.replace('10k', '')
    language = parse3.split('/')[0].lower()
    corpus = parse3.split('/')[1].lower()
    child = parse3.split('/')[2].lower()
    # fileout name change
    fileout = filein.replace('phonemized', 'wordseg')
    fileout = fileout.replace('espeak', 'diphones')
    # make directory if necessary
    basedir = os.path.dirname(fileout)
    if os.path.exists(basedir):
        pass
    else:
        os.system('mkdir -p '+basedir)
    # read corpus
    phondict = collections.Counter()
    boundaries = collections.Counter()
    with io.open(filein, 'r', encoding='utf8') as myfile:
        linecount = 0
        owucount = 0
        inputsofar = ''
        for line in myfile:
            inputsofar += line
            linecount += 1
            ewords = line.count(';eword')
            if ewords==1:
                owucount += 1
            #print('utterance: %s' % (line.rstrip()))
            phones = line.split()  # split on whitespace
            for (i, phone) in enumerate(phones):
                if i==0 or phones[i]==';eword' or phones[i-1]==';eword':
                    pass  # ignore phone 1 in utterance or word and word delimiters
                else:
                    diphone = phones[i-1] + phones[i]
                    phondict[diphone] += 1
                    if i==1 or phones[i+1]==';eword' or phones[i-2]==';eword':
                        #print('boundary diphone: %s' % (diphone))
                        boundaries[diphone] += 1
                        #print('count: %i' % (boundaries[diphone]))
            # reached iteration point? (round 1000)
            if thousand.search(str(linecount)):
                csvline1 = process_corpus(inputsofar, language, corpus, child, linecount, owucount, phondict, boundaries, fileout)
                for a in algos:
                    csvline2 = word_seg(inputsofar, a, csvline1)
                    statscsv.writerow((csvline2))
        # run again at end of file, if not 10k utterances
        if linecount!=10000:
            csvline1 = process_corpus(inputsofar, language, corpus, child, linecount, owucount, phondict, boundaries, fileout)
            for a in algos:
                csvline2 = word_seg(inputsofar, a, csvline1)
                statscsv.writerow((csvline2))
    myfile.close()

print('FINISHED')
print('see '+ statsfile)
