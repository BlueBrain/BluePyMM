TEST_REQUIREMENTS=nose coverage pep8

all: install
install: clean
	python setup.py sdist
	pip install `ls dist/bluepymm-*.tar.gz` --upgrade
install_test_requirements:
	pip install -q $(TEST_REQUIREMENTS) --upgrade
virtualenv:
	virtualenv pyenv
	. ./pyenv/bin/activate
test: clean virtualenv codingstyle unit functional
clean:
	rm -rf bluepymm.egg-info
	rm -rf dist
	rm -rf pyenv
	find . -name '*.pyc' -delete
	rm -rf bluepymm/tests/examples/simple1/tmp
	rm -rf bluepymm/tests/examples/simple1/output
codingstyle: install_test_requirements
	pep8 --ignore=E402 bluepymm
unit: install install_test_requirements
	cd bluepymm/tests; nosetests -a 'unit' -s -v -x --with-coverage --cover-xml \
		--cover-package bluepymm
functional: install install_test_requirements simple1_git
	cd bluepymm/tests; nosetests -a '!unit' -s -v -x --with-coverage --cover-xml \
		--cover-package bluepymm
simple1_git:
	cd bluepymm/tests/examples/simple1; python build_git.py
autopep8: clean virtualenv
	pip install autopep8
	autopep8 -i bluepymm/*.py
	autopep8 -i bluepymm/prepare_combos/*.py
	autopep8 -i bluepymm/run_combos/*.py
	autopep8 -i bluepymm/select_combos/*.py
	autopep8 -i bluepymm/legacy/*.py
