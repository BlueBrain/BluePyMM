all: install
install:
	pip install . --upgrade
test: install clean
	cd examples; rm -rf emodels_dir; mmpy ./mm_conf.json	
clean:
	# rm -rf examples/etype_dirs
