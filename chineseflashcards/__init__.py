import collections
import functools
import genanki
import os.path
import re

CHINESE_NOTE_MODEL_ID = 2828301746
CEDICT_FILE = os.path.join(
  os.path.dirname(os.path.abspath(__file__)),
  'cedict.txt')
FIELDS_FILE = os.path.join(
  os.path.dirname(os.path.abspath(__file__)),
  'fields.json')
TEMPLATES_FILE = os.path.join(
  os.path.dirname(os.path.abspath(__file__)),
  'templates.yaml')
CSS_FILE = os.path.join(
  os.path.dirname(os.path.abspath(__file__)),
  'cards.css')


class ChineseNote(genanki.Note):
  def __init__(self, **kwargs):
    super().__init__(load_chinese_note_model(), **kwargs)

  @property
  def guid(self):
    # match the format used by hsk_flashcards_rust, normally we'd just do guid_for(simp, trad, pinyin)
    return genanki.guid_for(' '.join([
      'kerrick hsk',
      self.fields[0],  # simp
      self.fields[1],  # trad
      self.fields[2],  # pinyin
    ]))


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
      simp, rest = rest.split('[')
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


def prettify_defs(defs):
  pieces = ['<ol>']

  for def_ in defs:
    pieces.append('<li>')
    pieces.append(def_)
    pieces.append('</li>')

  pieces.append('</ol>')

  return ''.join(pieces)


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


def prettify_classifiers(clfrs, simp_first=False):
  if clfrs is None:
    return ''

  rv = []
  for clfr in clfrs:
    first, second = clfr.trad, clfr.simp
    if simp_first:
      first, second = second, first

    s = first
    if second != first:
      s += '|' + second

    s += '(' + prettify_pinyin(clfr.pinyin, True) + ')'

    rv.append(s)

  return ', '.join(rv)


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


@functools.lru_cache()
def load_chinese_note_model():
  with open(FIELDS_FILE) as fields, open(TEMPLATES_FILE) as templates, open(CSS_FILE) as css:
    templates_formatted = templates.read()
    templates_formatted = templates_formatted.replace(
      'CHARACTER',
      '{{#Traditional}}<span class="nobr">{{Traditional}}</span>|{{/Traditional}}'
      '<span class="nobr">{{Simplified}}</span>')
    templates_formatted = templates_formatted.replace(
      'PINYIN', '{{#Taiwan Pinyin}}{{Taiwan Pinyin}} | {{/Taiwan Pinyin}}{{Pinyin}}')
    return genanki.Model(
      CHINESE_NOTE_MODEL_ID,
      'Chinese',
      fields=fields.read(),
      templates=templates_formatted,
      css=css.read(),
    )


class MultipleMatchingWordsException(Exception):
  pass


class NoMatchingWordsException(Exception):
  pass


class ChineseDeck(genanki.Deck):
  def __init__(self, deck_id=None, name=None):
    super().__init__(deck_id, name)
    self._cedict = load_cedict()

  def _lookup_word(self, word, alt_word, pinyin):
    candidates = self._cedict.get(word, [])

    matching_candidates = []
    for candidate in candidates:
      if alt_word not in [None, candidate.simp, candidate.trad]:
        continue
      if pinyin not in [None, candidate.pinyin]:
        continue
      matching_candidates.append(candidate)

    if len(matching_candidates) > 1:
      # trimmed candidates excludes entries that are just variants of another entry
      trimmed_candidates = []
      for candidate in matching_candidates:
        if (candidate.defs[0].startswith('variant of')
            or candidate.defs[0].startswith('old variant of')):
          continue
        if re.match(r'see [^ ]+\[[^\]]+\]', candidate.defs[0]):
          continue
        trimmed_candidates.append(candidate)
    else:
      trimmed_candidates = matching_candidates

    if len(trimmed_candidates) > 1:
      help_text = 'you need to disambiguate by passing '
      if alt_word is None and pinyin is None:
        help_text += 'alt_word and/or pinyin'
      elif alt_word is None:
        help_text += 'alt_word'
      else:  # pinyin is None
        help_text += 'pinyin'

      raise MultipleMatchingWordsException(
        'multiple entries for word={} alt_word={} pinyin={}; {}: {}'.format(
          repr(word), repr(alt_word), repr(pinyin), help_text, matching_candidates))

    if not trimmed_candidates:
      raise NoMatchingWordsException(
        'no entries for word={} alt_word={} pinyin={}'.format(
          repr(word), repr(alt_word), repr(pinyin)))

    return trimmed_candidates[0]

  def add_word(self, word, alt_word=None, pinyin=None):
    word = self._lookup_word(word, alt_word, pinyin)
    note = ChineseNote(
      fields=[
        word.simp,
        word.trad if word.trad != word.simp else '',
        prettify_pinyin(word.pinyin, True),
        prettify_defs(word.defs),
        prettify_classifiers(word.clfrs),
        prettify_pinyin(word.tw_pinyin or ''),
        '',
      ])
    self.add_note(note)
