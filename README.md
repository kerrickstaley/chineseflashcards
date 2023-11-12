# chineseflashcards
This is a Python 3 library for generating Chinese vocabulary flashcards. It is based on [genanki](https://github.com/kerrickstaley/genanki); the genanki documentation is useful for getting started with this library. This library is used in [Chinese-Prestudy](https://github.com/kerrickstaley/Chinese-Prestudy).

[![Build Status](https://travis-ci.org/kerrickstaley/chineseflashcards.svg?branch=master)](https://travis-ci.org/kerrickstaley/chineseflashcards)

## Publishing to PyPI
If your name is Kerrick, you can publish the `chineseflashcards` package to PyPI by running these commands from the root of the repo:
```
rm -rf dist/*
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*
```
Note that this directly uploads to prod PyPI and skips uploading to test PyPI.
