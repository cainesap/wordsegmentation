#!/usr/bin/env python
# coding: utf-8
import sys, os, glob

# n.b. phonemizer requires eSpeak for multilingual support
# eSpeak 1.48.04 installed @ /usr/local/Cellar/espeak/1.48.04_1/bin/espeak
langcodes = { 'Cantonese':'yue', 'Croatian':'hr', 'Danish':'da', 'Dutch':'nl',
              'EnglishUK':'en-gb', 'Estonian':'et', 'French':'fr-fr', 'German':'de', 
              'Hungarian':'hu', 'Indonesian':'id', 'Irish':'ga', 'Italian':'it', 
              'Mandarin':'cmn', 'Polish':'pl', 'Spanish':'es', 'Swedish':'sv' }

# get username
import getpass
uname = getpass.getuser()

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
    os.system("cat %s | phonemize -p ' ' -s ';esyll ' -w ';eword ' -l %s -o %s" % (filein, lang, fileout))  # phonemize
    if lang=='Mandarin':  # amendment for Chinese Mandarin: rm punctuation in phonemes and code-switching markers
        os.system("cat %s | sed 's/\.//g; s/-//g' | egrep -v '\(zh\)|\(en\)' > %s" % (fileout, fileout))

print("== FINISHED ==")
