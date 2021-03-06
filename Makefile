PYTHON2_CMD	?= /usr/bin/python

PREFIX 		?= /usr/local
LIBINSTALLDIR 	?= /lib
XDGCONFDIR 	?= /etc/xdg

PESTERCHUMBINDIR	= ${DESTDIR}${PREFIX}/bin
PESTERCHUMLIBDIR	= $(DESTDIR)$(PREFIX)$(LIBINSTALLDIR)/pesterchum

all:
	@echo "Ready to install..."

make-install-dirs:
	mkdir -p ${PESTERCHUMBINDIR}
	mkdir -p ${PESTERCHUMLIBDIR}
	mkdir -p ${PESTERCHUMLIBDIR}/libs
	mkdir -p ${PESTERCHUMLIBDIR}/oyoyo
	mkdir -p ${PESTERCHUMLIBDIR}/quirks
	mkdir -p ${PESTERCHUMLIBDIR}/smilies
	mkdir -p ${PESTERCHUMLIBDIR}/themes

uninstall:
	rm -f  ${PESTERCHUMBINDIR}/pesterchum
	rm -rf ${PESTERCHUMLIBDIR}

install: make-install-dirs
	install -m 644 *.py ${PESTERCHUMLIBDIR}
	install -m 644 libs/*.py ${PESTERCHUMLIBDIR}/libs
	install -m 644 oyoyo/*.py ${PESTERCHUMLIBDIR}/oyoyo
	install -m 644 quirks/*.py ${PESTERCHUMLIBDIR}/quirks
	install -m 644 smilies/* ${PESTERCHUMLIBDIR}/smilies
	cp -r themes/* ${PESTERCHUMLIBDIR}/themes
	@echo '#!/bin/sh' > ${PESTERCHUMBINDIR}/pesterchum
	@echo 'cd ${PREFIX}$(LIBINSTALLDIR)/pesterchum' >> ${PESTERCHUMBINDIR}/pesterchum
	@echo 'python2 pesterchum.py' >> ${PESTERCHUMBINDIR}/pesterchum
	chmod +x ${PESTERCHUMBINDIR}/pesterchum
