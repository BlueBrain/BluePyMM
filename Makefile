TEST_REQUIREMENTS=nose coverage pep8 pylint
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
	$(VENV) python setup.py sdist bdist_wheel
	$(VENV) pip install `ls dist/bluepymm-*.tar.gz` --upgrade
install_test_requirements:
	$(VENV) pip install -q $(TEST_REQUIREMENTS) -I --upgrade
test: codingstyle unit functional
clean:
	rm -rf bluepymm.egg-info
	rm -rf dist
	rm -rf venv
	find . -name '*.pyc' -delete
	rm -rf bluepymm/tests/examples/simple1/tmp
	rm -rf bluepymm/tests/examples/simple1/output
	rm -rf bluepymm/tests/examples/simple1/output_megate
	rm -rf bluepymm/tests/.coverage
	rm -rf bluepymm/tests/coverage.xml
	rm -rf bluepymm/tests/output
	rm -rf bluepymm/tests/tmp
	rm -rf docs/build
	rm -rf build
codingstyle: pep8
pep8: clean venv install_test_requirements
	$(VENV) pep8 --ignore=E402 bluepymm
pylint: clean venv install_test_requirements
	$(VENV) pylint -d C0103,E1101,R0901,R0902,R0903,R0904,R0913,R0915,W0141,W0142,W0221,W0232,W0613,W0631,I0011,W0105,W0511,C0413,E1120,E1130,E1103,W1401 --ignore=bluepymm._version bluepymm
unit: clean venv install_in_venv install_test_requirements
	$(VENV) cd bluepymm/tests; nosetests -a 'unit' -v -x --with-coverage --cover-xml \
		--cover-package bluepymm
functional: clean venv install_in_venv install_test_requirements simple1_git
	$(VENV) cd bluepymm/tests; nosetests -a '!unit' -v -x --with-coverage --cover-xml \
		--cover-package bluepymm
simple1_git:
	$(VENV) cd bluepymm/tests/examples/simple1; python build_git.py
autopep8: clean venv
	$(VENV) pip install autopep8
	$(VENV) find bluepymm -name '*.py' -exec autopep8 -i '{}' \;
doc: venv install_in_venv
	$(VENV) pip install -q sphinx sphinx-autobuild sphinx_rtd_theme -I
	$(VENV) sphinx-apidoc -o docs/source bluepymm
	$(VENV) cd docs; $(MAKE) clean; $(MAKE) html
docpdf: venv install_in_venv
	$(VENV) pip install sphinx sphinx-autobuild -I
	$(VENV) cd docs; $(MAKE) clean; $(MAKE) latexpdf
docopen: doc
	open docs/build/html/index.html
