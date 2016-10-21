all: install
install:
	pip install -q . --upgrade
test: install clean
clean:
