# Automatic Word Segmentation Experiments

Code repository associated with 'The cross-linguistic performance of word segmentation models over time', by Andrew Caines, Emma Altmann-Richer & Paula Buttery, University of Cambridge, U.K. Submitted to the Journal of Child Language.


## Prerequisites

To use this code, please ensure you have an up-to-date installation of [Python 3](https://www.python.org/downloads), preferably running in a [virtual environment](https://docs.python.org/3/tutorial/venv.html).

You'll need to install the following Python packages: [NLTK](https://www.nltk.org/install.html), [SciPy](https://www.scipy.org/install.html). You might do something like `pip3 install numpy scipy nltk` once you've [upgraded pip](https://pip.pypa.io/en/stable/installing/#upgrading-pip)

And also install [R](https://www.r-project.org), along with the [zipfR](http://zipfr.r-forge.r-project.org) library (run R and enter `install.packages('zipfR')`).

Finally, this experiment depends on the [phonemizer](https://github.com/bootphon/phonemizer) and [wordseg](https://wordseg.readthedocs.io) tools developed by Alex Cristia, Mathieu Bernard, and colleagues. Please see the installation instructions on their websites.


## Data

Note that these experiments were run on XML corpora downloaded from [CHILDES](https://childes.talkbank.org/access). We unzip and store the files under the path `~/Corpora/CHILDES/xml/` on a Unix-like system (i.e. Mac, Linux). Our corpus selections depended on factors described in our paper. In total we worked with 41 corpora covering 16 languages.


## Usage

1. Corpus preparation.

2. Phonemize the corpora.

3. Wordseg experiments.



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

_Andrew Caines_, apc38@cam.ac.uk, _December 2018_
