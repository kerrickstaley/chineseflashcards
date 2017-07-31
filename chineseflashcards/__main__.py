from argparse import ArgumentParser
import os
import random

from . import ChineseDeck


parser = ArgumentParser()
parser.add_argument('wordsfile', help='list of words, one per line')
parser.add_argument('outfile', nargs='?', help='apkg file to write, defaults to input filename with .apkg extension')
parser.add_argument('--preferred-words', help='preferred words yaml file')
parser.add_argument('--name', help='deck name, defaults to input filename (without extension)')


args = parser.parse_args()

wordsfile_basename = os.path.basename(args.wordsfile).split('.')[0]
wordsfile_dir = os.path.dirname(args.wordsfile)

if args.outfile is None:
  args.outfile = os.path.join(wordsfile_dir, wordsfile_basename) + '.apkg'

if args.name is None:
  args.name = wordsfile_basename


deck = ChineseDeck(random.randrange(1 << 30, 1 << 31), args.name)
if args.preferred_words:
  deck.add_preferred_words_yaml_from_file(args.preferred_words)

with open(args.wordsfile) as words:
  for word in words:
    word = word.strip()
    deck.add_word(word)

deck.write_to_file(args.outfile)
