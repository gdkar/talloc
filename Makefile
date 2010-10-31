# simple makefile wrapper to run waf

WAFPATH:=$(shell PATH=../../buildtools/bin:buildtools/bin:$(PATH) which waf)

WAF=WAF_MAKE=1 $(WAFPATH)

all:
	$(WAF) build

install:
	$(WAF) install

uninstall:
	$(WAF) uninstall

test:
	$(WAF) test $(TEST_OPTIONS)

testenv:
	$(WAF) test --testenv $(TEST_OPTIONS)

quicktest:
	$(WAF) test --quick $(TEST_OPTIONS)

dist:
	$(WAF) dist

distcheck:
	$(WAF) distcheck

clean:
	$(WAF) clean

distclean:
	$(WAF) distclean

reconfigure: configure
	$(WAF) reconfigure

show_waf_options:
	$(WAF) --help

# some compatibility make targets
everything: all

testsuite: all

check: test

torture: all

# this should do an install as well, once install is finished
installcheck: test

etags:
	$(WAF) etags

ctags:
	$(WAF) ctags

bin/%:: FORCE
	$(WAF) --targets=`basename $@`
FORCE:

configure: autogen-waf.sh ../../buildtools/scripts/configure.waf
	./autogen-waf.sh

Makefile: autogen-waf.sh configure ../../buildtools/scripts/Makefile.waf
	./autogen-waf.sh
