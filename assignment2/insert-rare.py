import sys
import json
import cPickle
#tree = json.loads(open("tree.example").readline())
#print str(tree)

def atom( e ):
    return type( e ) == str or type( e ) == unicode

def words( t ):
    if atom( t[-1] ):
        if rewrite( t[-1] ):
            #print "# rewite:", t[-1]
            t[-1] = '_RARE_'
            
    else:
        for e in t[1:]:
            words( e )

infile = open("ordbog.pickle")
d = cPickle.load( infile )

def rewrite( word ):
    return d[ word ] < 5
        

for line in sys.stdin:
    tree = json.loads( line )
    words( tree )
    print json.dumps( tree )
    #print '================================='
