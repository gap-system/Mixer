#
# Makefile for the mixer.
#
# Copyright (C) 2003 Max Neunhoeffer, 
#                    Lehrstuhl D fuer Mathematik, RWTH Aachen
# 
# This file is protected under the GNU General Public License
# (see the file "GPL.txt" in die main distribution directory for details).
#
# $Id$
#
pyRXP.so:
	(cd pyRXP ; python setup.py build_ext)
	cp `find pyRXP/build -name pyRXP.so` .
	cp `find pyRXP/build -name pyRXPU.so` .

clean:
	(cd pyRXP ; python setup.py clean)
	rm -rf pyRXP/build
	rm -f pyRXP.so
	rm -f pyRXPU.so
	rm -f mixer.pdf mixer.aux mixer.log mixer.dvi mixer.out mixer.toc
	rm -f `find testsite -name "*.html"`
	rm -f *.pyc

mixer.pdf:	mixer.tex
	pdflatex mixer
	pdflatex mixer
	pdflatex mixer

dist: clean mixer.pdf
	rm -rf tmp
	mkdir tmp
	mkdir tmp/mixer
	cp -l *.py GPL.txt Makefile mixer.README mixer.pdf mixer.tex tmp/mixer
	cp -rl pyRXP tmp/mixer
	cp -rl testsite tmp/mixer
	(cd tmp ; tar czvf ../../mixer.tar.gz mixer)
	rm -rf tmp

copytoweb: mixer.pdf ../mixer.tar.gz
	cp -a mixer.pdf ../mixer.tar.gz \
              /usr/local/www-homes/Max.Neunhoeffer/Computer/Software/mixer
	
