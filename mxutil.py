#
# mxutil.py - utilities for the mixer.
#
# Copyright (C) 2003 Max Neunhoeffer, 
#                    Lehrstuhl D fuer Mathematik, RWTH Aachen
# 
# This file is protected under the GNU General Public License
# (see the file "GPL.txt" in die main distribution directory for details).
#
# $Id$
#

import os,sys
import pyRXP

def make_abs_path(c,p):
    '''Makes an absolute path name from p. If it is not yet absolute c
       is joined with it and the result is normalized.'''
    if os.path.isabs(p): return p
    return os.path.normpath(os.path.join(c,p))
       
def terminate_with_slash(p):
    '''Appends a slash if p does not end in a slash 
       (or backslash on Windows).'''
    if p[-1] != os.sep: return p+os.sep
    else:               return p

def find_root():
    '''Finds the current working directory and the MIXERROOT and returns 
    an pair of absolute paths ending in a slash.'''
    
    # First we determine the current working directory:
    try:
        pwd = os.environ['PWD']
    except:
        pwd = os.sep
    cwd = os.getcwd()
    if os.path.realpath(pwd) != cwd: pwd = cwd
    pwd = terminate_with_slash(pwd)

    e = sys.stderr
    if os.environ.has_key('MIXERROOT'):
        # First we consider the environment:
        m = os.environ['MIXERROOT']
        if not(os.path.isabs(m)):
            e.write('Warning: environment variable MIXERROOT is set to '+
                    'a non-absolute path (ignored).\n')
        elif not(os.path.isdir(m)):
            e.write('Warning: environment variable MIXERROOT is set to '+
                    'a non-directory (ignored).\n')
        else: return (pwd,terminate_with_slash(m))

    # "Eiertanz" for Windows drive letters:
    if os.sep == '/':
        top = '/'
    else:
        (drive,tail) = os.path.splitdrive(pwd)
        top = drive+os.sep
    # Search for an entry called 'MIXERROOT':
    c = pwd
    while c != top:
        t = os.path.join(c,'MIXERROOT')
        if os.path.exists(t):
            if os.path.isfile(t):
                if os.path.getsize(t) == 0:
                    return (pwd,c)
                else:
                    f = file(t)
                    m = f.readline().strip()
                    f.close()
                    m = make_abs_path(c,m)
                    if not(os.path.isdir(m)):
                        e.write('Error: path in '+t+' does not '+
                                'point to a directory!\n')
                        sys.exit(2)
                    return (pwd,terminate_with_slash(m))
            elif os.path.islink(t):
                m = os.readlink(t)
                m = make_abs_path(c,m)
                if not(os.path.isdir(m)):
                    e.write('Error: link '+t+' does not point to a '+
                            'directory!\n')
                    sys.exit(3)
                return (pwd,terminate_with_slash(m))
        # if we come here, we have to go up one directory
        p = c.rfind(os.sep,0,-1)
        if p < 0: break    # we terminate
        else: c = c[:p+1]
    # here we terminated, we have no idea of the MIXERROOT:
    e.write("Error: cannot determine MIXERROOT!\n")
    sys.exit(4)


def completeaddress(p):
    '''Takes the dictionary information of a person in p and completes it
    with respect to some nice combinations of the data.'''
    # name_link:
    if p.has_key('name'):
        if p.has_key('www'):
            p['name_link'] = '<a href="'+p['www']+'">'+p['name']+'</a>'
        else:
            p['name_link'] = p['name']
        # name_link_email:
        if p.has_key('email'):
            p['name_link_email'] = p['name_link'] + \
               '(<a href="mailto:'+p['email']+'">'+p['email']+'</a>)'
    # title_name:
    if p.has_key('title') and p.has_key('name'):
        p['title_name'] = p['title'] + ' ' + p['name']
    # email_link:
    if p.has_key('email'):
        p['email_link'] = '<a href="mailto:'+p['email']+'">'+p['email']+'</a>'

    # address:
    a = p.get('name_link','')
    if a: a += '<br />'
    if p.has_key('department'): a += p['department'] + '<br />\n'
    if p.has_key('university'): a += p['university'] + '<br />\n'
    if p.has_key('building'): a += p['building'] + '<br />\n'
    if p.has_key('street'): a += p['street'] + '<br />\n'
    zipbefore = 0
    c = p.get('country','').lower()
    if c == 'germany' or c == 'france' or c == 'italy': zipbefore = 1
    c = p.get('city','')
    if p.has_key('county'): c += ', '+p['county']
    if p.has_key('zipcode'):
        if zipbefore: 
            c = p['zipcode'] + ' ' + c
        else:
            c += ', ' + p['zipcode']
    if c: a += c + '<br />\n'
    if p.has_key('country'): a += p['country'] + '<br />\n'
    if a: 
        p.setdefault('address',a)
    if p.has_key('address'):   # note: might be given explicitly!
        p['contact'] = p['address']
        if p.has_key('email'):
            p['contact'] +='email: <a href="mailto:' + p['email'] + '">' + \
                           p['email'] + '</a><br />\n'
    # name_city:
    if p.has_key('name'):
        if p.has_key('city'):
            p['name_city'] = p['name'] + ', ' + p['city']
        else:
            p['name_city'] = p['name']
    # name_link_city:
    if p.has_key('name_link'):
        if p.has_key('city'):
            p['name_link_city'] = p['name_link'] + ', ' + p['city']
        else:
            p['name_link_city'] = p['name_link']


