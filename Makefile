TEST_REQUIREMENTS=nose coverage

all: install
install:
	pip install . --upgrade
install_test_requirements:
	pip install -q $(TEST_REQUIREMENTS) --upgrade	
test: clean unit functional
clean:
unit: install install_test_requirements
	cd bluepymm/tests; nosetests -a 'unit' -s -v -x --with-coverage --cover-xml \
		--cover-package bluepymm
functional: install install_test_requirements
	cd bluepymm/tests; nosetests -a '!unit' -s -v -x --with-coverage --cover-xml \
		--cover-package bluepymm
