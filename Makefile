all: install
install:
	pip install -q . --upgrade
test: install clean
	cd examples/test_run; bluepymm ./mm_conf.json	
clean:
	rm -rf examples/test_run/emodels_dir;
	rm -rf examples/test_run/opt_dir;
	rm -f examples/test_run/scores.sqlite;
