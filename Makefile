all: install
install:
	pip install -q . --upgrade
test: install clean
	cd examples; mmpy ./mm_conf.json	
clean:
	# rm -rf examples/etype_dirs
