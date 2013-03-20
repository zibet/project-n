#!/usr/bin/python

from __future__ import division

import sys
import re
import nlp

#Target: 
# correct 424 genes
# F1 0.256116

nlp.read_counts( "RARE.gene.count" )

#lines = open( "gene.dev" ).readlines()

for wordline in sys.stdin:
    word = wordline.strip()
    original = word
    if word == '':
        print
        continue
    # calculate e(word, I-GENE)
    # and e( word, O)
    if not word in nlp.words:
        word = '_RARE_'
    E_GENE = nlp.e2( word, nlp.GENE )
    E_O = nlp.e2( word, nlp.O )
    tag = nlp.O
    if E_GENE > E_O:
        tag = nlp.GENE
    print original, tag



