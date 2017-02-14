TEST_REQUIREMENTS=nose coverage

all: install
install:
	pip install . --upgrade
install_test_requirements:
	pip install -q $(TEST_REQUIREMENTS) --upgrade	
test: clean unit functional
clean:
	find . -name '*.pyc' -delete
	rm -rf bluepymm/tests/examples/simple1/tmp
	rm -rf bluepymm/tests/examples/simple1/output
unit: install install_test_requirements
	cd bluepymm/tests; nosetests -a 'unit' -s -v -x --with-coverage --cover-xml \
		--cover-package bluepymm
functional: install install_test_requirements
	cd bluepymm/tests; nosetests -a '!unit' -s -v -x --with-coverage --cover-xml \
		--cover-package bluepymm
