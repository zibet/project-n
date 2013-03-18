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
        #print 'GRAM', gram, count
        continue
#exit()

lines = open( "gene.dev" ).readlines()

GENE = 'I-GENE'
O = 'O'

def e( word, tag ):
    val = 0
    key = ( tag, word )
    if key in emits:
        val = emits[ key ]
    return val / grams[ (tag,) ]


for wordline in lines:
    word = wordline.strip()
    original = word
    if word == '':
        print
        continue
    # calculate e(word, I-GENE)
    # and e( word, O)
    if not word in words:
        word = '_RARE_'
    E_GENE = e( word, GENE )
    E_O = e( word, O )
    tag = O
    if E_GENE > E_O:
        tag = GENE
    print original, tag



