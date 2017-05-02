TEST_REQUIREMENTS=nose coverage

all: install
install:
	pip install . --upgrade
install_test_requirements:
	pip install -q $(TEST_REQUIREMENTS) --upgrade
virtualenv:
	virtualenv pyenv
	. ./pyenv/bin/activate
test: clean virtualenv unit functional
clean:
	rm -rf pyenv
	find . -name '*.pyc' -delete
	rm -rf bluepymm/tests/examples/simple1/tmp
	rm -rf bluepymm/tests/examples/simple1/output
unit: install install_test_requirements
	cd bluepymm/tests; nosetests -a 'unit' -s -v -x --with-coverage --cover-xml \
		--cover-package bluepymm
functional: install install_test_requirements
	cd bluepymm/tests; nosetests -a '!unit' -s -v -x --with-coverage --cover-xml \
		--cover-package bluepymm

autopep8: clean virtualenv
	pip install autopep8
	autopep8 -i bluepymm/*.py
	autopep8 -i bluepymm/megate/*.py
	autopep8 -i bluepymm/legacy/*.py
