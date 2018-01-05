import chineseflashcards


def test_diacritic_syl_r():
    assert chineseflashcards.diacritic_syl('r') == 'r'


def test_diacritic_syl_and_tone_r():
    assert chineseflashcards.diacritic_syl_and_tone('r') == ('r', 5)
