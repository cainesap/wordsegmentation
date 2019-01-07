# Automatic Word Segmentation Experiments

Code repository associated with 'The cross-linguistic performance of word segmentation models over time', by Andrew Caines, Emma Altmann-Richer & Paula Buttery, University of Cambridge, U.K. 

Submitted to the Journal of Child Language.


## Prerequisites

To use this code, please ensure you have an up-to-date installation of [Python 3](https://www.python.org/downloads), preferably running in a [virtual environment](https://docs.python.org/3/tutorial/venv.html).

You'll need to install the following Python packages: [NLTK](https://www.nltk.org/install.html), [SciPy](https://www.scipy.org/install.html). You might do something like `pip3 install numpy scipy nltk` once you've [upgraded pip](https://pip.pypa.io/en/stable/installing/#upgrading-pip). Be sure to also download the data associated with NLTK (`python -m nltk.downloader all`).

And also install [R](https://www.r-project.org), along with the [zipfR](http://zipfr.r-forge.r-project.org) library (run R and enter `install.packages('zipfR')`).

Finally, this experiment depends on the [phonemizer](https://github.com/bootphon/phonemizer) and [wordseg](https://wordseg.readthedocs.io) tools developed by Alex Cristia, Mathieu Bernard, and colleagues. Please see the installation instructions on their websites. Note that phonemizer requires `festival` and/or `eSpeak` as back-end text-to-speech systems, plus optionally segments grapheme-to-phoneme mapping. We use [espeak-ng](https://github.com/espeak-ng/espeak-ng) with extended dictionaries for Cantonese, Mandarin, Russian; plus [segments](https://github.com/cldf/segments) for Japanese etc.

Wordseg has various dependencies too, [detailed here](https://wordseg.readthedocs.io/en/latest/installation.html). Since it needs Python 3, it's cleaner to set up a virtual environment and install wordseg there.


## Data

Note that these experiments were run on XML corpora downloaded from [CHILDES](https://childes.talkbank.org/data-xml). We unzip and store the files under the path `~/Corpora/CHILDES/xml/` on a Unix-like system (i.e. Mac, Linux). Our corpus selections depended on factors described in our paper. In total we worked with 41 corpus collections, containing 70 child corpora and covering 16 languages.

Note that we removed the diary and 0notrans/0untranscribed/0extra directories in the Lara (Eng.UK), Braunwald, MacWhinney, Nelson (Eng.NA) and LeeWongLeung collections before further processing.


## Directory structure

In your `~/Corpora/CHILDES/` directory, you need to have at least the following subdirectories: `xml`, `non_child_utterances`, `phonemized`, `wordseg`, plus a `~/tmp/` directory for temporary files created during the wordseg experiments.

It's important that within `~/Corpora/CHILDES/xml/` you have subdirectories for each language: e.g. `~/Corpora/CHILDES/xml/Spanish/`, `~/Corpora/CHILDES/xml/French/`. The downloaded and unzipped CHILDES corpora go into the language appropriate directory, maintaining the structure they come in, i.e. `collectionName` or `collectionName/childName` (e.g. `Lara/` or `Brown/Adam/`).

Experiment output files will save to your working directory (i.e. where you download the repository and/or run the experiment from) unless you update the code.


## Usage

1. Corpus preparation: takes XML transcriptions for all corpora in the data directory, filters child utterances, and outputs plain text strings one line per utterance if there are the requisite number of non-child utterances in the corpus (default=10000; must be edited in file). Also counts corpora, non-child utterances and words, and outputs a statistics file in the directory above the XML. Run as --
```
python3 step1_prepare_childes_xml_for_phonemizer.py
```

2. Phonemize the corpora: transforms plain text utterances and transforms them into phonemic form with the `phonemizer` toolkit. Deals with a known set of languages, listed at the top of the script (to add new languages: add to the dictionary in the script with the new language name and eSpeak code, available by querying `espeak --voices` from the command line). Outputs a limited number of utterances (default=10000; edit in file, or set to zero to indicate no limit). Note that we used espeak-ng (version 1.49.3) for all languages except segments for Japanese (note that we edited error-handling so that all invalid graphemes would be ignored rather than causing exit; to do this replace the raise error line in the strict function in `segments/src/segments/errors.py` with `return ''`). Run as --
```
python3 step2_run_phonemizer.py
```

3. Wordseg experiments: prepares each phonemized file for use by wordseg. Runs selected wordseg algorithms (currently: baselines, transitional probabilities, DiBS, PUDDLE) on every file and evaluates against the true word segmentations. Requires `lnre.R` (which installs the `zipfR` library if you don't already have it) and a `~/tmp/' directory. Outputs experiment files to `~/Corpora/CHILDES/wordseg/` and a results file to `~/Corpora/CHILDES/segmentation_experiment_stats.csv`.

Run within a virtual environment if that's where you've installed `wordseg`, e.g.
```
source ~/venvs/Py3/wordseg/bin/activate
```
And then run as --
```
python3 step3_wordsegmentation_experiments.py
```

4. Regression models: 


## Citation

If you use this code please cite our paper:

```
@article{caines-et-al-xxxx,
  author = {Andrew Caines and Emma Altmann-Richer and Paula Buttery},
  year = {submitted},
  title = {The cross-linguistic performance of word segmentation models over time},
  journal = {Journal of Child Language},
}
```

_Andrew Caines_, andrew.caines@cl.cam.ac.uk, _January 2019_
