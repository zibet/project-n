#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import division


# sentence is list of words, tic is trigram dict with counts
def trigram_count_sentence( s, tic ):
    for i in range( 0, len( s ) - 2) :
        tri = (s[i], s[i+1], s[i+2])
        if not ( tri in tic ):
            tic[ tri ] = 1
        else:
            tic[ tri ] += 1
    return tic


# sentence is list of words, bid is bigram dict with counts
def bigram_count_sentence( s, bic ):
    for i in range( 0, len( s ) - 1) :
        bi = (s[i], s[i+1])
        if not ( bi in bic ):
            bic[ bi ] = 1
        else:
            bic[ bi ] += 1
    return bic

# ss: list of list of words
def bigram_counter( ss ):
    bic = {}
    for s in ss:
        bic = bigram_count_sentence( s, bic )
    print "bigram counts:"
    for k in sorted( bic.iterkeys() ):
        print k, bic[ k ]
    return bic

# ss: list of list of words
def trigram_counter( ss ):
    tic = {}
    for s in ss:
        tic = trigram_count_sentence( s, tic )
    print "trigram counts:"
    for k in sorted( tic.iterkeys() ):
        print k, tic[ k ]
    return tic

def unigram_counter( ss ):
    c = {}
    for s in ss:
        for w in s:
            if not w in c:
                c[ w ] = 1
            else:
                c[ w ] += 1
    print "unigram counts:"
    for k in sorted( c.iterkeys() ):
        print k, c[ k ]
    return c
    
# ss list of lists of [ taglist, words]
def emit_count( ss ):
    c = {}
    for tw in ss:
        tags = tw[0]
        words = tw[1]
        for tag, word in zip( tags, words):
            t = ( tag, word )
            if not t in c:
                c[ t ] = 1
            else:
                c[ t ] += 1
    print "emit counts:"
    for k in sorted( c.iterkeys() ):
        print k[0], '->', k[1], c[k]
    return c
    



if __name__ == "__main__":
    s1 = [ 'D', 'N', 'V', 'D', 'N']
    s2 = [ 'D', 'N', 'V', 'D', 'N']
    ss = [ s1, s2 ]

    w1 = [ 'the', 'dog', 'saw', 'the', 'cat']
    w2 = "the cat saw the saw".split(' ')
    print "w2:", w2

    unic = unigram_counter( ss )
    bic = bigram_counter( ss )
    tric = trigram_counter( ss )
    emitc = emit_count( [ [s1, w1], [s2, w2] ] )

    def q(s, u, v):
        cuvs = tric[ (u, v, s) ]
        cuv = bic[ (u, v)]
        r = cuvs/cuv
        print "q( {0} |, {1}, {2}) = {3}".format( s, u, v, r) 
        return r

    def emit( x, s):
        csx = emitc[ (s, x) ]
        cs = unic[ s ]
        print "csx", csx, 'cs', cs
        r = csx / cs
        print "e( {0} |, {1}) = {2}".format( x, s, r) 
        return r

    q( 'V', 'D', 'N')
    emit( 'the', 'D')
    emit( 'cat', 'N')
    emit( 'saw', 'N')
    emit( 'saw', 'V')
    emit( 'the', 'D')

    V = 'V'
    D = 'D'
    N = 'N'
    the = 'the'
    cat = 'cat'
    saw = 'saw'

    # the cat saw the saw
    #  D   N   V   D   N
    q1_6_qs = q( V, D, N) * q( D, N, V) * q( N, V, D)
    q1_6_es =  emit( 'the', 'D')**2 * emit( 'cat', 'N') *     emit( 'saw', 'V') *     emit( 'saw', 'N')
    q1_6 = q1_6_qs * q1_6_es
    print q1_6, q1_6_qs, q1_6_es

    print 'manual:', (0.5 * 0.5) * (0.5 * 0.25)
