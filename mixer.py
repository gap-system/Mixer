#!/usr/bin/env python
#
# The mixer - a tool for the management of web sites.
#
# Copyright (C) 2003 Max Neunhoeffer, 
#                    Lehrstuhl D fuer Mathematik, RWTH Aachen
# 
# This file is protected under the GNU General Public License
# (see the file "GPL.txt" in die main distribution directory for details).
#
# $Id$
#

__version__ = "1.01"

import os,sys,types,time
import mxutil,maxml

err = sys.stderr

# First we find the MIXERROOT (note: this does not return if nothing is found!)
(startdir,MIXERROOT) = mxutil.find_root()
MIXERLIB = MIXERROOT+'lib/'
if startdir[:len(MIXERROOT)] != MIXERROOT:
    err.write("Error: Current directory is not in subtree of MIXERROOT!\n")
    err.write("       Current dir: "+startdir+"\n")
    err.write("       MIXERROOT  : "+MIXERROOT+"\n")

# Now we add the lib directory to our Python path and import user funcs:
sys.path.insert(0,MIXERLIB)
print "Importing user functions..."
import funcs

# Call the user initialization function:
funcs.init(MIXERROOT)

# Now some primitive command line processing:
force = 0
nodoctype = 0
for a in sys.argv[1:]:
    if a == '-f': force = 1
    if a == '-n': nodoctype = 1


def search_up(MIXERROOT,path,filename):
    '''Searches for a file with name filename from MIXERROOT+path on
    upwards until MIXERROOT and afterwards in MIXERROOT/lib. Returns
    None if the file is not found. filename should usually not contain
    slashes. If found the path to it from MIXERROOT is returned.'''
    while 1:
        if os.path.exists(MIXERROOT+path+filename):
            return path
        if path == '': break
        p = path.rfind('/',0,-1)
        if p < 0: 
            path = ''
        else:
            path = path[p+1]
    if os.path.exists(MIXERROOT+'lib/'+filename):
        return 'lib/'
    return None

def workerfunc(path,filename):
    '''This function is called for all files ending in '.mixer' in the
    mixer hierarchy. 'path' is a path to the directory (relative from 
    the MIXERROOT and filename is the name of the file (without '.mixer' at
    the end. So we have to make MIXERROOT+path+filename+".html" from
    MIXERROOT+path+filename+'.mixer' plus things in MIXERLIB and files like
    MIXERROOT+path+filename+'.something'.'''

    currentlang = ''   # this means "unset"

    def make_link_relative(l):
        '''Takes the link in l and
        leaves it     if it contains a colon,
        leaves it     if it does not start with a slash and
        makes it into a relative one  if it starts with a slash. In the
        last case it will point to the position which is specified by
        l relative from the MIXERROOT.'''
        if l.find(':') >= 0 or (len(l) > 0 and l[0] != '/'):
            return l
        return ('../' * path.count('/'))+l[1:]

    # in the following dictionary we collect handlers for special nodes:
    specialnodehandlers = {}

    def mixer_handler(node,out):
        '''Handler function for nodes of type 'mixer'.'''
        if node.attr: a = node.attr
        else:         a = {}
        if a.has_key('part'):
            if a['part'] == 'main':
                # write out the main part:
                writeoutdoc(main,out)
            elif a['part'] == 'title':
                # write out the title from the main part
                if title != None: writeoutdoc(title,out)
                else:             writeoutdoc('Empty title!',out)
            else:  # handle other parts
                partfile = MIXERROOT+path+filename+'.'+a['part']
                if a.haskey('needed') and a['needed'] == 'no':
                    ignore = 1
                if not(os.path.exists(partfile)):
                    if not(ignore):
                      err.write('Warning: Part "'+a['part']+'" not found for '+
                                'document "'+path+filename+'.mixer"!\n')
                else:
                    e = maxml.parse_file_for_rewrite(partfile)
                    writeoutdoc(e.subs,out)
        elif a.has_key('var'):
            if a['var'] == 'source':
                out.write('<a href="'+path+filename+'.mixer">MIXERFILE</a>')
            elif a['var'] == 'timestamp':
                out.write(time.ctime(
                          os.stat(MIXERROOT+path+filename+'.mixer').st_mtime))
            elif config.has_key(a['var']):
                out.write(config[a['var']])
            else:
                err.write('Warning: Variable '+a['var']+' undefined!\n')
        elif a.has_key('parsevar'):
            if config.has_key(a['parsevar']):
                t = '<?xml version="1.0" encoding="ISO-8859-1"?>\n<mixer>\n'+\
                    config[a['parsevar']] + \
                    '</mixer>'
                e = maxml.parse_string_for_rewrite(t)
                writeoutdoc(e.subs,out)
            else:
                err.write('Warning: Variable '+a['parsevar']+' undefined!\n')
        elif a.has_key('func'):
            if not(funcs.__dict__.has_key(a['func'])):
                err.write('Warning: Function "'+a['func']+'" not found for '+
                          'document "'+path+filename+'.mixer"!\n')
            else:
                writeoutdoc(funcs.__dict__[a['func']](MIXERROOT,path,filename,
                                                      main,node), out)
        elif a.has_key('person') and a.has_key('data'):
            if not(people.has_key(a['person'])):
                err.write('Warning: Person unknown: "'+a['person']+'"!\n')
            elif not(people[a['person']].has_key(a['data'])):
                err.write('Warning: Data "'+a['data']+'" for person "'+
                          a['person']+'" not in database!\n')
            else:
                writeoutdoc(people[a['person']][a['data']],out)
        elif len(a.keys()) == 1:    # the short form for functions:
            f = a.keys()[0]
            if not(funcs.__dict__.has_key(f)):
                err.write('Warning: Function "'+f+'" not found for '+
                          'document "'+path+filename+'.mixer"!\n')
            else:
                writeoutdoc(funcs.__dict__[f](MIXERROOT,path,filename,
                                              main,node),out)
        return 1
    specialnodehandlers['mixer'] = mixer_handler

    def comment_handler(node,out):
        '''Handler function for comment nodes.'''
        out.write('<!--')
        writeoutdoc(node.subs,out)
        out.write('-->')
        return 1
    specialnodehandlers['<!--'] = comment_handler

    def pi_handler(node,out):
        '''Handler function for processing instruction nodes.'''
        out.write('<?'+node.attr['name']+' ')
        writeoutdoc(node.subs,out)
        out.write('?>')
        return 1
    specialnodehandlers['<?'] = pi_handler

    def cdata_handler(node,out):
        '''Handler function for CDATA section nodes.'''
        #out.write('<![CDATA[')
        out.write(node.subs[0])
        #out.write(']]>')
        return 1
    specialnodehandlers['<![CDATA['] = cdata_handler

    def link_handler(node,out):
        '''Handler function for link nodes.'''
        # handle stylesheet declaration in link element:
        if node.attr != None and node.attr.has_key('rel') and \
           node.attr['rel'] == 'StyleSheet':
            # Make a copy:
            if attr.has_key('oldstyle'): 
                newhref = make_link_relative(attr['oldstyle'])
            else:
                newhref = make_link_relative(node.attr['href'])
            out.write('<link href="'+newhref+'"')
            for k in node.attr.keys(): 
                 if k != 'href':
                     out.write(' '+k+'="'+node.attr[k]+'"')
            out.write(' />')
            return 1
        return 0
    specialnodehandlers['link'] = link_handler

    def style_handler(node,out):
        '''Handler function for style nodes.'''
        # handle stylesheet declaration in style element:
        if node.attr != None and node.attr.has_key('type') and \
           node.attr['type'] == 'text/css':
            if attr.has_key('style'):
                return '@import url('+make_link_relative(attr['style'])+');'
            # handle rewriting of the default link in here:
            if node.subs[0][:12] == '@import url(' and \
               node.subs[0][-2:] == ');':
              return '@import url('+make_link_relative(node.subs[0][12:-2])+');'
        return 0
    specialnodehandlers['style'] = style_handler

    def title_handler(node,out):
        '''Handler function for style nodes.'''
        if title != None: return title
        return 0
    specialnodehandlers['title'] = title_handler

    def writeoutdoc(node,out):
        '''This function really writes out a document recursively. 
        node is a tuple describing one node of an xml tree or a string
        or a list of such things.
        This function uses the local variables 'main', 'attr', 'path' and
        'filename' from the surrounding function. 'out' is a file object
        where the output is written to.'''
        # First handle different data types:
        if node == None: return
        elif type(node) == types.ListType:
            for s in node: writeoutdoc(s,out)
            return
        elif type(node) == types.StringType:
            out.write(node)
            return
        elif type(node) != types.InstanceType:
            err.write("Error: Strange object in tree:"+str(node)+"\n")
            sys.exit(9)

        # now we know it is a real node, is there special action necessary?
        replacement = 0
        if specialnodehandlers.has_key(node.type):
            replacement = specialnodehandlers[node.type](node,out)
            if replacement == 1: return

        # now write it out:

        # first adjust a possible 'href' attribute in case of an internal link:
        if node.attr != None and node.attr.has_key('href'):
            href = node.attr['href']
            done = 0
            while not(done):
                done = 1
                ps = href.find('{{')
                pe = href.find('}}')
                if ps >= 0 and pe >= 0 and pe > ps:
                    varname = href[ps+2:pe]
                    if config.has_key(varname):
                        href = href[:ps] + config[varname] + href[pe+2:]
                        done = 0  # possibly more to replace
                    else:
                        err.write("Warning: Variable undefined: "+varname+"\n")
            # we make it relative:
            href = make_link_relative(href)

        # throw it away if language is set and not the current one:
        if currentlang != '' and node.attr != None:
            if node.attr.has_key('xml:lang'): l = node.attr['xml:lang']
            elif node.attr.has_key('lang'):   l = node.attr['lang']
            else: l = ''
            if l != '' and currentlang != l: return

        # now write out the node:
        out.write('<'+node.type)
        if node.attr != None:
            for k in node.attr: 
                if k == 'href':
                    out.write(' href="'+href+'"')
                else:
                    out.write(' '+k+'="'+node.attr[k]+'"')
        if replacement == 0 and node.subs == None:   # is it empty?
            out.write(' />')
        else:
            out.write('>')    # no, at least not explicitly empty
            if replacement != 0:
                writeoutdoc(replacement,out)
            else:
                writeoutdoc(node.subs,out)   # this can handle a list
            out.write('</'+node.type+'>')

        # end of function 'writeoutdoc'

    source = MIXERROOT+path+filename+'.mixer'
    target = MIXERROOT+path+filename+'.html'
    if force or not(os.path.exists(target)) or \
       (os.stat(source).st_mtime > os.stat(target).st_mtime):
        # we have to do something:
        main = maxml.parse_file_for_rewrite(source)
        if main.type != 'mixer': 
            err.write("Error: No <mixer> element!\n")
            sys.exit(8)
        attr = main.attr
        main = main.subs
        i = 0
        while i < len(main) and \
              (type(main[i]) != types.InstanceType or
               main[i].type != 'mixertitle'): i += 1
        if i < len(main): 
            title = main[i].subs
            del main[i]
        else:
            title = None

        attr.setdefault('template','default.tmpl')
        template = attr['template']
        tmpl = search_up(MIXERROOT,path,template)
        if tmpl == None:
            err.write("Error: Unknown template file: "+template+"\n")
            sys.exit(9)
        template = maxml.parse_file_for_rewrite(MIXERROOT+tmpl+template)
        out = file(target,"w")
        out.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n\n')
        if not(nodoctype):
            out.write('''<!DOCTYPE html 
     PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n\n''')
        writeoutdoc(template,out)
        out.write('\n<!-- Created by mixer. -->\n')
        out.close()
    else:
        print "Nothing to be done."

print 'Starting directory:'+startdir
print 'MIXERROOT         :'+MIXERROOT
print 'MIXERLIB          :'+MIXERLIB

print 'Reading configuration...'
config = {}
execfile(MIXERLIB+'config',config)
config['today'] = time.ctime()

# Update our configuration from the local one in funcs:
try: config.update(funcs.config)
except: pass   # we ignore if there is no funcs.config

print 'Reading addresses...'
addresses = maxml.parse_file(MIXERLIB+'addresses')
if addresses.type != 'addresses':
    err.write("Error: Address database has no top element <addresses>!\n")
    sys.exit(6)
people = {}
for t in addresses.subs:
    if type(t) == types.InstanceType and t.type == 'person':
        if t.attr.has_key('id'):
            people[ t.attr['id'] ] = t.attr
for p in people:
    if people[p].has_key('sameaddressas'):
        other = people[people[p]['sameaddressas']]
        for a in ('phone','fax','department','university','city','zipcode',
                  'county','country','street','building'):
            if other.has_key(a): people[p].setdefault(a,other.get(a))
    mxutil.completeaddress(people[p])


###########################################################################
def walker(arg,dirname,files):
    l = len(MIXERROOT)
    dirname = mxutil.terminate_with_slash(dirname)
    if dirname[:l] != MIXERROOT:
        err.write("Error: Path does not start with MIXERROOT!\n")
        err.write("       "+dirname+"\n")
        sys.exit(7)
    for f in files:
        if f[-6:] == ".mixer":
            print 'Processing:'+dirname+f
            workerfunc(dirname[l:],f[:-6])

os.path.walk(MIXERROOT,walker,None)

