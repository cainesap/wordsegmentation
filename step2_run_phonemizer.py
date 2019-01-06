#!/usr/bin/env python
# coding: utf-8
import sys, os, glob

# n.b. phonemizer requires eSpeak and segments for multilingual support
langcodes = { 'Basque':'eu', 'Cantonese':'zh-yue', 'Croatian':'hr', 'Danish':'da', 'Dutch':'nl',
              'EnglishNA':'en-us', 'EnglishUK':'en-gb', 'Estonian':'et', 'Farsi':'fa', 'French':'fr-fr', 'German':'de', 'Greek':'el',
              'Hungarian':'hu', 'Icelandic':'is', 'Indonesian':'id', 'Irish':'ga', 'Italian':'it', 'Japanese':'ja', 'Korean':'ko',
              'Mandarin':'cmn', 'Norwegian':'no', 'Polish':'pl', 'PortugueseBR':'pt-br', 'PortuguesePT':'pt-pt',
              'Romanian':'ro', 'Serbian':'sv', 'Spanish':'es', 'Swedish':'sv', 'Turkish':'tr', 'Welsh':'cy' }

# get username
import getpass
uname = getpass.getuser()

# utterance limit? Or zero for no limit
#limit = 0
limit = 10000

# work through all corpora in the CHILDES non_child_utterance directory: assumes 'language_collection_child' filename pattern set in step1
directory = '/Users/' + uname + '/Corpora/CHILDES/non_child_utterances/'
corpuscount = 0
print("== Phonemizing all files in: %s ==" % directory)

for filein in glob.glob(directory+'*.txt', recursive=True):
    corpuscount += 1
    language = filein.split('/')[-1].split('_')[0]  # language code for eSpeak
    lang = langcodes[language]
    fileout = filein.replace('non_child_utterances', 'phonemized').replace('.txt', '_phonemes.txt')  # name of fileout
    print(corpuscount, filein, lang, fileout)
    # phonemize command
    if language=='Japanese':  # use segments for Japanese, as transcript in romanized form
        os.system("cat %s | phonemize -b segments -s ';esyll ' -w ';eword ' -l japanese -o %s" % (filein, fileout))
        os.system("cat %s | phonemize -b segments -p ' ' -s ';esyll ' -w ';eword ' -l japanese -o %s" % (filein, fileout))
    else:
        #os.system("cat %s | phonemize -p ' ' -s ';esyll ' -w ';eword ' -l %s -o %s" % (filein, lang, fileout))
        os.system("cat %s | phonemize -p ' ' -s ';esyll ' -w ';eword ' -l %s -o %s" % (filein, lang, fileout))
    if language=='Mandarin':  # amendment for Chinese Mandarin: rm punctuation in phonemes and code-switching markers
        os.system("cat %s | sed 's/\.//g; s/-//g' | egrep -v '\(zh\)|\(en\)' > tmp.txt" % fileout)
        os.system("mv tmp.txt %s" % fileout)  # put back in place
    elif language=='Cantonese':  # ditto for Cantonese
        os.system("cat %s | sed 's/\.//g; s/-//g' | egrep -v '\(zhy\)|\(en\)' > tmp.txt" % fileout)
        os.system("mv tmp.txt %s" % fileout)  # put back in place
    # limit file to first N utterances if necessary
    if limit>0:
        os.system("head -n %i %s > tmp.txt; mv tmp.txt %s" % (limit, fileout, fileout))

print("== FINISHED ==")
print("Processed %i corpora in %i languages" % (corpuscount, len(langcodes)))
