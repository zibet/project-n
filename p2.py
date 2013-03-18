#!/usr/bin/python

from __future__ import division

import sys
import re
# map words x to labels y always picking the label with the highest
# count


# read lines like:
# 92 WORDTAG O reading
# 5 WORDTAG I-GENE reading

# 345128 1-GRAM O
# 13796 2-GRAM * *
# 1813 3-GRAM I-GENE O STOP

lines = open( "RARE.gene.count" ).readlines()

re_wordtag = re.compile( r'^(\d+) WORDTAG (\S+) (\S+)' ); 
re_gram = re.compile( r'^(\d+) ([123])-GRAM (.*)$' );



# map: (tag, word) -> count
emits = dict()

# map (a,b,b) -> count
grams = dict()

words = set() # know words

for line in lines:
    #print line
    wordtag_m = re.match( re_wordtag, line )
    if wordtag_m:
        count = int( wordtag_m.group(1) );
        tag = wordtag_m.group( 2 );
        word = wordtag_m.group( 3 )        
        words.add( word )
        emit = ( tag, word )
        assert( not emit in emits )
        emits[ emit ] = count
        #print 'EMIT', emit, count
        continue
    gram_m = re.match( re_gram, line )
    if gram_m:
        count = int( gram_m.group(1) );
        gtype = int( gram_m.group( 2 ) );
        tags = gram_m.group( 3 ).split(' ')        
        assert( len(tags) == gtype )
        gram = tuple( tags )
        grams[ gram ] = count
        print 'GRAM', gram, count
        continue
#exit()

lines = open( "gene.dev" ).readlines()

GENE = 'I-GENE'
O = 'O'
STAR = '*'
RARE = '_RARE_'
STOP = 'STOP'

def e( word, tag ):
    val = 0
    key = ( tag, word )
    if key in emits:
        val = emits[ key ]
    else:
        val = emits[ tag, RARE ]
    r = val / grams[ (tag,) ]
    print 'e()', word, tag, '=', r
    return r


def q(yi, yi_2, yi_1):
    """q(yi| yi_2, yi_1)"""
    r = grams[ (yi_2, yi_1, yi) ] / grams[ (yi_2, yi_1) ]
    print 'q()', yi, yi_2, yi_1, '=', r
    return r

def K( n ):
    if n <= 0:
        return ( STAR )
    else:
        return ( GENE, O)


# def pi( k, u, v,):
#     if k == 0:
#         assert(u == '*' and v = '*')
#         return 1
#     r = set()
#     for w in K( k - 2 ):
#         r.add( pi( k-1, w, u) * q(v, w, u) * e( x[k], v) )
#     return max( r )

bp = dict()

def pi( k, u, v, xs ):
    if ( k == 0 ):
        print "k {%s}, u {%s}, v {%s}" % ( k, u, v )
        return 1
    print "k {%s}, u {%s}, v {%s}, xk{%s}" % ( k, u, v, xs[k] )
    vs = dict() # value -> params
    for w in K( k-2 ):
        qq = q(v, w, u)
        ee = e(xs[k], v)
        print 'qq', qq, 'ee', ee
        vs[ pi( k-1, w, u, xs) * qq * ee ] = ( k, u, v) 
    maxx = max( vs.iterkeys() )
    #maxargs = vs[ maxx ]
    #bp[ ]
    #print 'MAXARGS', maxargs
    return maxx

pis = dict()

def viterbi( xs ):
    n = len( xs ) - 1
    for k in range(1, n+1 ):
        for u in K( k-1 ):
            for v in K( k ):
                t = pi( k, u, v, xs )
                key = (k, u, v) 
                print 'pi', key, "t", t
                pis[ key ] = t
    foos = set()
    for u in K( n-1 ):
        for v in K ( n ):
            foos.add( pis[ (n, u, v) ] * q( STOP, u, v) )
    print "VITERBI:", max( foos )

viterbi( [ 'IGNORE', 'Third', ',', 'consistent' ])



