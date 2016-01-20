### The MIXER

Copyright (C) 2003 Max Neunhoeffer, 
                   Lehrstuhl D fuer Mathematik, RWTH Aachen
 
This software is protected under the GNU General Public License
(see the file "GPL.txt" in die main distribution directory for details).


The mixer is little Max's version  of a "Content Management System". The
goal  is to  help  the user  to  maintain  a web  site  consisting of  a
hierarchy of  web pages in  a consistent  way. Repeating parts  of these
pages should  each be  stored and  maintained in a  single place  and an
easily understandable  procedure should  make the  final pages  from the
input the user enters.
 
For each  page this  procedure basically  pastes together  various files
from  different  places  in  a well-defined  way  and  replaces  certain
elements by other  stuff. Things like navigation tools  for the visitors
of the site are generated automatically from available data.
 
The main design principles are:
 * SIMPLICITY,
 * well-definedness,
 * good documentation,
 * the use of standard web technology (XML, XHTML, style sheets).

For installation instructions see the manual in the distribution.

Short version: untar, make, link to "mixer.py" from /usr/local/bin
Prerequisites: Python version >= 2.2

Note: This software includes the RXP parser by Richard Tobin and Python
      bindings "pyRXP.c" by ReportLab Inc.
