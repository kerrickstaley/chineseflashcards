test:
	py.test tests
	node chineseflashcards/add_pinyin_diacritics_and_color.js

publish_test:
	python3 setup.py sdist bdist_wheel
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

publish_real:
	python3 setup.py sdist bdist_wheel
	twine upload dist/*
