TEST_REQUIREMENTS=nose coverage pep8
VENV=. ./venv/bin/activate;

all: install
venv:
	virtualenv --system-site-packages venv
	$(VENV) pip install pip --upgrade
venv3:
	python3 -m venv venv
	$(VENV) pip install pip --upgrade
install: clean
	python setup.py sdist
	pip install `ls dist/bluepymm-*.tar.gz` --upgrade
install_in_venv:
	$(VENV) python setup.py sdist
	$(VENV) pip install `ls dist/bluepymm-*.tar.gz` --upgrade
install_test_requirements:
	$(VENV) pip install -q $(TEST_REQUIREMENTS) --upgrade
test: clean venv codingstyle unit functional
test3: clean venv3 codingstyle unit functional
clean:
	rm -rf bluepymm.egg-info
	rm -rf dist
	rm -rf venv
	find . -name '*.pyc' -delete
	rm -rf bluepymm/tests/examples/simple1/tmp
	rm -rf bluepymm/tests/examples/simple1/output
	rm -rf bluepymm/tests/.coverage
	rm -rf bluepymm/tests/coverage.xml
codingstyle: install_test_requirements
	$(VENV) pep8 --ignore=E402 bluepymm
unit: install_in_venv install_test_requirements
	$(VENV) cd bluepymm/tests; nosetests -a 'unit' -s -v -x --with-coverage --cover-xml \
		--cover-package bluepymm
functional: install_in_venv install_test_requirements simple1_git
	$(VENV) cd bluepymm/tests; nosetests -a '!unit' -s -v -x --with-coverage --cover-xml \
		--cover-package bluepymm
simple1_git:
	$(VENV) cd bluepymm/tests/examples/simple1; python build_git.py
autopep8: clean venv
	$(VENV) pip install autopep8
	$(VENV) find bluepymm -name '*.py' -exec autopep8 -i '{}' \;
