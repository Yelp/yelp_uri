export PATH := $(PWD)/bin:$(PWD)/venv/bin:$(PATH)

REBUILD_FLAG =

.PHONY: all
all: venv test

venv: .venv.touch
	rm -rf venv
	virtualenv venv --python python2.7
	pip install -r requirements_dev.txt

.PHONY: tests test
tests: test
test: venv
	tox $(REBUILD_FLAG)


.venv.touch: setup.py requirements.txt requirements_dev.txt
	$(eval REBUILD_FLAG := --recreate)
	touch .venv.touch


.PHONY: clean
clean:
	find . -iname '*.pyc' | xargs rm -f
	rm -rf .tox
	rm -rf ./venv
	rm -f .venv.touch
