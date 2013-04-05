#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division

import sys
import re
import logging
import json
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
        count = int( count )
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
            logging.debug( "nonterminal %s: %s" % ( X, count ) )
            key = ( X, )
            insert( key, count )
            continue
        m = re_unary.match( line )
        if m:
            count = m.group(1)
            X = m.group(2)
            Y = m.group(3)
            logging.debug( "unary %s -> %s: %s" % ( X, Y, count ) )
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
            logging.debug( "binary %s -> %s %s: %s" % ( X, Y1, Y2, count ) )
            key = X, Y1, Y2
            insert( key, count )
            insert_bin( X, Y1, Y2 )
            continue
        logging.fatal( "????"+line)
        raise invalid_line
    logging.debug( "lines: %s dict len: %s" % ( lines, len( ml )))
    return (ml, words, bins)

def q1( ml, x, y1, y2 ):
    return ml[ ( x, y1, y2)] / ml[(x,) ]

def q2( ml, x, w ):
    return ml[ (x, w)] / ml[(x,) ]

RARE = '_RARE_'


def backtrack2( bp, key, S ):
    (i,j) = key
    entry = bp[ key ][ S ]
    if type( entry ) == str:
        return [ S, entry ] # word         
    else:
        (k, B, C) = entry
        return [ S, backtrack2(bp, (i,k), B), backtrack2(bp, (k,j), C) ]



def cky_prob2( sentence, words, bins ):
    table = {}
    bp = {}
    sentence_rare = [ replace_rare(words, word) for word in sentence ]
    for j in range(1, len( sentence_rare )+1 ):
        word = sentence_rare[ j - 1]
        original_word = sentence[ j - 1]
        key = (j-1, j)
        if not key in table:
            table[ key ] = {}
            bp[ key ] = {}
        for A in words[ word ]: # tag list
            table[ key ][A] = q2( ml, A, word ) 
            bp[ key ][A] = original_word 
        for i in reversed( range(0, (j-2)+1) ):
            for k in range(i+1, (j-1)+1 ):
                if (i,k) in table and (k,j) in table:
                    for B,pB in table[ (i,k) ].iteritems(): 
                        for C,pC in table[ (k,j) ].iteritems():
                            if (B, C) in bins:
                                if not ( i, j ) in table:
                                    table[(i,j)] = {}
                                    bp[(i,j)] = {}
                                for A in bins[ ( B, C ) ]:
                                    p = q1( ml, A, B, C) * pB * pC
                                    if (not A in table[(i,j)]) or (p > table[ (i, j) ][A]):
                                        table[ (i, j) ][A] = p
                                        bp[ (i,j) ][A] = (k, B, C)
    return table,bp


 
def get_element( set_ ):
    """return an element from the set"""
    for e in set_:
        return e

def replace_rare( words, word ):
    if word in words:
        return word
    return RARE


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
        #logging.warn( str(sentence) + " "+str(len(sentence)) )
        #print sentence
        #print 'len', len(sentence)
        (table, bp) = cky_prob2( sentence, words, bins )
        if False:
            for k,v in sorted( table.iteritems()):
                print "table", k, v
            for k,v in sorted( bp.iteritems()):
                print "bp",k, v
        print json.dumps( backtrack2(bp, (0, len( sentence )), 'SBARQ') )
                
        #hail( sentence, t)

        #for w in sentence:
        #    if not w in words:
        #        w = RARE
        #    print w
