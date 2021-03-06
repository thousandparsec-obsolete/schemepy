# Default action
default: test

########################################
# Distribution
########################################
release:
	misc/release.py

install:
	cp -a schemepy /usr/lib/python2.5/site-packages/

########################################
# Documentation
########################################
DOCC = doc/src/compile-doc.py
doc/html/%.html: doc/src/%.rst doc/src/template.txt doc/src/compile-doc.py
	$(DOCC) doc/src/$*.rst > doc/html/$*.html

doc: $(patsubst doc/src/%.rst,doc/html/%.html,$(wildcard doc/src/*.rst))



########################################
# Test
########################################
TRUNNER = nosetests tests

test_guile:
	BACKEND=guile $(TRUNNER)
test_pyscheme:
	BACKEND=pyscheme $(TRUNNER)
test_mzscheme:
	BACKEND=mzscheme $(TRUNNER)
test_skime:
	BACKEND=skime $(TRUNNER)

test: test_guile



########################################
# Git tasks
########################################
push:
	doc/gen_index.py
	git-add doc/index.html
	GIT_EDITOR=/bin/true git-commit --amend
	git push

