all: install
install:
	pip install . --upgrade
test: install clean
	cd examples; rm -rf emodels_dir; bluepymm ./mm_conf.json	
clean:
	# rm -rf examples/etype_dirs
