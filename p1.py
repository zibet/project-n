#!/usr/bin/python

from __future__ import division

import sys
import re
import nlp


#Target: 
# correct 424 genes
# F1 0.256116

# map words x to labels y always picking the label with the highest
# count

# read lines like:
# 92 WORDTAG O reading
# 5 WORDTAG I-GENE reading

# 345128 1-GRAM O
# 13796 2-GRAM * *
# 1813 3-GRAM I-GENE O STOP

emits, grams, words = nlp.read_counts( "RARE.gene.count" )


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



