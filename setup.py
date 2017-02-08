from setuptools import setup

setup(name='chineseflashcards',
      version='0.1',
      description='Create Chinese flashcards for Anki using the genanki lib',
      url='http://github.com/kerrickstaley/chineseflashcards',
      author='Kerrick Staley',
      author_email='k@kerrickstaley.com',
      license='MIT',
      packages=['chineseflashcards'],
      zip_safe=False,
      install_requires=[
        'genanki>=0.1',
      ])
