#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division

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
    d = {}
    def insert( key, count ):
        if key in d:
            d[ key ] += count
        else:
            d[ key ] = count
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
            continue
        logging.fatal( "????"+line)
        raise invalid_line
    logging.warn( "lines: %s dict len: %s" % ( lines, len( d )))
    return d


if __name__ == "__main__":
    d = readCounts( "parser_train.counts.out" )
    #for k,v in d.iteritems():
        #print k, v
