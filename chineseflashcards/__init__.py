import collections
import functools
import genanki
import os.path
import re

CEDICT_FILE = os.path.join(
  os.path.dirname(os.path.abspath(__file__)),
  'cedict.txt')


class CedictWord:
  def __init__(self, trad, simp, pinyin, tw_pinyin, defs, clfrs):
    self.trad = trad
    self.simp = simp
    self.pinyin = pinyin
    self.tw_pinyin = tw_pinyin
    self.defs = defs
    self.clfrs = clfrs

  def __repr__(self):
    return '{}({}, {}, {}, {}, {}, {})'.format(
      self.__class__.__name__,
      repr(self.trad),
      repr(self.simp),
      repr(self.pinyin),
      repr(self.tw_pinyin),
      repr(self.defs),
      repr(self.clfrs),
    )


class Classifier:
  def __init__(self, trad, simp, pinyin):
    self.trad = trad
    self.simp = simp
    self.pinyin = pinyin

  @classmethod
  def parse(cls, s):
    if '|' in s:
      trad, rest = s.split('|')
      simp, rest = s.split('[')
    else:
      trad, rest = s.split('[')
      simp = trad
    pinyin = rest.rstrip(']')

    return cls(trad, simp, pinyin)


def _parse_line(line):
  m = re.match(r'(.+?) (.+?) \[(.+?)\] /(.+)/', line.strip())
  defs = m.group(4).split('/')

  actual_defs = []
  clfrs = None
  tw_pinyin = None
  for def_ in defs:
    if def_.startswith('CL:'):
      pieces = def_.split(':', 2)[1].split(',')
      clfrs = [Classifier.parse(piece) for piece in pieces]
    elif def_.startswith('Taiwan pr. '):
      tw_pinyin = def_.split('[')[1].rstrip(']')
    else:
      actual_defs.append(def_)

  return CedictWord(
    m.group(1), m.group(2), m.group(3), tw_pinyin, actual_defs, clfrs)


def toned_char(c, tone):
  data = [
    ['ā', 'á', 'ǎ', 'à', 'a'],
    ['ē', 'é', 'ě', 'è', 'e'],
    ['ī', 'í', 'ǐ', 'ì', 'i'],
    ['ō', 'ó', 'ǒ', 'ò', 'o'],
    ['ū', 'ú', 'ǔ', 'ù', 'u'],
    ['ǖ', 'ǘ', 'ǚ', 'ǜ', 'ü'],
  ]
  for row in data:
    if row[4] == c:
      return row[tone - 1]


def toned_syl(syl):
  rv = []
  tone = int(syl[-1])
  curr = syl[0]
  toned = False
  for next_ in syl[1:]:
    if curr == 'u' and next_ == ':':
      curr = 'ü'
      continue
    if (curr in 'ae'
        or not toned and curr == 'o' and next_ == 'u'
        or not toned and curr in 'aeiouü' and next_ not in 'aeiouü'):
      rv.append(toned_char(curr, tone))
      toned = True
    else:
      rv.append(curr)

    curr = next_

  return ''.join(rv)


def prettify_pinyin(p, lower=False):
  rv = []
  for syl in p.split():
    if syl[-1] not in '1234':
      rv.append(syl.rstrip('5'))
      continue

    tone = int(syl[-1])
    toned = toned_syl(syl)
    rv.append('<span class="tone{}">{}</span>'.format(tone, toned))

  rv = ' '.join(rv)
  if lower:
    rv = rv.lower()
  return rv


@functools.lru_cache()
def load_cedict():
  rv = collections.defaultdict(list)

  with open(CEDICT_FILE) as inf:
    for line in inf:
      if line.startswith('#'):
        continue

      word = _parse_line(line)
      rv[word.trad].append(word)
      if word.simp != word.trad:
        rv[word.simp].append(word)

  return dict(rv)


class MultipleMatchingWordsException(Exception):
  pass

class ChineseDeck(genanki.Deck):
  def __init__(self, deck_id=None, name=None):
    flds = open('/home/kerrick/Open_Source_Contrib/hsk_flashcards_rust/src/flds.json')
    templates = open('/home/kerrick/Open_Source_Contrib/hsk_flashcards_rust/src/templates.yaml').read()
    templates = templates.replace('CHARACTER', '{{#Traditional}}<span class="nobr">{{Traditional}}</span>|{{/Traditional}}<span class="nobr">{{Simplified}}</span>')
    templates = templates.replace('PINYIN', '{{#Taiwan Pinyin}}{{Taiwan Pinyin}} | {{/Taiwan Pinyin}}{{Pinyin}}')
    css = open('/home/kerrick/Open_Source_Contrib/hsk_flashcards_rust/src/card.css')
    super().__init__(deck_id, name, flds, templates, css)
    self._cedict = load_cedict()

  def _lookup_word(self, word, alt_word, pinyin):
    candidates = self._cedict[word]

    new_candidates = []
    for candidate in candidates:
      if alt_word not in [None, candidate.simp, candidate.trad]:
        continue
      if pinyin not in [None, candidate.pinyin]:
        continue
      new_candidates.append(candidate)

    candidates = new_candidates
    if len(candidates) > 1:
      new_candidates = []
      for candidate in candidates:
        if (candidate.defs[0].startswith('variant of')
            or candidate.defs[0].startswith('old variant of')):
          continue
        if re.match(r'see [^ ]+\[[^\]]+\]', candidate.defs[0]):
          continue
      candidates = new_candidates

    if len(candidates) > 1:
      raise MultipleMatchingWordsException(
        'multiple entries for word={} alt_word={} pinyin={}: {}'.format(
          repr(word), repr(alt_word), repr(pinyin), candidates))

    return candidates[0]

  def add_word(self, word, alt_word=None, pinyin=None):
    word = self._lookup_word(word, alt_word, pinyin)
    note = genanki.Note(
      None,
      [word.simp, word.trad if word.trad != word.simp else '',
      prettify_pinyin(word.pinyin), '/'.join(word.defs), '', '', ''])
    note.add_card(0)
    note.add_card(1)
    self.add_note(note)
