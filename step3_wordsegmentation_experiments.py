## n.b. uses python 3 wordseg virtualenv (wordseg needs Py3)
# e.g. $ source ~/venvs/Py3/wordseg/bin/activate

## wordseg: see https://wordseg.readthedocs.io
from __future__ import division
import io, collections, os, glob, csv, re
from scipy.stats import entropy
from copy import deepcopy

# get username
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
    # get C_WALS stat (not in use)
    #langcode = langcodes[lang]
    return lineout1

## run wordseg
def word_seg(text, algo, lineout1, language, corpus, child, pcount, wcount):
    # start point is output of process_corpus()
    lineout2 = deepcopy(lineout1)
    pboundary = round(wcount/pcount, 6)
    lineout2.append(wcount)
    lineout2.append(pcount)
    lineout2.append(pboundary)
    # prepare filenames
    tmpfile = '/Users/' + uname + '/tmp/tmp.txt'
    goldfile = '/Users/' + uname + '/tmp/gold.txt'
    prepfile = '/Users/' + uname + '/tmp/prepared.txt'
    segfile = '/Users/' + uname + '/Corpora/CHILDES/wordseg/' + language + '_' + corpus + '_' + child + '_segmented-by_' + algo + '.txt'
    evalfile = '/Users/' + uname + '/Corpora/CHILDES/wordseg/' + language + '_' + corpus + '_' + child + '_segmented-by_' + algo + '_eval.txt'
    # write text so far to temporary file
    tmp = open(tmpfile, 'w')
    tmp.write(text)
    tmp.close()
    # prepare gold and input files for wordseg
    os.system('cat %s | wordseg-prep -u phone --punctuation --gold %s > %s' % (tmpfile, goldfile, prepfile))  # ignore punctuation
    lineout2.append(algo)
    # run wordseg command
    if algo=='dibs':  # DIBS-phrasal uses phrases (utterances) as chunks
        os.system('cat %s | wordseg-%s -t phrasal %s > %s' % (prepfile, algo, tmpfile, segfile))
    elif algo=='utt_baseline':  # utterance baseline
        os.system('cat %s | wordseg-baseline -P 0 %s > %s' % (prepfile, tmpfile, segfile))
    elif algo=='rand_baseline':  # random baseline
        os.system('cat %s | wordseg-baseline -P 0.5 %s > %s' % (prepfile, tmpfile, segfile))
    elif algo=='unit_baseline':  # basic unit baseline
        os.system('cat %s | wordseg-baseline -P 1 %s > %s' % (prepfile, tmpfile, segfile))
    elif algo=='oracle':  # oracle baseline: P(word|phone)
        os.system('cat %s | wordseg-baseline -P %.6f %s > %s' % (prepfile, pboundary, tmpfile, segfile))
    elif algo=='tp_ftp':  # transitional prob: forwards
        os.system('cat %s | wordseg-tp -d ftp %s > %s' % (prepfile, tmpfile, segfile))
    elif algo=='tp_btp':  # transitional prob: forwards
        os.system('cat %s | wordseg-tp -d btp %s > %s' % (prepfile, tmpfile, segfile))
    elif algo=='tp_mi':  # transitional prob: mutual information
        os.system('cat %s | wordseg-tp -d mi %s > %s' % (prepfile, tmpfile, segfile))
    else:
        os.system('cat %s | wordseg-%s > %s' % (prepfile, algo, segfile))
    # evaluate
    os.system('cat %s | wordseg-eval %s > %s' % (segfile, goldfile, evalfile))
    with open(evalfile, 'r') as eval:
        for line in eval:
            lineout2.append(re.sub('[^\d\.]', '', line.rstrip()))
    eval.close()
    print(lineout2)
    return lineout2

## open results file
statsfile = '/Users/' + uname + '/Corpora/CHILDES/segmentation_experiment_stats.csv'
statsopen = open(statsfile,'wt')
statscsv = csv.writer(statsopen)
statscsv.writerow(('language', 'corpus', 'child', 'n.utterances', 'prop.owus', 'tokens', 'types', 'TTR', 'boundary.entropy', 'diphone.entropy', 'zm.alpha', 'zm.X2', 'zm.p', 'n.words', 'n.phones', 'boundary.prob', 'wordseg', 'typeP', 'typeR', 'typeF', 'tokenP', 'tokenR', 'tokenF', 'boundary.all.P', 'boundary.all.R', 'boundary.all.F', 'boundary.noedge.P', 'boundary.noedge.R', 'boundary.noedge.F'))

## input directory (the phonemized files)
thousand = re.compile('000$')
algos = ['utt_baseline', 'rand_baseline', 'unit_baseline', 'oracle', 'tp_ftp', 'tp_btp', 'tp_mi', 'dibs', 'puddle']
directory = '/Users/' + uname + '/Corpora/CHILDES/phonemized/'
for filein in glob.glob(directory+'*_phonemes.txt', recursive=True):
    print(filein)
    # parse filename
    (language, corpus, child) = filein.split('/')[-1].split('_')[0:3]
    fileout = filein.replace('phonemized', 'wordseg')
    fileout = fileout.replace('phonemes', 'diphones')
    # read corpus
    phondict = collections.Counter()
    boundaries = collections.Counter()
    phonecount = 0
    wordcount = 0
    with io.open(filein, 'r', encoding='utf8') as myfile:
        linecount = 0
        owucount = 0
        inputsofar = ''
        for line in myfile:
            inputsofar += line
            linecount += 1
            ewords = line.count(';eword')
            wordcount += ewords
            if ewords==1:
                owucount += 1
            #print('utterance: %s' % (line.rstrip()))
            phones = line.split()  # split on whitespace
            nwords = len(phones) - ewords
            phonecount += nwords
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
                    csvline2 = word_seg(inputsofar, a, csvline1, language, corpus, child, phonecount, wordcount)
                    statscsv.writerow((csvline2))
        # run again at end of file, if not round 1000 line count
        if not thousand.search(str(linecount)):
            csvline1 = process_corpus(inputsofar, language, corpus, child, linecount, owucount, phondict, boundaries, fileout)
            for a in algos:
                csvline2 = word_seg(inputsofar, a, csvline1, language, corpus, child, phonecount, wordcount)
                statscsv.writerow((csvline2))
    myfile.close()

print('FINISHED')
print('see '+ statsfile)
