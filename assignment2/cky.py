#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division

import sys
import re
import logging
logging.getLogger().setLevel( logging.WARNING )

class invalid_line( Exception ):
    pass



re_nonterm = re.compile( r'^(\d+)\s+NONTERMINAL\s+(\S+)')
re_binary = re.compile( r'^(\d+)\s+BINARYRULE\s+(\S+)\s+(\S+)\s+(\S+)')
re_unary = re.compile( r'^(\d+)\s+UNARYRULE\s+(\S+)\s+(\S+)')


def readCounts( filename ):
    f = open( filename )
    ml = {} # max likelihood counts
    words = {} # seen words, mapped to possible tags of speech
    bins = {} # map from BC to possible As from binaries: A -> B C
    def insert( key, count ):
        if key in ml:
            ml[ key ] += count
        else:
            ml[ key ] = count
    def insert_word( word, tag ):
        if not word in words:
            words[ word ] = set()
        words[ word ].add( tag )
    def insert_bin( A, B, C ):
        key = ( B, C )
        if not key in bins:
            bins[ key ] = set()
        bins[ key ].add( A )        
    lines = 0
    for line in f.readlines():
        lines+=1
        m = re_nonterm.match( line )
        if m:
            count = m.group(1)
            X = m.group(2)
            logging.warn( "nonterminal %s: %s" % ( X, count ) )
            key = ( X, )
            insert( key, count )
            continue
        m = re_unary.match( line )
        if m:
            count = m.group(1)
            X = m.group(2)
            Y = m.group(3)
            logging.warn( "unary %s -> %s: %s" % ( X, Y, count ) )
            key = X, Y
            insert( key, count )
            insert_word( Y, X )
            continue
        m = re_binary.match( line )
        if m:
            count = m.group(1)
            X = m.group(2)
            Y1 = m.group(3)
            Y2 = m.group(4)
            logging.warn( "binary %s -> %s %s: %s" % ( X, Y1, Y2, count ) )
            key = X, Y1, Y2
            insert( key, count )
            insert_bin( X, Y1, Y2 )
            continue
        logging.fatal( "????"+line)
        raise invalid_line
    logging.warn( "lines: %s dict len: %s" % ( lines, len( ml )))
    return (ml, words, bins)

def q1( d, x, y1, y2 ):
    return d[ ( x, y1, y2)] /d[(x,)]

def q2(d, x, w):
    return d[(x, w)] / d[x]

RARE = '_RARE_'

def cky_parse( sentence, words, bins ):
    table = {}
    bp = {}
    for j in range(1, len( sentence ) ):
        word = sentence[ j - 1]
        table[ (j-1, j) ] = words[ word ]
        bp[ ( j-1, j ) ] = word
        for i in reversed( range(0, (j-2)+1) ):
            for k in range(i+1, (j-1)+1 ):
                key = (i, j)
                if not key in table:
                    table[key] = set()
                for B in table[ (i, k) ]: 
                    for C in table[ (k,j) ]:
                        if (B, C) in bins:
                            for A in bins[ ( B, C ) ]:
                                table[ key ].add( A )
                                bp[ (i,j, A )] = ((i,k,B), (k,j,C))
    return table,bp

def cky_parse2( sentence, words, bins ):
    parse = {}
    # first fill in tags of speech
    level = 0
    for i in range(0, len( sentence ) ):
        word = sentence[ i ]
        parse[ ( level, i ) ] = words[ word]
    # the other levels
    for level in range(1, len( sentence) ):
        #print "level", level
        for i in range(0, (len( sentence) - level) ):
            #print "i", i
            # depends on level-1 place i and i+1
            parse[ ( level, i )] = set()
            for B in parse[ (level-1, i) ]:
                for C in parse[ (level-1, i+1) ]:
                    #print "B", B, "C", C
                    if (B, C) in bins:
                        for A in bins[ ( B, C ) ]:
                            #print "A", A
                            parse[ (level, i) ].add( A )
    return parse

def hail( sentence, parse ):
    for level in range( 0, len( sentence )):
        print "================================ level", level
        for i in range(0, len(sentence)-level-1):
            print i, parse[(level, i+1)]



 
def get_element( set_ ):
    """return an element from the set"""
    for e in set_:
        return e

def replace_rare( words, word ):
    if word in words:
        return word
    return RARE

cc = 0

def backtrack( bp, t ):
    global cc
    #(start, end, SYMBOL)
    me = cc
    cc += 1
    if t in bp:
        print "<< %s %s" % (me, t)
        backtrack(bp, bp[t][0])
        backtrack(bp, bp[t][1])
        print "%s >>" % me
    else:
        word = bp[(t[0], t[1])]
        print "<< %s %s %s>>" % (me, t, word)

if __name__ == "__main__":
    # setup counts
    (ml, words, bins) = readCounts( "parser_train.counts.out" )
    
    dump = False
    if dump:
        for k,v in words.iteritems():
            print "WORD", k, v

        for k,v in bins.iteritems():
            print "BIN", k, v
        exit(0)

    for line in sys.stdin:
        sentence = line.split()        
        print "======================="
        print sentence
        s2 = [ replace_rare(words, word) for word in sentence ]
        print s2
        (table, bp) = cky_parse( s2, words, bins )
        backtrack(bp, (0, 12, 'SBARQ'))
        
        exit(0)
        for k,v in sorted( table.iteritems()):
            print "table", k, v
        for k,v in sorted( bp.iteritems()):
            print "bp",k, v

        #hail( sentence, t)

        #for w in sentence:
        #    if not w in words:
        #        w = RARE
        #    print w
