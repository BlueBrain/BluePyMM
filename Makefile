all: install
install:
	pip install -q . --upgrade
test: install clean
	cd examples; bluepymm ./mm_conf.json	
clean:
	rm -rf examples/emodels_dir; rm -f examples/scores.sqlite;
