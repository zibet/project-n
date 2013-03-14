import sys
import re
# map words x to labels y always picking the label with the highest
# count


# read lines like:
# 92 WORDTAG O reading
# 5 WORDTAG I-GENE reading

lines = open( "gene.counts" ).readlines()
re_line = re.compile( r'^(\d+) WORDTAG (\S+) (\S+)' ); 

# map af words til (map tag->count)
D = dict()

tagcounts = dict()
tagcounts[ 'O' ] = 0;
tagcounts[ 'I-GENE' ] = 0;


for line in lines:
    #print line
    match = re.match( re_line, line )
    if match:
        count = int( match.group(1) );
        tag = match.group( 2 );
        word = match.group( 3 )        
        d = dict()
        d[ tag ] = count;
        tagcounts[ tag ] += count
        if not word in D:
            D[ word ] = dict()
        D[ word ][ tag ] = count
        #print word , str( D[word] )
# produce lines like:
# nucleotidase I-GENE
# Pharmacologic O

#exit

lines = open( "gene.dev" ).readlines()

for wordline in lines:
    word = wordline.strip()
    if word == '':
        print
        continue
    try:
        d = D[ word ]
    except KeyError:
        d = D[ '_RARE_' ]
    tag = 0
    count = 0
    for t,c in d.iteritems():
        #print '>',word, t, c
        tagcount = tagcounts[ t ]
        ML = float(c) / tagcount
        if tagcount > count:
            tag = t
            count = tagcount 
    print word, tag


