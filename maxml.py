#
# maxml.py - Utility functions for the parsing of XML using pyRXP
#
# Copyright (C) 2003 Max Neunhoeffer, 
#                    Lehrstuhl D fuer Mathematik, RWTH Aachen
# 
# This file is protected under the GNU General Public License
# (see the file "GPL.txt" in die main distribution directory for details).
#
# $Id$
#

import os,sys,types
import pyRXP

class xmltree:
    '''Class to represent an XML tree in memory.'''
    type = ''        # the name of the element
    attr = {}        # the attribute dictionary
    subs = []        # or None for an empty element
    meta = None      # for meta data
    def __init__(self,type,attr,meta = None):
        self.type = type
        self.attr = attr
        self.subs = []     # a new empty list
        self.meta = meta
    def add(self,child):
        self.subs.append(child)
    def __repr__(self):
        if self.subs != None:
            return '<xmltree '+self.type+' nrsubs='+ \
                   str(len(self.subs))+ '>'
        else:
            return '<xmltree type='+self.type+' empty>'
    def show(s,depth = 1,cur = 0):
        o = sys.stdout
        if cur == 0:
            o.write('<xmltree '+s.type)
        else:
            o.write('  '*cur+'<'+s.type)
        if s.attr != None:
            for k in s.attr:
                o.write(' '+k+'="'+s.attr[k]+'"')
        if s.subs == None:
            o.write(' />\n')
        else:
            o.write('>\n')
            if cur < depth:
                for i in s.subs: 
                    if type(i) == types.StringType:
                        o.write('  '*(cur+1)+'STRING\n')
                    else:
                        i.show(depth,cur+1)

def objectify(tree):
    '''Changes the output of pyRXP into a tree of objects.'''
    x = xmltree(tree[0],tree[1],tree[3])
    if tree[2] != None:
        for s in tree[2]:
            if type(s) == types.TupleType:
                x.add(objectify(s))
            else:
                x.add(s)
    else:
        x.subs = None
    return x


def parse_file_for_rewrite(f):
    '''Parses an XML document, returns a tree structure from which the
    file can be reconstructed (i.e. entities, comments and CDATA sections
    are preserved). If a parser error occurs, the error is printed and
    an exception is thrown.'''
    p = pyRXP.Parser()
    p.ReturnComments = 1
    p.ReturnCDATASectionsAsTuples = 1
    p.ReturnProcessingInstructions = 1
    p.ExpandGeneralEntities = 0
    p.ExpandCharacterEntities = 0
    #p.ReturnList = 1
    fi = file(f)
    s = fi.read()
    fi.close()
    return objectify(p(s))


def parse_file(f):
    '''Parses an XML document, returns a tree structure, removing comments
    and expanding entities and CDATA sections. If a parser error occurs,
    the error is printed and an exception is thrown.'''
    p = pyRXP.Parser()
    p.ReturnComments = 0
    p.ReturnCDATASectionsAsTuples = 0
    p.ReturnProcessingInstructions = 1
    p.ExpandGeneralEntities = 1
    p.ExpandCharacterEntities = 1
    fi = file(f)
    s = fi.read()
    fi.close()
    return objectify(p(s))


def writeoutxml(tree,out,specialnodehandlers):
    '''Writes out the tree to the file out. Elements are looked up in
    the specialnodehandlers for handlers.'''

    def comment_handler(node,out):
        '''Handler function for comment nodes.'''
        out.write('<!--')
        writeoutdoc(node.subs,out)
        out.write('-->')
        return 1

    def pi_handler(node,out):
        '''Handler function for processing instruction nodes.'''
        out.write('<?'+node.attr['name']+' ')
        writeoutdoc(node.subs,out)
        out.write('?>')
        return 1

    def cdata_handler(node,out):
        '''Handler function for CDATA section nodes.'''
        out.write('<![CDATA[')
        out.write(node.subs[0])
        out.write(']]>')
        return 1

    def recurse(ob,out,specialnodehandlers):
        if ob == None: 
            return
        if type(ob) == types.StringType: 
            out.write(ob)
            return
        if type(ob) == types.ListType:
            for s in ob: recurse(s,out,specialnodehandlers)
            return
        if not(isinstance(ob,xmltree)):
            sys.stderr.write("Error: Strange object in tree:"+str(ob)+"\n")
            sys.exit(1)
        # now we know it is an xmltree:
        contentreplacement = None
        if specialnodehandlers.has_key(ob.type):
            contentreplacement = specialnodehandlers[ob.type](ob,out)
            if contentreplacement == 1: return
        
        # now write it out:
        out.write('<'+ob.type)
        if ob.attr != None:
            for k in ob.attr:
                out.write(' '+k+'="'+ob.attr[k]+'"')
        if contentreplacement == None and ob.subs == None:   # is it empty?
            out.write(' />')
        else:
            out.write('>')
            if contentreplacement != None:
                recurse(contentreplacement,out,specialnodehandlers)
            else:
                recurse(ob.subs,out,specialnodehandlers)
            out.write('</'+ob.type+'>')
        # end of function recurse


    if not(specialnodehandlers.has_key('<!--')):
        specialnodehandlers['<!--'] = comment_handler
    if not(specialnodehandlers.has_key('<?')):        
        specialnodehandlers['<?'] = pi_handler
    if not(specialnodehandlers.has_key('<![CDATA[')): 
        specialnodehandlers['<![CDATA['] = cdata_handler
    recurse(tree,out,specialnodehandlers)

