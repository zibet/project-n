#!/usr/bin/python

from __future__ import division

import sys
import re

emits = {}
grams = {}
words = set()

def read_counts( filename ):
    # read lines like:
    # 92 WORDTAG O reading
    # 5 WORDTAG I-GENE reading

    # 345128 1-GRAM O
    # 13796 2-GRAM * *
    # 1813 3-GRAM I-GENE O STOP

    lines = open( filename ).readlines()

    re_wordtag = re.compile( r'^(\d+) WORDTAG (\S+) (\S+)' ); 
    re_gram = re.compile( r'^(\d+) ([123])-GRAM (.*)$' );

    # map: (tag, word) -> count
    #emits = dict()

    # map (a)or (a,b) or (a,b,c) -> count
    #grams = dict()

    #words = set() # known words

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
            #print 'GRAM', gram, count
            continue
    #print "grams: ", str( grams )
    return emits, grams, words

def printer( d, name = '' ):
    for k,v in sorted( d.iteritems() ):
        print name, k, v

def print_counts():
    printer( grams, "GRAM" )
    printer( emits, "EMIT" )

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
    r = val / grams[ (tag,) ]
    print 'e( {%s} -> {%s} ) = {%f}' % (word, tag, r)
    return r

def q(yi, yi_2, yi_1):
    """q(yi| yi_2, yi_1)"""
    r = grams[ (yi_2, yi_1, yi) ] / grams[ (yi_2, yi_1) ]
    print 'q({%s}|{%s}, {%s}) = {%f}' % (yi, yi_2, yi_1, r)
    return r

def K( n ):
    if n <= 0:
        return ( STAR )
    else:
        return ( GENE, O)


#bp = dict()

def pi( k, u, v, xs ):
    if (k, u, v) in pis:
        #print "CACHED"
        print "k {%s}, u {%s}, v {%s} = {%s} [CACHED]" % ( k, u, v, pis[ (k, u, v)] )
        return pis[ (k, u, v)]
    if ( k == 0 ):
        print "pi({%s}, {%s}, {%s}) {%f} argmax = {%s}" % ( k, u, v, 1, '-')
        print "k {%s}, u {%s}, v {%s} = 1" % ( k, u, v )
        return 1
    #print "k {%s}, u {%s}, v {%s}, xk{%s}" % ( k, u, v, xs[k] )
    vs = dict() # value -> params
    for w in K( k-2 ):
        qq = q(v, w, u)
        ee = e(xs[k], v)
        #print 'qq', qq, 'ee', ee
        vs[ pi( k-1, w, u, xs) * qq * ee ] = w 
    maxx = max( vs.iterkeys() )
    pis[ (k, u, v) ] = maxx
    print "pi({%s}, {%s}, {%s}) {%f} argmax = {%s}" % ( k, u, v, pis[ (k, u, v)], vs[ maxx ] )
    bp[ (k, u, v)] = vs[ maxx ]
    return maxx

pis = dict()
bp = dict() # k -> { tags: (tags), value: n}


def viterbi( xs ):
    """read list of words, return list of corresponding tags"""
    ys = [ None for x in xs ]
    n = len( xs ) - 1
    for k in range(1, n+1 ):
        for u in K( k-1 ):
            for v in K( k ):
                pi( k, u, v, xs )
    value = 0
    for u in K( n-1 ):
        for v in K ( n ):
            val =  pis[ (n, u, v) ] * q( STOP, u, v)
            if val > value:
                ys[ n-1 ] = u
                ys[ n ] = v
    #print ys
    for k in reversed( range(1, (n-2) + 1) ):
        ys[ k ] = bp[ k+2, ys[ k+ 1], ys[ k+2 ] ] 
            #pis[ (4, v, STOP) ] = value
            #print "????", value, (n,u,v)
            #if not 4 in bp or bp[ 4 ]['value'] < value:
            #    bp[ 4 ] = { 'tags': (v, STOP), 'value': value }
    #print "VITERBI:", max( foos )
    #for k,v in bp.iteritems():
    #    print k, v
    #for k in sorted( pis.iterkeys() ):
    #    print k, pis[ k ]
    return ys

def viterbi_wrap( xs ):
    print "VITERBI START:", xs
    ys = viterbi( [None] + xs) 
    r = ys[ 1: ]
    print "VITERBI END:", xs, r
    return r

#viterbi( [ 'IGNORE', 'Third', ',', 'consistent' ])




def do():    
    read_counts( "RARE.gene.count" )

    #lines = open( "gene.dev" ).readlines()
    lines = open( "test-sentence" ).readlines()

    original = []
    sentence = []

    for wordline in lines:
        word = wordline.strip()
        if word == '':
            tags = viterbi_wrap( sentence )
            for (word, tag) in zip( original, tags):
                print word, tag
            original = []
            sentence = []
            print # copy empty line
            continue
        original.append( word )
        if not word in words:
            word = RARE
        sentence.append( word )

    if len( sentence ) > 0:
        tags = viterbi_wrap( sentence )
        for (word, tag) in zip( original, tags):
            print word, tag
        


