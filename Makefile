all: install
install:
	pip install . --upgrade
test: clean unit functional
clean:
unit: install
	cd bluepymm/tests; nosetests -a 'unit' -s -v -x --with-coverage --cover-xml \
		--cover-package bluepymm
functional: install
	cd bluepymm/tests; nosetests -a '!unit' -s -v -x --with-coverage --cover-xml \
		--cover-package bluepymm
