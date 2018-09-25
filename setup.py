from setuptools import setup

setup(name='chineseflashcards',
      version='0.4.4',
      description='Create Chinese flashcards for Anki using the genanki lib',
      url='http://github.com/kerrickstaley/chineseflashcards',
      author='Kerrick Staley',
      author_email='k@kerrickstaley.com',
      license='MIT',
      packages=['chineseflashcards'],
      package_data={'chineseflashcards': ['cedict.txt', 'fields.json', 'templates.yaml', 'cards.css', 'add_pinyin_diacritics_and_color.js']},
      zip_safe=False,
      install_requires=[
        'genanki>=0.4',
        'pyyaml>=3.12',
      ])
